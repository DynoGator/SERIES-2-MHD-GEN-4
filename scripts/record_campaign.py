#!/usr/bin/env python3
import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telemetry.campaign_recorder import CampaignRecorder

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--mock-source", action="store_true")
    
    args = parser.parse_args()
    
    out_dir = os.path.join("data", "campaigns")
    recorder = CampaignRecorder(args.site, out_dir)
    
    print(f"Recording campaign for {args.duration}s at site {args.site}...")
    cid = recorder.record(args.duration)
    paths = recorder.paths(cid)
    print(f"Campaign {cid} complete.")
    print(f"JSONL: {paths['jsonl']}")
    print(f"HDF5: {paths['hdf5']}")

if __name__ == "__main__":
    main()
