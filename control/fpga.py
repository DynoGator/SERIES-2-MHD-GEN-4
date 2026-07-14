"""
Fixed-Point Phase Engine (FPGA)
"""
from __future__ import annotations
import numpy as np
import math
from typing import List
from config.system_config import SystemConfig

class FPGAPhaseEngine:
    def __init__(self, config: SystemConfig):
        self.config = config
        self.PHASE_MAX = 4294967296  # 2**32
        self.EIGHTH_OFFSET = self.PHASE_MAX // 8
        self.QUAD_OFFSET = self.PHASE_MAX // 4
        
        self.f_base = 43.2
        self.f_clk = 100e6
        self.phase_step = int((self.f_base * self.PHASE_MAX) / self.f_clk)
        
        self.DEADTIME_TICKS = 100
        
        self.reset()
        
    def reset(self):
        self._phase_accumulator = 0
        self._drive_outputs = np.zeros(8, dtype=int)
        self._last_switch_tick = np.full(8, -self.DEADTIME_TICKS, dtype=int)
        self.tick_count = 0
        self.phase_lock_ok = False

    @property
    def phase_accumulator(self) -> int:
        return self._phase_accumulator

    @property
    def drive_outputs(self) -> np.ndarray:
        return self._drive_outputs.copy()

    def tick(self, phase_cmd: float, fault_latch: bool) -> np.ndarray:
        self.tick_count += 1
        
        if fault_latch:
            self._drive_outputs = np.zeros(8, dtype=int)
            self.phase_lock_ok = False
        else:
            self._phase_accumulator = (self._phase_accumulator + self.phase_step) % self.PHASE_MAX
            
            phase_cmd_int = int(phase_cmd * self.PHASE_MAX / (2 * math.pi))
            
            new_drive = np.zeros(8, dtype=int)
            for k in range(8):
                phase_k = (self._phase_accumulator + phase_cmd_int + k * self.EIGHTH_OFFSET) % self.PHASE_MAX
                desired_state = 1 if phase_k < self.PHASE_MAX // 2 else 0
                
                if desired_state != self._drive_outputs[k]:
                    neighbor_left = (k - 1) % 8
                    neighbor_right = (k + 1) % 8
                    
                    if (self.tick_count - self._last_switch_tick[neighbor_left] >= self.DEADTIME_TICKS) and \
                       (self.tick_count - self._last_switch_tick[neighbor_right] >= self.DEADTIME_TICKS):
                        new_drive[k] = desired_state
                        self._last_switch_tick[k] = self.tick_count
                    else:
                        new_drive[k] = self._drive_outputs[k]
                else:
                    new_drive[k] = desired_state
                    
            self._drive_outputs = new_drive
            self.phase_lock_ok = True
            
        return self._drive_outputs.copy()
