#!/usr/bin/env python3
import argparse
import sys
import json
from hardware.gpsdo_sync import GPSDOSync

def main():
    parser = argparse.ArgumentParser(description="Pre-flight GPSDO gate")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    parser.add_argument("--device", type=str, default="/dev/ttyUSB0", help="GPSDO device path")
    parser.add_argument("--threshold", type=float, default=1.0e-9, help="Max Allan deviation")
    args = parser.parse_args()

    if args.mock:
        # Provide a mock instance directly to test the threshold logic
        class MockGPSDOSync:
            def is_locked(self):
                return True
            def get_allan_deviation(self):
                return 1.0e-10
            def start(self): pass
            def stop(self): pass
        gpsdo = MockGPSDOSync()
        # In mock mode, we'll let tests patch it if they want to fail it
        # But for default CLI, we just pretend it passed
        import os
        if os.environ.get("GPSDO_MOCK_FAIL_LOCK"):
            gpsdo.is_locked = lambda: False
        if os.environ.get("GPSDO_MOCK_ALLAN"):
            gpsdo.get_allan_deviation = lambda: float(os.environ["GPSDO_MOCK_ALLAN"])
    else:
        gpsdo = GPSDOSync(args.device)
        gpsdo.start()
        
    try:
        locked = gpsdo.is_locked()
        allan = gpsdo.get_allan_deviation()
        
        verdict = "PASS"
        if not locked:
            verdict = "FAIL"
        elif allan > args.threshold:
            verdict = "FAIL"
            
        res = {
            "locked": locked,
            "allan_dev": allan,
            "threshold": args.threshold,
            "verdict": verdict
        }
        
        print(json.dumps(res))
        sys.exit(0 if verdict == "PASS" else 1)
    finally:
        if not args.mock:
            gpsdo.stop()

if __name__ == "__main__":
    main()
