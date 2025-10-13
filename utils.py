"""
Utility functions for the trading platform
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import yfinance as yf

def format_percentage(value, decimals=2):
    """Format a decimal as a percentage"""
    if pd.isna(value) or np.isinf(value):
        return "N/A"
    return f"{value:.{decimals}%}"

def format_number(value, decimals=2):
    """Format a number with specified decimal places"""
    if pd.isna(value) or np.isinf(value):
        return "N/A"
    return f"{value:.{decimals}f}"

def validate_date_range(start_date, end_date):
    """Validate date range inputs"""
    if start_date >= end_date:
        raise ValueError("Start date must be before end date")
    
    if end_date > datetime.now().date():
        raise ValueError("End date cannot be in the future")
    
    if (end_date - start_date).days < 30:
        raise ValueError("Date range must be at least 30 days")
    
    return True

def calculate_trading_days(start_date, end_date):
    """Calculate approximate number of trading days"""
    total_days = (end_date - start_date).days
    return int(total_days * 0.714)  # Approximate trading days ratio

def clean_numeric_data(data, fill_value=0):
    """Clean numeric data by handling NaN and infinite values"""
    if isinstance(data, pd.Series):
        data = data.fillna(fill_value)
        data = data.replace([np.inf, -np.inf], fill_value)
    elif isinstance(data, pd.DataFrame):
        data = data.fillna(fill_value)
        data = data.replace([np.inf, -np.inf], fill_value)
    elif isinstance(data, np.ndarray):
        data = np.nan_to_num(data, nan=fill_value, posinf=fill_value, neginf=fill_value)
    
    return data

def validate_portfolio_weights(weights):
    """Validate that portfolio weights sum to 1.0"""
    total_weight = sum(weights)
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(f"Portfolio weights must sum to 1.0, got {total_weight:.3f}")
    return True

def get_market_status():
    """Get current market status (simplified)"""
    now = datetime.now()
    if now.weekday() >= 5:  # Weekend
        return "Market Closed (Weekend)"
    elif now.hour < 9 or now.hour >= 16:  # Outside trading hours
        return "Market Closed"
    else:
        return "Market Open"

def calculate_annualized_metrics(returns, periods_per_year=252):
    """Calculate annualized return and volatility"""
    if len(returns) == 0:
        return 0, 0
    
    mean_return = returns.mean() * periods_per_year
    volatility = returns.std() * np.sqrt(periods_per_year)
    
    return mean_return, volatility

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0 or pd.isna(denominator) or np.isinf(denominator):
        return default
    return numerator / denominator

@st.cache_data(ttl=3600)
def get_stock_data_cached(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch stock data with 1-hour cache TTL to prevent stale data
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD format or datetime)
        end_date: End date (YYYY-MM-DD format or datetime)
        
    Returns:
        DataFrame with stock price data
    """
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if data is None or data.empty:
        return pd.DataFrame()
    return data

def clear_stock_data_cache():
    """Clear the stock data cache to force fresh data fetch"""
    get_stock_data_cached.clear()
    
def format_currency(value, decimals=2):
    """Format a value as currency (USD)"""
    if pd.isna(value) or np.isinf(value):
        return "N/A"
    if value >= 1_000_000:
        return f"${value/1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"${value/1_000:.{decimals}f}K"
    else:
        return f"${value:.{decimals}f}"
