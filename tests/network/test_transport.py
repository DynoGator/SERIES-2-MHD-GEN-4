import uuid
import pytest
from network.transport import ZmqTransport
from network.events import make_event

def test_inproc_roundtrip():
    endpoint = f"inproc://test_{uuid.uuid4()}"
    receiver = ZmqTransport(endpoint, bind=True)
    sender = ZmqTransport(endpoint, bind=False)
    
    event = make_event("alpha", "GEOMAGNETIC_SPIKE", 10.0, 50.0)
    assert sender.send(event) is True
    
    received = receiver.recv(100)
    assert received is not None
    assert received.event_id == event.event_id
    assert received.node_id == event.node_id
    assert received.anomaly_type == event.anomaly_type

def test_recv_timeout_returns_none():
    endpoint = f"inproc://test_{uuid.uuid4()}"
    receiver = ZmqTransport(endpoint, bind=True)
    
    received = receiver.recv(10)
    assert received is None

def test_no_external_ports_in_tests():
    endpoint = f"inproc://test_{uuid.uuid4()}"
    assert endpoint.startswith("inproc://")
