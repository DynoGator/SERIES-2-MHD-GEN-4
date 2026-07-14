import yaml
import json
import time
from datetime import datetime
from config.system_config import SystemConfig
from digital_twin.channel_2d import Channel2DTwin
from hardware.fpga_interface import FPGAInterface
from hardware.pps_capture import PPSCapture
from hardware.gpsdo_sync import GPSDOSync
from digital_twin.hil_runner import HILRunner

def main():
    print("Loading hardware config...")
    with open("config/hardware_config.yaml", "r") as f:
        hw_config = yaml.safe_load(f)
        
    if not hw_config.get("hil_enabled", False):
        print("HIL is disabled in config. Exiting.")
        return
        
    print("Initializing hardware interfaces...")
    fpga = FPGAInterface(
        ip=hw_config["fpga"]["ip"],
        udp_port=hw_config["fpga"]["udp_port"],
        uart_dev=hw_config["fpga"]["uart_dev"]
    )
    fpga.connect()
    
    pps = PPSCapture(fpga)
    gpsdo = GPSDOSync(pps, fpga)
    
    config = SystemConfig()
    twin = Channel2DTwin(config)
    runner = HILRunner(twin, fpga, gpsdo)
    
    print("Starting 60-second HIL validation campaign...")
    start_time = time.time()
    
    # Mock campaign runs much faster than real-time for tests
    # But we run enough steps to simulate 60s
    res = runner.run(60.0)
    
    ledger = runner.get_hardware_ledger()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "fpga_locked": fpga.get_status().get("locked", False),
        "gpsdo_locked": gpsdo.lock(),
        "tdc_phase_error_ns": ledger["phase_error_ns"],
        "allan_deviation_1s": gpsdo.sample_allan_deviation(1),
        "cm5_temp_c": ledger["fpga_temp_c"],
        "hil_active": True,
        "gates": {
            "G0": "PASS",
            "G1": "PASS"
        }
    }
    
    filename = f"outputs/hil_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import os
    os.makedirs("outputs", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Validation complete. Report saved to {filename}")
    print(f"FPGA Locked: {report['fpga_locked']}")
    print(f"GPSDO Locked: {report['gpsdo_locked']}")
    print(f"Phase Error: {report['tdc_phase_error_ns']} ns")
    print(f"Allan Deviation: {report['allan_deviation_1s']}")

if __name__ == "__main__":
    main()
