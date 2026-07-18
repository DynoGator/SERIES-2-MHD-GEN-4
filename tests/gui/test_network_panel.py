import pytest
from PyQt6.QtWidgets import QApplication
from gui.widgets.network_panel import NetworkPanel
import sys

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_network_panel_instantiation(qapp):
    panel = NetworkPanel()
    assert panel.event_table.columnCount() == 4
    assert "BROKERED" in panel.mode_led.text()
