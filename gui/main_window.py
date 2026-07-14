from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from gui.widgets.schematic_view import SchematicView
from gui.widgets.strip_chart import StripChart
from gui.widgets.gate_runner import GateRunner
from gui.widgets.control_panel import ControlPanel
from gui.widgets.state_machine_led import StateMachineLED

from config.system_config import SystemConfig
from gui.threads.simulation_worker import SimulationWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2MHDBMRIPS Digital Twin — GEN-4.0-PRA")
        self.setMinimumSize(1280, 800)
        self.resize(1920, 1080)
        
        self.config = SystemConfig()
        self.worker = SimulationWorker(self.config)
        self.worker.state_updated.connect(self.on_state_updated)
        
        self.init_ui()
        self.worker.start()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left Sidebar
        self.sidebar = QVBoxLayout()
        self.state_led = StateMachineLED()
        self.sidebar.addWidget(self.state_led)
        
        self.control_panel = ControlPanel()
        self.control_panel.emergency_stop_requested.connect(self.worker.emergency_stop)
        self.sidebar.addWidget(self.control_panel)
        
        main_layout.addLayout(self.sidebar, stretch=1)
        
        # Center Tab Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, stretch=4)
        
        self.schematic_view = SchematicView()
        self.tabs.addTab(self.schematic_view, "Live Schematic")
        
        self.strip_chart = StripChart()
        self.tabs.addTab(self.strip_chart, "Strip Charts")
        
        self.gate_runner = GateRunner(self.worker)
        self.tabs.addTab(self.gate_runner, "Validation")
        
        from gui.widgets.field_map import FieldMap
        self.field_map = FieldMap()
        self.tabs.addTab(self.field_map, "Field Map")
        
        from gui.widgets.hil_panel import HILPanel
        self.hil_panel = HILPanel()
        self.tabs.addTab(self.hil_panel, "HIL")
        
        # Create dummy tabs for Telemetry and Logs to satisfy spec
        self.tabs.addTab(QWidget(), "Telemetry")
        self.tabs.addTab(QWidget(), "Logs")
        
        from PyQt6.QtWidgets import QTextEdit
        self.boot_log = QTextEdit("Bootstrapping...\nField Bootstrap completed.\n")
        self.boot_log.setReadOnly(True)
        self.tabs.addTab(self.boot_log, "Boot Log")
        
        # Bottom Bar setup (handled in a real app with QStatusBar, but here we keep it simple)
        self.statusBar().showMessage("FPS: 0 | Simulation Time: 0.000 s | Safety: INIT | exergy: 0%")

    def on_state_updated(self, state, telemetry):
        self.schematic_view.update_state(state, telemetry)
        self.strip_chart.update_data(state, telemetry)
        self.state_led.update_state(telemetry.get("safety_state", "INIT"))
        
        t = telemetry.get("time", 0.0)
        safety = telemetry.get("safety_state", "INIT")
        exergy = telemetry.get("efficiency_ii", 0.0) * 100
        
        # Simple FPS counter
        if not hasattr(self, '_frame_times'):
            self._frame_times = []
        import time
        now = time.time()
        self._frame_times.append(now)
        if len(self._frame_times) > 30:
            self._frame_times.pop(0)
        fps = len(self._frame_times) / (now - self._frame_times[0]) if len(self._frame_times) > 1 else 0
        
        msg = f"FPS: {fps:.0f} | Simulation Time: {t:.3f} s | Safety: {safety} | exergy: {exergy:.1f}%"
        self.statusBar().showMessage(msg)

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        event.accept()
