import pytest
from telemetry.statistical_detector import StatisticalDetector

def test_catches_injected_spike():
    detector = StatisticalDetector("alpha")
    
    # 100 samples of quiet baseline
    for i in range(100):
        detector.process(float(i), {"geomagnetic_nt": 50000.0})
        
    # Inject 5-sigma spike
    # std of constant series is 0, so any deviation will have infinite z-score.
    # We should add a small noise to baseline to get a real std.
    import numpy as np
    np.random.seed(42)
    detector.history["geomagnetic_nt"].clear()
    
    for i in range(100):
        detector.process(float(i), {"geomagnetic_nt": 50000.0 + np.random.randn()})
        
    # The std is ~ 1.0
    # Add a spike of 6.0
    events = detector.process(100.0, {"geomagnetic_nt": 50006.0})
    assert len(events) == 1
    assert events[0].anomaly_type == "GEOMAGNETIC_SPIKE"

def test_quiet_baseline_zero_false_positives():
    detector = StatisticalDetector("alpha")
    import numpy as np
    np.random.seed(42)
    
    events = []
    for i in range(600): # 10 minutes at 1Hz
        evs = detector.process(float(i), {"geomagnetic_nt": 50000.0 + np.random.randn()})
        events.extend(evs)
        
    assert len(events) == 0

def test_detection_arms_only_after_min_samples():
    detector = StatisticalDetector("alpha")
    events = detector.process(1.0, {"geomagnetic_nt": 999999.0})
    assert len(events) == 0

def test_gpsdo_unlock_state_based():
    detector = StatisticalDetector("alpha")
    events = detector.process(1.0, {"gpsdo_lock": 0.0})
    assert len(events) == 1
    assert events[0].anomaly_type == "GPSDO_UNLOCK"
