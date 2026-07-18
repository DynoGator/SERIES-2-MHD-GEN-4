from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class CorrelationResult:
    coincident: bool
    lag_s: float
    coefficient: float

class CrossNodeCorrelator:
    def __init__(self, tolerance_s: float = 5.0):
        self.tolerance_s = tolerance_s

    def correlate(self, series_a: np.ndarray, series_b: np.ndarray, dt: float) -> CorrelationResult:
        if len(series_a) == 0 or len(series_b) == 0:
            return CorrelationResult(False, 0.0, 0.0)
            
        n = len(series_a)
        # Normalize
        a = series_a - np.mean(series_a)
        b = series_b - np.mean(series_b)
        
        std_a = np.std(a)
        std_b = np.std(b)
        if std_a == 0 or std_b == 0:
            return CorrelationResult(False, 0.0, 0.0)
            
        a = a / std_a
        b = b / std_b
        
        # Cross correlation
        corr = np.correlate(a, b, mode='full') / n
        
        # Find peak
        max_idx = np.argmax(corr)
        max_coeff = corr[max_idx]
        
        # Lag calculation
        # If max_idx is at the end of the first signal, lag is positive
        lag_idx = max_idx - (n - 1)
        lag_s = lag_idx * dt
        
        coincident = abs(lag_s) <= self.tolerance_s and max_coeff > 0.5
        
        return CorrelationResult(
            coincident=bool(coincident),
            lag_s=float(lag_s),
            coefficient=float(max_coeff)
        )
