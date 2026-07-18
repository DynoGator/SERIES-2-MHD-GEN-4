from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt

class NetworkPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Node Status Cards
        nodes_layout = QHBoxLayout()
        for node in ["Alpha (Penrose)", "Beta (Albuquerque)", "Gamma (Hessdalen)"]:
            box = QGroupBox(node)
            form = QFormLayout(box)
            form.addRow("Site:", QLabel(node))
            form.addRow("GPSDO Lock:", QLabel("LOCKED"))
            form.addRow("Last Seen:", QLabel("0.0s ago"))
            nodes_layout.addWidget(box)
        layout.addLayout(nodes_layout)

        # Status Indicators
        status_box = QGroupBox("Network State")
        status_layout = QHBoxLayout(status_box)
        self.consensus_led = QLabel("CONSENSUS: IDLE")
        self.mode_led = QLabel("MODE: BROKERED")
        status_layout.addWidget(self.consensus_led)
        status_layout.addWidget(self.mode_led)
        layout.addWidget(status_box)

        # Cross-node Event Table
        table_box = QGroupBox("Cross-Node Event Correlation")
        table_layout = QVBoxLayout(table_box)
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(4)
        self.event_table.setHorizontalHeaderLabels(["Event ID", "Type", "Nodes", "Consensus"])
        table_layout.addWidget(self.event_table)
        layout.addWidget(table_box)
