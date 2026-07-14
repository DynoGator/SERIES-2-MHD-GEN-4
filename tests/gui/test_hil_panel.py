import pytest
from gui.widgets.hil_panel import HILPanel

def test_panel_instantiates(qtbot):
    panel = HILPanel()
    qtbot.addWidget(panel)
    assert panel is not None

def test_led_widgets_exist(qtbot):
    panel = HILPanel()
    qtbot.addWidget(panel)
    
    assert hasattr(panel, "lbl_fpga_conn")
    assert hasattr(panel, "lbl_pps_lock")
    assert hasattr(panel, "lbl_gpsdo_lock")

def test_estop_button_emits_signal(qtbot):
    panel = HILPanel()
    qtbot.addWidget(panel)
    
    with qtbot.waitSignal(panel.hil_emergency_stop, timeout=1000):
        panel.btn_estop.click()
