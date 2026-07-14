import pytest
import math
from physics.thermo.seed_loop import SeedLoop
from config.system_config import SystemConfig
from physics.base import ControlVector
from core.state_vector import StateVector

def test_mass_balance_closes():
    config = SystemConfig()
    loop = SeedLoop(config)
    
    state = StateVector(theta=0.0, omega=0.0, T_core=3000.0, p_vessel=100000.0, V_accum=0.1, m_seed=0.01)
    control = ControlVector()
    control.seed_injection_rate = 0.005
    loop.leak_rate = 0.001
    
    contrib = loop.compute(state, control, config)
    dm_dt = contrib.dydt["m_seed"]
    
    m_total = config.gas_mass + state.m_seed
    p_partial = (state.m_seed / m_total) * state.p_vessel
    cond = loop.condensation_rate(config.coolant_temp, p_partial)
    
    assert math.isclose(dm_dt, 0.005 - cond - 0.001, rel_tol=1e-9)

def test_condensation_increases_with_cold_wall():
    config = SystemConfig()
    loop = SeedLoop(config)
    
    cond_hot = loop.condensation_rate(T_condenser=400.0, p_partial=1000.0)
    cond_cold = loop.condensation_rate(T_condenser=300.0, p_partial=1000.0)
    
    assert cond_cold > cond_hot

def test_efficiency_penalty_with_leak():
    config = SystemConfig()
    loop = SeedLoop(config)
    
    eta_perfect = loop.recovery_efficiency(m_unaccounted=0.0, m_injected=10.0)
    eta_leaky = loop.recovery_efficiency(m_unaccounted=1.0, m_injected=10.0)
    
    assert eta_perfect == 1.0
    assert eta_leaky < eta_perfect
    assert math.isclose(eta_leaky, 0.9, rel_tol=1e-9)
