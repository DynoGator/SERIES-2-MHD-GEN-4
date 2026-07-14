import os
import yaml
import zmq
from typing import Dict
from telemetry.streaming_server import TwinStreamingServer
import time

class FieldBootstrap:
    def __init__(self, config_path: str = "config/hardware_config.yaml"):
        self.config_path = config_path
        self.hw_config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.hw_config = yaml.safe_load(f)

    def probe_hardware(self) -> Dict[str, bool]:
        # Mock probing
        return {
            "fpga": False,
            "gpsdo": False,
            "sdr": False
        }

    def fallback_if_needed(self) -> None:
        hw_status = self.probe_hardware()
        if not hw_status["fpga"]:
            os.environ["FPGA_MOCK"] = "1"
            print("Warning: FPGA not found. Falling back to mock mode.")

    def start_telemetry(self) -> None:
        server = TwinStreamingServer(port=5555)
        server.start()
        print("Telemetry stream started on port 5555")
        # Keep alive in background
        self._server = server

    def run(self) -> None:
        self.fallback_if_needed()
        self.start_telemetry()
        print("Field Bootstrap completed.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._server.stop()

if __name__ == "__main__":
    bootstrapper = FieldBootstrap()
    bootstrapper.run()
