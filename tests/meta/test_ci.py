import os
import yaml

def test_ci_file_exists():
    assert os.path.exists(".github/workflows/ci.yml")

def test_ci_contains_test_job():
    with open(".github/workflows/ci.yml", "r") as f:
        content = f.read()
    assert "pytest" in content

def test_ci_contains_python_matrix():
    with open(".github/workflows/ci.yml", "r") as f:
        config = yaml.safe_load(f)
    matrix = config["jobs"]["test"]["strategy"]["matrix"]["python-version"]
    assert len(matrix) >= 3
    assert "3.11" in matrix
    assert "3.12" in matrix
    assert "3.13" in matrix
