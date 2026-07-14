import os
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.system_config import SystemConfig
from digital_twin.validation_runner import ValidationRunner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--twin', type=str, default='network1d', choices=['lumped', 'network1d'])
    parser.add_argument('--gates', type=str, help='Comma separated gates e.g. G0,G1,G2')
    parser.add_argument('--full-campaign', action='store_true')
    parser.add_argument('--ab-test', type=str, help='Scavenger to A/B test')
    parser.add_argument('--duration', type=float, default=10.0)
    args = parser.parse_args()

    config = SystemConfig()
    runner = ValidationRunner(config, twin_type=args.twin)

    if args.ab_test:
        print(f"Running A/B test on {args.ab_test} for {args.duration}s")
        runner.run_ab_campaign(args.ab_test)
        print(runner.generate_report())
        return

    gates = None
    if args.gates:
        gates = [g.strip() for g in args.gates.split(',')]
    
    if args.full_campaign or gates:
        runner.run_campaign(gates)
        report = runner.generate_report()
        
        os.makedirs('outputs', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"outputs/validation_report_{timestamp}.md"
        with open(report_path, "w") as f:
            f.write(report)
        print(report)
        print(f"\nValidation Report saved to {report_path}")

if __name__ == "__main__":
    main()
