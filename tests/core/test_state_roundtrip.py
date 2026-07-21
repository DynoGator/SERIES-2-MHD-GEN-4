import numpy as np
from numpy.testing import assert_allclose
from core.state_vector import StateVector

def test_state_roundtrip_no_segments():
    s = StateVector(theta=1.0, omega=100.0, T_core=3000.0, p_vessel=1e5, V_accum=0.1, m_seed=0.01, T_electron=300.0, coherence_r=1.0)
    arr = s.to_array()
    s2 = StateVector.from_array(arr, has_segments=False)
    assert_allclose(s.to_array()[:8], s2.to_array()[:8])

def test_state_roundtrip_with_segments():
    s = StateVector(theta=1.0, omega=100.0, T_core=3000.0, p_vessel=1e5, V_accum=0.1, m_seed=0.01, T_electron=300.0, coherence_r=1.0,
                    segment_currents=np.ones(8), segment_voltages=np.ones(8)*2)
    arr = s.to_array()
    s2 = StateVector.from_array(arr, has_segments=True)
    assert_allclose(s.to_array(), s2.to_array())
