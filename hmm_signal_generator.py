"""
Hidden Markov Model Signal Generator
Regime detection and trading signal generation
"""

import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from pattern_utils import compute_cdl, latest_signal, get_pattern_summary, combine_with_hmm_signal
import warnings
warnings.filterwarnings('ignore')

class HMMSignalGenerator:
    """HMM Signal Generator with regime detection"""
    
    def __init__(self, n_states=3):
        self.n_states = n_states
        self.model = None
        self.scaler = StandardScaler()
        self.regime_names = {0: 'Bear', 1: 'Sideways', 2: 'Bull'}
        self.regime_colors = {0: '#dc3545', 1: '#ffc107', 2: '#28a745'}
        self.regime_icons = {0: '📉', 1: '➡️', 2: '📈'}
    
    def prepare_features(self, data):
        """Feature preparation with error handling"""
        if len(data) < 60:
            raise ValueError("Need at least 60 days of data")
        
        # Handle MultiIndex columns from yfinance
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        
        # Extract price and volume as Series and ensure they're 1D
        close_prices = data['Close'].squeeze()
        volume = data['Volume'].squeeze()
        
        # Calculate basic features
        returns = close_prices.pct_change()
        volatility = returns.rolling(window=20, min_periods=1).std()
        
        # Volume features
        volume_ma = volume.rolling(window=20, min_periods=1).mean()
        volume_ratio = volume / volume_ma
        
        # Momentum
        momentum = close_prices.pct_change(10)
        
        # Simple RSI
        rsi = self.calculate_rsi(close_prices)
        
        # Create features DataFrame
        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility,
            'volume_ratio': volume_ratio,
            'momentum': momentum,
            'rsi': rsi
        })
        
        # Clean the data
        features = features.fillna(0)
        features = features.replace([np.inf, -np.inf], 0)
        
        # Remove first 30 rows for stability
        features_clean = features.iloc[30:].copy()
        
        if len(features_clean) < 50:
            raise ValueError("Insufficient clean data")
        
        return features_clean
    
    def calculate_rsi(self, prices):
        """RSI calculation with proper error handling"""
        # Convert Series to numpy array first, then to list
        if hasattr(prices, 'values'):
            price_array = prices.values.flatten()
        else:
            price_array = np.array(prices).flatten()
        
        price_list = price_array.tolist()
        
        if len(price_list) < 15:
            return pd.Series([50] * len(price_list), index=prices.index)
        
        # Calculate RSI using the list
        rsi_values = []
        period = 14
        
        for i in range(len(price_list)):
            if i < period:
                rsi_values.append(50)
            else:
                # Calculate price changes
                changes = []
                for j in range(i - period + 1, i + 1):
                    if j > 0:
                        changes.append(price_list[j] - price_list[j-1])
                
                if not changes:
                    rsi_values.append(50)
                    continue
                
                # Gains and losses
                gains = [c for c in changes if c > 0]
                losses = [-c for c in changes if c < 0]
                
                avg_gain = sum(gains) / len(changes) if gains else 0
                avg_loss = sum(losses) / len(changes) if losses else 0
                
                if avg_loss == 0:
                    rsi_values.append(100)
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    rsi_values.append(rsi)
        
        return pd.Series(rsi_values, index=prices.index)
    
    def fit_model(self, features):
        """Fit HMM model"""
        try:
            # Convert to numpy array safely
            feature_values = features.values
            
            # Clean any remaining issues
            feature_values = np.nan_to_num(feature_values, nan=0, posinf=1, neginf=-1)
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_values)
            
            # Fit model
            self.model = GaussianMixture(
                n_components=self.n_states,
                covariance_type='diag',
                random_state=42,
                max_iter=100
            )
            
            self.model.fit(scaled_features)
            
            # Get predictions
            states = self.model.predict(scaled_features)
            probabilities = self.model.predict_proba(scaled_features)
            
            # Sort regimes by average return
            regime_returns = {}
            for regime in range(self.n_states):
                mask = states == regime
                if np.sum(mask) > 0:
                    regime_returns[regime] = features.loc[features.index[mask], 'returns'].mean()
                else:
                    regime_returns[regime] = 0
            
            # Create mapping: Bear=0, Sideways=1, Bull=2
            sorted_regimes = sorted(regime_returns.items(), key=lambda x: x[1])
            regime_mapping = {old: new for new, (old, _) in enumerate(sorted_regimes)}
            
            # Remap states
            remapped_states = np.array([regime_mapping[state] for state in states])
            
            # Remap probabilities
            remapped_probs = np.zeros_like(probabilities)
            for old_regime, new_regime in regime_mapping.items():
                remapped_probs[:, new_regime] = probabilities[:, old_regime]
            
            return remapped_states, remapped_probs
            
        except Exception as e:
            raise ValueError(f"Model fitting failed: {str(e)}")
    
    def analyze_regimes(self, features, states, probabilities):
        """Analyze regime characteristics"""
        regime_stats = {}
        
        for regime in range(self.n_states):
            mask = states == regime
            if np.sum(mask) > 0:
                regime_features = features.iloc[mask]
                
                regime_stats[regime] = {
                    'name': self.regime_names[regime],
                    'icon': self.regime_icons[regime],
                    'color': self.regime_colors[regime],
                    'days': int(np.sum(mask)),
                    'percentage': float(np.sum(mask) / len(states) * 100),
                    'avg_return': float(regime_features['returns'].mean() * 100),
                    'volatility': float(regime_features['returns'].std() * 100),
                    'persistence': self.calculate_persistence(states, regime)
                }
        
        return regime_stats
    
    def calculate_persistence(self, states, regime):
        """Calculate regime persistence"""
        if len(states) < 2:
            return 0.0
        
        same_transitions = 0
        total_regime_days = 0
        
        for i in range(1, len(states)):
            if states[i-1] == regime:
                total_regime_days += 1
                if states[i] == regime:
                    same_transitions += 1
        
        return (same_transitions / total_regime_days * 100) if total_regime_days > 0 else 0.0
    
    def generate_signal(self, current_regime, confidence, regime_stats, data=None):
        """Generate trading signal with optional candlestick pattern enhancement"""
        regime_name = self.regime_names[current_regime]
        
        # Base HMM signal
        if confidence >= 0.7:
            if regime_name == 'Bull':
                base_signal = 'BUY'
                strength = min(10, max(6, int(confidence * 12)))
            elif regime_name == 'Bear':
                base_signal = 'SELL'
                strength = min(10, max(6, int(confidence * 12)))
            else:
                base_signal = 'HOLD'
                strength = max(3, int(confidence * 8))
        else:
            base_signal = 'HOLD'
            strength = max(1, int(confidence * 6))
        
        result = {
            'signal': base_signal,
            'strength': strength,
            'regime': regime_name,
            'confidence': confidence * 100,
            'regime_stats': regime_stats.get(current_regime, {}),
            'pattern_signal': None,
            'combined_signal': None,
            'pattern_summary': None
        }
        
        # Add candlestick pattern analysis if data is provided
        if data is not None and len(data) > 0:
            try:
                # Compute candlestick patterns
                data_with_patterns = compute_cdl(data)
                
                # Get latest pattern signal
                pattern_signal = latest_signal(data_with_patterns)
                
                # Get pattern summary
                pattern_summary = get_pattern_summary(data_with_patterns, lookback_days=30)
                
                # Combine HMM and pattern signals
                combined_signal = combine_with_hmm_signal(base_signal, confidence, pattern_signal)
                
                # Update result with pattern information
                result.update({
                    'pattern_signal': pattern_signal,
                    'combined_signal': combined_signal,
                    'pattern_summary': pattern_summary
                })
                
            except Exception as e:
                print(f"Error in pattern analysis: {e}")
                # Continue with base HMM signal if pattern analysis fails
        
        return result
