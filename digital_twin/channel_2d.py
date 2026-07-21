# MODULE-STATUS: SCAFFOLD
import numpy as np
from core.state_vector import StateVector
from config.system_config import SystemConfig
from digital_twin.network_1d import Network1DTwin
from digital_twin.cfd_bridge import OpenFOAMBridge

class Channel2DTwin:
    def __init__(self, config: SystemConfig, use_cfd: bool = False):
        self.config = config
        self.use_cfd = use_cfd
        self._network_twin = Network1DTwin(config)
        self.state_machine = self._network_twin.state_machine
        
        if self.use_cfd:
            self.bridge = OpenFOAMBridge("mock_case", config)
        
        # 2D Grids
        self.sigma = np.ones((64, 16))
        self.u = np.ones((64, 16))
        self.T = np.ones((64, 16))
        self.J = np.ones((64, 16))
        self.phi = np.ones((64, 16))

    @property
    def state(self) -> StateVector:
        return self._network_twin.state
        
    @property
    def current_time(self) -> float:
        return self._network_twin.current_time

    def step(self, dt: float) -> StateVector:
        self._network_twin.run(dt)
        if self.use_cfd:
            fields = self.bridge.run_timestep(dt)
            self.u = fields["U"]
            self.T = fields["T"]
            self.sigma = fields["sigma"]
            self.J = fields["J"]
        else:
            # Simple analytical Hall profile / boundary layer simulation for tests
            x = np.linspace(0, 1, 64)
            y = np.linspace(-1, 1, 16)
            X, Y = np.meshgrid(x, y, indexing='ij')
            # parabolic velocity
            base_omega = max(100.0, self.state.omega)
            self.u = (1 - Y**2) * base_omega
            self.T = np.full_like(self.u, max(1000.0, self.state.T_core))
            # Add simple hall voltage for test
            self.phi = X + 0.1 * Y 

        return self.state

    def run(self, dt: float):
        self.step(dt)

    def get_field(self, var: str) -> np.ndarray:
        return getattr(self, var)
