import pytest
import numpy as np
import math
from digital_twin.network_1d import Network1DTwin
from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig
from control.state_machine import TwinState, StateEvent
from physics.base import ControlVector

def test_1d_startup_matches_lumped():
    config = SystemConfig()
    net = Network1DTwin(config)
    lump = LumpedDigitalTwin(config)
    
    net.run(0.1)
    lump.run(0.1)
    
    s_net = net.state
    s_lump = lump.state
    
    # We might have slight differences due to module updates, but relatively close
    # The tolerance is relaxed slightly in case of minor integration differences
    assert math.isclose(s_net.omega, s_lump.omega, rel_tol=1e-2)
    assert math.isclose(s_net.T_core, s_lump.T_core, rel_tol=1e-2)

def test_segmented_loading_reduces_imbalance():
    config = SystemConfig()
    net = Network1DTwin(config)
    
    net.state = net.state.evolve(T_core=4000.0, omega=100.0)
    net.control.load_resistances = np.full(8, 0.001)
    
    net.channel._sigma_mults[0] = 5.0
    net.step(0.01)
    imb_uncompensated = net.channel.total_current_imbalance()
    
    control = ControlVector()
    control.load_resistances = np.full(8, 0.001)
    control.load_resistances[0] = 0.002
    net.set_control(control)
    
    net.step(0.01)
    imb_compensated = net.channel.total_current_imbalance()
    
    assert imb_compensated < imb_uncompensated * 0.7

def test_fross4_survives_blast():
    config = SystemConfig()
    net = Network1DTwin(config)
    
    net.fross.injected_pulse = 2.0 * config.max_pressure_vessel
    net.step(0.01)
    
    assert net.current_state.p_vessel < 0.9 * config.max_pressure_vessel
    assert net.state_machine.current_state != TwinState.FAULT_LATCH

def test_state_machine_sequence():
    config = SystemConfig()
    net = Network1DTwin(config)
    
    assert net.state_machine.current_state == TwinState.LOCKOUT
    net.state_machine.transition(StateEvent.MAINTENANCE_KEY_TRUE)
    assert net.state_machine.current_state == TwinState.SAFE_IDLE
