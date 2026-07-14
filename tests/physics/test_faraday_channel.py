import pytest
from physics.mhd.faraday_channel import FaradayChannel

def test_ideal_max_at_half_load():
    fc = FaradayChannel({})
    sigma = 100.0
    u = 500.0
    B = 2.0
    pe_05 = fc.power_density(sigma, u, B, 0.5)
    pe_02 = fc.power_density(sigma, u, B, 0.2)
    pe_08 = fc.power_density(sigma, u, B, 0.8)
    assert pe_05 > pe_02
    assert pe_05 > pe_08
    
def test_power_scales_with_b_squared():
    fc = FaradayChannel({})
    sigma = 100.0
    u = 500.0
    pe_1 = fc.power_density(sigma, u, 1.0, 0.5)
    pe_2 = fc.power_density(sigma, u, 2.0, 0.5)
    assert abs(pe_2 / pe_1 - 4.0) < 1e-6

def test_lorentz_opposes_motion():
    fc = FaradayChannel({})
    # I_arc, B_eff, r_eff, kappa_psmic are all positive for generator
    tau_em = fc.lorentz_torque(100.0, 2.0, 0.5, 1.0)
    assert tau_em > 0 # Torque magnitude is positive, will be subtracted from drive in rotor dynamics

def test_derating_bounds():
    fc = FaradayChannel({})
    # P_gross = C_d * p_e * V_MHD
    # P_ideal = p_e * V_MHD
    # Ratio is C_d
    ratio = fc.C_d
    assert 0.2 <= ratio <= 0.4
