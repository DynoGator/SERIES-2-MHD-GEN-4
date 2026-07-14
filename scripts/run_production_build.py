"""
Phase 8 — Production build orchestrator.

Steps:
  1. Load config/cost_model.yaml
  2. Generate BOM CSV
  3. Run the full test suite (unless --skip-tests)
  4. Build the Docker image (skipped/mocked if Docker is unavailable)
  5. Emit outputs/production_report_YYYYMMDD.md

Completes without exception even when Docker is absent — that path is mocked.
"""
import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime

# Add the project root to sys.path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
from config.materials_db import BOMGenerator
from scripts.generate_production_report import generate_report

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def step(msg: str) -> None:
    print(f"[production-build] {msg}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="2MHDBMRIPS production build")
    parser.add_argument("--skip-tests", action="store_true", help="skip the pytest gate")
    parser.add_argument("--skip-docker", action="store_true", help="skip the docker build")
    args = parser.parse_args(argv)

    date_str = datetime.now().strftime("%Y%m%d")

    # 1. Cost model -----------------------------------------------------------
    with open(os.path.join(ROOT, "config", "cost_model.yaml")) as f:
        cost_model = yaml.safe_load(f)
    target = cost_model["unit_cost_target_usd"]
    step(f"Cost target band: ${target['min']:,}–${target['max']:,} (target ${target['target']:,})")

    # 2. BOM CSV --------------------------------------------------------------
    bom_gen = BOMGenerator(
        materials_db_path=os.path.join(ROOT, "config", "materials_db.yaml"),
        cost_model_path=os.path.join(ROOT, "config", "cost_model.yaml"),
    )
    csv_path = os.path.join(ROOT, "outputs", f"bom_{date_str}.csv")
    bom_gen.export_csv(csv_path)
    summary = bom_gen.get_cost_summary()
    step(f"BOM exported -> {csv_path}  (unit cost ${summary['total']:,.2f})")

    # 3. Tests ----------------------------------------------------------------
    if args.skip_tests:
        step("Skipping test gate (--skip-tests).")
    else:
        step("Running test suite...")
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q"],
            cwd=ROOT,
        )
        if r.returncode != 0:
            step("TEST GATE FAILED — build halted.")
            return r.returncode
        step("Test gate passed.")

    # 4. Docker ---------------------------------------------------------------
    if args.skip_docker:
        step("Skipping docker build (--skip-docker).")
    elif shutil.which("docker") is None:
        step("MOCK: docker not available on host — skipping image build "
             "(Dockerfile validated by tests/deployment/test_docker.py).")
    else:
        step("Building docker image 2mhd-twin:latest ...")
        r = subprocess.run(
            ["docker", "build", "-f", "docker/Dockerfile", "-t", "2mhd-twin:latest", "."],
            cwd=ROOT,
        )
        if r.returncode != 0:
            step("Docker build failed.")
            return r.returncode
        step("Docker image built.")

    # 5. Report ---------------------------------------------------------------
    report = generate_report(output_dir=os.path.join(ROOT, "outputs"), date_str=date_str)
    step(f"Production report -> {report}")
    step("Production build complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
