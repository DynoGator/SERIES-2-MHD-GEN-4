#!/usr/bin/env python3
import sys
import os
import argparse
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telemetry.replay import CampaignReplayer
from telemetry.statistical_detector import StatisticalDetector
from network.consensus import ConsensusEngine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", required=True)
    args = parser.parse_args()
    
    # Path assumption
    jsonl_path = os.path.join("data", "campaigns", f"{args.campaign}.jsonl")
    if not os.path.exists(jsonl_path):
        print(f"Campaign {args.campaign} not found at {jsonl_path}")
        sys.exit(1)
        
    replayer = CampaignReplayer(jsonl_path)
    detector = StatisticalDetector("alpha") # Just use alpha for replay demo
    consensus = ConsensusEngine(window_s=60.0)
    
    print(f"Replaying campaign: {args.campaign}")
    res = replayer.run(detector, consensus)
    
    print("\nVerdicts Table:")
    print("Event | Type | Verdict")
    print("-" * 40)
    for i, (ev, verdict) in enumerate(zip(res["events"], res["verdicts"])):
        print(f"{i+1:03d} | {ev.anomaly_type} | {verdict}")
        
    print(f"\nDigest: {res['digest']}")

if __name__ == "__main__":
    main()
