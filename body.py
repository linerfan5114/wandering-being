# body.py
# ============================================================
# بدن Noesis - حواس، موقعیت، حرکت، چشم فضایی
# نسخه ۲: با میدان دید ۳ بعدی
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
        
        self.visual_field = {}
        self.visual_field_size = 1
        
        self.sense_history = []
        self.max_history = 50
        
        self.breath_phase = 0.0
        self.heartbeat_phase = 0.0
        
    def update(self, world):
        self._update_position(world)
        self._update_senses(world)
        self._update_visual_field(world)
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
            
    def _update_visual_field(self, world):
        self.visual_field = {}
        
        r = self.visual_field_size
        
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    wx = int(self.x) + dx
                    wy = int(self.y) + dy
                    wz = int(self.z) + dz
                    
                    if not world.is_inside(wx, wy, wz):
                        continue
                    
                    light = world.get_light_at(wx, wy, wz)
                    is_wall = world._is_near_wall(wx, wy)
                    is_water = world._is_near_water(wx, wy)
                    
                    cell_type = "empty"
                    if is_wall:
                        cell_type = "wall"
                    elif is_water:
                        cell_type = "water"
                    elif wz == 0:
                        cell_type = "ground"
                    
                    sun_dist = math.sqrt(
                        (wx - world.objects["sun"]["position"][0])**2 +
                        (wy - world.objects["sun"]["position"][1])**2 +
                        (wz - world.objects["sun"]["position"][2])**2
                    )
                    
                    key = (dx, dy, dz)
                    self.visual_field[key] = {
                        "world_pos": (wx, wy, wz),
                        "light": round(light, 3),
                        "type": cell_type,
                        "sun_distance": round(sun_dist, 1)
                    }
        
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
        
        visual_cells = len(self.visual_field)
        self.senses["visual_cells"] = visual_cells
        
        wall_cells = sum(1 for v in self.visual_field.values() if v["type"] == "wall")
        water_cells = sum(1 for v in self.visual_field.values() if v["type"] == "water")
        self.senses["walls_visible"] = wall_cells
        self.senses["water_visible"] = water_cells
        
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
            self.senses["sight"] * 0.25 +
            self.senses["hearing"] * 0.15 +
            self.senses["touch"] * 0.15 +
            (self.senses["temperature"] - 20.0) / 20.0 * 0.10 +
            self.senses["comfort"] * 0.15 +
            (self.senses.get("walls_visible", 0) / 27.0) * 0.10 +
            (self.senses.get("water_visible", 0) / 27.0) * 0.10
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
            "near_wall": self.senses["near_wall"],
            "visual_cells": self.senses.get("visual_cells", 0),
            "walls_visible": self.senses.get("walls_visible", 0),
            "water_visible": self.senses.get("water_visible", 0)
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