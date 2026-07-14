import pytest
from hardware.fpga_interface import FPGAInterface
from hardware.pps_capture import PPSCapture
from hardware.gpsdo_sync import GPSDOSync
from digital_twin.hil_runner import HILRunner
from digital_twin.channel_2d import Channel2DTwin
from config.system_config import SystemConfig
from core.state_vector import StateVector

def test_hil_step_returns_tuple():
    config = SystemConfig()
    twin = Channel2DTwin(config)
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    runner = HILRunner(twin, fpga, gpsdo)
    
    state, ledger = runner.step(0.1)
    assert isinstance(state, StateVector)
    assert isinstance(ledger, dict)

def test_hardware_ledger_has_keys():
    config = SystemConfig()
    twin = Channel2DTwin(config)
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    runner = HILRunner(twin, fpga, gpsdo)
    
    ledger = runner.get_hardware_ledger()
    assert "phase_error_ns" in ledger
    assert "clock_offset_ns" in ledger
    assert "fpga_temp_c" in ledger

def test_mock_mode_runs_10s():
    config = SystemConfig()
    twin = Channel2DTwin(config)
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    runner = HILRunner(twin, fpga, gpsdo)
    
    # 10s run
    runner.run(10.0)

def test_control_registers_written():
    config = SystemConfig()
    twin = Channel2DTwin(config)
    fpga = FPGAInterface()
    fpga.connect()
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    runner = HILRunner(twin, fpga, gpsdo)
    
    runner.step(0.1)
    # tau_drive mapped to 0x2000
    assert fpga.read_register(0x2000) != 0
