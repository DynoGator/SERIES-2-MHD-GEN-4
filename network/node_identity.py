from dataclasses import dataclass
from config.sites import SITES

@dataclass(frozen=True)
class NodeIdentity:
    node_id: str            # "alpha" | "beta" | "gamma"
    site_key: str           # key into config/sites.py profiles
    role: str               # "primary" | "relay"
    gpsdo_disciplined: bool

def load_node(node_id: str) -> NodeIdentity:
    for site_key, data in SITES.items():
        if data.get("node_id") == node_id:
            role = "primary" if node_id == "alpha" else "relay"
            return NodeIdentity(
                node_id=node_id,
                site_key=site_key,
                role=role,
                gpsdo_disciplined=True
            )
    raise ValueError(f"Unknown node_id: {node_id}")
