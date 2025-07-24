"""
Professional Sharpe Ratio Calculator
Risk-adjusted performance analysis
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SharpeCalculator:
    """Professional Sharpe Ratio Calculator"""
    
    def __init__(self):
        # Default risk-free rate (10-year Treasury approximation)
        self.risk_free_rate = 0.045
        
    def calculate_simple_sharpe(self, symbols, weights, start_date, end_date, risk_free_rate=None):
        """Calculate Sharpe ratio for a portfolio"""
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Download data
        data = {}
        for symbol in symbols:
            try:
                stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                if stock_data is None or stock_data.empty:
                    raise ValueError(f"No data available for {symbol}")
                data[symbol] = stock_data['Adj Close']
            except Exception as e:
                raise ValueError(f"Error downloading {symbol}: {str(e)}")
        
        # Create portfolio dataframe
        portfolio_df = pd.DataFrame(data)
        portfolio_df = portfolio_df.dropna()
        
        if len(portfolio_df) < 30:
            raise ValueError("Insufficient data for reliable calculation")
        
        # Calculate daily returns
        returns = portfolio_df.pct_change().dropna()
        
        # Calculate portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Calculate metrics
        annual_return = portfolio_returns.mean() * 252
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Sharpe ratio
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Additional metrics
        cumulative_returns = (1 + portfolio_returns).cumprod()
        max_drawdown = self.calculate_max_drawdown(cumulative_returns)
        win_rate = (portfolio_returns > 0).mean()
        total_return = cumulative_returns.iloc[-1] - 1
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'risk_free_rate': risk_free_rate,
            'max_drawdown': abs(max_drawdown),
            'win_rate': win_rate,
            'total_return': total_return,
            'cumulative_returns': cumulative_returns,
            'num_observations': len(portfolio_returns)
        }
    
    def calculate_manual_sharpe(self, portfolio_return, portfolio_volatility, risk_free_rate):
        """Calculate Sharpe ratio from manual inputs"""
        
        if portfolio_volatility <= 0:
            raise ValueError("Portfolio volatility must be positive")
        
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_volatility,
            'risk_free_rate': risk_free_rate
        }
    
    def calculate_max_drawdown(self, cumulative_returns):
        """Calculate maximum drawdown"""
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        return drawdown.min()
    
    def get_sharpe_rating(self, sharpe_ratio):
        """Get Sharpe ratio rating and color"""
        if sharpe_ratio >= 2.0:
            return "Excellent", "#28a745"
        elif sharpe_ratio >= 1.5:
            return "Very Good", "#28a745"
        elif sharpe_ratio >= 1.0:
            return "Good", "#ffc107"
        elif sharpe_ratio >= 0.5:
            return "Acceptable", "#ffc107"
        elif sharpe_ratio >= 0.0:
            return "Poor", "#dc3545"
        else:
            return "Very Poor", "#dc3545"
    
    def get_benchmark_comparison(self, sharpe_ratio):
        """Get benchmark comparison text"""
        if sharpe_ratio >= 2.0:
            return "Outstanding performance - significantly outperforms most benchmarks"
        elif sharpe_ratio >= 1.5:
            return "Strong performance - beats most market indices"
        elif sharpe_ratio >= 1.0:
            return "Good performance - competitive with major indices"
        elif sharpe_ratio >= 0.5:
            return "Moderate performance - below average market returns"
        else:
            return "Poor performance - significantly underperforms benchmarks"
