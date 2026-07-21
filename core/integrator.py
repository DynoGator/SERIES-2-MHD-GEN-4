from abc import ABC, abstractmethod
from typing import Callable, List, Tuple, Optional
import numpy as np
from scipy.integrate import solve_ivp

class OdeResult:
    def __init__(self, t: np.ndarray, y: np.ndarray, 
                 t_events: Optional[List] = None, sol=None,
                 success: bool = True, status: int = 0, message: str = ""):
        self.t = t
        self.y = y
        self.t_events = t_events
        self.sol = sol
        self.success = success
        self.status = status
        self.message = message

class Integrator(ABC):
    @abstractmethod
    def solve(self, t_span: Tuple[float, float], y0: np.ndarray,
              dydt_fn: Callable, events: List[Callable]) -> OdeResult:
        pass

class RK45Integrator(Integrator):
    """
    SciPy-backed RK45 with dense output and event detection.
    All safety boundaries must be registered as terminal events.
    """
    def __init__(self, max_step: float = 0.01, rtol: float = 1e-4, 
                 atol: float = 1e-6):
        self.max_step = max_step
        self.rtol = rtol
        self.atol = atol
    
    def solve(self, t_span, y0, dydt_fn, events=None) -> OdeResult:
        # Ensure events are terminal
        if events:
            for ev in events:
                if hasattr(ev, 'terminal'):
                    ev.terminal = True
        
        sol = solve_ivp(
            fun=dydt_fn,
            t_span=t_span,
            y0=y0,
            method='BDF',
            dense_output=True,
            events=events,
            max_step=self.max_step,
            rtol=self.rtol,
            atol=self.atol,
        )
        
        return OdeResult(
            t=sol.t,
            y=sol.y,
            t_events=sol.t_events,
            sol=sol.sol,
            success=sol.success,
            status=sol.status,
            message=sol.message
        )
    
    def interpolate(self, sol: OdeResult, t_new: np.ndarray) -> np.ndarray:
        """Interpolate solution to uniform timesteps for logging."""
        if hasattr(sol, 'sol') and sol.sol is not None:
            return sol.sol(t_new)
        raise ValueError("No dense output available. Use dense_output=True.")
