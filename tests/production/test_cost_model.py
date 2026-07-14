import yaml


def _load():
    with open("config/cost_model.yaml") as f:
        return yaml.safe_load(f)


def test_targets_within_range():
    t = _load()["unit_cost_target_usd"]
    assert t["min"] < t["target"] < t["max"]


def test_breakdown_sums_to_one():
    b = _load()["bom_breakdown"]
    total = b["materials_pct"] + b["labor_pct"] + b["overhead_pct"] + b["margin_pct"]
    assert abs(total - 1.0) < 1e-6


def test_regulatory_budget_positive():
    reg = _load()["regulatory_budget_usd"]
    assert all(v > 0 for v in reg.values())
