import pytest
import os
import json
from telemetry.campaign_recorder import CampaignRecorder
from telemetry.replay import CampaignReplayer
from telemetry.statistical_detector import StatisticalDetector
from network.consensus import ConsensusEngine

def inject_spike(jsonl_path, start_idx, mag):
    with open(jsonl_path, "r") as f:
        lines = f.readlines()
        
    for i in range(len(lines)):
        record = json.loads(lines[i])
        if start_idx <= i < start_idx + 10:
            if "mhd" not in record["sensors"]:
                record["sensors"]["mhd"] = {}
            record["sensors"]["mhd"]["B_field"] = mag
        lines[i] = json.dumps(record) + "\n"
        
    with open(jsonl_path, "w") as f:
        f.writelines(lines)

def test_replay_to_consensus(tmp_path):
    # Record mock campaigns for alpha, beta, gamma
    rec_a = CampaignRecorder("penrose_co", str(tmp_path))
    rec_b = CampaignRecorder("albuquerque_nm", str(tmp_path))
    rec_c = CampaignRecorder("hessdalen_style", str(tmp_path))
    
    cid_a = rec_a.record(20.0) # 200 samples
    cid_b = rec_b.record(20.0)
    cid_c = rec_c.record(20.0)
    
    path_a = rec_a.paths(cid_a)["jsonl"]
    path_b = rec_b.paths(cid_b)["jsonl"]
    path_c = rec_c.paths(cid_c)["jsonl"]
    
    # Inject correlated geomagnetic spike: alpha at 11.0s (idx 110), beta at 13.0s (idx 130)
    # B_field > 50,006 to trigger 5-sigma
    inject_spike(path_a, 110, 60000.0)
    inject_spike(path_b, 130, 60000.0)
    
    # Inject lone gamma thermal anomaly at 15.0s (idx 150)
    # Thermal anomaly
    with open(path_c, "r") as f:
        lines = f.readlines()
    for i in range(150, 160):
        rec = json.loads(lines[i])
        rec["sensors"]["thermal"]["T_core"] = 400.0
        lines[i] = json.dumps(rec) + "\n"
    with open(path_c, "w") as f:
        f.writelines(lines)
        
    # Replay through detection and consensus
    replayer_a = CampaignReplayer(path_a)
    replayer_b = CampaignReplayer(path_b)
    replayer_c = CampaignReplayer(path_c)
    
    det_a = StatisticalDetector("alpha")
    det_b = StatisticalDetector("beta")
    det_c = StatisticalDetector("gamma")
    
    consensus = ConsensusEngine(window_s=60.0)
    
    # Interleave processing
    # The stream() is a generator, so we just zip them
    def run_all(replayers, detectors, cons):
        verdicts = []
        events_list = []
        streams = [r.stream() for r in replayers]
        
        while True:
            try:
                for i in range(3):
                    ts, channels = next(streams[i])
                    evs = detectors[i].process(ts, channels)
                    for e in evs:
                        verdict = cons.report(e)
                        verdicts.append(verdict)
                        events_list.append(e)
                        print(f"Node {e.node_id} reported {e.anomaly_type} at {e.timestamp_gps}, verdict: {verdict}")
            except StopIteration:
                break
                
        # advance time to expire
        print("Expiring at", ts + 61.0)
        cons.expire(ts + 61.0)
        
        import hashlib
        verdicts_str = ",".join(verdicts)
        digest = hashlib.sha256(verdicts_str.encode("utf-8")).hexdigest()[:16]
        return verdicts, events_list, digest

    # First run
    v1, e1, d1 = run_all([replayer_a, replayer_b, replayer_c], [det_a, det_b, det_c], consensus)
    
    # Second run (re-instantiate everything to reset state)
    replayer_a2 = CampaignReplayer(path_a)
    replayer_b2 = CampaignReplayer(path_b)
    replayer_c2 = CampaignReplayer(path_c)
    det_a2 = StatisticalDetector("alpha")
    det_b2 = StatisticalDetector("beta")
    det_c2 = StatisticalDetector("gamma")
    consensus2 = ConsensusEngine(window_s=60.0)
    v2, e2, d2 = run_all([replayer_a2, replayer_b2, replayer_c2], [det_a2, det_b2, det_c2], consensus2)
    
    # Assertions
    assert d1 == d2, "Digest not stable"
    
    # 1. Correlated event reaches CONFIRMED
    assert "CONFIRMED" in v1
    
    # 2. Lone gamma event REJECTED_UNCORROBORATED
    assert consensus.state("THERMAL_ANOMALY") == "REJECTED_UNCORROBORATED"
