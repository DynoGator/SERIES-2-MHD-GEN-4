from __future__ import annotations

import numpy as np
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator
import pint

# Global unit registry — singleton, initialized once
ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

class StateVector(BaseModel):
    """
    Canonical immutable state vector for 2MHDBMRIPS GEN-4.0-PRA.
    All physical quantities are stored as SI base floats.
    Use .with_units() to attach Pint dimensions for display or validation.
    """
    # ─── Core Lumped States (Whitepaper §10.4) ───
    theta: float = Field(..., ge=0.0, description="Rotor angle [rad]")
    omega: float = Field(..., description="Rotor angular velocity [rad/s]")
    T_core: float = Field(..., gt=0.0, description="Plasma core temperature [K]")
    p_vessel: float = Field(..., gt=0.0, description="Vessel pressure [Pa]")
    V_accum: float = Field(..., gt=0.0, description="Accumulator gas volume [m³]")
    
    # ─── 1D Extension Points ───
    segment_currents: Optional[np.ndarray] = Field(None, description="8-segment currents [A]")
    segment_voltages: Optional[np.ndarray] = Field(None, description="8-segment voltages [V]")
    segment_powers: Optional[np.ndarray] = Field(None, description="8-segment powers [W]")
    
    # ─── Thermodynamic & Control Extensions ───
    m_seed: float = Field(0.0, ge=0.0, description="Seed mass inventory [kg]")
    T_electron: float = Field(300.0, gt=0.0, description="Electron temperature [K]")
    coherence_r: float = Field(0.0, ge=0.0, le=1.0, description="Kuramoto order parameter")
    
    # ─── Safety & State Machine ───
    safety_state: str = Field("ARMED", description="Safety machine state")
    machine_state: str = Field("LOCKOUT", description="Twin state machine state")
    
    model_config = {
        "arbitrary_types_allowed": True,
        "frozen": True,
    }
    
    # ─── Validation ───
    @field_validator("segment_currents", "segment_voltages", "segment_powers", mode="before")
    @classmethod
    def validate_segments(cls, v):
        if v is not None and len(v) != 8:
            raise ValueError("Segment arrays must be length 8")
        return v
    
    # ─── Serialization ───
    def to_array(self) -> np.ndarray:
        """Serialize core + segments to contiguous 1D float64 array."""
        core = np.array([
            self.theta, self.omega, self.T_core,
            self.p_vessel, self.V_accum, self.m_seed,
            self.T_electron, self.coherence_r,
        ], dtype=np.float64)
        
        if self.segment_currents is not None:
            core = np.concatenate([core, self.segment_currents.astype(np.float64)])
        else:
            core = np.concatenate([core, np.zeros(8, dtype=np.float64)])
            
        if self.segment_voltages is not None:
            core = np.concatenate([core, self.segment_voltages.astype(np.float64)])
        else:
            core = np.concatenate([core, np.zeros(8, dtype=np.float64)])
            
        return core
    
    @classmethod
    def from_array(cls, arr: np.ndarray, has_segments: bool = False) -> StateVector:
        """Deserialize from 1D numpy array."""
        if len(arr) < 8:
            raise ValueError(f"Array too short: expected >=8, got {len(arr)}")
        
        base = {
            "theta": float(arr[0]),
            "omega": float(arr[1]),
            "T_core": max(float(arr[2]), 1e-3),
            "p_vessel": max(float(arr[3]), 1e-3),
            "V_accum": max(float(arr[4]), 1e-6),
            "m_seed": max(float(arr[5]), 0.0),
            "T_electron": max(float(arr[6]), 1e-3),
            "coherence_r": min(max(float(arr[7]), 0.0), 1.0),
        }
        
        if has_segments and len(arr) >= 24:
            base["segment_currents"] = arr[8:16].copy()
            base["segment_voltages"] = arr[16:24].copy()
        
        return cls(**base)
    
    # ─── Immutability Interface ───
    def evolve(self, **updates: Any) -> StateVector:
        """
        Return a new StateVector with updated fields.
        Usage: new_state = state.evolve(T_core=3200.0, p_vessel=2.5e5)
        """
        current = self.model_dump()
        for key, val in updates.items():
            if key not in current:
                raise KeyError(f"StateVector has no field '{key}'")
            current[key] = val
        return StateVector(**current)
    
    # ─── Unit-Aware Display ───
    def with_units(self) -> Dict[str, pint.Quantity]:
        """Return mapping of field names to Pint Quantities."""
        return {
            "theta": Q_(self.theta, "rad"),
            "omega": Q_(self.omega, "rad/s"),
            "T_core": Q_(self.T_core, "K"),
            "p_vessel": Q_(self.p_vessel, "Pa"),
            "V_accum": Q_(self.V_accum, "m**3"),
            "m_seed": Q_(self.m_seed, "kg"),
        }
    
    def __repr__(self) -> str:
        return (
            f"<StateVector θ={self.theta:.4f} ω={self.omega:.2f} "
            f"T={self.T_core:.1f}K p={self.p_vessel/1e5:.3f}bar "
            f"Vacc={self.V_accum*1e3:.2f}L>"
        )
