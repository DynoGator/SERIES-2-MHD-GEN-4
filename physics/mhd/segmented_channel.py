# MODULE-STATUS: SCAFFOLD
"""
1D Segmented Faraday Channel
"""
from __future__ import annotations
import math
import numpy as np
from typing import Set, List
from physics.base import AbstractPhysicsModule, DerivativeContribution, ControlVector, PowerLedger, ValidationError
from core.state_vector import StateVector
from config.system_config import SystemConfig

class SegmentedFaradayChannel(AbstractPhysicsModule):
    def __init__(self, n_segments: int, config: SystemConfig):
        self.n_segments = n_segments
        self.config = config
        
        self.L_seg = getattr(config, 'channel_length', 1.0) / self.n_segments
        
        self._currents = np.zeros(self.n_segments)
        self._voltages = np.zeros(self.n_segments)
        self._powers = np.zeros(self.n_segments)
        self._sigma_mults = np.ones(self.n_segments)
        self._u_mults = np.ones(self.n_segments)

    def required_state_vars(self) -> Set[str]:
        return {"omega", "T_core"}

    def contributed_derivatives(self) -> Set[str]:
        return {"omega", "T_core"}

    def compute(self, state: StateVector, control: ControlVector, config: SystemConfig) -> DerivativeContribution:
        phi_psmic = control.phase_cmd
        kappa_psmic = 1.0 + 0.35 * math.sin(4.0 * phi_psmic)
        B_eff = config.B_max * (abs(kappa_psmic) ** 0.6)
        
        if state.T_core < 3000.0:
            sigma_eff = 1e-5
        else:
            sigma_eff = min(1.5e-3 * (state.T_core ** 1.5), 20000.0)
            
        r_eff = 0.5
        S_shear = 1.0
        u_plasma = state.omega * S_shear * r_eff
        
        total_P_extract = 0.0
        total_Q_joule = 0.0
        total_tau_em = 0.0
        
        # To match the lumped model exactly when uniform:
        # L_seg = 0.25 / 8
        self.L_seg = 0.25 / self.n_segments
        
        for i in range(self.n_segments):
            sigma_i = self._sigma_mults[i] * sigma_eff
            u_i = self._u_mults[i] * u_plasma
            
            E_i = u_i * B_eff * self.L_seg
            # R_internal_i scales so that total R_internal = 0.01 when sigma_mult = 1
            # Since segments are in series for total voltage, but parallel for current?
            # Actually we decided I_i = I_arc. So R_internal_i = 0.01 / 8 = 0.00125
            base_R_int = 0.01 / self.n_segments
            R_internal_i = base_R_int * (1.0 / self._sigma_mults[i]) if self._sigma_mults[i] > 0 else 1e6
            
            R_load_i = control.load_resistances[i] if control.load_resistances is not None else 1.0
            
            I_i = E_i / (R_load_i + R_internal_i)
            P_extract_i = I_i * E_i
            Q_joule_i = (I_i ** 2) * R_internal_i
            tau_em_i = I_i * B_eff * r_eff * kappa_psmic * (self.L_seg / 0.25)
            
            self._voltages[i] = E_i
            self._currents[i] = I_i
            self._powers[i] = P_extract_i
            
            total_P_extract += P_extract_i
            total_Q_joule += Q_joule_i
            total_tau_em += tau_em_i
            
        domega = -total_tau_em / config.rotor_moi
        m_cv = config.gas_mass * config.cv
        dT = (total_Q_joule - total_P_extract) / m_cv
        
        ledger = PowerLedger(
            power_generated_w=total_P_extract,
            power_dissipated_w=total_Q_joule,
            power_uncertain_w=0.0
        )
        return DerivativeContribution(
            dydt={"omega": domega, "T_core": dT},
            power_ledger=ledger
        )

    def segment_power(self, idx: int) -> float:
        return float(self._powers[idx])

    def segment_voltage(self, idx: int) -> float:
        return float(self._voltages[idx])

    def segment_current(self, idx: int) -> float:
        return float(self._currents[idx])

    def total_current_imbalance(self) -> float:
        I_max = np.max(self._currents)
        I_min = np.min(self._currents)
        I_mean = np.mean(self._currents)
        if I_mean == 0.0:
            return 0.0
        return float((I_max - I_min) / I_mean)

    def validate(self, config: SystemConfig) -> List[ValidationError]:
        return []
