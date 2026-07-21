import subprocess
import os
import sys

def verify_phase3():
    print("Running CI Verification...")
    
    # 1. Check pytest
    print("Running pytest on harness_selftest and physics...")
    res = subprocess.run(["pytest", "tests/harness_selftest/", "tests/physics/", "-v"], capture_output=True, text=True)
    if res.returncode != 0:
        print("Pytest failed!")
        print(res.stdout)
        print(res.stderr)
        sys.exit(1)
    else:
        print("Pytest passed.")
        
    # 2. Check Margin Report
    report_path = "Margin_Report.md"
    if not os.path.exists(report_path):
        print(f"Margin Report {report_path} not found!")
        sys.exit(1)
        
    with open(report_path, "r") as f:
        content = f.read()
        
    if "1200000.0" not in content and "Accumulator" not in content:
        print("Margin Report looks empty or invalid!")
        sys.exit(1)
        
    print("Margin Report verified.")
    print("Phase 3 Verification Complete.")

if __name__ == "__main__":
    verify_phase3()
