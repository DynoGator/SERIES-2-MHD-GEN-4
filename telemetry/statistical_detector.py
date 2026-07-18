import yaml
import os
import numpy as np
from collections import deque
from network.events import make_event, AnomalyEvent
from typing import Dict, List, Deque

class StatisticalDetector:
    def __init__(self, node_id: str, config_path: str = None):
        self.node_id = node_id
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "detection_thresholds.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["channels"]
            
        self.history: Dict[str, Deque[float]] = {}
        for channel, cfg in self.config.items():
            self.history[channel] = deque(maxlen=cfg["rolling_window"])

        self.channel_map = {
            "geomagnetic_nt": "GEOMAGNETIC_SPIKE",
            "acoustic_db": "ACOUSTIC_MODE_SHIFT",
            "thermal_c": "THERMAL_ANOMALY",
            "hall_voltage_mv": "HALL_VOLTAGE_ANOMALY"
        }

    def process(self, ts_gps: float, channels: dict) -> List[AnomalyEvent]:
        events = []
        
        # GPSDO Unlock (state based)
        if "gpsdo_lock" in channels and channels["gpsdo_lock"] == 0.0:
            events.append(make_event(self.node_id, "GPSDO_UNLOCK", ts_gps, 1.0))
            
        # Statistical channels
        for channel, anomaly_type in self.channel_map.items():
            if channel in channels:
                val = channels[channel]
                cfg = self.config[channel]
                
                # Arm check
                if len(self.history[channel]) >= cfg["min_samples"]:
                    # Compute mean and std
                    hist_arr = np.array(self.history[channel])
                    mean = float(np.mean(hist_arr))
                    std = float(np.std(hist_arr))
                    
                    if std > 0:
                        z_score = abs(val - mean) / std
                        if z_score > cfg["sigma_threshold"]:
                            events.append(make_event(self.node_id, anomaly_type, ts_gps, float(z_score)))
                            
                # Update history
                self.history[channel].append(val)
                
        # Existing mock check compatibility
        if "simulate_anomaly" in channels:
            mock_type = channels["simulate_anomaly"]
            events.append(make_event(self.node_id, mock_type, ts_gps, 1.0))
            
        return events
