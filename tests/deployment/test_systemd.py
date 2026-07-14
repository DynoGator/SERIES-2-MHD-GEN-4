import os

def test_service_file_exists():
    assert os.path.exists("systemd/2mhd-digital-twin.service")

def test_exec_path_present():
    with open("systemd/2mhd-digital-twin.service", "r") as f:
        content = f.read()
    assert "ExecStart=" in content
    assert "python" in content or "2mhd-digital-twin" in content

def test_restart_policy_always():
    with open("systemd/2mhd-digital-twin.service", "r") as f:
        content = f.read()
    assert "Restart=always" in content
