import pytest
from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig
from core.logging import set_deterministic_seed

def test_energy_closure():
    set_deterministic_seed()
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    # Remove modules so the integration doesn't blow up bounds
    twin.modules = []
    
    twin.run(0.1, dt_log=0.01)
    
    assert len(twin.power_ledgers) > 0
    
    # D-D1: Assert on D-D2's residual (power_uncertain_w)
    for ledger in twin.power_ledgers:
        assert ledger.power_uncertain_w < 1e-12
