from physics.base import NonPhysicalStateError
import pytest
import pytest
from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig
from core.safety_machine import SafetyState
from core.logging import set_deterministic_seed

def test_lumped_startup():
    set_deterministic_seed()
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    
    twin.run(5.0)
    
    assert twin.safety_machine.state == SafetyState.ARMED
    assert twin.time >= 4.9 # Close to 5.0
    assert len(twin.telemetry.buffer) > 0
