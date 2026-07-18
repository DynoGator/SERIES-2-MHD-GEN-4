import subprocess
import os

def test_bash_syntax_valid():
    script_path = "deployment/alpha_node_provision.sh"
    result = subprocess.run(["bash", "-n", script_path], capture_output=True)
    assert result.returncode == 0, f"Syntax error: {result.stderr.decode()}"

def test_dry_run_logs_all_steps():
    script_path = "deployment/alpha_node_provision.sh"
    result = subprocess.run(["bash", script_path, "--dry-run"], capture_output=True, text=True)
    
    assert result.returncode == 0
    
    output = result.stdout
    assert "[DRY-RUN] hostnamectl set-hostname alpha" in output
    assert "[DRY-RUN] apt-get update" in output
    assert "[DRY-RUN] apt-get install -y python3" in output
    assert "[DRY-RUN] git clone https://github.com/DynoGator/SERIES-2-MHD-GEN-4.git" in output
    assert "[DRY-RUN] python3 -m venv /opt/2mhd/venv" in output
    assert "[DRY-RUN] systemctl daemon-reload" in output

def test_dry_run_zero_side_effects():
    script_path = "deployment/alpha_node_provision.sh"
    result = subprocess.run(["bash", script_path, "--dry-run"], capture_output=True, text=True)
    
    # Assert no lines lack the prefix except headers/informational
    lines = result.stdout.strip().split("\n")
    for line in lines:
        if line.startswith("===") or line.startswith("Provisioning"):
            continue
        assert line.startswith("[DRY-RUN]"), f"Live side effect suspected: {line}"

def test_dry_run_deterministic():
    script_path = "deployment/alpha_node_provision.sh"
    r1 = subprocess.run(["bash", script_path, "--dry-run"], capture_output=True, text=True)
    r2 = subprocess.run(["bash", script_path, "--dry-run"], capture_output=True, text=True)
    
    assert r1.stdout == r2.stdout
