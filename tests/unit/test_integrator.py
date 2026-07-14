import numpy as np
from core.integrator import RK45Integrator

def test_exponential_decay():
    integrator = RK45Integrator(rtol=1e-4)
    def dydt(t, y):
        return -y
    
    sol = integrator.solve((0.0, 5.0), np.array([1.0]), dydt, events=None)
    assert np.isclose(sol.y[0, -1], np.exp(-5), rtol=1e-4)

def test_event_termination():
    integrator = RK45Integrator()
    def dydt(t, y):
        return -y
    
    def event_y_half(t, y):
        return y[0] - 0.5
    
    # Event attributes
    event_y_half.terminal = True
    event_y_half.direction = -1
    
    sol = integrator.solve((0.0, 5.0), np.array([1.0]), dydt, events=[event_y_half])
    
    assert sol.t[-1] < 5.0
    assert np.isclose(sol.y[0, -1], 0.5, atol=1e-3)
    assert len(sol.t_events[0]) > 0
