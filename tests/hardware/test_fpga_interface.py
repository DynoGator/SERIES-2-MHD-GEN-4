import pytest
from hardware.fpga_interface import FPGAInterface

def test_mock_mode_fallback():
    fpga = FPGAInterface()
    assert fpga.connect() is True
    assert fpga.mock_mode is True
    status = fpga.get_status()
    assert status["locked"] is True

def test_register_round_trip():
    fpga = FPGAInterface()
    fpga.connect()
    fpga.write_register(0xDEAD, 0xBEEF)
    assert fpga.read_register(0xDEAD) == 0xBEEF

def test_status_has_required_keys():
    fpga = FPGAInterface()
    fpga.connect()
    status = fpga.get_status()
    assert "locked" in status
    assert "temp_c" in status
    assert "uptime_ms" in status

def test_close_idempotent():
    fpga = FPGAInterface()
    fpga.connect()
    fpga.close()
    fpga.close() # should not raise
