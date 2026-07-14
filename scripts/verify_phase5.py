import subprocess
import zmq
import json
import time
import h5py
from telemetry.dslv_zpdi_pipeline import DSLVZPDIPipeline
from config.sites import SITES

def main():
    print("Starting node script...")
    p = subprocess.Popen(["python", "scripts/run_distributed_node.py", "--site", "penrose_co", "--duration", "2.0"])
    
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect("tcp://127.0.0.1:5555")
    sub.setsockopt_string(zmq.SUBSCRIBE, "")
    
    msg_count = 0
    start_time = time.time()
    
    msgs = []
    
    while True:
        try:
            # use poller with timeout
            if p.poll() is not None and not sub.poll(100):
                break
            msg = sub.recv_json(zmq.NOBLOCK)
            msg_count += 1
            if msg_count <= 5:
                msgs.append(msg)
        except zmq.Again:
            time.sleep(0.01)
            
    p.wait()
    duration = time.time() - start_time
    
    print(f"Received {msg_count} messages in {duration:.2f}s (~{msg_count/duration:.1f} Hz)")
    print("\nFirst 5 messages:")
    for m in msgs:
        print(json.dumps(m)[:200] + "...")
        
    print("\nValidating HDF5:")
    site = SITES["penrose_co"]
    pipeline = DSLVZPDIPipeline("alpha", site)
    is_valid = pipeline.validate_schema("snapshot.h5")
    print(f"HDF5 Valid: {is_valid}")
    
    with h5py.File("snapshot.h5", "r") as f:
        print("Root keys:", list(f.keys()))
        print("Meta attrs:", dict(f["node_alpha/meta"].attrs))

if __name__ == "__main__":
    main()
