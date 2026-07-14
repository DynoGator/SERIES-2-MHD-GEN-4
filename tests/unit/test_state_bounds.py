from core.state_vector import StateVector
from core.state_bounds import check_bounds, SafetyAction

def test_temp_violation():
    state = StateVector(theta=0.0, omega=10.0, T_core=4000.0, p_vessel=1e5, V_accum=0.1)
    event = check_bounds(state)
    assert event is not None
    assert event.bound_violated == "T_core"

def test_pressure_violation():
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=6.0e6, V_accum=0.1)
    event = check_bounds(state)
    assert event is not None
    assert event.bound_violated == "p_vessel"

def test_safe_state():
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=1e5, V_accum=0.1)
    event = check_bounds(state)
    assert event is None

def test_v_accum_warning():
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=1e5, V_accum=1e-7)
    event = check_bounds(state)
    assert event is not None
    assert event.bound_violated == "V_accum"
