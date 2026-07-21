# MODULE-STATUS: SCAFFOLD
from typing import Tuple, Dict, Any, Optional, Callable, Union
from core.state_vector import StateVector
from hardware.fpga_interface import FPGAInterface
from hardware.gpsdo_sync import GPSDOSync

class HILRunner:
    def __init__(self, twin: Any, fpga: FPGAInterface, gpsdo: GPSDOSync):
        self.twin = twin
        self.fpga = fpga
        self.gpsdo = gpsdo

    def step(self, dt: float) -> Tuple[StateVector, Dict[str, Any]]:
        # 1. Twin computes control vector (dummy implementation since not fully defined)
        tau_drive = 1.0
        B_max = 5.0
        phase_cmd = 0.0
        
        # 2. HIL writes control registers to FPGA (0x2000-0x200F)
        self.fpga.write_register(0x2000, int(tau_drive * 100))
        self.fpga.write_register(0x2004, int(B_max * 100))
        self.fpga.write_register(0x2008, int(phase_cmd * 100))
        
        # 3. HIL triggers PPS capture
        self.gpsdo.pps.wait_for_edge()
        
        # 4. HIL reads FPGA sensor registers (0x3000-0x3007 for segment currents)
        segment_currents = [self.fpga.read_register(0x3000 + i) for i in range(8)]
        
        # 5. Twin integrates next state
        state = self.twin.step(dt)
        
        ledger = self.get_hardware_ledger()
        return state, ledger

    def run(self, t_end: float, callback: Optional[Callable] = None) -> Dict[str, Any]:
        dt = 0.1
        steps = int(t_end / dt)
        last_state = None
        for _ in range(steps):
            last_state, ledger = self.step(dt)
            if callback:
                callback(last_state, ledger)
        return {"final_state": last_state}

    def get_hardware_ledger(self) -> Dict[str, float]:
        return {
            "phase_error_ns": self.gpsdo.get_clock_offset_ns(),
            "clock_offset_ns": self.gpsdo.get_clock_offset_ns(),
            "fpga_temp_c": self.fpga.get_status().get("temp_c", 0.0)
        }
