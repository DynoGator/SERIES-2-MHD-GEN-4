import subprocess
import json
import sys
import os

# Ensure scripts directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from scripts.anomaly_detector import AnomalyDetector
from scripts.field_stress_test import FieldStressTest

def test_alpha_provision_script():
    res = subprocess.run(["bash", "deployment/alpha_node_provision.sh"], capture_output=True)
    assert b"Provisioning complete" in res.stdout

def test_field_calibration():
    res = subprocess.run(["python3", "scripts/field_calibration.py", "--site", "penrose_co"], capture_output=True, text=True)
    data = json.loads(res.stdout)
    assert data["site"] == "penrose_co"
    assert "geomagnetic_baseline_nt" in data

def test_anomaly_detector():
    detector = AnomalyDetector()
    res = detector.detect({"simulate_anomaly": "GPSDO_UNLOCK"})
    assert "GPSDO_UNLOCK" in res

def test_field_stress_mock():
    tester = FieldStressTest(mock_mode=True)
    assert tester.run_tests() is True
