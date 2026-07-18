import numpy as np
from network.correlator import CrossNodeCorrelator

def test_known_lag_recovered():
    correlator = CrossNodeCorrelator(tolerance_s=5.0)
    dt = 0.1
    t = np.arange(0, 20.0, dt)
    # create a spike train
    series_a = np.zeros_like(t)
    series_a[50:60] = 1.0  # Spike at 5.0s
    
    # inject 2.0s lag (20 samples)
    series_b = np.zeros_like(t)
    series_b[70:80] = 1.0  # Spike at 7.0s
    
    res = correlator.correlate(series_a, series_b, dt)
    assert res.coincident is True
    # lag_s should be around -2.0 or 2.0 depending on convention
    assert abs(abs(res.lag_s) - 2.0) < 1e-5
    assert res.coefficient > 0.8

def test_uncorrelated_noise_not_flagged():
    correlator = CrossNodeCorrelator(tolerance_s=5.0)
    np.random.seed(42)
    series_a = np.random.randn(100)
    series_b = np.random.randn(100)
    res = correlator.correlate(series_a, series_b, 0.1)
    assert res.coincident is False
    assert res.coefficient < 0.5

def test_identical_series_zero_lag():
    correlator = CrossNodeCorrelator(tolerance_s=5.0)
    t = np.arange(0, 10.0, 0.1)
    series_a = np.sin(t)
    res = correlator.correlate(series_a, series_a, 0.1)
    assert res.coincident is True
    assert abs(res.lag_s) < 1e-5
    assert res.coefficient > 0.99
