# MODULE-STATUS: SCAFFOLD
import numpy as np
from typing import Set, Any
from physics.base import AbstractPhysicsModule, DerivativeContribution, PowerLedger

class RotorDynamics(AbstractPhysicsModule):
    def __init__(self, config: Any):
        self.config = config
        self.c_fric = 0.008

    def required_state_vars(self) -> Set[str]:
        return {"omega", "theta"}

    def contributed_derivatives(self) -> Set[str]:
        return {"omega", "theta"}

    def friction_torque(self, omega: float) -> float:
        return self.c_fric * omega

    def angular_acceleration(self, tau_drive: float, tau_em: float, tau_fric: float, J: float) -> float:
        return (1.0 / J) * (tau_drive - tau_em - tau_fric)

    def compute(self, state, control, config) -> DerivativeContribution:
        J = getattr(config, 'rotor_moi', 0.5)
        tau_drive = getattr(control, 'tau_drive', 0.0)
        # Note: tau_em could be computed here, or by LorentzForce. For lumped model, we assume tau_em is passed or we just use 0 here, and LorentzForce subtracts it.
        # But wait, alpha is (tau_drive - tau_em - tau_fric)/J. We will just compute the tau_drive - tau_fric part here.
        tau_fric = self.friction_torque(state.omega)
        domega = (tau_drive - tau_fric) / J
        return DerivativeContribution(
            dydt={"omega": domega, "theta": state.omega},
            power_ledger=PowerLedger(
                power_generated_w=tau_drive * state.omega,
                power_dissipated_w=tau_fric * state.omega
            )
        )

    def validate(self, config) -> list:
        return []
