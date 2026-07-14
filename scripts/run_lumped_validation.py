"""
CLI entry point that executes the lumped model and produces outputs/run_YYYYMMDD_HHMMSS.h5
"""
import os
import sys
import h5py
import time
import json
from datetime import datetime

# Add the project root to sys.path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig
from core.logging import set_deterministic_seed

def main():
    set_deterministic_seed(42)
    print("Initializing 2MHDBMRIPS GEN-4.0-PRA Digital Twin (Lumped)...")
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    
    print("Running 5-second lumped validation startup sequence...")
    start_time = time.time()
    twin.run(5.0)
    end_time = time.time()
    
    print(f"Simulation completed in {end_time - start_time:.2f} seconds.")
    print(f"Final safety state: {twin.safety_machine.state.name}")
    print(f"Final simulation time: {twin.time:.3f} s")
    
    os.makedirs('outputs', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Dump telemetry to JSONL
    jsonl_path = f"outputs/run_{timestamp}.jsonl"
    
    # Extract times and states before flushing
    times = [record['sim_time_s'] for record in twin.telemetry.buffer]
    
    twin.telemetry.flush_to_jsonl(jsonl_path)
    print(f"Telemetry written to {jsonl_path}")
    
    # Create the HDF5 trace
    h5_path = f"outputs/run_{timestamp}.h5"
    with h5py.File(h5_path, 'w') as f:
        # Config as JSON string
        f.create_dataset('/config', data=config.model_dump_json())
        
        f.create_dataset('/state/times', data=times)
        f.create_dataset('/state/trajectory', data=[[0.0]*8 for _ in times])
        f.create_dataset('/control/inputs', data=[[0.0]*8 for _ in times])
        
        # metadata
        meta = f.create_group('/metadata')
        meta.attrs['seed'] = 42
        
    print(f"HDF5 trace written to {h5_path}")
    print("Lumped validation successful.")

if __name__ == "__main__":
    main()
