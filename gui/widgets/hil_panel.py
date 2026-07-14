from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox
from PyQt6.QtCore import pyqtSignal

class HILPanel(QWidget):
    hil_emergency_stop = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Status Indicators
        group_status = QGroupBox("Hardware Status")
        lyt_status = QVBoxLayout()
        
        self.lbl_fpga_conn = QLabel("FPGA Connection: 🔴 DISCONNECTED")
        self.lbl_pps_lock = QLabel("PPS Lock: 🔴 UNLOCKED")
        self.lbl_gpsdo_lock = QLabel("GPSDO Stability: 🔴 UNSTABLE")
        
        lyt_status.addWidget(self.lbl_fpga_conn)
        lyt_status.addWidget(self.lbl_pps_lock)
        lyt_status.addWidget(self.lbl_gpsdo_lock)
        group_status.setLayout(lyt_status)
        layout.addWidget(group_status)

        # Data Display
        group_data = QGroupBox("HIL Telemetry")
        lyt_data = QVBoxLayout()
        self.lbl_phase_error = QLabel("TDC Phase Error: 0 ns")
        self.lbl_adev = QLabel("Allan Deviation (1s): N/A")
        self.lbl_cm5_temp = QLabel("CM5 Temp: N/A")
        
        lyt_data.addWidget(self.lbl_phase_error)
        lyt_data.addWidget(self.lbl_adev)
        lyt_data.addWidget(self.lbl_cm5_temp)
        group_data.setLayout(lyt_data)
        layout.addWidget(group_data)
        
        # Controls
        group_controls = QGroupBox("HIL Controls")
        lyt_controls = QHBoxLayout()
        
        self.btn_load_bitstream = QPushButton("Load Bitstream")
        self.btn_estop = QPushButton("HIL EMERGENCY STOP")
        self.btn_estop.setStyleSheet("background-color: #FF0000; color: white; font-weight: bold;")
        self.btn_estop.clicked.connect(self.hil_emergency_stop.emit)
        
        lyt_controls.addWidget(self.btn_load_bitstream)
        lyt_controls.addWidget(self.btn_estop)
        group_controls.setLayout(lyt_controls)
        layout.addWidget(group_controls)

        layout.addStretch()

    def update_telemetry(self, ledger: dict):
        if ledger.get("phase_error_ns", 1000) < 100:
            self.lbl_pps_lock.setText("PPS Lock: 🟢 LOCKED")
        else:
            self.lbl_pps_lock.setText("PPS Lock: 🔴 UNLOCKED")
            
        self.lbl_fpga_conn.setText("FPGA Connection: 🟢 CONNECTED")
        self.lbl_phase_error.setText(f"TDC Phase Error: {ledger.get('phase_error_ns', 0):.1f} ns")
        self.lbl_cm5_temp.setText(f"CM5 Temp: {ledger.get('fpga_temp_c', 0):.1f} °C")
