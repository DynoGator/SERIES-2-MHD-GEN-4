import pytest
import numpy as np
import math
from control.fpga import FPGAPhaseEngine
from config.system_config import SystemConfig

def test_quadrature_spacing():
    config = SystemConfig()
    fpga = FPGAPhaseEngine(config)
    
    assert fpga.QUAD_OFFSET == 4294967296 // 4
    assert fpga.EIGHTH_OFFSET * 2 == 4294967296 // 4

def test_fault_latch_zeroes():
    config = SystemConfig()
    fpga = FPGAPhaseEngine(config)
    
    for _ in range(1000):
        drive = fpga.tick(0.0, False)
        if any(drive):
            break
            
    assert any(fpga.drive_outputs)
    
    drive = fpga.tick(0.0, True)
    assert not any(drive)
    assert not fpga.phase_lock_ok

def test_frequency_accuracy():
    config = SystemConfig()
    fpga = FPGAPhaseEngine(config)
    
    total_phase = 0
    prev_acc = fpga.phase_accumulator
    for _ in range(100000):
        fpga.tick(0.0, False)
        acc = fpga.phase_accumulator
        if acc < prev_acc:
            total_phase += fpga.PHASE_MAX
        prev_acc = acc
    total_phase += fpga.phase_accumulator
    
    assert math.isclose(total_phase, 185542587, rel_tol=0.05)

def test_deadtime_enforced():
    config = SystemConfig()
    fpga = FPGAPhaseEngine(config)
    
    fpga.tick(0.0, False)
    fpga._last_switch_tick[1] = fpga.tick_count
    
    for _ in range(fpga.DEADTIME_TICKS - 2):
        fpga.tick(0.0, False)
