from config.system_config import SystemConfig
import pytest
from physics.mechanical.rotor import RotorDynamics

def test_spin_up():
    rd = RotorDynamics(SystemConfig())
    tau_drive = 100.0
    tau_fric = rd.friction_torque(10.0)
    alpha = rd.angular_acceleration(tau_drive, 0.0, tau_fric, 5.0)
    assert alpha > 0

def test_steady_state():
    rd = RotorDynamics(SystemConfig())
    tau_drive = 10.0
    tau_em = 8.0
    tau_fric = 2.0
    alpha = rd.angular_acceleration(tau_drive, tau_em, tau_fric, 5.0)
    assert abs(alpha) < 1e-6

def test_friction_opposes_motion():
    rd = RotorDynamics(SystemConfig())
    assert rd.friction_torque(10.0) > 0
    assert rd.friction_torque(-10.0) < 0
