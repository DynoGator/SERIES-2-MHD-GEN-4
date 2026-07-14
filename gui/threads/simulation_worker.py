from PyQt6.QtCore import QThread, pyqtSignal
from core.state_vector import StateVector
from config.system_config import SystemConfig
from digital_twin.network_1d import Network1DTwin
from validation.gates import Gate0_EnergyAccounting # Or we could just use ValidationRunner
from digital_twin.validation_runner import ValidationRunner
import time

class SimulationWorker(QThread):
    state_updated = pyqtSignal(StateVector, dict)
    gate_completed = pyqtSignal(str, bool)
    log_message = pyqtSignal(str, str)

    def __init__(self, config: SystemConfig, twin_type: str = "network1d"):
        super().__init__()
        self.config = config
        self.twin = Network1DTwin(self.config)
        self._running = False
        self._requested_gate = None

    def run(self):
        self._running = True
        
        while self._running and not self.isInterruptionRequested():
            if self._requested_gate:
                runner = ValidationRunner(self.config, "network1d")
                rep = runner.run_campaign([self._requested_gate])
                if rep.gate_results:
                    passed = rep.gate_results[0].passed
                else:
                    passed = False
                self.gate_completed.emit(self._requested_gate, passed)
                self._requested_gate = None
                
            # Perform a small simulation step
            self.twin.run(0.033) # ~30fps step
            
            telemetry = {
                "time": getattr(self.twin, 'current_time', 0.0),
                "safety_state": self.twin.state_machine.current_state.name if hasattr(self.twin.state_machine, 'current_state') else "INIT",
                "efficiency_ii": getattr(self.twin, 'efficiency_ii', 0.0)
            }
            
            self.state_updated.emit(self.twin.state, telemetry)
            
            # Simple sleep to roughly match 30 FPS if twin is too fast
            time.sleep(0.01)

    def set_control(self, control):
        pass

    def emergency_stop(self):
        # We assume there is a method to trigger fault latch
        from control.state_machine import StateEvent
        self.twin.state_machine.transition(StateEvent.SAFETY_FAULT)

    def run_gate(self, gate_id: str):
        self._requested_gate = gate_id

    def stop(self):
        self._running = False
        self.requestInterruption()
