import os
import json
import h5py
import time
import uuid
from datetime import datetime, timezone
import numpy as np

class MockSource:
    def __init__(self, site_key: str):
        self.site_key = site_key
        self.t = 0.0

    def get_sample(self):
        self.t += 0.1
        return {
            "meta": {
                "node_type": "2MHDBMRIPS",
                "timestamp_utc": datetime.now(timezone.utc).isoformat()
            },
            "sensors": {
                "mhd": {
                    "B_field": 50e-6 + np.random.randn() * 1e-9
                },
                "thermal": {
                    "T_core": 300.0 + np.random.randn() * 0.1
                },
                "acoustic": {
                    "modal_freq": 40.0 + np.random.randn() * 0.1
                }
            },
            "control": {
                "state_machine": "RUNNING"
            },
            "derived": {
                "exergy_efficiency": 0.8
            }
        }

class CampaignRecorder:
    def __init__(self, site_key: str, out_dir: str, source=None):
        self.site_key = site_key
        self.out_dir = out_dir
        self.source = source or MockSource(site_key)
        os.makedirs(out_dir, exist_ok=True)
        self._paths = {}

    def record(self, duration_s: float, rate_hz: float = 10.0) -> str:
        campaign_id = str(uuid.uuid4())[:8]
        jsonl_path = os.path.join(self.out_dir, f"{campaign_id}.jsonl")
        hdf5_path = os.path.join(self.out_dir, f"{campaign_id}.h5")
        self._paths[campaign_id] = {"jsonl": jsonl_path, "hdf5": hdf5_path}
        
        num_samples = int(duration_s * rate_hz)
        dt = 1.0 / rate_hz
        
        samples = []
        with open(jsonl_path, "w") as jf:
            for _ in range(num_samples):
                sample = self.source.get_sample()
                jf.write(json.dumps(sample) + "\n")
                samples.append(sample)
                # In real scenario we would sleep(dt) but for mock we can just loop
                # The instructions say record mock campaigns, so no sleep for tests.
                
        # Write HDF5
        with h5py.File(hdf5_path, "w") as f:
            grp = f.create_group(f"campaign_{campaign_id}")
            # Just store raw JSON strings in HDF5 for simplicity if not fully expanding,
            # or expand numeric arrays. For alignment with DSLV-ZPDI, let's make lists.
            # This is a simplified HDF5 schema mapping:
            ts_list = [s["meta"]["timestamp_utc"].encode("utf-8") for s in samples]
            grp.create_dataset("timestamp_utc", data=ts_list)
            
            sensors = grp.create_group("sensors")
            b_fields = [s["sensors"]["mhd"]["B_field"] for s in samples if "mhd" in s["sensors"]]
            if b_fields:
                sensors.create_dataset("B_field", data=b_fields)
                
        return campaign_id

    def paths(self, campaign_id: str) -> dict:
        return self._paths.get(campaign_id, {})
