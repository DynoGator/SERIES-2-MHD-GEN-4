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


# ---------------------------------------------------------------------------
# Phase 8: Bill of Materials (procurement) generator.
#
# This is distinct from the physics MATERIALS_DB above. It reads the
# procurement BOM (config/materials_db.yaml) and the cost model
# (config/cost_model.yaml) to produce costed, lead-time-aware BOMs for
# commercial packaging. "If the BOM doesn't close, the machine doesn't ship."
# ---------------------------------------------------------------------------
import os
import csv
import yaml
from typing import Any, List

BOM_CATEGORIES = ("mechanical", "electrical", "thermal", "control")


class BOMGenerator:
    """Generate a costed Bill of Materials from the procurement database."""

    def __init__(
        self,
        materials_db_path: str = "config/materials_db.yaml",
        cost_model_path: str = "config/cost_model.yaml",
    ):
        self.materials_db_path = materials_db_path
        self.cost_model_path = cost_model_path

        with open(materials_db_path, "r") as f:
            self._db = yaml.safe_load(f) or {}
        self._items: List[Dict[str, Any]] = self._db.get("items", [])

        with open(cost_model_path, "r") as f:
            self._cost_model = yaml.safe_load(f) or {}
        self._breakdown = self._cost_model.get("bom_breakdown", {})

    # -- core -----------------------------------------------------------------
    def _line_cost(self, item: Dict[str, Any], qty: int) -> float:
        return float(item["unit_cost_usd"]) * int(item.get("qty_per_unit", 1)) * qty

    def materials_cost(self, qty: int = 1) -> float:
        """Sum of all BOM line items (materials only)."""
        return round(sum(self._line_cost(it, qty) for it in self._items), 2)

    def generate_bom(self, qty: int = 1) -> Dict[str, Any]:
        """Return a structured BOM for the requested quantity of units."""
        lines = []
        categories: Dict[str, float] = {c: 0.0 for c in BOM_CATEGORIES}
        for it in self._items:
            line_cost = self._line_cost(it, qty)
            cat = it.get("category", "mechanical")
            categories[cat] = round(categories.get(cat, 0.0) + line_cost, 2)
            lines.append({
                "name": it["name"],
                "category": cat,
                "unit_cost_usd": float(it["unit_cost_usd"]),
                "qty": int(it.get("qty_per_unit", 1)) * qty,
                "line_cost_usd": round(line_cost, 2),
                "supplier": it.get("supplier", ""),
                "supplier_url": it.get("supplier_url", ""),
                "lead_time_weeks": float(it.get("lead_time_weeks", 0)),
            })
        return {
            "quantity": qty,
            "items": lines,
            "categories": categories,
            "materials_cost_usd": self.materials_cost(qty),
            "lead_time_weeks": self.get_lead_time_weeks(),
        }

    def get_cost_summary(self) -> Dict[str, float]:
        """Fully-burdened per-unit cost, derived from the cost model breakdown."""
        materials = self.materials_cost(1)
        materials_pct = float(self._breakdown.get("materials_pct", 0.45)) or 0.45
        total = materials / materials_pct
        labor = total * float(self._breakdown.get("labor_pct", 0.25))
        overhead = total * float(self._breakdown.get("overhead_pct", 0.20))
        return {
            "materials": round(materials, 2),
            "labor": round(labor, 2),
            "overhead": round(overhead, 2),
            "total": round(total, 2),
        }

    def get_lead_time_weeks(self) -> float:
        """Critical-path lead time = longest single-item lead time."""
        if not self._items:
            return 0.0
        return float(max(it.get("lead_time_weeks", 0) for it in self._items))

    def export_csv(self, path: str) -> None:
        """Write the qty=1 BOM to a CSV file with a header row."""
        bom = self.generate_bom(1)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        fields = [
            "name", "category", "unit_cost_usd", "qty",
            "line_cost_usd", "supplier", "supplier_url", "lead_time_weeks",
        ]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for line in bom["items"]:
                writer.writerow(line)
