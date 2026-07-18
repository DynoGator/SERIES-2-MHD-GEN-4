import pytest
from PyQt6.QtWidgets import QApplication
from gui.widgets.field_ops_panel import FieldOpsPanel
import sys

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_field_ops_panel_instantiation(qapp):
    panel = FieldOpsPanel()
    assert panel.site_selector.count() == 3
    assert panel.batt_gauge.value() == 95
