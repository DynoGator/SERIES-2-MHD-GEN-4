#!/usr/bin/env python3
import time

class AnomalyDetector:
    ANOMALY_TYPES = [
        "GEOMAGNETIC_SPIKE", "THERMAL_ANOMALY", "ACOUSTIC_MODE_SHIFT", 
        "PLASMA_INSTABILITY", "HALL_VOLTAGE_ANOMALY", "GPSDO_UNLOCK"
    ]
    
    def detect(self, telemetry):
        if telemetry.get("simulate_anomaly"):
            return [telemetry["simulate_anomaly"]]
        return []

if __name__ == "__main__":
    print("Anomaly Detector Running")
    detector = AnomalyDetector()
    print("Detected:", detector.detect({"simulate_anomaly": "GPSDO_UNLOCK"}))
