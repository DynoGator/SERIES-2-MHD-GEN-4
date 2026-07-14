import pytest
import zmq
import json
import time
from telemetry.streaming_server import TwinStreamingServer
from core.state_vector import StateVector

def test_publish_receives():
    # Setup sub
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect("tcp://127.0.0.1:5560")
    sub.setsockopt_string(zmq.SUBSCRIBE, "")
    
    server = TwinStreamingServer(port=5560)
    server.start()
    
    time.sleep(0.5) # Wait for bind and connect
    
    state = StateVector(theta=0.0, omega=100.0, T_core=3000.0, p_vessel=1.5e5, V_accum=0.5)
    meta = {"node_id": "alpha", "safety": "STEADY_OPERATION", "exergy": {"eta_ii": 0.36}}
    
    server.publish(state, meta)
    
    # Wait for recv with timeout
    poller = zmq.Poller()
    poller.register(sub, zmq.POLLIN)
    socks = dict(poller.poll(500))
    assert sub in socks
    
    msg = sub.recv_json()
    assert msg["node_id"] == "alpha"
    assert msg["state"]["omega"] == 100.0
    
    server.stop()
    sub.close()
    ctx.term()

def test_json_schema_valid():
    server = TwinStreamingServer(port=5557)
    # the publish method internally validates against schema
    # if it fails it won't send.
    # we can test the schema validation directly
    
    msg = {
        "node_id": "alpha",
        "timestamp_utc": "2026-07-14T20:00:00Z",
        "state": {"T_core": 3000.0, "p_vessel": 150000.0},
        "safety": "STEADY_OPERATION",
        "exergy": {"eta_ii": 0.36, "X_destroyed_W": 2500.0}
    }
    
    import jsonschema
    jsonschema.validate(instance=msg, schema=server.schema) # Should not raise
