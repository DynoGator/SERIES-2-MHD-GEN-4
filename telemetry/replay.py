import json
import hashlib
import dateutil.parser
from typing import Generator, Tuple, Dict, List, Any

class CampaignReplayer:
    def __init__(self, jsonl_path: str):
        self.jsonl_path = jsonl_path

    def stream(self) -> Generator[Tuple[float, Dict[str, float]], None, None]:
        with open(self.jsonl_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                ts_str = record.get("meta", {}).get("timestamp_utc")
                if not ts_str:
                    continue
                dt_obj = dateutil.parser.isoparse(ts_str)
                ts_gps = dt_obj.timestamp()
                
                sensors = record.get("sensors", {})
                mhd = sensors.get("mhd", {})
                thermal = sensors.get("thermal", {})
                acoustic = sensors.get("acoustic", {})
                
                channel_dict = {
                    "geomagnetic_nt": mhd.get("B_field", 0.0) * 1e9,
                    "acoustic_db": acoustic.get("modal_freq", 0.0), # mapping for mock
                    "thermal_c": thermal.get("T_core", 0.0),
                    "hall_voltage_mv": mhd.get("segment_voltages", [0.0])[0] if isinstance(mhd.get("segment_voltages"), list) else 0.0,
                    "gpsdo_lock": 1.0 # 1.0 = locked, 0.0 = unlocked
                }
                yield ts_gps, channel_dict

    def run(self, detector: Any, consensus: Any = None) -> Dict[str, Any]:
        verdicts = []
        events_list = []
        
        for ts_gps, channel_dict in self.stream():
            events = detector.process(ts_gps, channel_dict)
            if events:
                events_list.extend(events)
                if consensus:
                    for e in events:
                        verdict = consensus.report(e)
                        verdicts.append(verdict)
                else:
                    verdicts.extend(["DETECTED"] * len(events))
                    
        # Hash verdicts
        verdicts_str = ",".join(verdicts)
        digest = hashlib.sha256(verdicts_str.encode("utf-8")).hexdigest()[:16]
        
        return {
            "verdicts": verdicts,
            "events": events_list,
            "digest": digest
        }
