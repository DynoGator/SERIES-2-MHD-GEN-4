from network.mesh import MeshFallback
from network.events import make_event

class MockTransport:
    def __init__(self):
        self.sent = []
    def send(self, event, via):
        self.sent.append((event, via))
        return True

def test_failover_sequence():
    mesh = MeshFallback(heartbeat_s=2.0)
    mesh.broker_alive(True, now=1.0)
    assert mesh.tick(1.0) == "BROKERED"
    
    # Kill broker
    assert mesh.tick(3.1) == "DEGRADED"
    assert mesh.tick(5.1) == "MESH"
    
    # Restore broker
    mesh.broker_alive(True, now=6.0)
    assert mesh.tick(6.0) == "BROKERED"

def test_telemetry_continues_in_mesh():
    transport = MockTransport()
    mesh = MeshFallback(heartbeat_s=2.0, transport=transport)
    mesh.broker_alive(True, now=1.0)
    mesh.tick(5.1) # Forces MESH state
    assert mesh.state == "MESH"
    
    event = make_event("alpha", "TYPE1", 100.0, 1.0)
    assert mesh.send(event) is True
    assert transport.sent[0][1] == "MESH"

def test_no_event_loss_across_failover():
    transport = MockTransport()
    mesh = MeshFallback(heartbeat_s=2.0, transport=transport)
    event1 = make_event("alpha", "TYPE1", 100.0, 1.0)
    event2 = make_event("alpha", "TYPE2", 101.0, 1.0)
    
    mesh.broker_alive(True, now=1.0)
    mesh.tick(1.0)
    mesh.send(event1)
    
    mesh.tick(5.1) # MESH
    mesh.send(event2)
    
    assert mesh._events_sent == 2
    assert transport.sent[0][1] == "BROKERED"
    assert transport.sent[1][1] == "MESH"
