import pytest
from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig
from core.safety_machine import SafetyState
from core.logging import set_deterministic_seed

def test_fault_latch():
    set_deterministic_seed()
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    
    twin.run(1.0)
    assert twin.safety_machine.state == SafetyState.ARMED
    
    # Inject p_vessel = 6.0e6 at t=1.0
    twin.state = twin.state.evolve(p_vessel=6.0e6)
    
    twin.run(1.0)
    assert twin.safety_machine.state == SafetyState.FAULT_LATCH
    assert twin.time < 2.0  # Should have terminated integration early
