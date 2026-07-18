from network.events import AnomalyEvent

class MeshFallback:
    STATES = ("BROKERED", "DEGRADED", "MESH")
    
    def __init__(self, heartbeat_s: float = 2.0, transport=None):
        self.heartbeat_s = heartbeat_s
        self.transport = transport
        self.state = "BROKERED"
        self._last_broker_seen = 0.0
        self._events_sent = 0

    def tick(self, now: float) -> str:
        elapsed = now - self._last_broker_seen
        if elapsed > self.heartbeat_s * 2:
            self.state = "MESH"
        elif elapsed > self.heartbeat_s:
            self.state = "DEGRADED"
        else:
            self.state = "BROKERED"
                
        return self.state

    def broker_alive(self, alive: bool, now: float = 0.0) -> None:
        if alive:
            self._last_broker_seen = now

    def send(self, event: AnomalyEvent) -> bool:
        success = False
        if self.transport:
            success = self.transport.send(event, via=self.state)
        else:
            success = True # Mock success
            
        if success:
            self._events_sent += 1
            
        return success
