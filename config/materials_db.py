"""
Materials Database for the Digital Twin.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Dict

@dataclass
class Material:
    name: str
    melting_point_K: float
    thermal_conductivity_WmK: Callable[[float], float]  # T-dependent
    creep_rupture_MPa: Callable[[float, float], float]  # (T_K, hours) -> limit in MPa
    sputter_yield: Optional[Dict[str, float]] = None  # ion -> yield

# Dummy property functions for phase 0 scaffolding
def dummy_k(T: float) -> float: return 100.0
def dummy_creep(T: float, h: float) -> float: return 1000.0

MATERIALS_DB = {
    "Tungsten": Material(
        name="Tungsten",
        melting_point_K=3695.0,
        thermal_conductivity_WmK=lambda T: max(173.0 - 0.05 * T, 90.0),
        creep_rupture_MPa=lambda T, h: 50.0 if T > 2500 else 500.0,
        sputter_yield={"Ar": 1e-4}
    ),
    "Molybdenum": Material("Molybdenum", 2896.0, dummy_k, dummy_creep),
    "SiC_SiC_CMC": Material("SiC_SiC_CMC", 3000.0, dummy_k, dummy_creep),
    "Inconel_718": Material("Inconel_718", 1600.0, dummy_k, dummy_creep),
    "Copper_CuCrZr": Material("Copper_CuCrZr", 1350.0, dummy_k, dummy_creep),
    "Galinstan": Material("Galinstan", 262.0, dummy_k, dummy_creep),
    "Argon": Material("Argon", 83.8, dummy_k, dummy_creep),
    "Helium": Material("Helium", 4.22, dummy_k, dummy_creep),
    "Potassium": Material("Potassium", 336.7, dummy_k, dummy_creep),
    "Xenon": Material("Xenon", 161.4, dummy_k, dummy_creep)
}
