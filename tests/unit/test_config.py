import pytest
from pydantic import ValidationError
from config.system_config import SystemConfig

def test_config_valid():
    config = SystemConfig()
    assert config.accum_vol > 0

def test_config_invalid_accum_vol():
    with pytest.raises(ValidationError):
        SystemConfig(accum_vol=0.0)

def test_config_invalid_temp():
    with pytest.raises(ValidationError):
        SystemConfig(max_temp_electrode=4000.0)

def test_config_invalid_pressure():
    with pytest.raises(ValidationError):
        SystemConfig(max_pressure_vessel=6.0e6)

def test_config_invalid_inductance():
    with pytest.raises(ValidationError):
        SystemConfig(L_radial=-1.0)
        
def test_config_use_rembco_requires_cooling():
    with pytest.raises(ValidationError):
        SystemConfig(use_rembco=True, cryo_cooling_power=None)
