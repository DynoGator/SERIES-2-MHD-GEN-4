from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRectF
from config.sites import SITES

class FieldMap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("Distributed Node Field Map")
        self.label.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(self.label)
        self.nodes_state = {site["node_id"]: "INIT" for site in SITES.values()}

    def update_node_state(self, node_id: str, state: str):
        self.nodes_state[node_id] = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw some markers for nodes
        cx, cy = self.width() / 2, self.height() / 2
        
        node_positions = {
            "alpha": (cx - 100, cy),     # Penrose
            "beta": (cx - 200, cy + 50), # ABQ
            "gamma": (cx + 300, cy - 100) # Hessdalen
        }
        
        for nid, (nx, ny) in node_positions.items():
            state = self.nodes_state.get(nid, "INIT")
            if state == "FAULT_LATCH":
                c = QColor("#FF4D4D")
            elif state == "STEADY_OPERATION":
                c = QColor("#00D4AA")
            else:
                c = QColor("#F0883E")
                
            painter.setBrush(c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(nx - 10, ny - 10, 20, 20))
            
            painter.setPen(QColor("#E6EDF3"))
            painter.drawText(int(nx - 20), int(ny + 25), f"Node: {nid.upper()}\n{state}")
            
        painter.end()
