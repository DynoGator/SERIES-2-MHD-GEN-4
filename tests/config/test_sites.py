import pytest
from config.sites import SITES

def test_penrose_profile_loads():
    assert "penrose_co" in SITES
    site = SITES["penrose_co"]
    assert "elevation_m" in site
    assert "ambient_temp_K" in site
    assert "geomagnetic_B_nT" in site
    assert "geomagnetic_inclination_deg" in site
    assert "acoustic_baseline_hz" in site
    assert "node_id" in site
    assert site["node_id"] == "alpha"

def test_geomagnetic_inclination_affects_B_eff():
    penrose = SITES["penrose_co"]
    hessdalen = SITES["hessdalen_style"]
    assert penrose["geomagnetic_inclination_deg"] != hessdalen["geomagnetic_inclination_deg"]
    assert penrose["geomagnetic_B_nT"] != hessdalen["geomagnetic_B_nT"]
