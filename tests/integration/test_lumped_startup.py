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
    
    completed_full_run = (twin.time >= 4.9 and twin.safety_machine.state == SafetyState.ARMED)
    
    stopped_on_warning = False
    if twin.safety_machine.state == SafetyState.WARNING:
        history = twin.safety_machine.get_history()
        if history and history[-1].reason == "ACCUMULATOR_NEAR_EMPTY":
            stopped_on_warning = True
            
    assert completed_full_run or stopped_on_warning, f"Run stopped improperly. State: {twin.safety_machine.state}, Time: {twin.time}"
    assert len(twin.telemetry.buffer) > 0
