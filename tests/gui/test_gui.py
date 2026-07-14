import pytest
import sys
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from config.system_config import SystemConfig
from core.state_vector import StateVector
from gui.main_window import MainWindow
from gui.widgets.schematic_view import SchematicView
from gui.threads.simulation_worker import SimulationWorker
from control.state_machine import TwinState

# Setup QApplication instance for all tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

def test_main_window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "2MHDBMRIPS Digital Twin — GEN-4.0-PRA"
    assert window.tabs.count() == 8
    window.close()

def test_schematic_view(qtbot):
    view = SchematicView()
    qtbot.addWidget(view)
    state = StateVector(theta=0.0, omega=100.0, T_core=1500.0, p_vessel=2e5, V_accum=0.5, segments_current=np.array([500.0]*8))
    telemetry = {"time": 1.0}
    view.update_state(state, telemetry)
    # Just asserting it doesn't crash on paint
    view.repaint()

def test_simulation_worker(qtbot):
    config = SystemConfig()
    worker = SimulationWorker(config)
    
    with qtbot.waitSignal(worker.state_updated, timeout=1000):
        worker.start()
        
    worker.stop()
    worker.wait()
    assert not worker._running

def test_emergency_stop():
    config = SystemConfig()
    worker = SimulationWorker(config)
    worker.emergency_stop()
    assert worker.twin.state_machine.current_state == TwinState.FAULT_LATCH
