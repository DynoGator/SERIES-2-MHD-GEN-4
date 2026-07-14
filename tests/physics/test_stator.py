import pytest
import numpy as np
from physics.electromagnetic.stator import DICASHybridStator

def test_inductance_asymmetric():
    stator = DICASHybridStator({})
    L = stator.inductance_matrix()
    assert L[0, 0] != L[1, 1] # L_top (0.06) != L_center (0.12)
    assert np.isclose(L[0, 0], 0.06)
    assert np.isclose(L[1, 1], 0.12)

def test_psmic_periodicity():
    stator = DICASHybridStator({})
    k1 = stator.psmic_modulation(0.0)
    k2 = stator.psmic_modulation(np.pi / 2.0)
    assert np.isclose(k1, k2)

def test_b_eff_bounds():
    stator = DICASHybridStator({})
    B_max = 2.0
    for phi in np.linspace(0, 2*np.pi, 100):
        kappa = stator.psmic_modulation(phi)
        B_eff = stator.effective_b_field(B_max, kappa)
        assert 0.65 * B_max <= B_eff <= 1.35 * B_max
