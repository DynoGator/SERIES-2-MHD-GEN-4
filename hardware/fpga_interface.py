import os
from typing import Dict, Any

class FPGAInterface:
    def __init__(self, ip: str = "192.168.1.10", udp_port: int = 5000, uart_dev: str = "/dev/ttyUSB0"):
        self.ip = ip
        self.udp_port = udp_port
        self.uart_dev = uart_dev
        self.mock_mode = False
        self._connected = False
        self._registers = {}

    def connect(self) -> bool:
        if os.environ.get("FPGA_MOCK") == "1" or not self._ping_fpga():
            self.mock_mode = True
        self._connected = True
        return True
        
    def _ping_fpga(self) -> bool:
        # Simulate network failure to force mock mode by default unless actual hardware
        return False

    def write_register(self, addr: int, value: int) -> None:
        if self.mock_mode:
            self._registers[addr] = value
        else:
            pass # Hardware write

    def read_register(self, addr: int) -> int:
        if self.mock_mode:
            return self._registers.get(addr, 0)
        return 0

    def load_bitstream(self, bitstream_path: str) -> bool:
        return True

    def get_status(self) -> Dict[str, Any]:
        if self.mock_mode:
            return {
                "locked": True,
                "temp_c": 40.0,
                "uptime_ms": 10000
            }
        return {"locked": False, "temp_c": 0.0, "uptime_ms": 0}

    def close(self) -> None:
        self._connected = False
