from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QGroupBox
from PyQt6.QtCore import Qt, pyqtSignal

class ControlPanel(QWidget):
    emergency_stop_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        # Thermal
        group_thermal = QGroupBox("THERMAL SOURCE")
        lyt_thermal = QVBoxLayout()
        lyt_thermal.addWidget(QLabel("Q_source (0-500 kW)"))
        self.slider_q = QSlider(Qt.Orientation.Horizontal)
        self.slider_q.setRange(0, 500)
        lyt_thermal.addWidget(self.slider_q)
        group_thermal.setLayout(lyt_thermal)
        layout.addWidget(group_thermal)
        
        # EM
        group_em = QGroupBox("ELECTROMAGNETIC")
        lyt_em = QVBoxLayout()
        lyt_em.addWidget(QLabel("B_max (0.5-5.0 T)"))
        self.slider_b = QSlider(Qt.Orientation.Horizontal)
        self.slider_b.setRange(5, 50) # x10
        lyt_em.addWidget(self.slider_b)
        group_em.setLayout(lyt_em)
        layout.addWidget(group_em)
        
        # Safety
        group_safety = QGroupBox("SAFETY")
        lyt_safety = QVBoxLayout()
        
        self.btn_start = QPushButton("START")
        self.btn_start.setStyleSheet("background-color: #00D4AA; color: black; font-weight: bold;")
        lyt_safety.addWidget(self.btn_start)
        
        self.btn_shutdown = QPushButton("CONTROLLED SHUTDOWN")
        self.btn_shutdown.setStyleSheet("background-color: #F0883E; color: black; font-weight: bold;")
        lyt_safety.addWidget(self.btn_shutdown)
        
        self.btn_estop = QPushButton("EMERGENCY STOP")
        self.btn_estop.setStyleSheet("background-color: #FF4D4D; color: white; font-weight: bold; border-radius: 20px; height: 40px;")
        self.btn_estop.clicked.connect(self.emergency_stop_requested.emit)
        lyt_safety.addWidget(self.btn_estop)
        
        from PyQt6.QtWidgets import QCheckBox
        self.chk_cfd = QCheckBox("Enable CFD Bridge (Level 2/3)")
        lyt_safety.addWidget(self.chk_cfd)
        
        group_safety.setLayout(lyt_safety)
        layout.addWidget(group_safety)
        
        layout.addStretch()
