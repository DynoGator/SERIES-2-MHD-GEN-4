"""
Unit registry and dimensional analysis guard.
"""
from __future__ import annotations
import pint

# Create a single global unit registry
ureg = pint.UnitRegistry(system='mks')
Q_ = ureg.Quantity

def enforce_units(value: float | Q_, expected_unit: str | pint.Unit) -> float:
    """
    Ensure the value has the correct units and return its magnitude in the expected unit.
    Rejects naked floats.
    
    Args:
        value: The pint Quantity to check.
        expected_unit: The unit string (e.g., 'kelvin', 'pascal') to convert to.
        
    Returns:
        float: The magnitude in the expected unit.
        
    Raises:
        ValueError: If value is a naked float or has incompatible units.
    """
    if not isinstance(value, pint.Quantity):
        raise ValueError(f"Value must be a pint Quantity with units, got {type(value)}")
    
    try:
        converted = value.to(expected_unit)
        return float(converted.magnitude)
    except pint.DimensionalityError as e:
        raise ValueError(f"Dimensionality mismatch: {e}")
