from typing import Dict, List
from network.events import AnomalyEvent

class ConsensusEngine:
    def __init__(self, window_s: float = 60.0, quorum: int = 2):
        self.window_s = window_s
        self.quorum = quorum
        # dict mapped by anomaly_type -> list of distinct events
        self.active_events: Dict[str, List[AnomalyEvent]] = {}
        # current state per anomaly_type
        self._states: Dict[str, str] = {}

    def report(self, event: AnomalyEvent) -> str:
        a_type = event.anomaly_type
        if a_type not in self.active_events:
            self.active_events[a_type] = []
            self._states[a_type] = "IDLE"

        # Check for dedup (same event_id)
        if any(e.event_id == event.event_id for e in self.active_events[a_type]):
            return self._states[a_type]

        self.active_events[a_type].append(event)
        
        # Check quorum (distinct nodes)
        distinct_nodes = set(e.node_id for e in self.active_events[a_type])
        if len(distinct_nodes) >= self.quorum:
            self._states[a_type] = "CONFIRMED"
        else:
            self._states[a_type] = "SUSPECT"
            
        return self._states[a_type]

    def state(self, anomaly_type: str) -> str:
        return self._states.get(anomaly_type, "IDLE")

    def expire(self, now_gps: float) -> None:
        for a_type, events in list(self.active_events.items()):
            if not events:
                continue
            
            # Remove expired events
            valid_events = [e for e in events if now_gps - e.timestamp_gps <= self.window_s]
            
            if len(valid_events) < len(events):
                # We expired some
                self.active_events[a_type] = valid_events
                distinct_nodes = set(e.node_id for e in valid_events)
                
                if len(distinct_nodes) >= self.quorum:
                    self._states[a_type] = "CONFIRMED"
                elif len(distinct_nodes) > 0:
                    self._states[a_type] = "SUSPECT"
                else:
                    # Everything expired
                    # If it was SUSPECT and dropped to 0, it's rejected
                    if self._states.get(a_type) == "SUSPECT":
                        self._states[a_type] = "REJECTED_UNCORROBORATED"
                    else:
                        self._states[a_type] = "IDLE"
