"""
Regime Detection Service
Pulls prices, assigns regimes, detects changes, sends alerts
"""

import os
import json
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from regime_classifier import RegimeClassifier


class RegimeService:
    """Main service for regime detection and alerting"""
    
    def __init__(
        self,
        universe_path: str = 'config/universe.txt',
        prev_state_path: str = 'data/hmm_prev.json',
        output_dir: str = 'out'
    ):
        self.universe_path = universe_path
        self.prev_state_path = prev_state_path
        self.output_dir = output_dir
        self.classifier = RegimeClassifier(lookback_months=9)
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(prev_state_path), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
    
    def load_universe(self) -> List[str]:
        """Load ticker symbols from universe file"""
        with open(self.universe_path, 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
        return tickers
    
    def fetch_prices(self, symbol: str, months: int = 9) -> pd.Series:
        """
        Fetch historical prices for a symbol
        
        Returns:
            Series with dates as index, adjusted close as values
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            raise ValueError(f"No data for {symbol}")
        
        # Return adjusted close prices
        prices = hist['Close']
        return prices
    
    def load_previous_regimes(self) -> Dict[str, str]:
        """Load previous regime states from JSON"""
        if not os.path.exists(self.prev_state_path):
            return {}
        
        with open(self.prev_state_path, 'r') as f:
            return json.load(f)
    
    def save_regimes(self, regimes: Dict[str, str]):
        """Save current regime states to JSON"""
        with open(self.prev_state_path, 'w') as f:
            json.dump(regimes, f, indent=2)
    
    def detect_regimes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Main detection logic
        
        Returns:
            Tuple of (today_regimes_df, changes_df)
        """
        tickers = self.load_universe()
        previous_regimes = self.load_previous_regimes()
        
        results = []
        changes = []
        current_regimes = {}
        
        for symbol in tickers:
            try:
                # Fetch prices
                prices = self.fetch_prices(symbol, months=9)
                last_price = prices.iloc[-1]
                
                # Classify regime
                regime, confidence = self.classifier.classify_regime(prices)
                
                # Record current regime
                current_regimes[symbol] = regime
                
                # Add to results
                results.append({
                    'symbol': symbol,
                    'last_price': round(last_price, 2),
                    'regime': regime,
                    'confidence': round(confidence, 3),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Check for regime change
                if symbol in previous_regimes:
                    prev_regime = previous_regimes[symbol]
                    if prev_regime != regime:
                        changes.append({
                            'symbol': symbol,
                            'from_regime': prev_regime,
                            'to_regime': regime,
                            'timestamp': datetime.now().isoformat()
                        })
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
        
        # Save current regimes for next run
        self.save_regimes(current_regimes)
        
        # Create DataFrames
        today_df = pd.DataFrame(results)
        changes_df = pd.DataFrame(changes)
        
        return today_df, changes_df
    
    def write_outputs(self, today_df: pd.DataFrame, changes_df: pd.DataFrame):
        """Write CSV outputs"""
        today_path = os.path.join(self.output_dir, 'today_regimes.csv')
        changes_path = os.path.join(self.output_dir, 'changes.csv')
        
        today_df.to_csv(today_path, index=False)
        print(f"Wrote {len(today_df)} regimes to {today_path}")
        
        if not changes_df.empty:
            changes_df.to_csv(changes_path, index=False)
            print(f"Wrote {len(changes_df)} changes to {changes_path}")
    
    def send_alert(self, changes_df: pd.DataFrame, force: bool = False):
        """
        Send webhook alert for regime changes
        
        Args:
            changes_df: DataFrame with regime changes
            force: If True, send alert even without changes
        """
        webhook_url = os.getenv('ALERT_WEBHOOK_URL')
        
        # Build alert message
        if changes_df.empty and not force:
            return  # No changes, no alert
        
        if changes_df.empty:
            message = "No regime changes today"
        else:
            lines = ["Regime changes:"]
            for _, row in changes_df.iterrows():
                lines.append(f"{row['symbol']}: {row['from_regime']} → {row['to_regime']}")
            message = "\n".join(lines)
        
        # Send or print
        if webhook_url:
            try:
                payload = {"text": message}
                response = requests.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
                print(f"Alert sent: {len(changes_df)} changes")
            except Exception as e:
                print(f"Failed to send alert: {e}")
                print(f"Alert message:\n{message}")
        else:
            print(f"No ALERT_WEBHOOK_URL set. Alert message:\n{message}")
    
    def print_summary(self, today_df: pd.DataFrame, changes_df: pd.DataFrame):
        """Print console summary"""
        if today_df.empty:
            print("No regimes detected")
            return
        
        # Count by regime
        counts = today_df['regime'].value_counts()
        bull = counts.get('Bull', 0)
        neutral = counts.get('Neutral', 0)
        bear = counts.get('Bear', 0)
        
        print("\n" + "="*50)
        print("REGIME SUMMARY")
        print("="*50)
        print(f"Total symbols: {len(today_df)}")
        print(f"Bull: {bull} | Neutral: {neutral} | Bear: {bear}")
        print(f"Changes detected: {len(changes_df)}")
        print("="*50 + "\n")
