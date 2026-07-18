#!/usr/bin/env python3
import argparse
import sys
import json
import os
from datetime import datetime

# Standalone execution: add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rehearsal.scenario import ScenarioEngine

def main():
    parser = argparse.ArgumentParser(description="Run Phase 13 Full Dress Rehearsal")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed for deterministic output")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    engine = ScenarioEngine(seed=args.seed)
    engine.run()
    rep = engine.report()
    
    # Write to archive
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    archive_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "archive", date_str)
    os.makedirs(archive_dir, exist_ok=True)
    with open(os.path.join(archive_dir, f"rehearsal_{args.seed}.json"), "w") as f:
        json.dump(rep, f, indent=2)

    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"=== FULL DRESS REHEARSAL (Seed: {args.seed}) ===")
        print(f"{'GATE':<20} | {'VERDICT':<7} | {'T_MISSION':<9} | DETAIL")
        print("-" * 80)
        for g in rep["gates"]:
            print(f"{g['gate']:<20} | {g['verdict']:<7} | {g['t_mission_s']:<9.1f} | {g['detail']}")
        
        print("-" * 80)
        print(f"MISSION STATUS: {rep['mission']}")
        if rep['mission'] == 'SUCCESS':
            print(f"DIGEST:         {rep['digest']}")
            
        # specifically print out the consensus details to satisfy visual check
        if rep['mission'] == 'SUCCESS':
            print("\nVerification checks:")
            # Find consensus output
            cv = next(g for g in rep["gates"] if g["gate"] == "CONSENSUS_VERDICT")
            print(cv["detail"])
            
    if rep["mission"] != "SUCCESS":
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
