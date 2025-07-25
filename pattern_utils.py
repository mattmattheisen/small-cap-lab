"""
Candlestick Pattern Recognition Utilities
High-information pattern detection for trading signals
"""

import pandas as pd
import numpy as np

def detect_bullish_engulfing(o, h, l, c, i):
    """Detect bullish engulfing pattern"""
    if i < 1:
        return 0
    
    # Previous candle (bearish)
    prev_body = abs(c.iloc[i-1] - o.iloc[i-1])
    prev_bearish = c.iloc[i-1] < o.iloc[i-1]
    
    # Current candle (bullish)
    curr_body = abs(c.iloc[i] - o.iloc[i])
    curr_bullish = c.iloc[i] > o.iloc[i]
    
    # Engulfing conditions
    if (prev_bearish and curr_bullish and 
        c.iloc[i] > o.iloc[i-1] and o.iloc[i] < c.iloc[i-1] and
        curr_body > prev_body * 1.1):  # Current body is at least 10% bigger
        return 100
    
    return 0

def detect_bearish_engulfing(o, h, l, c, i):
    """Detect bearish engulfing pattern"""
    if i < 1:
        return 0
    
    # Previous candle (bullish)
    prev_body = abs(c.iloc[i-1] - o.iloc[i-1])
    prev_bullish = c.iloc[i-1] > o.iloc[i-1]
    
    # Current candle (bearish)
    curr_body = abs(c.iloc[i] - o.iloc[i])
    curr_bearish = c.iloc[i] < o.iloc[i]
    
    # Engulfing conditions
    if (prev_bullish and curr_bearish and 
        c.iloc[i] < o.iloc[i-1] and o.iloc[i] > c.iloc[i-1] and
        curr_body > prev_body * 1.1):  # Current body is at least 10% bigger
        return -100
    
    return 0

def detect_morning_star(o, h, l, c, i):
    """Detect morning star pattern"""
    if i < 2:
        return 0
    
    # Three candles
    first_bearish = c.iloc[i-2] < o.iloc[i-2]
    second_small = abs(c.iloc[i-1] - o.iloc[i-1]) < abs(c.iloc[i-2] - o.iloc[i-2]) * 0.5
    third_bullish = c.iloc[i] > o.iloc[i]
    
    # Gap conditions
    gap_down = max(o.iloc[i-1], c.iloc[i-1]) < c.iloc[i-2]
    gap_up = o.iloc[i] > max(o.iloc[i-1], c.iloc[i-1])
    
    if first_bearish and second_small and third_bullish and gap_down and gap_up:
        return 100
    
    return 0

def detect_evening_star(o, h, l, c, i):
    """Detect evening star pattern"""
    if i < 2:
        return 0
    
    # Three candles
    first_bullish = c.iloc[i-2] > o.iloc[i-2]
    second_small = abs(c.iloc[i-1] - o.iloc[i-1]) < abs(c.iloc[i-2] - o.iloc[i-2]) * 0.5
    third_bearish = c.iloc[i] < o.iloc[i]
    
    # Gap conditions
    gap_up = min(o.iloc[i-1], c.iloc[i-1]) > c.iloc[i-2]
    gap_down = o.iloc[i] < min(o.iloc[i-1], c.iloc[i-1])
    
    if first_bullish and second_small and third_bearish and gap_up and gap_down:
        return -100
    
    return 0

def detect_hammer(o, h, l, c, i):
    """Detect hammer/doji patterns"""
    body = abs(c.iloc[i] - o.iloc[i])
    upper_shadow = h.iloc[i] - max(o.iloc[i], c.iloc[i])
    lower_shadow = min(o.iloc[i], c.iloc[i]) - l.iloc[i]
    total_range = h.iloc[i] - l.iloc[i]
    
    # Hammer: small body, long lower shadow, short upper shadow
    if (body < total_range * 0.3 and 
        lower_shadow > body * 2 and 
        upper_shadow < body):
        return 100  # Bullish hammer
    
    return 0

