import pytest
from typing import Set, Tuple, Any
from digital_twin.validation_runner import ValidationRunner
from config.system_config import SystemConfig
from physics.scavengers.base import BaseScavenger
from physics.base import DerivativeContribution, PowerLedger, ControlVector
from core.state_vector import StateVector
from config.scavenger_registry import ScavengerEntry

class MockScavenger(BaseScavenger):
    def __init__(self, config: Any, output_w: float):
        super().__init__(config)
        self.output_w = output_w

    def net_contribution(self) -> float:
        return self.output_w

    def ab_test(self, twin, duration: float) -> Tuple[float, float]:
        return (0.0, 0.0)

    def compute(self, state: StateVector, control: ControlVector, config: Any) -> DerivativeContribution:
        if not self.is_enabled:
            return DerivativeContribution(
                dydt={}, power_ledger=PowerLedger()
            )
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(
                power_generated_w=self.output_w,
                power_dissipated_w=0.0
            )
        )

def test_ab_diff_engine_recovers_known_delta():
    config = SystemConfig()
    runner = ValidationRunner(config)
    
    # Register our mock scavenger
    class TestMockScavenger(MockScavenger):
        def __init__(self, config):
            super().__init__(config, 40.0)
            
    runner.registry["TestScavenger"] = ScavengerEntry(
        module_class=TestMockScavenger,
        status="PROVISIONAL",
        kill_criterion=lambda r: r.net_delta_w < 10.0
    )
    
    # Clear out other scavengers to isolate
    for k in list(runner.registry.keys()):
        if k != "TestScavenger":
            del runner.registry[k]
            
    report = runner.run_ab_campaign("TestScavenger")
    
    assert abs(report.net_delta_w - 40.0) < 1e-6, f"Expected 40.0 W delta, got {report.net_delta_w}"
