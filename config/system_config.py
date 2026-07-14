"""
System Configuration as an immutable Pydantic dataclass.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Optional

class SystemConfig(BaseModel):
    # Geometry
    rotor_moi: float = Field(default=0.5, description="Rotor moment of inertia (kg*m^2)")
    plasma_vol: float = Field(default=0.005, description="Plasma interaction volume (m^3)")
    vessel_area: float = Field(default=2.0, description="Vessel surface area (m^2)")
    R_torus: float = Field(default=0.5, description="Major radius of torus (m)")
    a_minor: float = Field(default=0.1, description="Minor radius of torus (m)")
    
    # Electromagnetic
    B_max: float = Field(default=2.0, description="Maximum magnetic flux density (T)")
    num_poles: int = Field(default=8, description="Number of electromagnetic poles")
    L_radial: float = Field(default=0.01, description="Radial inductance (H)")
    L_axial: float = Field(default=0.02, description="Axial inductance (H)")
    stator_turns: int = Field(default=100, description="Number of stator turns")
    
    # Thermodynamic
    p_init: float = Field(default=100000.0, description="Initial pressure (Pa)")
    accum_vol: float = Field(default=0.1, description="Accumulator volume (m^3)")
    accum_precharge: float = Field(default=50000.0, description="Accumulator precharge pressure (Pa)")
    coolant_temp: float = Field(default=300.0, description="Coolant temperature (K)")
    h_xfer_base: float = Field(default=500.0, description="Base heat transfer coefficient (W/m^2*K)")
    
    # Gas
    gas_mass: float = Field(default=0.1, description="Total gas mass (kg)")
    cv: float = Field(default=718.0, description="Specific heat at constant volume (J/kg*K)")
    r_specific: float = Field(default=287.0, description="Specific gas constant (J/kg*K)")
    gamma: float = Field(default=1.4, description="Heat capacity ratio")
    
    # Safety
    max_temp_electrode: float = Field(default=3695.0, description="Maximum electrode temperature (K)")
    max_pressure_vessel: float = Field(default=5.0e6, description="Maximum vessel pressure (Pa)")
    max_current: float = Field(default=1000.0, description="Maximum arc current (A)")
    max_rpm: float = Field(default=6000.0, description="Maximum RPM")
    
    # Control
    base_freq_hz: float = Field(default=50.0, description="Base electrical frequency (Hz)")
    phase_max_bits: int = Field(default=65536, description="Phase accumulator max value")
    deadtime_ticks: int = Field(default=100, description="Deadtime in clock ticks")

    # Options
    use_rembco: bool = Field(default=False, description="Use REBCO HTS magnets")
    cryo_cooling_power: Optional[float] = Field(default=None, description="Cryogenic cooling power (W)")

    model_config = {"frozen": True}

    @model_validator(mode='after')
    def validate_config(self) -> 'SystemConfig':
        if self.accum_vol <= 0:
            raise ValueError("accum_vol must be > 0")
        if self.max_temp_electrode > 3695.0:
            raise ValueError("max_temp_electrode must be <= 3695.0")
        if self.max_pressure_vessel > 5.0e6:
            raise ValueError("max_pressure_vessel must be <= 5.0e6")
        if self.L_radial <= 0 or self.L_axial <= 0:
            raise ValueError("All inductances must be > 0")
        if self.use_rembco and self.cryo_cooling_power is None:
            raise ValueError("cryo_cooling_power must be specified if use_rembco is True")
        return self
