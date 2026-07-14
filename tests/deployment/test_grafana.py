import json
import yaml


def _dashboard():
    with open("grafana/dashboard.json") as f:
        return json.load(f)


def test_dashboard_json_valid():
    d = _dashboard()
    assert isinstance(d.get("panels"), list)


def test_has_minimum_panels():
    assert len(_dashboard()["panels"]) >= 6


def test_has_t_core_panel():
    titles = [p.get("title", "") for p in _dashboard()["panels"]]
    assert any("T_core" in t or "Core Temp" in t for t in titles), titles


def test_datasource_configured():
    with open("grafana/datasource.yaml") as f:
        ds = yaml.safe_load(f)
    src = ds["datasources"][0]
    assert "url" in src and "name" in src
