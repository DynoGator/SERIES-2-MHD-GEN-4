import numpy as np
import math
from config.sites import SITES

class PenroseSignalModel:
    def __init__(self, site_key: str = "penrose_co", seed: int = 1337):
        self.site_key = site_key
        site_config = SITES[self.site_key]
        self.base_mag = site_config.get("geomagnetic_B_nT", 50000.0)
        self.noise_nt = site_config.get("noise_floor_nt", 5.0)
        
        self.rng = np.random.RandomState(seed)
        
        # Spikes: list of (start_t, magnitude, duration)
        self.spikes = []
        
    def geomagnetic_nt(self, t_s: float) -> float:
        # 50,000 nT baseline + diurnal (small sine wave) + noise
        diurnal = 50.0 * math.sin(2 * math.pi * t_s / 86400.0)
        noise = self.rng.normal(0, self.noise_nt)
        val = self.base_mag + diurnal + noise
        
        for start_t, mag, dur in self.spikes:
            if start_t <= t_s <= start_t + dur:
                val += mag
                
        return val
        
    def thermal_c(self, t_s: float) -> float:
        # diurnal curve + noise
        diurnal = 10.0 * math.sin(2 * math.pi * (t_s - 21600.0) / 86400.0)
        noise = self.rng.normal(0, 0.5)
        return 15.0 + diurnal + noise
        
    def acoustic_db(self, t_s: float) -> float:
        # ambient + noise
        noise = self.rng.normal(0, 2.0)
        return 35.0 + noise
        
    def inject_spike(self, t_s: float, magnitude_nt: float, duration_s: float) -> None:
        self.spikes.append((t_s, magnitude_nt, duration_s))
