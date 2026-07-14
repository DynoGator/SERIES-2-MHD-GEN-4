import pytest
import numpy as np
import math
from physics.mhd.segmented_channel import SegmentedFaradayChannel
from config.system_config import SystemConfig
from physics.base import ControlVector
from core.state_vector import StateVector

def get_test_state():
    return StateVector(theta=0.0, omega=100.0, T_core=4000.0, p_vessel=1e5, V_accum=0.1)

def test_uniform_load_balanced():
    config = SystemConfig()
    channel = SegmentedFaradayChannel(8, config)
    state = get_test_state()
    control = ControlVector()
    
    channel.compute(state, control, config)
    assert channel.total_current_imbalance() < 1e-6

def test_segmented_loading_compensates():
    config = SystemConfig()
    channel = SegmentedFaradayChannel(8, config)
    state = get_test_state()
    control = ControlVector()
    control.load_resistances = np.full(8, 0.001)
    
    # Baseline
    channel.compute(state, control, config)
    baseline_I = channel.segment_current(3)
    
    # Segment 3 has 2x conductivity
    channel._sigma_mults[3] = 2.0
    channel.compute(state, control, config)
    imb_uncompensated = channel.total_current_imbalance()
    assert imb_uncompensated > 0.05
    
    R_load_old = control.load_resistances[3]
    R_int_old = (channel.segment_voltage(3) / baseline_I) - R_load_old
    R_int_new = R_int_old / 2.0
    
    control.load_resistances[3] = R_load_old + R_int_old - R_int_new
    channel.compute(state, control, config)
    imb_compensated = channel.total_current_imbalance()
    assert imb_compensated < 1e-6

def test_total_power_equals_sum():
    config = SystemConfig()
    channel = SegmentedFaradayChannel(8, config)
    state = get_test_state()
    control = ControlVector()
    
    contrib = channel.compute(state, control, config)
    sum_P = sum(channel.segment_power(i) for i in range(8))
    assert math.isclose(sum_P, contrib.power_ledger.power_generated_w, rel_tol=1e-9)

def test_imbalance_detected():
    config = SystemConfig()
    channel = SegmentedFaradayChannel(8, config)
    state = get_test_state()
    control = ControlVector()
    control.load_resistances = np.full(8, 0.001)
    
    channel._sigma_mults[1] = 10.0
    channel.compute(state, control, config)
    
    assert channel.total_current_imbalance() > 0.1
