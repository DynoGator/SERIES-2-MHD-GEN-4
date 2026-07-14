"""
Deterministic Telemetry Logging.
"""
from __future__ import annotations
import json
import time
import numpy as np
from collections import deque
from typing import Dict, Any, List
import random

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        if isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if hasattr(obj, 'name'): # for Enums
            return obj.name
        return str(obj)

class TelemetryRingBuffer:
    def __init__(self, max_seconds: float = 60.0, dt: float = 0.01):
        self.max_len = int(max_seconds / dt)
        self.buffer = deque(maxlen=self.max_len)
        
    def log(self, sim_time_s: float, state_vector: dict, control_inputs: dict, power_terms: dict, safety_state: str, rng_seed: int, **kwargs) -> None:
        record = {
            "sim_time_s": sim_time_s,
            "wall_time_ns": time.time_ns(),
            "state_vector": state_vector,
            "control_inputs": control_inputs,
            "power_terms": power_terms,
            "safety_state": safety_state,
            "rng_seed": rng_seed
        }
        record.update(kwargs)
        self.buffer.append(record)

    def flush_to_jsonl(self, filepath: str) -> None:
        """Write the buffer to a JSON Lines file."""
        with open(filepath, 'a') as f:
            for record in self.buffer:
                f.write(json.dumps(record, cls=NumpyEncoder) + '\n')
        self.buffer.clear()

def set_deterministic_seed(seed: int = 42) -> None:
    """
    Ensure the twin is deterministic: same config + same seed = identical output.
    """
    random.seed(seed)
    np.random.seed(seed)
