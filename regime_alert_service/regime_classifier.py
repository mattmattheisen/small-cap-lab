"""
HMM-based Regime Classifier with Moving Average Fallback
Assigns Bull/Neutral/Bear labels to price series
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from sklearn.mixture import GaussianMixture
import warnings
warnings.filterwarnings('ignore')


class RegimeClassifier:
    """3-state HMM regime classifier with MA fallback"""
    
    def __init__(self, lookback_months: int = 9):
        self.lookback_months = lookback_months
        self.n_states = 3
    
    def classify_regime(self, prices: pd.Series) -> Tuple[str, float]:
        """
        Classify current regime for a price series
        
        Args:
            prices: Series of daily prices (index=dates, values=prices)
            
        Returns:
            Tuple of (regime_label, confidence)
            regime_label: 'Bull', 'Neutral', or 'Bear'
            confidence: probability of assigned state (0-1)
        """
        try:
            # Try HMM method first
            regime, confidence = self._hmm_regime(prices)
            return regime, confidence
        except Exception:
            # Fallback to MA trend proxy
            regime = self._ma_fallback(prices)
            return regime, 0.5  # Default confidence for fallback
    
    def _hmm_regime(self, prices: pd.Series) -> Tuple[str, float]:
        """
        3-state Gaussian HMM on daily returns
        Label states by mean return: lowest=Bear, middle=Neutral, highest=Bull
        """
        # Calculate daily returns
        returns = prices.pct_change().dropna()
        
        # Need at least 60 days for reliable HMM
        if len(returns) < 60:
            raise ValueError("Insufficient data for HMM")
        
        # Prepare features for GMM (using as HMM approximation)
        X = returns.values.reshape(-1, 1)
        
        # Fit 3-component Gaussian Mixture Model
        gmm = GaussianMixture(
            n_components=self.n_states,
            covariance_type='full',
            max_iter=100,
            random_state=42,
            n_init=3
        )
        gmm.fit(X)
        
        # Get state predictions
        states = gmm.predict(X)
        probabilities = gmm.predict_proba(X)
        
        # Get current state (last observation)
        current_state = states[-1]
        current_confidence = probabilities[-1, current_state]
        
        # Label states by mean return
        means = gmm.means_.flatten()
        sorted_indices = np.argsort(means)
        
        # Create mapping: lowest mean = Bear (0), middle = Neutral (1), highest = Bull (2)
        state_to_regime = {
            sorted_indices[0]: 'Bear',
            sorted_indices[1]: 'Neutral', 
            sorted_indices[2]: 'Bull'
        }
        
        regime = state_to_regime[current_state]
        
        return regime, current_confidence
    
    def _ma_fallback(self, prices: pd.Series) -> str:
        """
        Moving average trend proxy fallback
        Compare short MA (20-day) vs medium MA (50-day)
        """
        if len(prices) < 50:
            return 'Neutral'  # Not enough data
        
        # Calculate MAs
        ma_short = prices.rolling(20).mean().iloc[-1]
        ma_medium = prices.rolling(50).mean().iloc[-1]
        current_price = prices.iloc[-1]
        
        # Trend strength
        short_vs_medium = (ma_short - ma_medium) / ma_medium if ma_medium > 0 else 0
        price_vs_short = (current_price - ma_short) / ma_short if ma_short > 0 else 0
        
        # Classification thresholds
        if short_vs_medium > 0.02 and price_vs_short > 0:
            return 'Bull'
        elif short_vs_medium < -0.02 and price_vs_short < 0:
            return 'Bear'
        else:
            return 'Neutral'
