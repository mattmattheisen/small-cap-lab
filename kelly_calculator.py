"""
Kelly Criterion Position Sizing Calculator
Calculates optimal position sizes based on win probability and win/loss ratios
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional

class KellyCalculator:
    """Kelly Criterion calculator for position sizing"""
    
    def __init__(self):
        self.default_fraction = 0.5  # Half Kelly recommended
    
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
        
        avg_win = abs(bull_stats.get('avg_return', 0))
        avg_loss = abs(bear_stats.get('avg_return', 0))
        
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
        applied_fraction: float = 0.5,
        stop_loss_pct: float = 0.05
    ) -> Dict:
        """
        Complete Kelly calculation from HMM results
        
        Args:
            regime_stats: Regime statistics from HMM
            current_regime_probs: Current regime probabilities
            portfolio_value: Portfolio value
            applied_fraction: Fractional Kelly multiplier
            stop_loss_pct: Stop loss percentage
            
        Returns:
            Complete Kelly analysis results
        """
        win_prob, win_prob_breakdown = self.calculate_win_probability_from_regime(
            regime_stats, current_regime_probs
        )
        
        avg_win, avg_loss, wl_breakdown = self.calculate_win_loss_ratio(regime_stats)
        
        kelly_fraction = self.calculate_kelly_fraction(win_prob, wl_breakdown['win_loss_ratio'])
        
        position_info = self.calculate_position_size(
            portfolio_value, kelly_fraction, applied_fraction, stop_loss_pct
        )
        
        risk_level = self.get_risk_level(position_info['applied_kelly'])
        
        return {
            'win_probability': win_prob,
            'win_prob_breakdown': win_prob_breakdown,
            'win_loss_breakdown': wl_breakdown,
            'kelly_fraction': kelly_fraction,
            'position_info': position_info,
            'risk_level': risk_level,
            'recommendation': self.get_recommendation(kelly_fraction, applied_fraction)
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
