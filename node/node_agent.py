import yaml
import time
import threading
from typing import Optional, Dict, Any
from network.node_identity import load_node
from hardware.gpsdo_sync import GPSDOSync
from telemetry.campaign_recorder import CampaignRecorder

class NodeAgent:
    def __init__(self, node_id: str, config_path: str, transport=None, gpsdo=None, source=None):
        self.node_id = node_id
        self.config_path = config_path
        self.transport = transport
        
        # Load config
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.identity = load_node(self.node_id)
        
        # Hardware
        self.gpsdo = gpsdo if gpsdo else GPSDOSync(self.config["gpsdo"]["device_path"])
        self.source = source
        
        # State
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.start_time: float = 0.0
        self.last_campaign: Optional[str] = None
        
    def start(self) -> None:
        if self.running:
            return
            
        self.running = True
        self.start_time = time.time()
        
        if hasattr(self.gpsdo, 'start'):
            self.gpsdo.start()
            
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
    def stop(self) -> None:
        if not self.running:
            return
            
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            
        if hasattr(self.gpsdo, 'stop'):
            self.gpsdo.stop()
            
    def _run_loop(self) -> None:
        interval = self.config.get("heartbeat_interval_s", 5.0)
        while self.running:
            self.heartbeat_once()
            # sleep in smaller chunks to be responsive to stop()
            for _ in range(int(interval * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
                
    def heartbeat_once(self) -> bool:
        stat = self.status()
        if self.transport:
            # Assuming transport provides a publish or send method
            self.transport.send(stat)
            return True
        return False
        
    def status(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time if self.running else 0.0
        
        if hasattr(self.gpsdo, 'is_locked'):
            locked = self.gpsdo.is_locked()
            allan = self.gpsdo.get_allan_deviation()
        else:
            locked = True
            allan = 1.0e-11
            
        return {
            "node_id": self.node_id,
            "gpsdo_locked": locked,
            "allan_dev": allan,
            "last_campaign": self.last_campaign,
            "uptime_s": uptime
        }
