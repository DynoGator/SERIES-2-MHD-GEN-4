#!/usr/bin/env python3
import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from physics.acoustic.modal_id import AcousticModalID
from config.system_config import SystemConfig
from scipy.signal import lti, lsim

def main():
    config = SystemConfig()
    mod = AcousticModalID(config)
    
    import math
    w_n = 2 * math.pi * 43.2
    sys_tf = lti([w_n**2], [1, 2*0.05*w_n, w_n**2])
    
    t = np.linspace(0, 5, 5000)
    dt = t[1] - t[0]
    u = mod.inject_chirp(10.0, 100.0, 5.0, t)
    
    tout, y, x = lsim(sys_tf, u, t)
    H = mod.transfer_function(y, u)
    f_n, zeta = mod.dominant_mode(H, dt)
    
    print("Modal ID Extraction Complete:")
    print(f"Extracted f_n: {f_n:.2f} Hz (True: 43.20 Hz)")
    print(f"Extracted zeta: {zeta:.4f} (True: 0.0500)")

if __name__ == "__main__":
    main()
