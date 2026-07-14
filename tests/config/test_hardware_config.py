import pytest
import yaml
import re

def test_yaml_loads():
    with open("config/hardware_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    assert "hil_enabled" in config
    assert "fpga" in config
    assert "gpsdo" in config
    assert "cm5" in config

def test_fpga_ip_is_valid():
    with open("config/hardware_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    ip = config["fpga"]["ip"]
    assert re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip)

def test_mock_fallback_boolean():
    with open("config/hardware_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    assert isinstance(config["mock_fallback"], bool)
