# body.py
# ============================================================
# بدن Noesis - حواس، موقعیت، حرکت در جهان
# ============================================================

import math
from config import (
    BODY_START_X, BODY_START_Y, BODY_START_Z,
    BODY_MOVE_SPEED,
    EYE_SENSITIVITY, EAR_SENSITIVITY, TOUCH_SENSITIVITY
)


class Body:
    def __init__(self):
        self.x = BODY_START_X
        self.y = BODY_START_Y
        self.z = BODY_START_Z
        
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        
        self.eye_sensitivity = EYE_SENSITIVITY
        self.ear_sensitivity = EAR_SENSITIVITY
        self.touch_sensitivity = TOUCH_SENSITIVITY
        
        self.senses = {
            "sight": 0.0,
            "hearing": 0.0,
            "touch": 0.0,
            "temperature": 22.0,
            "position": (self.x, self.y, self.z),
            "on_ground": True,
            "near_water": False,
            "near_wall": False,
            "comfort": 0.5
        }
        
        self.sense_history = []
        self.max_history = 50
        
        self.breath_phase = 0.0
        self.heartbeat_phase = 0.0
        
    def update(self, world):
        self._update_position(world)
        self._update_senses(world)
        self._update_internal_rhythms()
        
        self.sense_history.append(self.senses.copy())
        if len(self.sense_history) > self.max_history:
            self.sense_history.pop(0)
        
    def _update_position(self, world):
        if self.senses["on_ground"]:
            self.vx *= 0.8
            self.vy *= 0.8
            self.vz *= 0.8
        
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        
        self.x = max(0.5, min(world.size_x - 1.5, self.x))
        self.y = max(0.5, min(world.size_y - 1.5, self.y))
        self.z = max(0, min(world.size_z - 1, self.z))
        
        if not world.is_inside(self.x, self.y, self.z):
            self.x = BODY_START_X
            self.y = BODY_START_Y
            self.z = BODY_START_Z
            
    def _update_senses(self, world):
        self.senses["sight"] = world.get_light_at(self.x, self.y, self.z + 1) * self.eye_sensitivity
        self.senses["sight"] = max(0.0, min(1.0, self.senses["sight"]))
        
        self.senses["hearing"] = world.get_sound_at(self.x, self.y, self.z) * self.ear_sensitivity
        self.senses["hearing"] = max(0.0, min(1.0, self.senses["hearing"]))
        
        self.senses["temperature"] = world.get_temperature_at(self.x, self.y, self.z)
        
        ground_texture = world.get_texture_at(self.x, self.y, 0)
        self.senses["touch"] = ground_texture * self.touch_sensitivity
        self.senses["touch"] = max(0.0, min(1.0, self.senses["touch"]))
        
        self.senses["position"] = (round(self.x, 2), round(self.y, 2), round(self.z, 2))
        self.senses["on_ground"] = self.z <= 0.1
        self.senses["near_water"] = world._is_near_water(self.x, self.y)
        self.senses["near_wall"] = world._is_near_wall(self.x, self.y)
        
        comfort = 0.5
        comfort += (self.senses["sight"] - 0.5) * 0.3
        comfort += (self.senses["hearing"] - 0.3) * 0.2
        temp_comfort = 1.0 - abs(self.senses["temperature"] - 22.0) / 15.0
        comfort += temp_comfort * 0.3
        comfort += self.senses["touch"] * 0.2
        self.senses["comfort"] = max(0.0, min(1.0, comfort))
        
    def _update_internal_rhythms(self):
        self.breath_phase += 0.05
        self.heartbeat_phase += 0.1
        
    def get_sense_signal(self):
        signal = (
            self.senses["sight"] * 0.3 +
            self.senses["hearing"] * 0.2 +
            self.senses["touch"] * 0.2 +
            (self.senses["temperature"] - 20.0) / 20.0 * 0.15 +
            self.senses["comfort"] * 0.15
        )
        return signal
        
    def get_body_state(self):
        return {
            "position": self.senses["position"],
            "sight": round(self.senses["sight"], 3),
            "hearing": round(self.senses["hearing"], 3),
            "touch": round(self.senses["touch"], 3),
            "temperature": round(self.senses["temperature"], 1),
            "comfort": round(self.senses["comfort"], 3),
            "on_ground": self.senses["on_ground"],
            "near_water": self.senses["near_water"],
            "near_wall": self.senses["near_wall"]
        }
        
    def save_state(self):
        return {
            "position": (round(self.x, 2), round(self.y, 2), round(self.z, 2)),
            "senses": {
                "sight": round(self.senses["sight"], 3),
                "hearing": round(self.senses["hearing"], 3),
                "touch": round(self.senses["touch"], 3),
                "temperature": round(self.senses["temperature"], 1),
                "comfort": round(self.senses["comfort"], 3)
            }
        }
        
    def restore_state(self, state):
        pos = state.get("position", (BODY_START_X, BODY_START_Y, BODY_START_Z))
        self.x, self.y, self.z = pos
        
        senses = state.get("senses", {})
        self.senses["sight"] = senses.get("sight", 0.5)
        self.senses["hearing"] = senses.get("hearing", 0.3)
        self.senses["touch"] = senses.get("touch", 0.5)
        self.senses["temperature"] = senses.get("temperature", 22.0)
        self.senses["comfort"] = senses.get("comfort", 0.5)