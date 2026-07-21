import pytest
import numpy as np
from core.state_vector import StateVector
from physics.base import NonPhysicalStateError

def test_no_launder_negative_temperature():
    arr = np.array([0.0, 100.0, -5.0, 1e5, 0.1, 0.01, 300.0, 1.0])
    with pytest.raises(NonPhysicalStateError) as exc:
        StateVector.from_array(arr)
    assert "T_core<=0" in str(exc.value)

def test_no_launder_non_finite():
    arr = np.array([0.0, 100.0, float('nan'), 1e5, 0.1, 0.01, 300.0, 1.0])
    with pytest.raises(NonPhysicalStateError) as exc:
        StateVector.from_array(arr)
    assert "non-finite:T_core" in str(exc.value)
