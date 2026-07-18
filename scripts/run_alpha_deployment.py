#!/usr/bin/env python3
import subprocess

def run_deployment():
    print("Starting Alpha Deployment Orchestrator...")
    print("Provisioning CM5...")
    subprocess.run(["bash", "deployment/alpha_node_provision.sh"], check=False)
    print("Running Calibration...")
    res = subprocess.run(["python3", "scripts/field_calibration.py", "--site", "penrose_co"], capture_output=True, text=True)
    print(res.stdout)
    print("Running Stress Test...")
    subprocess.run(["python3", "scripts/field_stress_test.py", "--mock"], check=False)
    print("Deployment Report: SUCCESS")

if __name__ == "__main__":
    run_deployment()
