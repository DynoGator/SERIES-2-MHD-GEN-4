import csv
import os
from config.materials_db import BOMGenerator, BOM_CATEGORIES


def test_bom_has_all_categories():
    bom = BOMGenerator().generate_bom(1)
    for cat in ("mechanical", "electrical", "thermal", "control"):
        assert cat in bom["categories"], f"missing category {cat}"
        assert bom["categories"][cat] > 0, f"category {cat} has no items"
    assert set(BOM_CATEGORIES) == {"mechanical", "electrical", "thermal", "control"}


def test_total_cost_positive():
    summary = BOMGenerator().get_cost_summary()
    assert summary["total"] > 0
    assert summary["materials"] > 0


def test_lead_time_realistic():
    lead = BOMGenerator().get_lead_time_weeks()
    assert 4 <= lead <= 52, f"lead time {lead} out of realistic band"


def test_csv_export_valid(tmp_path):
    out = tmp_path / "bom.csv"
    BOMGenerator().export_csv(str(out))
    assert out.exists()
    with open(out, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert "name" in reader.fieldnames
        assert "line_cost_usd" in reader.fieldnames
        assert len(rows) > 0
