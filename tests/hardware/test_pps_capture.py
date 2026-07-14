import pytest
from hardware.fpga_interface import FPGAInterface
from hardware.pps_capture import PPSCapture

def test_arm_sets_status():
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    pps.arm()
    assert fpga.read_register(PPSCapture.PPS_STATUS) == 1

def test_wait_returns_dict():
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    res = pps.wait_for_edge()
    assert "tdc_lo" in res
    assert "tdc_hi" in res
    assert res["status"] == 2

def test_phase_error_in_range():
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    err = pps.compute_phase_error()
    assert -0.5e-6 <= err <= 0.5e-6

def test_reset_zeroes_tdc():
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    pps.wait_for_edge() # populates mock registers
    pps.reset_tdc()
    assert fpga.read_register(PPSCapture.TDC_COUNT_LO) == 0
    assert fpga.read_register(PPSCapture.TDC_COUNT_HI) == 0
