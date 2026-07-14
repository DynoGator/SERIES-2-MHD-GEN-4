import pytest
from physics.thermo.working_fluid import WorkingFluid

def test_recipe_a_gamma():
    fluid = WorkingFluid('A', {})
    # Should be monatomic-dominant, around 1.66
    assert 1.6 < fluid.gamma < 1.7

def test_speed_of_sound():
    fluid = WorkingFluid('A', {})
    props1 = fluid.properties(300.0, 1e5)
    props2 = fluid.properties(1200.0, 1e5)
    assert props2.cs > props1.cs
    # Speed of sound scales with sqrt(T), so roughly double when temp quadruples
    assert abs(props2.cs / props1.cs - 2.0) < 0.05

def test_density_pressure_scaling():
    fluid = WorkingFluid('A', {})
    props1 = fluid.properties(300.0, 1e5)
    props2 = fluid.properties(300.0, 2e5)
    assert abs(props2.rho / props1.rho - 2.0) < 1e-5

def test_mixture_bounds():
    # Attempting to manipulate RECIPES for testing
    WorkingFluid.RECIPES['INVALID_NEG'] = {'Ar': 1.1, 'He': -0.1}
    with pytest.raises(ValueError, match="non-negative"):
        WorkingFluid('INVALID_NEG', {})
        
    WorkingFluid.RECIPES['INVALID_SUM'] = {'Ar': 0.9, 'He': 0.2}
    with pytest.raises(ValueError, match="sum to 1.0"):
        WorkingFluid('INVALID_SUM', {})
