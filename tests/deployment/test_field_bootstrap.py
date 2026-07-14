import pytest
import os
import zmq
from scripts.field_bootstrap import FieldBootstrap

def test_probe_returns_dict():
    bs = FieldBootstrap()
    hw = bs.probe_hardware()
    assert "fpga" in hw
    assert "gpsdo" in hw
    assert "sdr" in hw

def test_fallback_sets_mock():
    # Make sure we clean up env var if it exists
    if "FPGA_MOCK" in os.environ:
        del os.environ["FPGA_MOCK"]
        
    bs = FieldBootstrap()
    bs.fallback_if_needed()
    
    assert os.environ.get("FPGA_MOCK") == "1"

def test_telemetry_starts():
    bs = FieldBootstrap()
    bs.start_telemetry()
    assert bs._server._running is True
    bs._server.stop()
