# MODULE-STATUS: SCAFFOLD
"""
Level 0: ODE system from whitepaper §10.4
"""
from __future__ import annotations
import numpy as np
from typing import List

from core.integrator import RK45Integrator
from core.state_vector import StateVector
from core.safety_machine import SafetyMachine, SafetyState
from core.logging import TelemetryRingBuffer
from core.state_bounds import check_bounds
from config.system_config import SystemConfig
from physics.thermo.working_fluid import WorkingFluid
from physics.mhd.conductivity import PlasmaConductivity
from physics.mhd.faraday_channel import FaradayChannel
from physics.thermo.accumulator import FROSSAccumulator
from physics.mechanical.rotor import RotorDynamics
from physics.thermo.heat_transfer import HeatTransfer
from physics.electromagnetic.stator import DICASHybridStator
from physics.mhd.lorentz_force import LorentzForce
from physics.base import ControlVector, PowerLedger

class LumpedDigitalTwin:
    STATE_WIDTH = 8
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.integrator = RK45Integrator()
        self.safety_machine = SafetyMachine()
        self.telemetry = TelemetryRingBuffer()
        
        # Instantiate physics modules
        self.modules = [
            WorkingFluid("B", config),
            PlasmaConductivity("K", config),
            FaradayChannel(config),
            FROSSAccumulator(config),
            RotorDynamics(config),
            HeatTransfer(config),
            DICASHybridStator(config),
            LorentzForce(config)
        ]
        self.time = 0.0
        
        # Initial state
        self.state = StateVector(
            theta=0.0,
            omega=0.0,
            T_core=config.coolant_temp,
            p_vessel=config.p_init,
            V_accum=config.accum_vol
        )
        
        self.power_ledgers = []

    def dydt_wrapper(self, t: float, y: np.ndarray, control: ControlVector) -> np.ndarray:
        assert len(y) == self.STATE_WIDTH
        sv = StateVector.from_array(y, has_segments=False)
        d_total = {}
        for mod in self.modules:
            contrib = mod.compute(sv, control, self.config)
            for k, v in contrib.dydt.items():
                if not np.isfinite(v):
                    from physics.base import NonFiniteDerivativeError
                    raise NonFiniteDerivativeError(f"module={mod.__class__.__name__}, vars={k}")
                d_total[k] = d_total.get(k, 0.0) + v
                
        base_dydt = np.array([
            d_total.get("theta", 0.0),
            d_total.get("omega", 0.0),
            d_total.get("T_core", 0.0),
            d_total.get("p_vessel", 0.0),
            d_total.get("V_accum", 0.0),
            d_total.get("m_seed", 0.0),
            d_total.get("T_electron", 0.0),
            d_total.get("coherence_r", 0.0)
        ], dtype=np.float64)
        
        return base_dydt

    def run(self, t_end: float, dt_log: float = 0.01) -> None:
        control = ControlVector()
        
        from core.state_bounds import SAFETY_BOUNDS
        
        def event_T_core(t, y):
            sv = StateVector.from_array(y, has_segments=False)
            return SAFETY_BOUNDS["T_core"]["max"] - sv.T_core
            
        def event_p_vessel(t, y):
            sv = StateVector.from_array(y, has_segments=False)
            return SAFETY_BOUNDS["p_vessel"]["max"] - sv.p_vessel
            
        def event_omega(t, y):
            sv = StateVector.from_array(y, has_segments=False)
            return SAFETY_BOUNDS["omega"]["max"] - sv.omega
            
        def event_V_accum(t, y):
            sv = StateVector.from_array(y, has_segments=False)
            return sv.V_accum - SAFETY_BOUNDS["V_accum"]["min"]

        events = [event_T_core, event_p_vessel, event_omega, event_V_accum]
        for e in events:
            e.terminal = True
            
        def cur_dydt(t, y):
            return self.dydt_wrapper(t, y, control)

        t_span = (self.time, self.time + t_end)
        y0 = self.state.to_array(has_segments=False)
        
        from physics.base import NonPhysicalStateError
        try:
            sol = self.integrator.solve(t_span, y0, cur_dydt, events=events)
        except NonPhysicalStateError as e:
            self.telemetry.log(
                sim_time_s=self.time,
                state_vector=self.state.model_dump(),
                control_inputs={},
                power_terms={},
                safety_state="FAULT_LATCH",
                rng_seed=42,
                physics_modules_active=[],
                power_ledger_total_w=0.0,
                exergy_destroyed_w=0.0,
                fault_module=getattr(e, 'module_name', 'Unknown'),
                fault_reason=str(e)
            )
            raise        
        if not sol.success:
            from physics.base import IntegrationDivergedError
            raise IntegrationDivergedError(sol.message)
            
        if sol.status == 1:
            term_state = StateVector.from_array(sol.y[:, -1], has_segments=False)
            event = check_bounds(term_state)
            if event:
                self.safety_machine.process_event(event)
        
        # Post-process dense output to uniform timesteps
        if sol.t[-1] <= self.time:
            t_eval = np.array([self.time])
        else:
            t_eval = np.arange(self.time, sol.t[-1], dt_log)
            if len(t_eval) == 0 or t_eval[-1] != sol.t[-1]:
                t_eval = np.append(t_eval, sol.t[-1])

        y_eval = sol.sol(t_eval)
        
        E_prev = None
        t_prev = None
        
        for i in range(len(t_eval)):
            sv = StateVector.from_array(y_eval[:, i], has_segments=False)
            
            total_generated = 0.0
            total_dissipated = 0.0
            active_modules = []
            
            for mod in self.modules:
                contrib = mod.compute(sv, control, self.config)
                total_generated += contrib.power_ledger.power_generated_w
                total_dissipated += contrib.power_ledger.power_dissipated_w
                if contrib.dydt or contrib.power_ledger.power_generated_w != 0 or contrib.power_ledger.power_dissipated_w != 0:
                    active_modules.append(mod.__class__.__name__)
                    
            E_stored = 0.5 * self.config.rotor_moi * sv.omega**2 + 2.5 * sv.p_vessel * sv.V_accum
            if E_prev is not None and t_eval[i] > t_prev:
                dE_dt = (E_stored - E_prev) / (t_eval[i] - t_prev)
            else:
                dE_dt = 0.0
                
            E_prev = E_stored
            t_prev = t_eval[i]
            
            residual = total_generated - total_dissipated - dE_dt
            norm_residual = abs(residual) / total_generated if total_generated > 0 else 0.0

            ledger = PowerLedger(
                power_generated_w=total_generated,
                power_dissipated_w=total_dissipated,
                power_uncertain_w=norm_residual
            )
            self.power_ledgers.append(ledger)
            
            # Check bounds and safety
            event = check_bounds(sv)
            if event:
                self.safety_machine.process_event(event)

            self.telemetry.log(
                sim_time_s=t_eval[i],
                state_vector=sv.model_dump(),
                control_inputs={},
                power_terms=ledger.__dict__,
                safety_state=self.safety_machine.state.name,
                rng_seed=42,
                physics_modules_active=active_modules,
                power_ledger_total_w=total_generated - total_dissipated,
                exergy_destroyed_w=total_dissipated # Estimated
            )
            
            if self.safety_machine.state in (SafetyState.FAULT_LATCH, SafetyState.WARNING):
                break
        
        self.time = sol.t[-1]
        self.state = StateVector.from_array(sol.y[:, -1])
