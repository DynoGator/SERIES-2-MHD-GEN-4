import re
from scripts.generate_production_report import generate_report


def test_report_generated(tmp_path):
    path = generate_report(output_dir=str(tmp_path), date_str="20260714")
    import os
    assert os.path.exists(path)


def test_contains_bom_table(tmp_path):
    path = generate_report(output_dir=str(tmp_path), date_str="20260714")
    content = open(path).read()
    assert "|" in content
    assert "Bill of Materials" in content


def test_contains_risk_register(tmp_path):
    path = generate_report(output_dir=str(tmp_path), date_str="20260714")
    content = open(path).read()
    assert "Risk Register" in content


def test_total_cost_in_range(tmp_path):
    path = generate_report(output_dir=str(tmp_path), date_str="20260714")
    content = open(path).read()
    m = re.search(r"Total unit cost:\*\*\s*\$([\d,]+\.\d{2})", content)
    assert m, "total unit cost line not found"
    total = float(m.group(1).replace(",", ""))
    assert 10000 <= total <= 25000, f"unit cost {total} outside [$10k,$25k]"
