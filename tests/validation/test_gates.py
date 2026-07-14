import pytest
from config.system_config import SystemConfig
from digital_twin.network_1d import Network1DTwin
from validation.gates import Gate0_EnergyAccounting, Gate3_FROSS4Transient, Gate8_EnergyClosure

def test_g0_passes_with_balanced_ledger():
    config = SystemConfig()
    twin = Network1DTwin(config)
    # Default twin has no injected loss
    gate = Gate0_EnergyAccounting(config)
    res = gate.execute(twin)
    assert res.passed

def test_g0_fails_with_imbalanced_ledger():
    config = SystemConfig()
    twin = Network1DTwin(config)
    twin._injected_loss = 0.10 # 10%
    gate = Gate0_EnergyAccounting(config)
    res = gate.execute(twin)
    assert not res.passed
    assert res.measured_values["imbalance"] == 0.10

def test_g3_limits_pressure():
    config = SystemConfig()
    twin = Network1DTwin(config)
    twin.fross.injected_pulse = 2.0 * config.max_pressure_vessel
    gate = Gate3_FROSS4Transient(config)
    res = gate.execute(twin)
    # The pressure limit logic should keep it under 0.9 * max
    assert res.passed

def test_g8_closes_energy():
    config = SystemConfig()
    twin = Network1DTwin(config)
    # In a full simulation, scavengers help balance. Let's mock the final imbalance.
    twin._energy_imbalance = 0.02 # < 0.05
    gate = Gate8_EnergyClosure(config)
    res = gate.execute(twin)
    assert res.passed
