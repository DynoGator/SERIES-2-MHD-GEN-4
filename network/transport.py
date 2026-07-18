import zmq
import json
from typing import Optional
from network.events import AnomalyEvent, make_event

class ZmqTransport:
    def __init__(self, endpoint: str, bind: bool):
        self.endpoint = endpoint
        self.bind = bind
        self.context = zmq.Context.instance()
        
        if bind:
            self.socket = self.context.socket(zmq.PULL)
            self.socket.bind(self.endpoint)
        else:
            self.socket = self.context.socket(zmq.PUSH)
            self.socket.connect(self.endpoint)

    def send(self, event: AnomalyEvent) -> bool:
        try:
            # Serialize
            data = {
                "event_id": event.event_id,
                "node_id": event.node_id,
                "anomaly_type": event.anomaly_type,
                "timestamp_gps": event.timestamp_gps,
                "magnitude": event.magnitude,
                "metadata": event.metadata
            }
            self.socket.send_json(data)
            return True
        except zmq.ZMQError:
            return False

    def recv(self, timeout_ms: int = 1000) -> Optional[AnomalyEvent]:
        try:
            if self.socket.poll(timeout_ms, zmq.POLLIN):
                data = self.socket.recv_json()
                return AnomalyEvent(
                    event_id=data["event_id"],
                    node_id=data["node_id"],
                    anomaly_type=data["anomaly_type"],
                    timestamp_gps=data["timestamp_gps"],
                    magnitude=data["magnitude"],
                    metadata=data.get("metadata", {})
                )
            return None
        except zmq.ZMQError:
            return None
