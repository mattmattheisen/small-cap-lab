"""
Small Cap Stock Screener
Advanced fundamental analysis for small cap opportunities
"""

import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SmallCapScreener:
    """Small Cap Stock Screener with fundamental analysis"""
    
    def __init__(self):
        # Screening criteria defaults
        self.default_criteria = {
            'market_cap_min': 300_000_000,  # $300M minimum
            'market_cap_max': 2_000_000_000,  # $2B maximum
            'revenue_growth_min': 0.10,  # 10% minimum
            'revenue_growth_max': 0.20,  # 20% preferred
            'eps_growth_min': 0.10,  # 10% minimum
            'debt_equity_max': 0.50,  # 50% maximum
            'peg_ratio_max': 1.0,  # PEG < 1.0
            'min_volume_usd': 1_000_000,  # $1M minimum daily volume
            'profit_margin_min': 0.05,  # 5% minimum profit margin
        }
        
        # Expanded small cap stock universe - rotates to show different stocks
        # Tech & Software
        tech_stocks = [
            'SOFI', 'PLTR', 'RBLX', 'COIN', 'HOOD', 'AFRM', 'SQ', 'UPST',
            'OPEN', 'ROKU', 'SNOW', 'CRWD', 'ZM', 'DOCU', 'OKTA', 'TWLO',
            'DDOG', 'NET', 'ESTC', 'MDB', 'TEAM', 'HUBS', 'ZS', 'VEEV',
            'TTD', 'APPS', 'APPN', 'PD', 'BILL', 'GTLB', 'S', 'PATH',
            'IONQ', 'QBTS', 'RGTI', 'ARQQ', 'AI', 'BBAI', 'SOUN', 'SMCI'
        ]
        
        # EVs & Clean Energy  
        ev_stocks = [
            'LCID', 'RIVN', 'CHPT', 'BLNK', 'EVGO', 'NIO', 'XPEV', 'LI',
            'FSR', 'RIDE', 'GOEV', 'QS', 'ENVX', 'SES', 'PLUG', 'FCEL',
            'BE', 'RUN', 'ENPH', 'NOVA', 'WOLF', 'MAXN', 'CSIQ', 'JKS'
        ]
        
        # FinTech & Crypto
        fintech_stocks = [
            'PYPL', 'MARA', 'RIOT', 'CLSK', 'BITF', 'HUT', 'ARBK', 'CIFR',
            'UPST', 'LC', 'AVNT', 'OPFI', 'NU', 'DAVE', 'MGNI', 'PUBM',
            'ACHR', 'JOBY', 'LILM', 'EVTL', 'ASTS', 'RKLB', 'ASTR', 'SPIR'
        ]
        
        # Healthcare & Biotech
        health_stocks = [
            'IONS', 'VRTX', 'EXAS', 'TDOC', 'DOCS', 'HIMS', 'ONEM', 'TMDX',
            'CRSP', 'EDIT', 'NTLA', 'BEAM', 'VCYT', 'PACB', 'ILMN', 'NVTA',
            'RXRX', 'SDGR', 'LEGN', 'KYMR', 'SANA', 'FATE', 'LYEL', 'SURF'
        ]
        
        # Consumer & Retail
        consumer_stocks = [
            'ETSY', 'W', 'CHWY', 'CVNA', 'CARS', 'FOUR', 'GSHD', 'MNDY',
            'SHOP', 'MELI', 'SE', 'GRAB', 'DIDI', 'CPNG', 'LYFT', 'UBER',
            'DASH', 'ABNB', 'EXPE', 'BKNG', 'TOST', 'BROS', 'CAVA', 'WING'
        ]
        
        # Gaming & Entertainment
        gaming_stocks = [
            'RDDT', 'PINS', 'SNAP', 'MTCH', 'BMBL', 'RBLX', 'U', 'TTWO',
            'EA', 'DKNG', 'PENN', 'RSI', 'LNW', 'FUBO', 'NFLX', 'PARA',
            'WBD', 'DIS', 'ROKU', 'SPOT', 'SONO', 'ATUS', 'SIRI', 'LSXMA'
        ]
        
        # Industrial & Manufacturing
        industrial_stocks = [
            'TSLA', 'XPEV', 'MP', 'ALB', 'SQM', 'LAC', 'PLL', 'LTHM',
            'RR', 'CARR', 'GNRC', 'AZEK', 'TREX', 'WOLF', 'ENPH', 'SEDG',
            'FSLR', 'SPWR', 'RUN', 'MAXN', 'ARRY', 'AMPS', 'POWI', 'VICR'
        ]
        
        # Combine all and rotate selection
        all_stocks = (tech_stocks + ev_stocks + fintech_stocks + 
                     health_stocks + consumer_stocks + gaming_stocks + 
                     industrial_stocks)
        
        # Remove duplicates and store full universe
        self.full_universe = list(set(all_stocks))
        
        # Rotate universe - use microsecond timestamp for true randomness on each init
        import random
        import time
        # Use current timestamp in microseconds for unique seed each time
        random.seed(int(time.time() * 1000000))  # Changes every microsecond
        self.small_cap_universe = random.sample(self.full_universe, min(80, len(self.full_universe)))
    
    def get_stock_fundamentals(self, symbol):
        """Get fundamental data for a single stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get financial statements
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cash_flow
            
            # Calculate key metrics
            fundamentals = {
                'symbol': symbol,
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'trailing_pe': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'return_on_assets': info.get('returnOnAssets', 0),
                'profit_margin': info.get('profitMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'gross_margin': info.get('grossMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'free_cash_flow': info.get('freeCashflow', 0),
                'operating_cash_flow': info.get('operatingCashflow', 0),
                'avg_volume': info.get('averageVolume', 0),
                'float_shares': info.get('floatShares', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'bid_ask_spread': self.calculate_bid_ask_spread(info),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            }
            
            # Calculate additional metrics
            fundamentals.update(self.calculate_growth_metrics(financials))
            fundamentals.update(self.calculate_quality_metrics(info, balance_sheet, cash_flow))
            
            return fundamentals
            
        except Exception as e:
            st.warning(f"Could not fetch data for {symbol}: {str(e)}")
            return None
    
    def calculate_bid_ask_spread(self, info):
        """Calculate bid-ask spread percentage"""
        bid = info.get('bid', 0)
        ask = info.get('ask', 0)
        if bid > 0 and ask > 0:
            return ((ask - bid) / ((ask + bid) / 2)) * 100
        return 0
    
    def calculate_growth_metrics(self, financials):
        """Calculate revenue and earnings growth over multiple years"""
        metrics = {
            'revenue_3yr_cagr': 0,
            'revenue_5yr_cagr': 0,
            'eps_3yr_cagr': 0,
            'eps_5yr_cagr': 0,
            'consistent_revenue_growth': False,
            'consistent_eps_growth': False
        }
        
        if financials is None or financials.empty:
            return metrics
        
        try:
            # Get revenue data
            if 'Total Revenue' in financials.index:
                revenues = financials.loc['Total Revenue'].dropna()
                if len(revenues) >= 3:
                    metrics['revenue_3yr_cagr'] = self.calculate_cagr(revenues, 3)
                    metrics['consistent_revenue_growth'] = self.check_consistent_growth(revenues, 3)
                if len(revenues) >= 5:
                    metrics['revenue_5yr_cagr'] = self.calculate_cagr(revenues, 5)
            
            return metrics
            
        except Exception:
            return metrics
    
    def calculate_cagr(self, values, years):
        """Calculate Compound Annual Growth Rate"""
        try:
            if len(values) < years:
                return 0
            
            values_sorted = values.sort_index()
            start_value = values_sorted.iloc[-years]
            end_value = values_sorted.iloc[-1]
            
            if start_value <= 0:
                return 0
                
            cagr = (end_value / start_value) ** (1/years) - 1
            return cagr
        except:
            return 0
    
    def check_consistent_growth(self, values, years):
        """Check if growth has been consistent"""
        try:
            if len(values) < years:
                return False
            
            values_sorted = values.sort_index()
            recent_values = values_sorted.iloc[-years:]
            
            # Check if at least 70% of years showed growth
            growth_years = 0
            for i in range(1, len(recent_values)):
                if recent_values.iloc[i] > recent_values.iloc[i-1]:
                    growth_years += 1
            
            return growth_years >= (years - 1) * 0.7
        except:
            return False
    
    def calculate_quality_metrics(self, info, balance_sheet, cash_flow):
        """Calculate additional quality metrics"""
        metrics = {
            'debt_to_equity_ratio': 0,
            'current_ratio': 0,
            'cash_ratio': 0,
            'asset_turnover': 0,
            'inventory_turnover': 0,
            'working_capital': 0,
            'tangible_book_value': 0
        }
        
        try:
            # Debt to equity
            total_debt = info.get('totalDebt', 0)
            total_equity = info.get('totalStockholderEquity', 0)
            if total_equity > 0:
                metrics['debt_to_equity_ratio'] = total_debt / total_equity
            
            # Current ratio
            metrics['current_ratio'] = info.get('currentRatio', 0)
            
            return metrics
        except:
            return metrics
    
    def screen_stocks(self, criteria):
        """Screen stocks based on criteria"""
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(self.small_cap_universe):
            status_text.text(f"Analyzing {symbol}... ({i+1}/{len(self.small_cap_universe)})")
            progress_bar.progress((i + 1) / len(self.small_cap_universe))
            
            fundamentals = self.get_stock_fundamentals(symbol)
            if fundamentals:
                score = self.calculate_screening_score(fundamentals, criteria)
                if score > 0:  # Only include stocks that meet some criteria
                    fundamentals['screening_score'] = score
                    results.append(fundamentals)
        
        progress_bar.empty()
        status_text.empty()
        
        # Sort by screening score
        results.sort(key=lambda x: x['screening_score'], reverse=True)
        return results
    
    def calculate_screening_score(self, fundamentals, criteria):
        """Calculate screening score based on criteria"""
        score = 0
        max_score = 10
        
        # Market cap check (required)
        market_cap = fundamentals.get('market_cap', 0)
        if not (criteria['market_cap_min'] <= market_cap <= criteria['market_cap_max']):
            return 0  # Fails basic market cap requirement
        
        # Revenue growth (2 points)
        revenue_growth = fundamentals.get('revenue_growth', 0)
        if revenue_growth >= criteria['revenue_growth_min']:
            score += 2
            # Bonus point for exceptional growth (>20%)
            if revenue_growth >= 0.20:
                score += 1
        
        # EPS growth (2 points)
        earnings_growth = fundamentals.get('earnings_growth', 0)
        if earnings_growth >= criteria['eps_growth_min']:
            score += 2
        
        # Profit margins (1 point)
        profit_margin = fundamentals.get('profit_margin', 0)
        if profit_margin >= criteria['profit_margin_min']:
            score += 1
        
        # Debt to equity (1 point)
        debt_equity = fundamentals.get('debt_to_equity', 100)
        if debt_equity <= criteria['debt_equity_max']:
            score += 1
        
        # PEG ratio (2 points)
        peg_ratio = fundamentals.get('peg_ratio', 10)
        if 0 < peg_ratio <= criteria['peg_ratio_max']:
            score += 2
        
        # Volume/Liquidity (1 point)
        avg_volume = fundamentals.get('avg_volume', 0)
        current_price = fundamentals.get('current_price', 0)
        daily_volume_usd = avg_volume * current_price
        if daily_volume_usd >= criteria['min_volume_usd']:
            score += 1
        
        # Cash flow positive (1 point)
        free_cash_flow = fundamentals.get('free_cash_flow', 0)
        if free_cash_flow > 0:
            score += 1
        
        return score
    
    def format_screening_results(self, results):
        """Format screening results for display"""
        if not results:
            return pd.DataFrame()
        
        display_data = []
        for stock in results:
            display_data.append({
                'Symbol': stock['symbol'],
                'Score': f"{stock['screening_score']}/10",
                'Market Cap': f"${stock['market_cap']/1e9:.2f}B" if stock['market_cap'] > 0 else 'N/A',
                'Revenue Growth': f"{stock['revenue_growth']*100:.1f}%" if stock['revenue_growth'] else 'N/A',
                'EPS Growth': f"{stock['earnings_growth']*100:.1f}%" if stock['earnings_growth'] else 'N/A',
                'Profit Margin': f"{stock['profit_margin']*100:.1f}%" if stock['profit_margin'] else 'N/A',
                'PEG Ratio': f"{stock['peg_ratio']:.2f}" if stock['peg_ratio'] else 'N/A',
                'P/E Ratio': f"{stock['trailing_pe']:.1f}" if stock['trailing_pe'] else 'N/A',
                'Debt/Equity': f"{stock['debt_to_equity']:.1f}%" if stock['debt_to_equity'] else 'N/A',
                'Current Price': f"${stock['current_price']:.2f}" if stock['current_price'] else 'N/A',
            })
        
        return pd.DataFrame(display_data)
    
    def format_csv_export(self, results):
        """Format screening results for CSV export with proper number formatting"""
        if not results:
            return pd.DataFrame()
        
        export_data = []
        for stock in results:
            export_data.append({
                'Symbol': stock['symbol'],
                'Score (out of 10)': stock['screening_score'],  # Plain number, not date format
                'Market Cap ($B)': stock['market_cap']/1e9 if stock['market_cap'] > 0 else None,
                'Revenue Growth (%)': stock['revenue_growth']*100 if stock['revenue_growth'] else None,
                'EPS Growth (%)': stock['earnings_growth']*100 if stock['earnings_growth'] else None,
                'Profit Margin (%)': stock['profit_margin']*100 if stock['profit_margin'] else None,
                'PEG Ratio': stock['peg_ratio'] if stock['peg_ratio'] else None,
                'P/E Ratio': stock['trailing_pe'] if stock['trailing_pe'] else None,
                'Debt/Equity (%)': stock['debt_to_equity'] if stock['debt_to_equity'] else None,
                'Current Price ($)': stock['current_price'] if stock['current_price'] else None,
            })
        
        return pd.DataFrame(export_data)