import os
import yaml

MANIFESTS = [
    "k8s/namespace.yaml",
    "k8s/deployment.yaml",
    "k8s/service.yaml",
    "k8s/configmap.yaml",
    "k8s/pvc.yaml",
]


def test_all_manifests_exist():
    for m in MANIFESTS:
        assert os.path.exists(m), f"missing {m}"


def test_deployment_has_replicas():
    with open("k8s/deployment.yaml") as f:
        dep = yaml.safe_load(f)
    assert dep["spec"]["replicas"] == 2


def test_configmap_has_sites():
    content = open("k8s/configmap.yaml").read()
    assert "penrose_co" in content or "albuquerque_nm" in content


def test_manifests_parse():
    for m in MANIFESTS:
        with open(m) as f:
            doc = yaml.safe_load(f)
        assert "kind" in doc and "apiVersion" in doc
