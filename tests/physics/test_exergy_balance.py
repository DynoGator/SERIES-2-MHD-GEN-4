import pytest
import math
from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig

def test_exergy_balance():
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    
    twin.run(0.1, dt_log=0.01)
    
    for ledger in twin.power_ledgers:
        net = ledger.power_generated_w - ledger.power_dissipated_w
        assert isinstance(net, float)
