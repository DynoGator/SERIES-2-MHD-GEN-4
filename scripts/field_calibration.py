#!/usr/bin/env python3
import json
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--duration", type=float, default=1.0)
    args = parser.parse_args()

    calibration_data = {
        "site": args.site,
        "timestamp": datetime.utcnow().isoformat(),
        "geomagnetic_baseline_nt": 50000.0,
        "acoustic_ambient_db": 35.5,
        "thermal_ambient_c": 22.0
    }
    
    print(json.dumps(calibration_data, indent=2))
    
if __name__ == "__main__":
    main()
