import os
from telemetry.campaign_recorder import CampaignRecorder

def test_records_both_formats(tmp_path):
    recorder = CampaignRecorder("penrose_co", str(tmp_path))
    cid = recorder.record(1.0)
    paths = recorder.paths(cid)
    
    assert os.path.exists(paths["jsonl"])
    assert os.path.exists(paths["hdf5"])
    
    with open(paths["jsonl"], "r") as f:
        lines = f.readlines()
    assert len(lines) == 10 # 1.0s @ 10Hz

def test_schema_alignment(tmp_path):
    recorder = CampaignRecorder("penrose_co", str(tmp_path))
    cid = recorder.record(0.1)
    paths = recorder.paths(cid)
    
    import json
    with open(paths["jsonl"], "r") as f:
        data = json.loads(f.readline())
        
    assert "meta" in data
    assert "timestamp_utc" in data["meta"]
    assert "sensors" in data
    assert "control" in data
    assert "derived" in data

def test_timestamps_monotonic(tmp_path):
    recorder = CampaignRecorder("penrose_co", str(tmp_path))
    cid = recorder.record(0.5)
    paths = recorder.paths(cid)
    
    import json
    import dateutil.parser
    with open(paths["jsonl"], "r") as f:
        ts = [dateutil.parser.isoparse(json.loads(line)["meta"]["timestamp_utc"]) for line in f]
        
    for i in range(1, len(ts)):
        assert ts[i] >= ts[i-1]
