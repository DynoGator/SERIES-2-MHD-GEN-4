import pytest
import numpy as np
from pydantic import ValidationError
from core.state_vector import StateVector

def test_immutability():
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=1e5, V_accum=0.1)
    with pytest.raises(ValidationError): # Pydantic ValidationError
        state.theta = 1.0

def test_array_round_trip():
    state = StateVector(
        theta=1.0, omega=2.0, T_core=3000.0,
        p_vessel=2e5, V_accum=0.5, m_seed=0.1,
        T_electron=500.0, coherence_r=0.9
    )
    arr = state.to_array(has_segments=False)
    assert len(arr) == 8 # 8 core state vars
    
    new_state = StateVector.from_array(arr, has_segments=False)
    assert new_state.theta == 1.0
    assert new_state.omega == 2.0
    assert new_state.T_core == 3000.0
    assert new_state.p_vessel == 2e5
    assert new_state.V_accum == 0.5
    assert new_state.m_seed == 0.1
    assert new_state.T_electron == 500.0
    assert new_state.coherence_r == 0.9

def test_segment_array_round_trip():
    state = StateVector(
        theta=1.0, omega=2.0, T_core=3000.0,
        p_vessel=2e5, V_accum=0.5, m_seed=0.1,
        T_electron=500.0, coherence_r=0.9,
        segment_currents=np.ones(8),
        segment_voltages=np.full(8, 2.0)
    )
    arr = state.to_array()
    new_state = StateVector.from_array(arr, has_segments=True)
    assert new_state.segment_currents is not None
    assert np.allclose(new_state.segment_currents, np.ones(8))
    assert new_state.segment_voltages is not None
    assert np.allclose(new_state.segment_voltages, np.full(8, 2.0))

def test_evolve_returns_new_instance():
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=1e5, V_accum=0.1)
    new_state = state.evolve(T_core=3000.0)
    assert new_state is not state
    assert state.T_core == 1000.0
    assert new_state.T_core == 3000.0

def test_evolve_invalid_key():
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=1e5, V_accum=0.1)
    with pytest.raises(KeyError):
        state.evolve(invalid_field=1)

def test_with_units():
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=1e5, V_accum=0.1)
    units = state.with_units()
    assert units["T_core"].dimensionality == "[temperature]"
    assert units["omega"].dimensionality == "[angle] / [time]" or str(units["omega"].dimensionality) == "1 / [time]" # Pint might simplify rad to dimensionless
