"""
Quick validation script for IFO system (without pytest dependency)
"""

import sys
import pandas as pd
import numpy as np
from shared.institutional_flow import IFOEngine

def validate_ifo():
    """Run basic validation tests"""
    print("=" * 60)
    print("IFO System Validation")
    print("=" * 60)
    
    try:
        engine = IFOEngine('config/ifo.json')
        print("✓ IFO Engine initialized successfully")
        print(f"  - Gamma: {engine.gamma}")
        print(f"  - Beta: {engine.beta}")
        print(f"  - K_max: {engine.K_max}")
        print(f"  - EMA half-life: {engine.ema_hl} days")
        print()
        
        # Test 1: Weight renormalization
        print("Test 1: Weight Renormalization")
        ifs_raw, components = engine.calculate_ifs_raw(rv=1.5, ad_slope=0.8)
        print(f"  IFS_raw = {ifs_raw:.3f}")
        print(f"  has_RV = {components['has_RV']}")
        print(f"  has_ADslope = {components['has_ADslope']}")
        print(f"  has_ZH = {components['has_ZH']}")
        print(f"  has_ZDTC = {components['has_ZDTC']}")
        expected = 0.60 * 1.5 + 0.40 * 0.8
        assert abs(ifs_raw - expected) < 0.01, f"Expected {expected:.3f}, got {ifs_raw:.3f}"
        print("  ✓ PASSED")
        print()
        
        # Test 2: Clipping
        print("Test 2: IFS_raw Clipping to [-3, +3]")
        ifs_raw_extreme, _ = engine.calculate_ifs_raw(rv=10.0, ad_slope=5.0)
        print(f"  Extreme inputs (rv=10, ad_slope=5)")
        print(f"  IFS_raw (clipped) = {ifs_raw_extreme:.3f}")
        assert -3.0 <= ifs_raw_extreme <= 3.0
        print("  ✓ PASSED")
        print()
        
        # Test 3: Posterior adjustment
        print("Test 3: Posterior Adjustment (logit-shift)")
        p_bull_raw = 0.60
        ifs_smoothed = 1.0
        p_bull_adj = engine.adjust_posterior(p_bull_raw, ifs_smoothed)
        print(f"  P_bull_raw = {p_bull_raw:.3f}")
        print(f"  IFS_smoothed = {ifs_smoothed:.3f}")
        print(f"  P_bull_adj = {p_bull_adj:.3f}")
        assert p_bull_adj > p_bull_raw, "Positive IFS should increase posterior"
        print("  ✓ PASSED")
        print()
        
        # Test 4: Kelly scaling
        print("Test 4: Kelly Scaling")
        kelly_base = 0.20
        kelly_adj_pos = engine.scale_kelly(kelly_base, 1.0)
        kelly_adj_neg = engine.scale_kelly(kelly_base, -1.0)
        print(f"  kelly_base = {kelly_base:.3f}")
        print(f"  kelly_adj (IFS=+1.0) = {kelly_adj_pos:.3f}")
        print(f"  kelly_adj (IFS=-1.0) = {kelly_adj_neg:.3f}")
        assert 0 <= kelly_adj_pos <= engine.K_max
        assert 0 <= kelly_adj_neg <= engine.K_max
        print("  ✓ PASSED")
        print()
        
        # Test 5: Decision bands
        print("Test 5: Decision Bands")
        decisions = [
            (1.5, 0.65, 'Increase'),
            (0.5, 0.65, 'Maintain'),
            (-0.5, 0.65, 'Reduce'),
            (-1.5, 0.65, 'Exit'),
            (1.0, 0.30, 'Exit'),  # Tie-breaker: force Exit
            (0.5, 0.85, 'Increase'),  # Tie-breaker: allow Increase
        ]
        
        for ifs, p_bull, expected_decision in decisions:
            decision = engine.get_decision(ifs, p_bull)
            status = "✓" if decision == expected_decision else "✗"
            print(f"  {status} IFS={ifs:+.1f}, P_bull={p_bull:.2f} → {decision} (expected {expected_decision})")
            assert decision == expected_decision
        print("  ✓ ALL PASSED")
        print()
        
        # Test 6: RV calculation
        print("Test 6: Relative Volume Calculation")
        volumes = pd.Series([1000000] * 95 + [1500000] * 5)
        rv = engine.calculate_rv(volumes)
        print(f"  Normal vol: 1M, Spike vol: 1.5M")
        print(f"  RV z-score = {rv:.3f}")
        assert rv > 0, "RV should be positive for volume spike"
        print("  ✓ PASSED")
        print()
        
        # Test 7: A/D slope calculation
        print("Test 7: A/D Slope Calculation")
        dates = pd.date_range('2024-01-01', periods=120, freq='D')
        closes = np.linspace(90, 110, 120)
        ohlcv = pd.DataFrame({
            'Open': closes - 1,
            'High': closes + 1,
            'Low': closes - 1,
            'Close': closes,
            'Volume': [1000000] * 120
        }, index=dates)
        
        ad_slope = engine.calculate_ad_slope(ohlcv)
        print(f"  Uptrend: 90 → 110 over 120 days")
        print(f"  AD_slope = {ad_slope:.3f}")
        assert ad_slope > 0, "AD_slope should be positive for uptrend"
        assert -2.0 <= ad_slope <= 2.0, "AD_slope should be clipped"
        print("  ✓ PASSED")
        print()
        
        print("=" * 60)
        print("✓ ALL VALIDATION TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = validate_ifo()
    sys.exit(0 if success else 1)
