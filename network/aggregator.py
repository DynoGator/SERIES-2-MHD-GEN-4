from network.node_identity import NodeIdentity
from typing import List, Dict

class CentralAggregator:
    def __init__(self, nodes: List[NodeIdentity]):
        self.nodes = {n.node_id: n for n in nodes}
        self.ingested_data: Dict[str, dict] = {n.node_id: {} for n in nodes}
        
    def ingest(self, node_id: str, record: dict) -> None:
        if node_id in self.ingested_data:
            self.ingested_data[node_id].update(record)
            
    def report(self) -> dict:
        node_status = {}
        for node_id, data in self.ingested_data.items():
            # Align with DSLV-ZPDI keys
            node_status[node_id] = {
                "meta": {
                    "node_type": "2MHDBMRIPS",
                    "timestamp_utc": data.get("timestamp_utc", "")
                },
                "sensors": data.get("sensors", {}),
                "control": data.get("control", {}),
                "derived": data.get("derived", {})
            }
            
        return {
            "node_status": node_status,
            "consensus_ledger": {}, # mock
            "correlations": {}      # mock
        }
