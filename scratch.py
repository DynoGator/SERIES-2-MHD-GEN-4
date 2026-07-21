from config.system_config import SystemConfig
from digital_twin.network_1d import Network1DTwin
import numpy as np
config = SystemConfig()
net = Network1DTwin(config)
net.state = net.state.evolve(T_core=4000.0, omega=100.0)
net.control.load_resistances = np.full(8, 0.001)
net.channel._sigma_mults[0] = 5.0
for mod in net.modules:
    contrib = mod.compute(net.state, net.control, config)
    if 'coherence_r' in contrib.dydt:
        print(f"{mod.__class__.__name__} returns d(coherence_r)/dt = {contrib.dydt['coherence_r']}")
