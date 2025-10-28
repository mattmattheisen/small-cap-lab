"""
Universe Management System - CSV-based ticker universe with filtering and prioritization
"""

import pandas as pd
import json
import os
from typing import List, Dict, Tuple, Optional


class UniverseLoader:
    """Load and filter ticker universe from CSV"""
    
    def __init__(self, config_path: str = 'config/universe_config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        self.csv_path = 'data/universe.csv'
        self.exclusions = []
    
    def _load_config(self) -> dict:
        """Load configuration, create with defaults if missing"""
        if not os.path.exists(self.config_path):
            # Create default config
            default_config = {
                "max_tickers": 350,
                "filters": {
                    "min_price": 2.0,
                    "min_avg_vol_30d": 200000,
                    "market_cap_min_musd": 200,
                    "market_cap_max_musd": 5000,
                    "exchanges_allow": ["NYSE", "NASDAQ", "AMEX"],
                    "exclude_adr": True,
                    "exclude_etf": True
                },
                "prioritize": {
                    "watchlist_priority_first": True
                },
                "etf_blocklist": [
                    "SPY", "QQQ", "DIA", "VTI", "VOO", "IWM", "IJH", "IJR",
                    "VB", "VBK", "VBR", "VTWO", "SLY", "SLYG", "SLYV",
                    "MDY", "SPSM", "IWN"
                ],
                "schema_version": "universe.v1"
            }
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def load(self, use_priority_first: bool = None) -> Tuple[List[str], Dict]:
        """
        Load, filter, and sort ticker universe
        
        Args:
            use_priority_first: Override config priority setting
            
        Returns:
            (ticker_list, stats_dict)
        """
        # Reset exclusions
        self.exclusions = []
        
        # Check if CSV exists
        if not os.path.exists(self.csv_path):
            return [], {
                'error': f'Universe CSV not found: {self.csv_path}',
                'total': 0,
                'selected': 0,
                'exclusions': []
            }
        
        try:
            # Load CSV
            df = pd.read_csv(self.csv_path)
            
            # Validate required columns
            required_cols = ['ticker']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return [], {
                    'error': f'Missing required columns: {", ".join(missing_cols)}',
                    'total': 0,
                    'selected': 0,
                    'exclusions': []
                }
            
            total_tickers = len(df)
            
            # Apply filters
            df_filtered = self._apply_filters(df)
            
            # Sort by priority and other criteria
            if use_priority_first is None:
                use_priority_first = self.config['prioritize'].get('watchlist_priority_first', True)
            
            df_sorted = self._sort_tickers(df_filtered, use_priority_first)
            
            # Cap to max_tickers
            max_tickers = self.config['max_tickers']
            df_final = df_sorted.head(max_tickers)
            
            # Extract ticker list
            ticker_list = df_final['ticker'].tolist()
            
            # Build stats
            stats = {
                'total': total_tickers,
                'selected': len(ticker_list),
                'filtered_out': total_tickers - len(df_filtered),
                'capped': len(df_sorted) - len(df_final),
                'exclusions': self.exclusions[:10],  # Top 10
                'priority_counts': self._count_by_priority(df_final),
                'use_priority_first': use_priority_first
            }
            
            return ticker_list, stats
            
        except Exception as e:
            return [], {
                'error': f'Error loading universe: {str(e)}',
                'total': 0,
                'selected': 0,
                'exclusions': []
            }
    
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all configured filters"""
        filters = self.config['filters']
        
        # Start with all tickers
        result = df.copy()
        initial_count = len(result)
        
        # Filter: blank tickers
        blank_mask = result['ticker'].isna() | (result['ticker'] == '')
        if blank_mask.any():
            excluded = result[blank_mask]['ticker'].tolist()
            self.exclusions.extend([
                {'ticker': str(t), 'reason': 'Blank ticker'}
                for t in excluded if pd.notna(t)
            ])
            result = result[~blank_mask]
        
        # Filter: ADRs
        if filters.get('exclude_adr', True) and 'is_adr' in result.columns:
            adr_mask = result['is_adr'] == True
            if adr_mask.any():
                excluded = result[adr_mask]['ticker'].tolist()
                self.exclusions.extend([
                    {'ticker': t, 'reason': 'ADR excluded'}
                    for t in excluded
                ])
                result = result[~adr_mask]
        
        # Filter: ETFs
        if filters.get('exclude_etf', True):
            etf_blocklist = [etf.upper() for etf in self.config.get('etf_blocklist', [])]
            
            # Check is_etf column
            if 'is_etf' in result.columns:
                etf_mask = result['is_etf'] == True
                if etf_mask.any():
                    excluded = result[etf_mask]['ticker'].tolist()
                    self.exclusions.extend([
                        {'ticker': t, 'reason': 'ETF (column)'}
                        for t in excluded
                    ])
                    result = result[~etf_mask]
            
            # Check blocklist
            blocklist_mask = result['ticker'].str.upper().isin(etf_blocklist)
            if blocklist_mask.any():
                excluded = result[blocklist_mask]['ticker'].tolist()
                self.exclusions.extend([
                    {'ticker': t, 'reason': 'ETF (blocklist)'}
                    for t in excluded
                ])
                result = result[~blocklist_mask]
        
        # Filter: Min price
        if 'price' in result.columns and filters.get('min_price'):
            min_price = filters['min_price']
            price_mask = (result['price'].notna()) & (result['price'] < min_price)
            if price_mask.any():
                excluded = result[price_mask]['ticker'].tolist()
                self.exclusions.extend([
                    {'ticker': t, 'reason': f'Price < ${min_price}'}
                    for t in excluded
                ])
                result = result[~price_mask]
        
        # Filter: Min volume
        if 'avg_vol_30d' in result.columns and filters.get('min_avg_vol_30d'):
            min_vol = filters['min_avg_vol_30d']
            vol_mask = (result['avg_vol_30d'].notna()) & (result['avg_vol_30d'] < min_vol)
            if vol_mask.any():
                excluded = result[vol_mask]['ticker'].tolist()
                self.exclusions.extend([
                    {'ticker': t, 'reason': f'Volume < {min_vol:,}'}
                    for t in excluded
                ])
                result = result[~vol_mask]
        
        # Filter: Market cap range
        if 'market_cap_musd' in result.columns:
            if filters.get('market_cap_min_musd'):
                min_mcap = filters['market_cap_min_musd']
                mcap_min_mask = (result['market_cap_musd'].notna()) & (result['market_cap_musd'] < min_mcap)
                if mcap_min_mask.any():
                    excluded = result[mcap_min_mask]['ticker'].tolist()
                    self.exclusions.extend([
                        {'ticker': t, 'reason': f'MCap < ${min_mcap}M'}
                        for t in excluded
                    ])
                    result = result[~mcap_min_mask]
            
            if filters.get('market_cap_max_musd'):
                max_mcap = filters['market_cap_max_musd']
                mcap_max_mask = (result['market_cap_musd'].notna()) & (result['market_cap_musd'] > max_mcap)
                if mcap_max_mask.any():
                    excluded = result[mcap_max_mask]['ticker'].tolist()
                    self.exclusions.extend([
                        {'ticker': t, 'reason': f'MCap > ${max_mcap}M'}
                        for t in excluded
                    ])
                    result = result[~mcap_max_mask]
        
        # Filter: Exchanges
        if 'exchange' in result.columns and filters.get('exchanges_allow'):
            allowed_exchanges = [ex.upper() for ex in filters['exchanges_allow']]
            exchange_mask = (result['exchange'].notna()) & (~result['exchange'].str.upper().isin(allowed_exchanges))
            if exchange_mask.any():
                excluded = result[exchange_mask]['ticker'].tolist()
                self.exclusions.extend([
                    {'ticker': t, 'reason': 'Exchange not allowed'}
                    for t in excluded
                ])
                result = result[~exchange_mask]
        
        return result
    
    def _sort_tickers(self, df: pd.DataFrame, use_priority_first: bool) -> pd.DataFrame:
        """
        Sort tickers by priority, volume, and market cap
        
        Priority first (Option 2): Fill with all A, then B, then C
        """
        if not use_priority_first or 'priority' not in df.columns:
            # No priority sorting - just sort by volume and mcap
            sort_keys = []
            if 'avg_vol_30d' in df.columns:
                sort_keys.append(('avg_vol_30d', False))  # Descending
            if 'market_cap_musd' in df.columns:
                sort_keys.append(('market_cap_musd', False))  # Descending
            
            if sort_keys:
                result = df.sort_values(
                    by=[k[0] for k in sort_keys],
                    ascending=[k[1] for k in sort_keys],
                    na_position='last'
                )
            else:
                result = df
        else:
            # Priority first: A → B → C
            # Convert priority to sortable (A=0, B=1, C=2, other=3)
            priority_map = {'A': 0, 'B': 1, 'C': 2}
            df['_priority_sort'] = df['priority'].map(priority_map).fillna(3)
            
            # Sort by priority, then volume, then mcap
            sort_keys = [('_priority_sort', True)]  # Ascending (A first)
            if 'avg_vol_30d' in df.columns:
                sort_keys.append(('avg_vol_30d', False))  # Descending
            if 'market_cap_musd' in df.columns:
                sort_keys.append(('market_cap_musd', False))  # Descending
            
            result = df.sort_values(
                by=[k[0] for k in sort_keys],
                ascending=[k[1] for k in sort_keys],
                na_position='last'
            )
            
            result = result.drop(columns=['_priority_sort'])
        
        return result
    
    def _count_by_priority(self, df: pd.DataFrame) -> Dict[str, int]:
        """Count tickers by priority level"""
        if 'priority' not in df.columns:
            return {}
        
        counts = df['priority'].value_counts().to_dict()
        return {
            'A': counts.get('A', 0),
            'B': counts.get('B', 0),
            'C': counts.get('C', 0),
        }
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config = self._load_config()
