from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTextEdit, QProgressBar, QGroupBox, QFormLayout, QFileDialog, QLabel
)
from telemetry.replay import CampaignReplayer
from telemetry.statistical_detector import StatisticalDetector
from network.consensus import ConsensusEngine

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

        # Replay Controls
        replay_box = QGroupBox("Campaign Replay")
        replay_layout = QVBoxLayout(replay_box)
        self.btn_replay = QPushButton("Replay Campaign")
        self.btn_replay.clicked.connect(self._run_replay)
        self.replay_status = QLabel("Ready")
        replay_layout.addWidget(self.btn_replay)
        replay_layout.addWidget(self.replay_status)
        layout.addWidget(replay_box)

        
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

    def _run_replay(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Campaign", "", "JSONL Files (*.jsonl)")
        if file_path:
            replayer = CampaignReplayer(file_path)
            detector = StatisticalDetector("alpha")
            consensus = ConsensusEngine(window_s=60.0)
            res = replayer.run(detector, consensus)
            cid = file_path.split('/')[-1].replace('.jsonl', '')
            self.replay_status.setText(f"Campaign: {cid} | Digest: {res['digest']}")
