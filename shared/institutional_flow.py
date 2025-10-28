"""
Institutional Flow Overlay (IFO) - Core Calculation Engine
Implements IFS scoring, posterior adjustment, Kelly scaling, and decision bands
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Optional
import yaml


class IFOEngine:
    """Institutional Flow Overlay calculation engine"""
    
    def __init__(self, config_path: str = 'config/ifo.yaml'):
        """Load configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.weights = self.config['weights']
        self.gamma = self.config['gamma']
        self.beta = self.config['beta']
        self.K_max = self.config['K_max']
        self.ema_hl = self.config['ema_half_life_days']
        self.version = self.config['version']
    
    def calculate_rv(self, volumes: pd.Series) -> float:
        """
        Relative Volume z-score
        RV = (mean_vol_5d - mean_vol_100d) / std(vol_100d)
        """
        if len(volumes) < 100:
            return np.nan
        
        short_window = self.config['features']['rv_short_window']
        long_window = self.config['features']['rv_long_window']
        
        mean_5d = volumes.tail(short_window).mean()
        mean_100d = volumes.tail(long_window).mean()
        std_100d = volumes.tail(long_window).std()
        
        if std_100d == 0 or pd.isna(std_100d):
            return 0.0
        
        rv = (mean_5d - mean_100d) / std_100d
        return float(rv)
    
    def calculate_ad_slope(self, ohlcv: pd.DataFrame) -> float:
        """
        Accumulation/Distribution normalized slope
        
        Steps:
        1. MFM = ((C - L) - (H - C)) / max(H - L, 1e-6)
        2. MFV = MFM * Volume
        3. AD_t = cumulative sum of MFV (rolling 120-day window)
        4. AD_slope = OLS slope over last L=20 bars
        5. Normalize by MAD(AD over 120 bars)
        6. Clip to [-2, +2]
        """
        if len(ohlcv) < 120:
            return np.nan
        
        # Use last 120 days
        window = ohlcv.tail(120).copy()
        
        # Money Flow Multiplier
        numerator = (window['Close'] - window['Low']) - (window['High'] - window['Close'])
        denominator = np.maximum(window['High'] - window['Low'], 1e-6)
        mfm = numerator / denominator
        
        # Money Flow Volume
        mfv = mfm * window['Volume']
        
        # Accumulation/Distribution line (cumulative within window)
        ad = mfv.cumsum().values
        
        # OLS slope over last L=20 bars
        L = self.config['features']['ad_lookback']
        ad_recent = ad[-L:]
        x = np.arange(L)
        slope, _ = np.polyfit(x, ad_recent, 1)
        
        # Normalize by MAD of full 120-day AD
        mad = stats.median_abs_deviation(ad, scale='normal')
        if mad == 0 or np.isnan(mad):
            normalized_slope = 0.0
        else:
            normalized_slope = slope / mad
        
        # Clip to [-2, +2]
        clip_min = self.config['features']['ad_slope_clip']['min']
        clip_max = self.config['features']['ad_slope_clip']['max']
        normalized_slope = np.clip(normalized_slope, clip_min, clip_max)
        
        return float(normalized_slope)
    
    def calculate_ifs_raw(
        self,
        z_h: Optional[float] = None,
        rv: Optional[float] = None,
        ad_slope: Optional[float] = None,
        z_dtc: Optional[float] = None
    ) -> Tuple[float, Dict[str, bool]]:
        """
        Calculate raw IFS with weight renormalization
        
        Returns:
            (IFS_raw, components_present)
        """
        components = {
            'has_ZH': z_h is not None and not np.isnan(z_h),
            'has_RV': rv is not None and not np.isnan(rv),
            'has_ADslope': ad_slope is not None and not np.isnan(ad_slope),
            'has_ZDTC': z_dtc is not None and not np.isnan(z_dtc)
        }
        
        # Build active weights
        active_weights = {}
        if components['has_ZH']:
            active_weights['Z_H'] = self.weights['Z_H']
        if components['has_RV']:
            active_weights['RV'] = self.weights['RV']
        if components['has_ADslope']:
            active_weights['AD_slope'] = self.weights['AD_slope']
        if components['has_ZDTC']:
            active_weights['Z_DTC'] = self.weights['Z_DTC']
        
        # Renormalize to sum = 1
        total_weight = sum(active_weights.values())
        if total_weight == 0:
            return 0.0, components
        
        normalized_weights = {k: v / total_weight for k, v in active_weights.items()}
        
        # Calculate weighted score
        ifs_raw = 0.0
        if components['has_ZH']:
            ifs_raw += normalized_weights['Z_H'] * z_h
        if components['has_RV']:
            ifs_raw += normalized_weights['RV'] * rv
        if components['has_ADslope']:
            ifs_raw += normalized_weights['AD_slope'] * ad_slope
        if components['has_ZDTC']:
            ifs_raw += normalized_weights['Z_DTC'] * z_dtc
        
        # Clip to [-3, +3]
        ifs_raw = np.clip(ifs_raw, -3.0, 3.0)
        
        return float(ifs_raw), components
    
    def smooth_ifs(self, ifs_raw_series: pd.Series) -> pd.Series:
        """
        Smooth IFS with EMA (half-life = 21 days)
        
        Convert half-life to alpha: alpha = 1 - exp(ln(0.5) / half_life)
        """
        alpha = 1 - np.exp(np.log(0.5) / self.ema_hl)
        ifs_smoothed = ifs_raw_series.ewm(alpha=alpha, adjust=False).mean()
        return ifs_smoothed
    
    def rescale_ifs(self, ifs_smoothed_series: pd.Series) -> pd.Series:
        """
        Winsorize and rescale IFS to [-2, +2]
        
        Uses rolling 252-day window, winsorize at 5th/95th percentiles,
        then linearly map to [-2, +2]
        """
        if len(ifs_smoothed_series) < 252:
            # Use all available data if < 252 days
            window_data = ifs_smoothed_series
        else:
            window_data = ifs_smoothed_series.tail(252)
        
        # Winsorize
        lower_pct = self.config['winsor_pct']['lower']
        upper_pct = self.config['winsor_pct']['upper']
        
        lower_bound = window_data.quantile(lower_pct)
        upper_bound = window_data.quantile(upper_pct)
        
        winsorized = ifs_smoothed_series.clip(lower=lower_bound, upper=upper_bound)
        
        # Rescale to [-2, +2]
        if lower_bound == upper_bound:
            return pd.Series(0.0, index=ifs_smoothed_series.index)
        
        # Linear mapping
        rescaled = -2.0 + 4.0 * (winsorized - lower_bound) / (upper_bound - lower_bound)
        
        # Final clip to ensure [-2, +2]
        rescaled = rescaled.clip(-2.0, 2.0)
        
        return rescaled
    
    def adjust_posterior(self, p_bull_raw: float, ifs_smoothed: float) -> float:
        """
        Posterior adjustment with logit-shift
        
        P_bull_adj = sigmoid( logit(P_bull_raw) + gamma * IFS_smoothed )
        """
        # Clip p_bull_raw to avoid log(0) or log(1)
        p_bull_raw = np.clip(p_bull_raw, 1e-6, 1 - 1e-6)
        
        # Logit transform
        logit_p = np.log(p_bull_raw / (1 - p_bull_raw))
        
        # Add IFS shift
        adjusted_logit = logit_p + self.gamma * ifs_smoothed
        
        # Sigmoid back to probability
        p_bull_adj = 1.0 / (1.0 + np.exp(-adjusted_logit))
        
        return float(np.clip(p_bull_adj, 0.0, 1.0))
    
    def scale_kelly(self, kelly_base: float, ifs_smoothed: float) -> float:
        """
        Kelly scaling with IFS
        
        kelly_adj = min(K_max, max(0, kelly_base * (1 + beta * IFS_smoothed)))
        """
        kelly_adj = kelly_base * (1 + self.beta * ifs_smoothed)
        kelly_adj = np.clip(kelly_adj, 0.0, self.K_max)
        return float(kelly_adj)
    
    def get_decision(self, ifs_smoothed: float, p_bull_adj: float) -> str:
        """
        Decision bands with tie-breakers
        
        Primary by IFS:
        - > +1.0 → Increase
        - 0.0 to +1.0 → Maintain
        - -1.0 to 0.0 → Reduce
        - < -1.0 → Exit
        
        Tie-breakers:
        - P_bull_adj < 0.40 → force Exit
        - P_bull_adj > 0.80 and IFS ≥ 0 → allow Increase
        """
        bands = self.config['decision_bands']
        thresholds = self.config['bull_thresholds']
        
        # Tie-breaker 1: force Exit
        if p_bull_adj < thresholds['exit_force']:
            return 'Exit'
        
        # Tie-breaker 2: allow Increase
        if p_bull_adj > thresholds['inc_allow'] and ifs_smoothed >= 0:
            return 'Increase'
        
        # Primary bands
        if ifs_smoothed > bands['increase']:
            return 'Increase'
        elif ifs_smoothed >= bands['maintain']:
            return 'Maintain'
        elif ifs_smoothed >= bands['exit']:
            return 'Reduce'
        else:
            return 'Exit'
    
    def format_notes(
        self,
        components: Dict[str, bool],
        rv: Optional[float] = None,
        ad_slope: Optional[float] = None,
        z_h: Optional[float] = None,
        z_dtc: Optional[float] = None
    ) -> str:
        """Generate notes string for output"""
        notes_parts = []
        
        if components['has_RV'] and rv is not None:
            notes_parts.append(f"RV z={rv:.2f}")
        if components['has_ADslope'] and ad_slope is not None:
            notes_parts.append(f"AD_slope={ad_slope:.2f}")
        if components['has_ZH'] and z_h is not None:
            notes_parts.append(f"Z_H={z_h:.2f}")
        else:
            notes_parts.append("Z_H n/a")
        if components['has_ZDTC'] and z_dtc is not None:
            notes_parts.append(f"Z_DTC={z_dtc:.2f}")
        else:
            notes_parts.append("Z_DTC n/a")
        
        return "; ".join(notes_parts)
