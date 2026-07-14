import os
import re
import pytest

DOCS = {
    "compliance/fcc_pre_check.md": r"FCC Part 15",
    "compliance/ce_marking.md": r"2006/42/EC",
    "compliance/ul_listing.md": r"UL 508A",
    "compliance/emc_test_plan.md": r"(CISPR 11|EN 61000)",
}


def test_all_docs_exist():
    for path in DOCS:
        assert os.path.exists(path), f"missing {path}"


@pytest.mark.parametrize("path,pattern", list(DOCS.items()))
def test_each_has_standard_ref(path, pattern):
    content = open(path).read()
    assert re.search(pattern, content), f"{path} missing standard ref {pattern}"


@pytest.mark.parametrize("path", list(DOCS))
def test_each_has_cost_estimate(path):
    content = open(path).read()
    assert "$" in content, f"{path} missing a cost estimate"
