from typing import Dict
from hardware.fpga_interface import FPGAInterface

class PPSCapture:
    TDC_COUNT_LO = 0x1000
    TDC_COUNT_HI = 0x1004
    PPS_STATUS = 0x1008

    def __init__(self, fpga: FPGAInterface):
        self.fpga = fpga

    def arm(self) -> None:
        self.fpga.write_register(self.PPS_STATUS, 1)

    def wait_for_edge(self, timeout_ms: int = 2000) -> Dict[str, int]:
        if self.fpga.mock_mode:
            # Simulate a triggered state with a slight phase error (e.g. 50 ns)
            self.fpga.write_register(self.PPS_STATUS, 2)
            self.fpga.write_register(self.TDC_COUNT_LO, 50)
            self.fpga.write_register(self.TDC_COUNT_HI, 0)
            
        status = self.fpga.read_register(self.PPS_STATUS)
        lo = self.fpga.read_register(self.TDC_COUNT_LO)
        hi = self.fpga.read_register(self.TDC_COUNT_HI)
        return {"tdc_lo": lo, "tdc_hi": hi, "status": status}

    def get_tdc_delta_ns(self) -> int:
        res = self.wait_for_edge()
        return (res["tdc_hi"] << 32) | res["tdc_lo"]

    def compute_phase_error(self, expected_period_ns: int = 1_000_000_000) -> float:
        delta = self.get_tdc_delta_ns()
        error_ns = delta - expected_period_ns if delta > expected_period_ns/2 else delta
        return error_ns / expected_period_ns

    def reset_tdc(self) -> None:
        self.fpga.write_register(self.TDC_COUNT_LO, 0)
        self.fpga.write_register(self.TDC_COUNT_HI, 0)
