#!/usr/bin/env python3
import sys
import os
import json
import numpy as np

# Ensure scripts directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network.node_identity import load_node
from network.events import make_event
from network.consensus import ConsensusEngine
from network.correlator import CrossNodeCorrelator
from network.mesh import MeshFallback
from network.aggregator import CentralAggregator

def main():
    if "--mock" not in sys.argv:
        print("This script currently only supports --mock mode")
        sys.exit(1)
        
    print("Initializing Multi-Node Network (alpha, beta, gamma)...")
    nodes = [load_node("alpha"), load_node("beta"), load_node("gamma")]
    aggregator = CentralAggregator(nodes)
    consensus = ConsensusEngine()
    mesh = MeshFallback()
    correlator = CrossNodeCorrelator()
    
    # 1. Broker is alive
    mesh.broker_alive(True, 0.0)
    print(f"Network state: {mesh.tick(0.0)}")
    
    # 2. Correlated geomagnetic spike at alpha+beta (2.0s lag)
    e_alpha = make_event("alpha", "GEOMAGNETIC_SPIKE", 10.0, 100.0)
    e_beta = make_event("beta", "GEOMAGNETIC_SPIKE", 12.0, 95.0)
    
    dt = 0.1
    t = np.arange(0, 20.0, dt)
    series_a = np.zeros_like(t)
    series_a[100:110] = 1.0 # 10.0s
    series_b = np.zeros_like(t)
    series_b[120:130] = 1.0 # 12.0s
    corr_res = correlator.correlate(series_a, series_b, dt)
    print(f"Correlation: coincident={corr_res.coincident}, lag_s={corr_res.lag_s}")
    
    consensus.report(e_alpha)
    res = consensus.report(e_beta)
    print(f"alpha+beta GEOMAGNETIC_SPIKE consensus: {res}")
    
    # 3. Lone false anomaly at gamma
    e_gamma = make_event("gamma", "THERMAL_ANOMALY", 15.0, 80.0)
    res_gamma = consensus.report(e_gamma)
    consensus.expire(80.0) # expire 60s window
    res_gamma_expired = consensus.state("THERMAL_ANOMALY")
    print(f"gamma THERMAL_ANOMALY consensus: {res_gamma_expired}")
    
    # 4. Kill broker mid-run
    print(f"Network state: {mesh.tick(2.1)}") # DEGRADED
    print(f"Network state: {mesh.tick(4.2)}") # MESH
    
    # 5. Restore broker
    mesh.broker_alive(True, 6.0)
    print(f"Network state: {mesh.tick(6.0)}") # BROKERED
    
    # 6. Emit JSON report
    aggregator.ingest("alpha", {"timestamp_utc": "2026-07-18T10:00:00Z"})
    aggregator.ingest("beta", {"timestamp_utc": "2026-07-18T10:00:00Z"})
    aggregator.ingest("gamma", {"timestamp_utc": "2026-07-18T10:00:00Z"})
    report = aggregator.report()
    report["consensus_ledger"]["GEOMAGNETIC_SPIKE"] = res
    report["consensus_ledger"]["THERMAL_ANOMALY"] = res_gamma_expired
    
    print("\nFinal Report:")
    print(json.dumps(report, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
