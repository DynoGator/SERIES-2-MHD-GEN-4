# MODULE-STATUS: SCAFFOLD
"""
Level 1 Runner: 1D Network Model
"""
import numpy as np
from typing import List, Optional
from core.state_vector import StateVector
from core.integrator import RK45Integrator
from core.logging import TelemetryRingBuffer
from core.state_bounds import check_bounds, SafetyEvent
from config.system_config import SystemConfig
from physics.base import ControlVector, PowerLedger

from physics.thermo.working_fluid import WorkingFluid
from physics.mhd.conductivity import PlasmaConductivity
from physics.mhd.segmented_channel import SegmentedFaradayChannel
from physics.thermo.fross4 import FROSS4
from physics.mechanical.rotor import RotorDynamics
from physics.thermo.heat_transfer import HeatTransfer
from physics.electromagnetic.stator import DICASHybridStator
from physics.mhd.lorentz_force import LorentzForce
from physics.acoustic.modal_id import AcousticModalID
from physics.thermo.seed_loop import SeedLoop

from control.fpga import FPGAPhaseEngine
from control.state_machine import TwinStateMachine, TwinState, StateEvent
from core.safety_machine import SafetyMachine, SafetyState

class Network1DTwin:
    STATE_WIDTH = 24
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.integrator = RK45Integrator()
        self.telemetry = TelemetryRingBuffer()
        
        self.state_machine = TwinStateMachine(config)
        self.safety_machine = SafetyMachine()
        self.fpga = FPGAPhaseEngine(config)
        
        self.channel = SegmentedFaradayChannel(8, config)
        self.fross = FROSS4(config)
        
        self.modules = [
            WorkingFluid("B", config),
            PlasmaConductivity("K", config),
            self.channel,
            self.fross,
            RotorDynamics(config),
            HeatTransfer(config),
            DICASHybridStator(config),
            LorentzForce(config),
            AcousticModalID(config),
            SeedLoop(config)
        ]
        
        self.time = 0.0
        
        self.state = StateVector(
            theta=0.0,
            omega=0.0,
            T_core=config.coolant_temp,
            p_vessel=config.p_init,
            V_accum=config.accum_vol
        )
        
        self.control = ControlVector()
        self.power_ledgers = []

    @property
    def current_state(self) -> StateVector:
        return self.state

    def set_control(self, control: ControlVector):
        self.control = control

    def step(self, dt: float) -> StateVector:
        if self.state.p_vessel > self.config.max_pressure_vessel:
            self.state_machine.transition(StateEvent.SAFETY_FAULT)
            
        fault_latch = (self.state_machine.current_state == TwinState.FAULT_LATCH)
        
        self.fpga.tick(self.control.phase_cmd, fault_latch)
        
        def event_T_core(t, y):
            sv = StateVector.from_array(y, has_segments=True)
            return SAFETY_BOUNDS["T_core"]["max"] - sv.T_core
            
        def event_p_vessel(t, y):
            sv = StateVector.from_array(y, has_segments=True)
            return SAFETY_BOUNDS["p_vessel"]["max"] - sv.p_vessel
            
        def event_omega(t, y):
            sv = StateVector.from_array(y, has_segments=True)
            return SAFETY_BOUNDS["omega"]["max"] - sv.omega
            
        def event_V_accum(t, y):
            sv = StateVector.from_array(y, has_segments=True)
            return sv.V_accum - SAFETY_BOUNDS["V_accum"]["min"]

        events = [event_T_core, event_p_vessel, event_omega, event_V_accum]
        for e in events:
            e.terminal = True
        
        def cur_dydt(t, y):
            assert len(y) == self.STATE_WIDTH
            sv = StateVector.from_array(y, has_segments=True)
            d_total = {}
            for mod in self.modules:
                contrib = mod.compute(sv, self.control, self.config)
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
            
            return np.concatenate([base_dydt, np.zeros(16, dtype=np.float64)])
            
        t_span = (self.time, self.time + dt)
        y0 = self.state.to_array(has_segments=True)
        
        sol = self.integrator.solve(t_span, y0, cur_dydt)
        
        if not sol.success:
            from physics.base import IntegrationDivergedError
            raise IntegrationDivergedError(sol.message)
            
        if sol.status == 1:
            term_state = StateVector.from_array(sol.y[:, -1], has_segments=True)
            event = check_bounds(term_state)
            if event:
                self.state_machine.transition(StateEvent.SAFETY_FAULT)
        
        y_final = sol.y[:, -1]
        self.time = sol.t[-1]
        
        base_state = StateVector.from_array(y_final, has_segments=True)
        
        total_generated = 0.0
        total_dissipated = 0.0
        active_modules = []
        
        for mod in self.modules:
            contrib = mod.compute(base_state, self.control, self.config)
            total_generated += contrib.power_ledger.power_generated_w
            total_dissipated += contrib.power_ledger.power_dissipated_w
            if contrib.dydt or contrib.power_ledger.power_generated_w != 0 or contrib.power_ledger.power_dissipated_w != 0:
                active_modules.append(mod.__class__.__name__)
                
        E_stored = 0.5 * self.config.rotor_moi * base_state.omega**2 + 2.5 * base_state.p_vessel * base_state.V_accum
        E_stored_prev = 0.5 * self.config.rotor_moi * self.state.omega**2 + 2.5 * self.state.p_vessel * self.state.V_accum
        dE_dt = (E_stored - E_stored_prev) / (sol.t[-1] - self.time) if sol.t[-1] > self.time else 0.0
        
        residual = total_generated - total_dissipated - dE_dt
        norm_residual = abs(residual) / total_generated if total_generated > 0 else 0.0
        
        ledger = PowerLedger(
            power_generated_w=total_generated,
            power_dissipated_w=total_dissipated,
            power_uncertain_w=norm_residual
        )
        self.power_ledgers.append(ledger)
        
        self.state = base_state.evolve(
            segment_currents=self.channel._currents.copy(),
            segment_voltages=self.channel._voltages.copy()
        )

        event = check_bounds(self.state)
        if event:
            self.safety_machine.process_event(event)
            self.state_machine.transition(StateEvent.SAFETY_FAULT)
            
        modal_coherence = 1.0
        seed_inventory = self.state.m_seed

        self.telemetry.log(
            sim_time_s=self.time,
            state_vector=self.state.model_dump(),
            control_inputs={},
            power_terms=ledger.__dict__,
            safety_state=self.safety_machine.state.name,
            rng_seed=42,
            physics_modules_active=active_modules,
            power_ledger_total_w=total_generated - total_dissipated,
            exergy_destroyed_w=total_dissipated,
            segment_currents=self.state.segment_currents.tolist() if self.state.segment_currents is not None else [],
            segment_powers=self.channel._powers.tolist() if self.channel._powers is not None else [],
            state_machine_state=self.state_machine.current_state.name,
            fpga_phase_lock_ok=self.fpga.phase_lock_ok,
            modal_coherence=modal_coherence,
            seed_inventory=seed_inventory
        )
        
        return self.state

    def run(self, t_end: float) -> TelemetryRingBuffer:
        dt = 0.01
        steps = int(t_end / dt)
        for _ in range(steps):
            self.step(dt)
            if self.safety_machine.state in (SafetyState.FAULT_LATCH, SafetyState.WARNING):
                break
        return self.telemetry
