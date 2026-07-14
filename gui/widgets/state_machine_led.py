from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

class StateMachineLED(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("INIT")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.label.setFont(font)
        
        self.setAutoFillBackground(True)
        layout.addWidget(self.label)
        self.update_state("INIT")

    def update_state(self, state_name: str):
        self.label.setText(state_name)
        
        # Color logic
        bg = "#161B22"
        fg = "#E6EDF3"
        
        if state_name == "FAULT_LATCH":
            bg = "#FF4D4D"
            fg = "#FFFFFF"
        elif "WARNING" in state_name:
            bg = "#F0883E"
            fg = "#FFFFFF"
        elif state_name == "STEADY_OPERATION":
            bg = "#00D4AA"
            fg = "#000000"
            
        self.setStyleSheet(f"background-color: {bg}; color: {fg}; border-radius: 5px;")
