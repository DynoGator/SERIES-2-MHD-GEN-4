import os
from telemetry.campaign_recorder import CampaignRecorder
from telemetry.replay import CampaignReplayer
from network.events import make_event

class MockDetector:
    def process(self, ts, channels):
        if channels.get("geomagnetic_nt", 0.0) > 60000:
            return [make_event("alpha", "GEOMAGNETIC_SPIKE", ts, channels["geomagnetic_nt"])]
        return []

def test_replay_determinism(tmp_path):
    recorder = CampaignRecorder("alpha", str(tmp_path))
    cid = recorder.record(1.0)
    jsonl_path = recorder.paths(cid)["jsonl"]
    
    # Inject a spike manually
    with open(jsonl_path, "a") as f:
        f.write('{"meta": {"timestamp_utc": "2026-07-18T10:00:00Z"}, "sensors": {"mhd": {"B_field": 0.0001}}}\n')
    
    replayer = CampaignReplayer(jsonl_path)
    detector = MockDetector()
    
    res1 = replayer.run(detector)
    res2 = replayer.run(detector)
    
    assert res1["digest"] == res2["digest"]
    assert len(res1["events"]) == 1
    assert res1["events"][0].anomaly_type == "GEOMAGNETIC_SPIKE"

def test_order_preserved(tmp_path):
    recorder = CampaignRecorder("alpha", str(tmp_path))
    cid = recorder.record(1.0)
    jsonl_path = recorder.paths(cid)["jsonl"]
    
    replayer = CampaignReplayer(jsonl_path)
    last_ts = 0.0
    for ts, _ in replayer.stream():
        assert ts >= last_ts
        last_ts = ts

def test_empty_campaign_clean_run(tmp_path):
    empty_path = tmp_path / "empty.jsonl"
    empty_path.touch()
    replayer = CampaignReplayer(str(empty_path))
    res = replayer.run(MockDetector())
    assert len(res["verdicts"]) == 0
    assert len(res["events"]) == 0
