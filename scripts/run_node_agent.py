#!/usr/bin/env python3
import argparse
import sys
import time
from node.node_agent import NodeAgent

def main():
    parser = argparse.ArgumentParser(description="Run the 2MHD Node Agent")
    parser.add_argument("--node", type=str, required=True, help="Node ID (e.g. alpha)")
    parser.add_argument("--config", type=str, default="config/deployment.yaml", help="Path to config file")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no hardware)")
    args = parser.parse_args()

    agent_kwargs = {}
    
    if args.mock:
        class MockGPSDOSync:
            def is_locked(self): return True
            def get_allan_deviation(self): return 1.0e-10
            def start(self): pass
            def stop(self): pass
            
        class MockTransport:
            def send(self, msg):
                print(f"Heartbeat: {msg}")
                
        agent_kwargs["gpsdo"] = MockGPSDOSync()
        agent_kwargs["transport"] = MockTransport()
    
    agent = NodeAgent(args.node, args.config, **agent_kwargs)
    
    if args.mock:
        # Mock mode: run 3 heartbeats then exit cleanly
        agent.start()
        try:
            for _ in range(3):
                agent.heartbeat_once()
                time.sleep(0.1)
        finally:
            agent.stop()
        sys.exit(0)
    else:
        import signal
        def handle_sigterm(signum, frame):
            print("Received SIGTERM, stopping agent...")
            agent.stop()
            sys.exit(0)
            
        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigterm)
        
        agent.start()
        print(f"Node Agent {args.node} started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            handle_sigterm(None, None)

if __name__ == "__main__":
    main()
