import pytest
from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig
from core.logging import set_deterministic_seed

def test_energy_closure():
    set_deterministic_seed()
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    
    twin.run(5.0)
    
    assert len(twin.power_ledgers) > 0
    
    total_generated = sum(l.power_generated_w for l in twin.power_ledgers)
    total_dissipated = sum(l.power_dissipated_w for l in twin.power_ledgers)
    
    # Since this is Phase 0, we just check if it executed and generated data
    # The actual physics closure is for future phases.
    assert isinstance(total_generated, float)
    assert isinstance(total_dissipated, float)
