from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF

class SchematicView(QWidget):
    def __init__(self):
        super().__init__()
        self.state = None
        self.telemetry = {}
        # Set background
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("#161B22"))
        self.setPalette(p)

    def update_state(self, state, telemetry):
        self.state = state
        self.telemetry = telemetry
        self.update() # trigger paintEvent

    def paintEvent(self, event):
        if self.state is None:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center of widget
        cx, cy = self.width() / 2, self.height() / 2
        
        # Draw Toroidal Loop
        T = getattr(self.state, 'T_core', 300.0)
        # map 300K to blue, 3000K to red
        ratio = min(max((T - 300) / 2700.0, 0.0), 1.0)
        r, b = int(255 * ratio), int(255 * (1 - ratio))
        ring_color = QColor(r, 0, b)
        
        pen = QPen(ring_color)
        pen.setWidth(10)
        painter.setPen(pen)
        radius = min(cx, cy) * 0.6
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))
        
        # Draw Segments
        if hasattr(self.state, 'segments_current'):
            num_segments = len(self.state.segments_current)
            import math
            for i in range(num_segments):
                angle = 2 * math.pi * i / num_segments
                sx = cx + radius * math.cos(angle)
                sy = cy + radius * math.sin(angle)
                I = self.state.segments_current[i]
                
                # Green = nominal, Yellow = warning, Red = overcurrent
                if I > 1000:
                    c = QColor("#FF4D4D")
                elif I > 800:
                    c = QColor("#F0883E")
                else:
                    c = QColor("#00D4AA")
                    
                painter.setBrush(QBrush(c))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(QRectF(sx - 10, sy - 10, 20, 20))
                
                # Draw text overlay
                painter.setPen(QColor("#E6EDF3"))
                painter.drawText(int(sx - 20), int(sy + 25), f"{I:.1f}A")
                
        # Draw RPM gauge
        omega = getattr(self.state, 'omega', 0.0)
        painter.setPen(QColor("#7EE787"))
        painter.drawText(10, 20, f"RPM: {omega * 30 / math.pi:.0f}")
        
        # Draw Pressure
        p = getattr(self.state, 'p_vessel', 1e5)
        painter.drawText(10, 40, f"P_vessel: {p / 1e5:.2f} bar")
        
        painter.end()
