"""
Data loaders for IFO system
Handles institutional holdings, short interest, and staleness checks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple


class InstitutionalDataLoader:
    """Load and process institutional holdings data"""
    
    def __init__(self, csv_path: str = 'data/institutional_holdings.csv'):
        self.csv_path = csv_path
        self.data = None
        self._load_data()
    
    def _load_data(self):
        """Load CSV file"""
        try:
            self.data = pd.read_csv(self.csv_path)
            self.data['quarter_end'] = pd.to_datetime(self.data['quarter_end'])
        except FileNotFoundError:
            print(f"Warning: {self.csv_path} not found. Institutional holdings disabled.")
            self.data = None
    
    def get_holdings_change(
        self,
        ticker: str,
        as_of_date: datetime,
        staleness_days: int = 180
    ) -> Tuple[Optional[float], bool]:
        """
        Get quarterly institutional holdings % change (Z_H)
        
        Returns:
            (Z_H value, is_stale)
        """
        if self.data is None or ticker not in self.data['ticker'].values:
            return None, False
        
        # Get ticker history
        ticker_data = self.data[self.data['ticker'] == ticker].copy()
        ticker_data = ticker_data.sort_values('quarter_end')
        
        # Check staleness
        latest_quarter = ticker_data['quarter_end'].max()
        days_since_latest = (as_of_date - latest_quarter).days
        is_stale = days_since_latest > staleness_days
        
        if is_stale or len(ticker_data) < 2:
            return None, is_stale
        
        # Calculate quarterly % changes
        ticker_data['pct_change'] = ticker_data['inst_hold_pct'].pct_change()
        
        # Get last 12 quarters for z-score window
        if len(ticker_data) > 12:
            window = ticker_data.tail(12)
        else:
            window = ticker_data
        
        # Calculate z-score of most recent change
        recent_change = ticker_data['pct_change'].iloc[-1]
        
        if pd.isna(recent_change):
            return None, is_stale
        
        mean_change = window['pct_change'].mean()
        std_change = window['pct_change'].std()
        
        if std_change == 0 or pd.isna(std_change):
            z_h = 0.0
        else:
            z_h = (recent_change - mean_change) / std_change
        
        return float(z_h), is_stale


class ShortInterestLoader:
    """
    Placeholder for short interest data
    Phase 1A: Returns None (disabled)
    """
    
    def __init__(self):
        self.data = None
    
    def get_dtc_change(
        self,
        ticker: str,
        as_of_date: datetime
    ) -> Optional[float]:
        """
        Get Z_DTC (standardized days-to-cover improvement)
        
        Phase 1A: Always returns None
        """
        return None
