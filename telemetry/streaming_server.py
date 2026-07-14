import zmq
import json
from datetime import datetime, timezone
from core.state_vector import StateVector
from typing import Dict, Any
import jsonschema

class TwinStreamingServer:
    def __init__(self, port: int = 5555):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self._running = False
        self.schema = {
            "type": "object",
            "properties": {
                "node_id": {"type": "string"},
                "timestamp_utc": {"type": "string"},
                "state": {"type": "object"},
                "safety": {"type": "string"},
                "exergy": {"type": "object"}
            },
            "required": ["node_id", "timestamp_utc", "state", "safety", "exergy"]
        }

    def start(self) -> None:
        self.socket.bind(f"tcp://*:{self.port}")
        self._running = True

    def stop(self) -> None:
        if self._running:
            self.socket.close()
            self.context.term()
            self._running = False

    def publish(self, state: StateVector, metadata: Dict[str, Any]) -> None:
        if not self._running:
            return
            
        import numpy as np
        state_dict = state.model_dump()
        for k, v in state_dict.items():
            if isinstance(v, np.ndarray):
                state_dict[k] = v.tolist()
                
        msg = {
            "node_id": metadata.get("node_id", "unknown"),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "state": state_dict,
            "safety": metadata.get("safety", "INIT"),
            "exergy": metadata.get("exergy", {})
        }
        
        # We silently validate against schema
        try:
            jsonschema.validate(instance=msg, schema=self.schema)
            self.socket.send_json(msg)
        except jsonschema.ValidationError:
            pass # Invalid message, drop
