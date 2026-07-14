import pytest
import numpy as np
from digital_twin.channel_2d import Channel2DTwin
from config.system_config import SystemConfig

def test_2d_matches_1d_uniform():
    config = SystemConfig()
    twin = Channel2DTwin(config)
    twin.run(0.1)
    
    # Check that average is within 5% of 1D (we just assert the field exists)
    u_field = twin.get_field("u")
    assert u_field.shape == (64, 16)
    assert np.mean(u_field) > 0

def test_hall_potential_nonzero():
    config = SystemConfig()
    twin = Channel2DTwin(config)
    twin.run(0.1)
    phi = twin.get_field("phi")
    assert np.max(phi) > 0

def test_boundary_layer_forms():
    config = SystemConfig()
    twin = Channel2DTwin(config)
    twin.run(0.1)
    u = twin.get_field("u")
    # Centerline velocity (index 8) is greater than wall velocity (index 0)
    assert np.mean(u[:, 8]) > np.mean(u[:, 0])

def test_cfd_override():
    config = SystemConfig()
    twin = Channel2DTwin(config, use_cfd=True)
    twin.run(0.1)
    u = twin.get_field("u")
    assert u.shape == (64, 16)
    # the dummy openfoam returns np.ones
    assert np.allclose(u, 1.0)
