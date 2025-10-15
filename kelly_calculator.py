"""
Kelly Criterion Position Sizing Calculator with Transaction Costs
Upgraded: Adaptive Kelly with 0.15 base, transaction cost filtering, net edge calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import math

class KellyCalculator:
    """Kelly Criterion calculator with transaction cost filtering"""
    
    # Conservative base Kelly - multiplied by confidence and volatility adjustments
    BASE_KELLY = 0.15
    
    def __init__(self):
        self.default_fraction = 0.5  # Half Kelly recommended
    
    def calculate_transaction_costs(
        self,
        high: float,
        low: float, 
        close: float,
        volume: float,
        position_size_dollars: float
    ) -> Dict:
        """
        Estimate transaction costs in basis points
        
        Args:
            high: Day's high price
            low: Day's low price
            close: Day's close price
            volume: Day's volume
            position_size_dollars: Intended position size in dollars
            
        Returns:
            Dictionary with cost breakdown in basis points
        """
        # Estimate bid-ask spread from daily range
        # Use half the intraday range as spread proxy
        if close > 0:
            spread_bps = ((high - low) / close) * 10000 * 0.5
        else:
            spread_bps = 50  # Default 50 bps if no data
        
        # Calculate 20-day average dollar volume (use current as proxy)
        adv20 = volume * close if volume > 0 and close > 0 else 1000000  # $1M default
        
        # Market impact cost: 50 * sqrt(position / adv20)
        if adv20 > 0:
            impact_cost = 50 * math.sqrt(position_size_dollars / adv20)
        else:
            impact_cost = 25  # Default 25 bps
        
        # Slippage estimate
        slippage = 5  # 5 bps constant
        
        # Total round-trip cost (entry + exit)
        total_round_trip = 2 * (spread_bps + impact_cost + slippage)
        
        return {
            'spread_bps': spread_bps,
            'impact_bps': impact_cost,
            'slippage_bps': slippage,
            'total_round_trip_bps': total_round_trip,
            'total_round_trip_pct': total_round_trip / 10000
        }
    
    def calculate_net_edge(
        self,
        gross_edge: float,
        tx_cost_bps: float,
        holding_days: int = 5
    ) -> Dict:
        """
        Calculate net edge after transaction costs and edge decay
        
        Args:
            gross_edge: Gross edge before costs (as fraction, e.g., 0.023 for 2.3%)
            tx_cost_bps: Transaction costs in basis points
            holding_days: Expected holding period (default 5 days)
            
        Returns:
            Dictionary with edge breakdown
        """
        # Assumed 5-day holding period based on typical regime duration
        # Edge decays over time: gross * exp(-0.15 * days)
        decay_factor = math.exp(-0.15 * holding_days)
        decayed_edge = gross_edge * decay_factor
        
        # Convert tx cost to fraction
        tx_cost_fraction = tx_cost_bps / 10000
        
        # Net edge after costs
        net_edge = decayed_edge - tx_cost_fraction
        
        return {
            'gross_edge': gross_edge,
            'decay_factor': decay_factor,
            'decayed_edge': decayed_edge,
            'tx_cost_pct': tx_cost_fraction,
            'net_edge': max(net_edge, 0.0),  # Can't be negative
            'tradeable': net_edge > 0
        }
    
    def calculate_adaptive_kelly(
        self,
        confidence: float,
        atr_pct: float,
        base: Optional[float] = None
    ) -> float:
        """
        Calculate adaptive Kelly sizing based on confidence and volatility
        
        Args:
            confidence: Regime confidence (0-100)
            atr_pct: Average True Range as percentage (volatility measure)
            base: Base Kelly fraction (default 0.15)
            
        Returns:
            Adaptive Kelly fraction, capped at 0.25
        """
        if base is None:
            base = self.BASE_KELLY
        
        # Scale by confidence (0-100 scale)
        confidence_mult = confidence / 100
        
        # Scale inversely by volatility
        # Target: 5% ATR = 1.0x, higher ATR reduces sizing
        if atr_pct > 0:
            volatility_mult = min(1.0, 0.05 / atr_pct)
        else:
            volatility_mult = 0.5  # Default if no ATR data
        
        # Adaptive Kelly = base * confidence * vol_adjustment
        adaptive_kelly = base * confidence_mult * volatility_mult
        
        # Cap at 25% maximum
        return min(adaptive_kelly, 0.25)
    
    def calculate_atr_percentage(self, price_data: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range as percentage of price
        
        Args:
            price_data: DataFrame with High, Low, Close columns
            period: ATR period (default 14)
            
        Returns:
            ATR as percentage of close price
        """
        if len(price_data) < period:
            return 0.05  # Default 5% if insufficient data
        
        try:
            # True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
            high = price_data['High']
            low = price_data['Low']
            close = price_data['Close']
            
            prev_close = close.shift(1)
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR = moving average of True Range
            atr_series = tr.rolling(window=period).mean()
            atr = float(atr_series.iloc[-1]) if len(atr_series) > 0 else 0.05
            
            # ATR as percentage of close
            current_close = float(close.iloc[-1]) if len(close) > 0 else 1.0
            atr_pct = atr / current_close if current_close > 0 else 0.05
            
            return atr_pct
        except:
            return 0.05  # Default on error
    
    def calculate_win_probability_from_regime(
        self, 
        regime_stats: Dict,
        current_regime_probs: np.ndarray
    ) -> Tuple[float, Dict]:
        """
        Calculate win probability using hybrid approach:
        p_win = (bull_prob × bull_win_rate) + (sideways_prob × sideways_win_rate)
        
        Args:
            regime_stats: Dictionary with regime statistics
            current_regime_probs: Array of probabilities for each regime
            
        Returns:
            win_probability: Combined win probability
            breakdown: Dictionary with calculation breakdown
        """
        bull_prob = current_regime_probs[2] if len(current_regime_probs) > 2 else 0
        sideways_prob = current_regime_probs[1] if len(current_regime_probs) > 1 else 0
        bear_prob = current_regime_probs[0] if len(current_regime_probs) > 0 else 0
        
        bull_win_rate = regime_stats.get(2, {}).get('win_rate', 0) / 100
        sideways_win_rate = regime_stats.get(1, {}).get('win_rate', 0) / 100
        
        win_probability = (bull_prob * bull_win_rate) + (sideways_prob * sideways_win_rate)
        
        breakdown = {
            'bull_prob': bull_prob,
            'bull_win_rate': bull_win_rate,
            'sideways_prob': sideways_prob,
            'sideways_win_rate': sideways_win_rate,
            'bear_prob': bear_prob,
            'combined_win_prob': win_probability
        }
        
        return win_probability, breakdown
    
    def calculate_win_loss_ratio(self, regime_stats: Dict) -> Tuple[float, float, Dict]:
        """
        Calculate win/loss ratio using conditional averages:
        avg_win = mean of all positive return days in Bull regime
        avg_loss = mean of all negative return days in Bear regime
        
        Args:
            regime_stats: Dictionary with regime statistics
            
        Returns:
            avg_win: Average win amount (positive returns)
            avg_loss: Average loss amount (absolute value of negative returns)
            breakdown: Dictionary with calculation details
        """
        bull_stats = regime_stats.get(2, {})
        bear_stats = regime_stats.get(0, {})
        
        # Use conditional averages: only positive returns from Bull, only negative returns from Bear
        avg_win = bull_stats.get('avg_positive_return', 0)
        avg_loss = bear_stats.get('avg_negative_return', 0)
        
        # Fallback to overall avg_return if conditional averages not available
        if avg_win == 0:
            avg_win = abs(bull_stats.get('avg_return', 0))
        if avg_loss == 0:
            avg_loss = abs(bear_stats.get('avg_return', 0))
        
        # Ensure we don't divide by zero
        if avg_loss == 0:
            avg_loss = 0.01
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        breakdown = {
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio
        }
        
        return avg_win, avg_loss, breakdown
    
    def calculate_kelly_fraction(
        self, 
        win_probability: float,
        win_loss_ratio: float
    ) -> float:
        """
        Calculate Kelly Criterion fraction using the formula:
        f* = (p * b - q) / b
        
        Where:
        p = win probability
        q = loss probability (1 - p)
        b = win/loss ratio (avg_win / avg_loss)
        
        Args:
            win_probability: Probability of winning
            win_loss_ratio: Ratio of average win to average loss
            
        Returns:
            kelly_fraction: Optimal Kelly percentage (0 to 1)
        """
        if win_probability <= 0 or win_loss_ratio <= 0:
            return 0
        
        p = win_probability
        q = 1 - p
        b = win_loss_ratio
        
        kelly_fraction = (p * b - q) / b
        
        # Apply BASE_KELLY reduction (0.15 multiplier)
        kelly_fraction = kelly_fraction * self.BASE_KELLY
        
        kelly_fraction = max(0, min(kelly_fraction, 1.0))
        
        return kelly_fraction
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        kelly_fraction: float,
        applied_fraction: float = 0.5,
        stop_loss_pct: float = 0.05
    ) -> Dict:
        """
        Calculate actual position size and risk metrics
        
        Args:
            portfolio_value: Total portfolio value in dollars
            kelly_fraction: Full Kelly fraction (f*)
            applied_fraction: Fraction of Kelly to use (default 0.5 for half-Kelly)
            stop_loss_pct: Stop loss percentage (default 5%)
            
        Returns:
            Dictionary with position sizing details
        """
        applied_kelly = kelly_fraction * applied_fraction
        
        risk_budget = portfolio_value * applied_kelly
        
        position_size = risk_budget / stop_loss_pct if stop_loss_pct > 0 else risk_budget
        
        return {
            'full_kelly_fraction': kelly_fraction,
            'applied_fraction': applied_fraction,
            'applied_kelly': applied_kelly,
            'portfolio_value': portfolio_value,
            'risk_budget': risk_budget,
            'position_size': position_size,
            'stop_loss_pct': stop_loss_pct,
            'stop_loss_amount': position_size * stop_loss_pct
        }
    
    def calculate_from_hmm_results(
        self,
        regime_stats: Dict,
        current_regime_probs: np.ndarray,
        portfolio_value: float,
        price_data: pd.DataFrame,
        applied_fraction: float = 0.5,
        stop_loss_pct: float = 0.05,
        regime_multiplier: float = 1.0
    ) -> Dict:
        """
        Complete Kelly calculation from HMM results with transaction costs
        
        Args:
            regime_stats: Regime statistics from HMM
            current_regime_probs: Current regime probabilities
            portfolio_value: Portfolio value
            price_data: Price data for ATR and transaction cost calculations
            applied_fraction: Fractional Kelly multiplier
            stop_loss_pct: Stop loss percentage
            regime_multiplier: Risk multiplier from regime transition detection (default 1.0)
            
        Returns:
            Complete Kelly analysis results with transaction costs
        """
        # Calculate win probability and ratios
        win_prob, win_prob_breakdown = self.calculate_win_probability_from_regime(
            regime_stats, current_regime_probs
        )
        
        avg_win, avg_loss, wl_breakdown = self.calculate_win_loss_ratio(regime_stats)
        
        # Calculate ATR for adaptive sizing
        atr_pct = self.calculate_atr_percentage(price_data)
        
        # Get regime confidence (highest probability)
        confidence = max(current_regime_probs) * 100
        
        # Calculate base Kelly
        kelly_fraction = self.calculate_kelly_fraction(win_prob, wl_breakdown['win_loss_ratio'])
        
        # Apply adaptive Kelly adjustment
        adaptive_kelly = self.calculate_adaptive_kelly(confidence, atr_pct)
        
        # Use the more conservative of the two
        final_kelly = min(kelly_fraction, adaptive_kelly)
        
        # Apply regime transition multiplier
        final_kelly = final_kelly * regime_multiplier
        
        # Calculate position size
        position_info = self.calculate_position_size(
            portfolio_value, final_kelly, applied_fraction, stop_loss_pct
        )
        
        # Calculate transaction costs
        try:
            latest = price_data.iloc[-1]
            tx_costs = self.calculate_transaction_costs(
                latest['High'],
                latest['Low'],
                latest['Close'],
                latest['Volume'],
                position_info['position_size']
            )
        except:
            tx_costs = {
                'spread_bps': 50,
                'impact_bps': 25,
                'slippage_bps': 5,
                'total_round_trip_bps': 160,
                'total_round_trip_pct': 0.016
            }
        
        # Calculate gross edge (from win probability and win/loss ratio)
        gross_edge = win_prob * avg_win - (1 - win_prob) * avg_loss
        
        # Calculate net edge after costs
        edge_analysis = self.calculate_net_edge(
            gross_edge,
            tx_costs['total_round_trip_bps'],
            holding_days=5
        )
        
        # Final filter: only recommend if net edge > 0
        if not edge_analysis['tradeable']:
            final_kelly = 0
            position_info['applied_kelly'] = 0
            position_info['position_size'] = 0
            position_info['risk_budget'] = 0
        
        risk_level = self.get_risk_level(position_info['applied_kelly'])
        
        return {
            'win_probability': win_prob,
            'win_prob_breakdown': win_prob_breakdown,
            'win_loss_breakdown': wl_breakdown,
            'kelly_fraction': final_kelly,
            'position_info': position_info,
            'risk_level': risk_level,
            'recommendation': self.get_recommendation(final_kelly, applied_fraction),
            'transaction_costs': tx_costs,
            'edge_analysis': edge_analysis,
            'atr_pct': atr_pct,
            'confidence': confidence,
            'regime_multiplier': regime_multiplier
        }
    
    def get_risk_level(self, applied_kelly: float) -> Dict:
        """
        Get risk level based on applied Kelly percentage
        
        Args:
            applied_kelly: Applied Kelly fraction
            
        Returns:
            Dictionary with risk level info
        """
        pct = applied_kelly * 100
        
        if pct <= 25:
            return {
                'level': 'Conservative',
                'color': 'green',
                'emoji': '🟢',
                'description': 'Safe, lower growth potential'
            }
        elif pct <= 50:
            return {
                'level': 'Moderate',
                'color': 'yellow',
                'emoji': '🟡',
                'description': 'OPTIMAL ZONE - Half Kelly recommended'
            }
        elif pct <= 75:
            return {
                'level': 'Aggressive',
                'color': 'orange',
                'emoji': '🟠',
                'description': 'Higher risk, higher volatility'
            }
        else:
            return {
                'level': 'Very Aggressive',
                'color': 'red',
                'emoji': '🔴',
                'description': 'Danger zone - excessive risk'
            }
    
    def get_recommendation(self, kelly_fraction: float, applied_fraction: float) -> str:
        """Generate recommendation text"""
        if kelly_fraction <= 0:
            return "⚠️ No edge detected - avoid position or wait for better setup"
        
        applied_kelly = kelly_fraction * applied_fraction
        
        if applied_kelly > 0.75:
            return "🛑 Position too aggressive - consider reducing to 25-50% range"
        elif applied_kelly > 0.5:
            return "⚠️ Above optimal zone - consider using Half Kelly (0.5x) for lower volatility"
        elif applied_kelly >= 0.25:
            return "✅ In optimal zone - Half Kelly provides good growth with manageable risk"
        else:
            return "💡 Conservative sizing - safe but slower growth potential"
    
    def calculate_manual_kelly(
        self,
        win_probability: float,
        avg_win_pct: float,
        avg_loss_pct: float,
        portfolio_value: float,
        applied_fraction: float = 0.5,
        stop_loss_pct: float = 0.05
    ) -> Dict:
        """
        Manual Kelly calculation with user inputs
        
        Args:
            win_probability: Win probability (0 to 1)
            avg_win_pct: Average win percentage
            avg_loss_pct: Average loss percentage (positive number)
            portfolio_value: Portfolio value
            applied_fraction: Fractional Kelly
            stop_loss_pct: Stop loss percentage
            
        Returns:
            Kelly calculation results
        """
        win_loss_ratio = avg_win_pct / avg_loss_pct if avg_loss_pct > 0 else 0
        
        kelly_fraction = self.calculate_kelly_fraction(win_probability, win_loss_ratio)
        
        position_info = self.calculate_position_size(
            portfolio_value, kelly_fraction, applied_fraction, stop_loss_pct
        )
        
        risk_level = self.get_risk_level(position_info['applied_kelly'])
        
        return {
            'win_probability': win_probability,
            'win_loss_ratio': win_loss_ratio,
            'kelly_fraction': kelly_fraction,
            'position_info': position_info,
            'risk_level': risk_level,
            'recommendation': self.get_recommendation(kelly_fraction, applied_fraction)
        }
