import hashlib
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass(frozen=True)
class AnomalyEvent:
    event_id: str
    node_id: str
    anomaly_type: str
    timestamp_gps: float
    magnitude: float
    metadata: dict = field(default_factory=dict)

def make_event(node_id: str, anomaly_type: str, timestamp_gps: float, magnitude: float, metadata: Optional[Dict] = None) -> AnomalyEvent:
    raw_str = f"{node_id}:{anomaly_type}:{timestamp_gps}:{magnitude}"
    event_id = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]
    return AnomalyEvent(
        event_id=event_id,
        node_id=node_id,
        anomaly_type=anomaly_type,
        timestamp_gps=timestamp_gps,
        magnitude=magnitude,
        metadata=metadata or {}
    )
