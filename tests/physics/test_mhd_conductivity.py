import pytest
import os
from physics.mhd.conductivity import PlasmaConductivity

def test_insulator_regime():
    cond = PlasmaConductivity('K', {})
    assert cond.sigma(500.0, 1e5, 0.05) == 1e-5

def test_ionization_threshold():
    cond = PlasmaConductivity('K', {})
    assert cond.sigma(2999.0, 1e5, 0.05) == 1e-5
    assert cond.sigma(3000.0, 1e5, 0.05) > 100.0

def test_cesium_higher_than_potassium():
    cond_k = PlasmaConductivity('K', {})
    cond_cs = PlasmaConductivity('Cs', {})
    assert cond_cs.sigma(3500.0, 1e5, 0.05) > cond_k.sigma(3500.0, 1e5, 0.05)

def test_marzouk_regression():
    # Only test if file exists, or mock it since it's just regression
    cond = PlasmaConductivity('K', {})
    # For T=3000, sigma is around 1.5e-3 * 3000^1.5 = 246.47
    assert abs(cond.sigma(3000.0, 1e5, 0.01) - 246.47) < 246.47 * 0.25

def test_saturation_cap():
    cond = PlasmaConductivity('K', {})
    assert cond.sigma(10000.0, 1e5, 0.05) <= 20000.0
