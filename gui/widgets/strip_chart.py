import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import numpy as np

class StripChart(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.win = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.win)
        
        # Plot 1: RPM & Torque
        self.p1 = self.win.addPlot(title="RPM & Torque")
        self.curve_rpm = self.p1.plot(pen='b', name="RPM")
        self.win.nextRow()
        
        # Plot 2: Temps
        self.p2 = self.win.addPlot(title="Temperatures")
        self.curve_tcore = self.p2.plot(pen='r', name="T_core")
        self.win.nextRow()
        
        # Plot 3: Pressure
        self.p3 = self.win.addPlot(title="Pressure")
        self.curve_p = self.p3.plot(pen='c', name="P_vessel")
        
        self.data_time = []
        self.data_rpm = []
        self.data_tcore = []
        self.data_p = []

    def update_data(self, state, telemetry):
        t = telemetry.get('time', 0.0)
        self.data_time.append(t)
        
        rpm = getattr(state, 'omega', 0.0) * 30 / np.pi
        self.data_rpm.append(rpm)
        
        tcore = getattr(state, 'T_core', 300.0)
        self.data_tcore.append(tcore)
        
        p = getattr(state, 'p_vessel', 1e5)
        self.data_p.append(p)
        
        # Keep last 300 points (10s @ 30fps)
        if len(self.data_time) > 300:
            self.data_time.pop(0)
            self.data_rpm.pop(0)
            self.data_tcore.pop(0)
            self.data_p.pop(0)
            
        self.curve_rpm.setData(self.data_time, self.data_rpm)
        self.curve_tcore.setData(self.data_time, self.data_tcore)
        self.curve_p.setData(self.data_time, self.data_p)
