import pytest
import numpy as np
import math
from physics.acoustic.modal_id import AcousticModalID
from config.system_config import SystemConfig
from scipy.signal import lti, lsim

def test_chirp_frequency_sweep():
    config = SystemConfig()
    mod = AcousticModalID(config)
    
    t = np.linspace(0, 1, 1000)
    chirp = mod.inject_chirp(10.0, 100.0, 1.0, t)
    
    zero_crossings = np.where(np.diff(np.signbit(chirp)))[0]
    diffs = np.diff(zero_crossings)
    # diffs is distance between zero crossings. As frequency increases, distance decreases.
    # Allow a small numerical tolerance for discrete sampling.
    assert np.all(np.diff(diffs) <= 1)

def test_extracts_known_resonance():
    config = SystemConfig()
    mod = AcousticModalID(config)
    
    f_n_true = 43.2
    zeta_true = 0.05
    w_n = 2 * math.pi * f_n_true
    
    sys = lti([w_n**2], [1, 2*zeta_true*w_n, w_n**2])
    
    t = np.linspace(0, 5, 5000)
    dt = t[1] - t[0]
    u = mod.inject_chirp(10.0, 100.0, 5.0, t)
    
    tout, y, x = lsim(sys, u, t)
    
    H = mod.transfer_function(y, u)
    f_n_est, zeta_est = mod.dominant_mode(H, dt)
    
    assert math.isclose(f_n_est, f_n_true, rel_tol=0.02)
    assert 0.01 < zeta_est < 0.2

def test_coherence_unity_for_clean_signal():
    config = SystemConfig()
    mod = AcousticModalID(config)
    
    t = np.linspace(0, 1, 1000)
    u = mod.inject_chirp(10.0, 100.0, 1.0, t)
    y = 2.0 * u
    
    gamma2 = mod.modal_coherence(y, u)
    assert np.all(gamma2 > 0.99)

def test_coherence_drops_with_noise():
    config = SystemConfig()
    mod = AcousticModalID(config)
    
    t = np.linspace(0, 1, 1000)
    u = mod.inject_chirp(10.0, 100.0, 1.0, t)
    np.random.seed(42)
    y_clean = 2.0 * u
    y_noisy = y_clean + np.random.normal(0, 5.0, len(t))
    
    gamma2_clean = mod.modal_coherence(y_clean, u)
    gamma2_noisy = mod.modal_coherence(y_noisy, u)
    
    assert np.median(gamma2_noisy) < 0.9
