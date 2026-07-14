import pytest
from hardware.fpga_interface import FPGAInterface
from hardware.pps_capture import PPSCapture
from hardware.gpsdo_sync import GPSDOSync
import time

def test_lock_mock_stable():
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    # mock returns 50 ns error by default
    assert gpsdo.lock() is True

def test_lock_mock_unstable():
    fpga = FPGAInterface()
    fpga.connect()
    fpga.write_register(0x9999, 1) # flag to make mock return > 500ns
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    assert gpsdo.lock() is False

def test_allan_deviation_positive():
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    assert gpsdo.sample_allan_deviation() > 0

def test_disciplined_time_advances():
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    
    t1 = gpsdo.get_disciplined_time()
    t2 = gpsdo.get_disciplined_time()
    assert t2 > t1
