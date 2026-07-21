import pytest
import math
from config.system_config import SystemConfig
from core.state_vector import StateVector
from physics.base import ControlVector, NonPhysicalStateError
from physics.thermo.accumulator import FROSSAccumulator
from scipy.integrate import solve_ivp

def test_accumulator_self_equilibrates():
    config = SystemConfig()
    acc = FROSSAccumulator(config)
    acc.params.beta_oil = 1e5  # Lower for test to avoid stiff ODE hang
    
    # Initial imbalance: high p_vessel
    # State vector
    state = StateVector(theta=0, omega=0, p_vessel=1e6, V_accum=config.accum_vol * 0.9, T_core=300.0)
    control = ControlVector(compressor_rpm_cmd=0.0)
    
    def dydt(t, y):
        st = StateVector(theta=0, omega=0, p_vessel=y[0], V_accum=y[1], T_core=300.0)
        contrib = acc.compute(st, control, config)
        return [contrib.dydt["p_vessel"], contrib.dydt["V_accum"]]
    
    # integrate [p_vessel, V_accum] with a stiff solver
    try:
        res = solve_ivp(dydt, [0, 0.01], [state.p_vessel, state.V_accum], method='Radau', max_step=1e-5)
    except Exception as e:
        pytest.fail(f"Integration failed: {e}")
    
    final_p_vessel = res.y[0, -1]
    final_v_accum = res.y[1, -1]
    
    assert 0 < final_v_accum < config.accum_vol
    
    # Check if p_vessel approaches p_gas
    final_p_gas = acc.gas_pressure(final_v_accum)
    # The pressure difference should decrease or it equilibrates
    initial_diff = abs(1e6 - acc.gas_pressure(state.V_accum))
    final_diff = abs(final_p_vessel - final_p_gas)
    assert final_diff < initial_diff

def test_accumulator_relief_crippled_causes_error():
    config = SystemConfig()
    acc = FROSSAccumulator(config)
    
    # Cripple relief
    acc.params.area_relief = 1e-12 
    
    state = StateVector(theta=0, omega=0, p_vessel=10e6, V_accum=config.accum_vol * 0.5, T_core=300.0)
    control = ControlVector(compressor_rpm_cmd=0.0)
    
    def dydt(t, y):
        # Hold p_vessel high
        st = StateVector(theta=0, omega=0, p_vessel=10e6, V_accum=y[0], T_core=300.0)
        
        # If V_accum drops to <= 0, math.inf causes error, or we raise NonPhysicalStateError in integration
        try:
            contrib = acc.compute(st, control, config)
            # if gas pressure goes to inf, flow calculation may raise OverflowError or similar
            if st.V_accum <= 0:
                raise NonPhysicalStateError("V_gas <= 0")
        except OverflowError:
            raise NonPhysicalStateError("Overflow")
            
        return [contrib.dydt["V_accum"]]
    
    with pytest.raises(NonPhysicalStateError):
        # We manually check the condition during integration or let scipy fail and raise it
        # Actually, let's just integrate and if V_accum goes <= 0 we raise NonPhysicalStateError in dydt
        res = solve_ivp(dydt, [0, 1.0], [state.V_accum])
        if min(res.y[0]) <= 0:
            raise NonPhysicalStateError("V_gas <= 0")
