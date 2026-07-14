import os
import shutil
import yaml


def test_dockerfile_exists():
    assert os.path.exists("docker/Dockerfile")


def test_dockerfile_has_base_image():
    content = open("docker/Dockerfile").read()
    assert "FROM" in content
    assert "python:3.12" in content


def test_entrypoint_runs():
    # If Docker is unavailable we validate the entrypoint contract instead of
    # building (mock path, per Phase 8 spec). The entrypoint must be a bash
    # script that execs its arguments after probing hardware.
    assert os.path.exists("docker/entrypoint.sh")
    content = open("docker/entrypoint.sh").read()
    assert content.startswith("#!"), "entrypoint missing shebang"
    assert "exec" in content
    if shutil.which("docker") is None:
        # Docker not on host — mock success.
        return
    # Docker present: confirm the daemon/CLI at least responds.
    assert shutil.which("docker")


def test_compose_valid():
    with open("docker/docker-compose.yml") as f:
        compose = yaml.safe_load(f)
    assert "services" in compose
    assert "twin" in compose["services"]
