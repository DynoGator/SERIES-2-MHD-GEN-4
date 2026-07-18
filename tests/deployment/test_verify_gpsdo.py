import subprocess
import json
import os

def test_mock_locked_passes():
    env = os.environ.copy()
    res = subprocess.run(
        ["python3", "scripts/verify_gpsdo_lock.py", "--mock"],
        capture_output=True, text=True, env=env
    )
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["verdict"] == "PASS"

def test_mock_unlocked_fails():
    env = os.environ.copy()
    env["GPSDO_MOCK_FAIL_LOCK"] = "1"
    res = subprocess.run(
        ["python3", "scripts/verify_gpsdo_lock.py", "--mock"],
        capture_output=True, text=True, env=env
    )
    assert res.returncode == 1
    data = json.loads(res.stdout)
    assert data["verdict"] == "FAIL"

def test_mock_allan_over_threshold_fails():
    env = os.environ.copy()
    env["GPSDO_MOCK_ALLAN"] = "2.0e-9"
    res = subprocess.run(
        ["python3", "scripts/verify_gpsdo_lock.py", "--mock", "--threshold", "1.0e-9"],
        capture_output=True, text=True, env=env
    )
    assert res.returncode == 1
    data = json.loads(res.stdout)
    assert data["verdict"] == "FAIL"
