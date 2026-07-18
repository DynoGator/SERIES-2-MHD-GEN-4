#!/usr/bin/env python3
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from telemetry.statistical_detector import StatisticalDetector

class AnomalyDetector:
    ANOMALY_TYPES = [
        "GEOMAGNETIC_SPIKE", "THERMAL_ANOMALY", "ACOUSTIC_MODE_SHIFT", 
        "PLASMA_INSTABILITY", "HALL_VOLTAGE_ANOMALY", "GPSDO_UNLOCK"
    ]
    
    def __init__(self):
        self.detector = StatisticalDetector("alpha")

    def detect(self, telemetry):
        ts_gps = time.time()
        events = self.detector.process(ts_gps, telemetry)
        return [e.anomaly_type for e in events]

if __name__ == "__main__":
    print("Anomaly Detector Running")
    detector = AnomalyDetector()
    print("Detected:", detector.detect({"simulate_anomaly": "GPSDO_UNLOCK"}))
