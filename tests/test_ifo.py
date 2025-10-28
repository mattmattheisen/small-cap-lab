"""
Unit tests for IFO (Institutional Flow Overlay) system
Tests all 7 validation rules from the spec
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.institutional_flow import IFOEngine


@pytest.fixture
def ifo_engine():
    """Create IFO engine for testing"""
    return IFOEngine('config/ifo.yaml')


class TestIFOValidation:
    """Test suite for 7 validation rules"""
    
    def test_1_weight_renormalization(self, ifo_engine):
        """
        Rule 1: Weight renormalization when any component missing
        Record booleans in components_present
        """
        # Test with only RV and AD_slope (Phase 1A)
        ifs_raw, components = ifo_engine.calculate_ifs_raw(
            z_h=None,
            rv=1.5,
            ad_slope=0.8,
            z_dtc=None
        )
        
        assert components['has_RV'] == True
        assert components['has_ADslope'] == True
        assert components['has_ZH'] == False
        assert components['has_ZDTC'] == False
        
        # Check normalization: weights should sum to 1
        # With Phase 1A: RV=0.60, AD_slope=0.40
        expected_ifs = 0.60 * 1.5 + 0.40 * 0.8
        assert abs(ifs_raw - expected_ifs) < 0.01
    
    def test_2_clipping_and_winsorization(self, ifo_engine):
        """
        Rule 2: Clipping & winsorization exactly as specified
        IFS_raw ∈ [-3, +3]; IFS_smoothed ∈ [-2, +2]
        """
        # Test IFS_raw clipping
        ifs_raw, _ = ifo_engine.calculate_ifs_raw(
            rv=10.0,  # Extreme value
            ad_slope=5.0  # Extreme value
        )
        assert -3.0 <= ifs_raw <= 3.0
        
        # Test IFS_smoothed rescaling
        ifs_raw_series = pd.Series([2.5, 2.8, 3.0, -2.5, -3.0] * 100)
        ifs_smoothed = ifo_engine.smooth_ifs(ifs_raw_series)
        ifs_rescaled = ifo_engine.rescale_ifs(ifs_smoothed)
        
        assert ifs_rescaled.min() >= -2.0
        assert ifs_rescaled.max() <= 2.0
    
    def test_3_posterior_monotonicity(self, ifo_engine):
        """
        Rule 3: Posterior monotonicity
        If IFS_smoothed rises by ≥1.0 while P_bull_raw stable (±0.05),
        then P_bull_adj must increase
        """
        p_bull_raw = 0.60
        
        # Low IFS
        p_adj_low = ifo_engine.adjust_posterior(p_bull_raw, ifs_smoothed=-0.5)
        
        # High IFS (increase by ≥1.0)
        p_adj_high = ifo_engine.adjust_posterior(p_bull_raw, ifs_smoothed=0.6)
        
        # P_bull_adj should increase
        assert p_adj_high > p_adj_low, \
            f"Posterior should increase: {p_adj_low:.3f} -> {p_adj_high:.3f}"
    
    def test_4_kelly_guardrails(self, ifo_engine):
        """
        Rule 4: Kelly guardrails
        0 ≤ kelly_adj ≤ K_max
        """
        kelly_base = 0.20
        
        # Test various IFS values
        for ifs in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            kelly_adj = ifo_engine.scale_kelly(kelly_base, ifs)
            
            assert kelly_adj >= 0.0, f"Kelly cannot be negative: {kelly_adj}"
            assert kelly_adj <= ifo_engine.K_max, \
                f"Kelly exceeds K_max: {kelly_adj} > {ifo_engine.K_max}"
    
    def test_5_reproducibility(self, ifo_engine):
        """
        Rule 5: Reproducibility
        Identical inputs → identical outputs (no randomness)
        """
        # Run calculation twice with same inputs
        rv = 1.2
        ad_slope = 0.8
        
        ifs_raw_1, _ = ifo_engine.calculate_ifs_raw(rv=rv, ad_slope=ad_slope)
        ifs_raw_2, _ = ifo_engine.calculate_ifs_raw(rv=rv, ad_slope=ad_slope)
        
        assert ifs_raw_1 == ifs_raw_2, "IFS calculation must be deterministic"
        
        # Test posterior adjustment
        p_bull = 0.65
        ifs = 1.0
        
        p_adj_1 = ifo_engine.adjust_posterior(p_bull, ifs)
        p_adj_2 = ifo_engine.adjust_posterior(p_bull, ifs)
        
        assert p_adj_1 == p_adj_2, "Posterior adjustment must be deterministic"
    
    def test_6_staleness_flag(self, ifo_engine):
        """
        Rule 6: Staleness flag
        If latest 13F > 180 days old, set has_ZH=false and renormalize
        """
        # This is tested in data_loaders.py
        # When institutional holdings are stale, they return (None, True)
        # which causes has_ZH=False in calculate_ifs_raw
        
        ifs_raw, components = ifo_engine.calculate_ifs_raw(
            z_h=None,  # Stale data
            rv=1.0,
            ad_slope=0.5
        )
        
        assert components['has_ZH'] == False
        # Weights should renormalize to RV and AD_slope only
        assert ifs_raw is not None
    
    def test_7_numerical_safety(self, ifo_engine):
        """
        Rule 7: Numerical safety
        When High==Low, set MFM=0 via denominator max(High-Low, 1e-6)
        """
        # Create OHLCV data with High==Low (doji candle)
        dates = pd.date_range('2024-01-01', periods=120, freq='D')
        ohlcv = pd.DataFrame({
            'Open': [100.0] * 120,
            'High': [100.0] * 120,  # High == Low
            'Low': [100.0] * 120,
            'Close': [100.0] * 120,
            'Volume': [1000000] * 120
        }, index=dates)
        
        # Should not raise division by zero
        try:
            ad_slope = ifo_engine.calculate_ad_slope(ohlcv)
            assert not np.isnan(ad_slope), "AD_slope should not be NaN"
            assert np.isfinite(ad_slope), "AD_slope should be finite"
        except ZeroDivisionError:
            pytest.fail("AD_slope calculation raised ZeroDivisionError")


class TestIFOComponents:
    """Additional component tests"""
    
    def test_rv_calculation(self, ifo_engine):
        """Test relative volume z-score calculation"""
        volumes = pd.Series([1000000] * 95 + [1500000] * 5)  # Spike in last 5 days
        
        rv = ifo_engine.calculate_rv(volumes)
        
        assert rv > 0, "RV should be positive for volume spike"
        assert np.isfinite(rv), "RV should be finite"
    
    def test_ad_slope_calculation(self, ifo_engine):
        """Test A/D slope calculation"""
        # Create uptrending OHLCV
        dates = pd.date_range('2024-01-01', periods=120, freq='D')
        closes = np.linspace(90, 110, 120)
        
        ohlcv = pd.DataFrame({
            'Open': closes - 1,
            'High': closes + 1,
            'Low': closes - 1,
            'Close': closes,
            'Volume': [1000000] * 120
        }, index=dates)
        
        ad_slope = ifo_engine.calculate_ad_slope(ohlcv)
        
        assert ad_slope > 0, "AD_slope should be positive for uptrend"
        assert -2.0 <= ad_slope <= 2.0, "AD_slope should be clipped to [-2, +2]"
    
    def test_decision_bands(self, ifo_engine):
        """Test decision band logic"""
        # Test primary bands
        assert ifo_engine.get_decision(1.5, 0.65) == 'Increase'
        assert ifo_engine.get_decision(0.5, 0.65) == 'Maintain'
        assert ifo_engine.get_decision(-0.5, 0.65) == 'Reduce'
        assert ifo_engine.get_decision(-1.5, 0.65) == 'Exit'
        
        # Test tie-breaker: force Exit if P_bull_adj < 0.40
        assert ifo_engine.get_decision(1.0, 0.30) == 'Exit'
        
        # Test tie-breaker: allow Increase if P_bull_adj > 0.80 and IFS >= 0
        assert ifo_engine.get_decision(0.5, 0.85) == 'Increase'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
