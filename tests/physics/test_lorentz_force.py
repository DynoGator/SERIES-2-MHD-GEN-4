from config.system_config import SystemConfig
import pytest
import numpy as np
from physics.mhd.lorentz_force import LorentzForce

def test_force_perpendicular_to_j_and_b():
    lf = LorentzForce(SystemConfig())
    J = np.array([1.0, 2.0, 3.0])
    B = np.array([4.0, 5.0, 6.0])
    F = lf.body_force_density(J, B)
    # Dot product should be zero
    assert np.isclose(np.dot(F, J), 0.0)
    assert np.isclose(np.dot(F, B), 0.0)

def test_torque_sign():
    lf = LorentzForce(SystemConfig())
    F_mag = 100.0
    tau = lf.torque_from_force(F_mag, 0.5)
    # The magnitude is just passed through here, but essentially if I_arc is positive 
    # (generator action), tau opposes motion. 
    # We just check the calculation matches
    assert tau == 50.0
