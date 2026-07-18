import time
from node.node_agent import NodeAgent

class MockTransport:
    def __init__(self):
        self.messages = []
    def send(self, msg):
        self.messages.append(msg)

class MockGPSDO:
    def __init__(self):
        self._locked = True
        self._allan = 1.0e-10
    def is_locked(self):
        return self._locked
    def get_allan_deviation(self):
        return self._allan
    def start(self):
        pass
    def stop(self):
        pass

def test_lifecycle():
    agent = NodeAgent("alpha", "config/deployment.yaml", gpsdo=MockGPSDO())
    assert not agent.running
    agent.start()
    assert agent.running
    assert agent._thread is not None
    assert agent._thread.is_alive()
    agent.stop()
    assert not agent.running
    assert not agent._thread.is_alive()

def test_heartbeat_reaches_aggregator():
    transport = MockTransport()
    agent = NodeAgent("alpha", "config/deployment.yaml", transport=transport, gpsdo=MockGPSDO())
    
    agent.heartbeat_once()
    assert len(transport.messages) == 1
    msg = transport.messages[0]
    assert msg["node_id"] == "alpha"
    assert "gpsdo_locked" in msg

def test_status_fields():
    agent = NodeAgent("alpha", "config/deployment.yaml", gpsdo=MockGPSDO())
    agent.start()
    stat = agent.status()
    
    assert "node_id" in stat
    assert "gpsdo_locked" in stat
    assert "allan_dev" in stat
    assert "last_campaign" in stat
    assert "uptime_s" in stat
    
    assert isinstance(stat["node_id"], str)
    assert isinstance(stat["gpsdo_locked"], bool)
    assert isinstance(stat["allan_dev"], float)
    assert isinstance(stat["uptime_s"], float)
    
    agent.stop()

def test_stop_idempotent():
    agent = NodeAgent("alpha", "config/deployment.yaml", gpsdo=MockGPSDO())
    agent.start()
    agent.stop()
    agent.stop() # Should not raise
    assert not agent.running
