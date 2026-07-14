import os
import sys
import argparse
import time

# Add the project root to sys.path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.system_config import SystemConfig
from config.sites import SITES
from digital_twin.channel_2d import Channel2DTwin
from telemetry.dslv_zpdi_pipeline import DSLVZPDIPipeline
from telemetry.streaming_server import TwinStreamingServer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=str, required=True, help="Site profile name")
    parser.add_argument("--duration", type=float, default=10.0, help="Simulation duration")
    args = parser.parse_args()

    if args.site not in SITES:
        raise ValueError(f"Unknown site {args.site}")

    site_config = SITES[args.site]
    config = SystemConfig()
    
    twin = Channel2DTwin(config, use_cfd=False)
    pipeline = DSLVZPDIPipeline(site_config["node_id"], site_config)
    stream = TwinStreamingServer(port=5555)
    
    stream.start()
    
    dt = 0.1
    steps = int(args.duration / dt)
    
    for _ in range(steps):
        twin.step(dt)
        telemetry = {
            "safety": twin.state_machine.current_state.name if hasattr(twin.state_machine, "current_state") else "STEADY_OPERATION",
            "exergy": {"eta_ii": 0.35}
        }
        meta = {
            "node_id": site_config["node_id"],
            "safety": telemetry["safety"],
            "exergy": telemetry["exergy"]
        }
        stream.publish(twin.state, meta)
        time.sleep(0.01) # Simulating real-time step
        
    # Write snapshot at end
    snapshot_path = "snapshot.h5"
    pipeline.write_twin_snapshot(twin.state, telemetry, snapshot_path)
    
    stream.stop()
    print(f"Distributed node simulation complete. Snapshot saved to {snapshot_path}")

if __name__ == "__main__":
    main()
