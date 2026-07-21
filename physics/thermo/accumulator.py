# MODULE-STATUS: REAL-MODEL / PROVISIONAL-PARAMS
import math
from typing import Set
from dataclasses import dataclass
from config.system_config import SystemConfig
from physics.base import AbstractPhysicsModule, DerivativeContribution, PowerLedger
from physics.reference.mhd_reference import orifice_flow

@dataclass
class AccumulatorParams:
    p_pre: float
    V_shell: float
    p_crack: float
    n_poly: float = 1.3  # Bosch Rexroth, moderate cycling
    C_d: float = 0.61  # Merritt
    rho_oil: float = 850.0  # kg/m^3
    beta_oil: float = 1.5e9  # Pa
    eta_vol: float = 0.92
    eta_overall: float = 0.85
    area_orifice: float = 0.01  # PROVISIONAL
    area_relief: float = 0.005  # PROVISIONAL
    comp_disp: float = 1e-4  # PROVISIONAL

class FROSSAccumulator(AbstractPhysicsModule):
    def __init__(self, config: SystemConfig):
        self.config = config
        self.params = AccumulatorParams(
            p_pre=config.accum_precharge,
            V_shell=config.accum_vol,
            p_crack=0.9 * config.max_pressure_vessel
        )

    def required_state_vars(self) -> Set[str]:
        return {"p_vessel", "V_accum", "T_core"}

    def contributed_derivatives(self) -> Set[str]:
        return {"V_accum", "p_vessel"}
        
    def gas_pressure(self, V: float) -> float:
        if V <= 0:
            return float('inf')
        return self.params.p_pre * ((self.params.V_shell / V) ** self.params.n_poly)

    def gas_internal_energy(self, V: float) -> float:
        if V <= 0:
            return float('inf')
        P = self.gas_pressure(V)
        return (P * V) / (self.params.n_poly - 1.0)

    def _compute_impl(self, state, control, config) -> DerivativeContribution:
        p_gas = self.gas_pressure(state.V_accum)
        
        dP_orifice = state.p_vessel - p_gas
        Q_orifice_in = orifice_flow(self.params.C_d, self.params.area_orifice, dP_orifice, self.params.rho_oil)
        
        dP_relief = p_gas - self.params.p_crack
        Q_relief_out = 0.0
        if dP_relief > 0:
            Q_relief_out = orifice_flow(self.params.C_d, self.params.area_relief, dP_relief, self.params.rho_oil)
            
        rpm = control.compressor_rpm_cmd
        Q_comp_in = (rpm * self.params.comp_disp / 60.0) * self.params.eta_vol
        
        dV_dt = -(Q_orifice_in + Q_comp_in - Q_relief_out)
        
        V_vessel = config.plasma_vol
        dp_vessel_dt = -(self.params.beta_oil / V_vessel) * Q_orifice_in
        
        orifice_throttle = abs(Q_orifice_in * dP_orifice)
        relief_throttle = abs(Q_relief_out * dP_relief)
        
        p_atm = 101325.0
        dp_pump = max(0.0, p_gas - p_atm)
        pump_ideal = Q_comp_in * dp_pump
        if pump_ideal > 0:
            pump_shaft = pump_ideal / self.params.eta_overall
            pump_loss = pump_shaft - pump_ideal
        else:
            pump_loss = 0.0
            
        power_dissipated = orifice_throttle + relief_throttle + pump_loss
        
        return DerivativeContribution(
            dydt={"p_vessel": dp_vessel_dt, "V_accum": dV_dt},
            power_ledger=PowerLedger(
                power_generated_w=0.0,
                power_dissipated_w=power_dissipated
            )
        )

    def validate(self, config) -> list:
        return []
