#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from control.state_machine import TwinStateMachine, StateEvent
from config.system_config import SystemConfig

def main():
    config = SystemConfig()
    sm = TwinStateMachine(config)
    
    sequence = [
        StateEvent.MAINTENANCE_KEY_TRUE,
        StateEvent.SENSORS_NOMINAL,
        StateEvent.PRESSURE_DECAY_OK,
        StateEvent.COMPRESSOR_MAP_OK,
        StateEvent.MODES_IDENTIFIED,
        StateEvent.LINER_TEMP_OK,
        StateEvent.SEED_SYSTEM_PERMISSIVE,
        StateEvent.PLASMA_IMPEDANCE_OK,
        StateEvent.B_FIELD_STABLE,
        StateEvent.OPEN_CIRCUIT_VOLTAGE_OK,
        StateEvent.SEGMENTS_LOADED_BALANCED
    ]
    
    print(f"Initial State: {sm.current_state().name}")
    for event in sequence:
        sm.transition(event)
        print(f"Trigger {event.name} -> {sm.current_state().name}")

if __name__ == "__main__":
    main()
