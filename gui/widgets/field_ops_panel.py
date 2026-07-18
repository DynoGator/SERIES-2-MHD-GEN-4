from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTextEdit, QProgressBar, QGroupBox, QFormLayout
)

class FieldOpsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Site Selector
        site_box = QGroupBox("Field Site")
        site_layout = QFormLayout(site_box)
        self.site_selector = QComboBox()
        self.site_selector.addItems(["Penrose, CO", "Mojave, CA", "Fairbanks, AK"])
        site_layout.addRow("Site:", self.site_selector)
        layout.addWidget(site_box)

        # Actions
        action_box = QGroupBox("Calibration & Testing")
        action_layout = QHBoxLayout(action_box)
        self.btn_calibrate = QPushButton("Trigger Calibration")
        self.btn_stress = QPushButton("Run Stress Test")
        action_layout.addWidget(self.btn_calibrate)
        action_layout.addWidget(self.btn_stress)
        layout.addWidget(action_box)
        
        # Battery Gauge
        batt_box = QGroupBox("Power (18650 VTC6 x2)")
        batt_layout = QVBoxLayout(batt_box)
        self.batt_gauge = QProgressBar()
        self.batt_gauge.setRange(0, 100)
        self.batt_gauge.setValue(95)
        batt_layout.addWidget(self.batt_gauge)
        layout.addWidget(batt_box)

        # Anomaly Feed
        feed_box = QGroupBox("Anomaly Feed")
        feed_layout = QVBoxLayout(feed_box)
        self.anomaly_feed = QTextEdit()
        self.anomaly_feed.setReadOnly(True)
        feed_layout.addWidget(self.anomaly_feed)
        layout.addWidget(feed_box)