def compute_cdl(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds pattern columns to df with signals (+100 / -100 / 0).
    Custom implementation without external dependencies.
    """
    df_copy = df.copy()
    
    try:
        o, h, l, c = df_copy['Open'], df_copy['High'], df_copy['Low'], df_copy['Close']
        
        # Initialize pattern columns
        df_copy['cdl_engulfing'] = 0
        df_copy['cdl_morningstar'] = 0
        df_copy['cdl_eveningstar'] = 0
        df_copy['cdl_hammer'] = 0
        
        # Compute patterns for each row
        for i in range(len(df_copy)):
            # Engulfing patterns
            bullish_eng = detect_bullish_engulfing(o, h, l, c, i)
            bearish_eng = detect_bearish_engulfing(o, h, l, c, i)
            
            if bullish_eng:
                df_copy.iloc[i, df_copy.columns.get_loc('cdl_engulfing')] = bullish_eng
            elif bearish_eng:
                df_copy.iloc[i, df_copy.columns.get_loc('cdl_engulfing')] = bearish_eng
            
            # Star patterns
            morning = detect_morning_star(o, h, l, c, i)
            evening = detect_evening_star(o, h, l, c, i)
            
            if morning:
                df_copy.iloc[i, df_copy.columns.get_loc('cdl_morningstar')] = morning
            if evening:
                df_copy.iloc[i, df_copy.columns.get_loc('cdl_eveningstar')] = evening
            
            # Hammer pattern
            hammer = detect_hammer(o, h, l, c, i)
            if hammer:
                df_copy.iloc[i, df_copy.columns.get_loc('cdl_hammer')] = hammer
        
        return df_copy
        
    except Exception as e:
        print(f"Error in compute_cdl: {e}")
        return df

def latest_signal(df: pd.DataFrame) -> dict:
    """Return the tag, direction, and price trigger of today's candle."""
    sig = {'tag': None, 'dir': 0, 'trigger': None, 'strength': 0}
    
    if len(df) == 0:
        return sig
    
    try:
        row = df.iloc[-1]
        
        # Check all pattern columns
        for col, val in row.items():
            if isinstance(col, str) and col.startswith('cdl_') and val in (100, -100):
                pattern_name = col.replace('cdl_', '').replace('3whitesoldiers', '3white_soldiers').replace('3blackcrows', '3black_crows')
                sig.update({
                    'tag': pattern_name.title(),
                    'dir': 1 if val == 100 else -1,
                    'trigger': row['High'] if val == -100 else row['Low'],
                    'strength': abs(val)
                })
                break  # Return first pattern found
                
    except Exception as e:
        print(f"Error in latest_signal: {e}")
    
    return sig

def get_pattern_summary(df: pd.DataFrame, lookback_days: int = 30) -> dict:
    """Get summary of patterns over recent period"""
    summary = {
        'total_patterns': 0,
        'bullish_count': 0,
        'bearish_count': 0,
        'pattern_frequency': 0,
        'recent_patterns': []
    }
    
    if len(df) < lookback_days:
        return summary
    
    try:
        recent_df = df.tail(lookback_days)
        
        for idx, row in recent_df.iterrows():
            for col, val in row.items():
                if isinstance(col, str) and col.startswith('cdl_') and val in (100, -100):
                    pattern_name = col.replace('cdl_', '')
                    summary['total_patterns'] += 1
                    
                    if val == 100:
                        summary['bullish_count'] += 1
                        direction = 'Bullish'
                    else:
                        summary['bearish_count'] += 1
                        direction = 'Bearish'
                    
                    summary['recent_patterns'].append({
                        'date': idx,
                        'pattern': pattern_name.title(),
                        'direction': direction,
                        'strength': abs(val)
                    })
        
        # Calculate frequency
        summary['pattern_frequency'] = summary['total_patterns'] / lookback_days * 100
        
    except Exception as e:
        print(f"Error in get_pattern_summary: {e}")
    
    return summary

def combine_with_hmm_signal(hmm_signal: str, hmm_confidence: float, pattern_signal: dict) -> dict:
    """Combine HMM regime signal with candlestick pattern for enhanced decision making"""
    
    combined_signal = {
        'action': 'HOLD',
        'strength': 0,
        'reasoning': [],
        'hmm_component': hmm_signal,
        'pattern_component': pattern_signal.get('tag', 'None'),
        'combined_confidence': hmm_confidence
    }
    
    # Base HMM signal strength
    base_strength = 3 if hmm_confidence >= 0.7 else 1
    
    # Pattern enhancement
    pattern_boost = 0
    if pattern_signal.get('tag'):
        pattern_boost = 2 if pattern_signal.get('strength', 0) == 100 else 1
    
    # Decision logic
    if hmm_signal == 'BUY' and pattern_signal.get('dir', 0) == 1:
        # Both bullish
        combined_signal['action'] = 'STRONG_BUY'
        combined_signal['strength'] = min(10, base_strength + pattern_boost + 3)
        combined_signal['reasoning'].append("HMM Bull regime confirmed by bullish candlestick pattern")
        combined_signal['combined_confidence'] = min(1.0, hmm_confidence + 0.2)
        
    elif hmm_signal == 'SELL' and pattern_signal.get('dir', 0) == -1:
        # Both bearish
        combined_signal['action'] = 'STRONG_SELL'
        combined_signal['strength'] = min(10, base_strength + pattern_boost + 3)
        combined_signal['reasoning'].append("HMM Bear regime confirmed by bearish candlestick pattern")
        combined_signal['combined_confidence'] = min(1.0, hmm_confidence + 0.2)
        
    elif hmm_signal == 'BUY' and pattern_signal.get('dir', 0) == -1:
        # Conflicting signals - HMM bullish, pattern bearish
        combined_signal['action'] = 'HOLD'
        combined_signal['strength'] = 2
        combined_signal['reasoning'].append("Conflicting signals: HMM bullish vs bearish pattern - recommend caution")
        combined_signal['combined_confidence'] = hmm_confidence * 0.7
        
    elif hmm_signal == 'SELL' and pattern_signal.get('dir', 0) == 1:
        # Conflicting signals - HMM bearish, pattern bullish  
        combined_signal['action'] = 'HOLD'
        combined_signal['strength'] = 2
        combined_signal['reasoning'].append("Conflicting signals: HMM bearish vs bullish pattern - recommend caution")
        combined_signal['combined_confidence'] = hmm_confidence * 0.7
        
    elif hmm_signal in ['BUY', 'SELL'] and pattern_signal.get('dir', 0) == 0:
        # HMM signal with no pattern
        combined_signal['action'] = hmm_signal
        combined_signal['strength'] = base_strength
        combined_signal['reasoning'].append(f"HMM {hmm_signal} signal with no candlestick pattern confirmation")
        
    elif hmm_signal == 'HOLD' and pattern_signal.get('dir', 0) != 0:
        # Pattern signal with HMM hold
        if pattern_signal.get('dir', 0) == 1:
            combined_signal['action'] = 'WEAK_BUY'
            combined_signal['strength'] = pattern_boost + 1
            combined_signal['reasoning'].append("Bullish pattern in sideways HMM regime - weak buy signal")
        else:
            combined_signal['action'] = 'WEAK_SELL'
            combined_signal['strength'] = pattern_boost + 1
            combined_signal['reasoning'].append("Bearish pattern in sideways HMM regime - weak sell signal")
    
    return combined_signal