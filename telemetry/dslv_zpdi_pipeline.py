import h5py
import json
import zmq
from datetime import datetime, timezone
import jsonschema
from core.state_vector import StateVector

class DSLVZPDIPipeline:
    def __init__(self, node_id: str, site_config: dict):
        self.node_id = node_id
        self.site_config = site_config
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)

    def write_twin_snapshot(self, state: StateVector, telemetry: dict, h5_path: str = "snapshot.h5") -> str:
        with h5py.File(h5_path, "w") as f:
            grp = f.create_group(f"node_{self.node_id}")
            
            meta = grp.create_group("meta")
            meta.attrs["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            meta.attrs["gps_lat"] = self.site_config.get("gps_lat", 0.0)
            meta.attrs["gps_lon"] = self.site_config.get("gps_lon", 0.0)
            meta.attrs["elevation_m"] = self.site_config.get("elevation_m", 0.0)
            meta.attrs["node_type"] = "2MHDBMRIPS"
            
            sensors = grp.create_group("sensors")
            mhd = sensors.create_group("mhd")
            if hasattr(state, "segments_current"):
                mhd.create_dataset("segment_currents", data=state.segments_current)
            else:
                mhd.create_dataset("segment_currents", data=[0.0]*8)
            mhd.create_dataset("segment_voltages", data=[0.0]*8)
            mhd.create_dataset("B_field", data=self.site_config.get("geomagnetic_B_nT", 50000)/1e9)
            mhd.create_dataset("sigma_eff", data=10.0)
            
            thermal = sensors.create_group("thermal")
            thermal.create_dataset("T_core", data=state.T_core)
            thermal.create_dataset("T_wall", data=300.0)
            thermal.create_dataset("T_coolant", data=290.0)
            thermal.create_dataset("heat_flux", data=0.0)
            
            pressure = sensors.create_group("pressure")
            pressure.create_dataset("p_vessel", data=state.p_vessel)
            pressure.create_dataset("p_accum", data=0.0)
            pressure.create_dataset("fross_stage_active", data=[1,1,1,1])
            
            acoustic = sensors.create_group("acoustic")
            acoustic.create_dataset("modal_freq", data=self.site_config.get("acoustic_baseline_hz", 40.0))
            acoustic.create_dataset("modal_coherence", data=0.95)
            acoustic.create_dataset("chirp_response", data=[1.0, 2.0])
            
            control = grp.create_group("control")
            control.create_dataset("state_machine", data=telemetry.get("safety", "INIT"))
            control.create_dataset("fpga_phase", data=0.0)
            control.create_dataset("load_factors", data=[1.0]*8)
            
            derived = grp.create_group("derived")
            derived.create_dataset("exergy_efficiency", data=telemetry.get("exergy", {}).get("eta_ii", 0.0))
            derived.create_dataset("power_net", data=0.0)
            derived.create_dataset("bootstrap_fraction", data=0.0)
            
        return h5_path

    def validate_schema(self, h5_path: str) -> bool:
        # Check that expected groups and datasets exist
        with h5py.File(h5_path, "r") as f:
            if f"node_{self.node_id}" not in f: return False
            grp = f[f"node_{self.node_id}"]
            if "meta" not in grp: return False
            if "sensors/mhd/segment_currents" not in grp: return False
            if "control/state_machine" not in grp: return False
            if "derived/exergy_efficiency" not in grp: return False
        return True

    def stream_zmq(self, endpoint: str = "tcp://127.0.0.1:5555") -> None:
        self.socket.bind(endpoint)
