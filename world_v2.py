# world_v2.py
# ============================================================
# جهان فیزیکی Noesis - اتاق سه‌بعدی با خورشید و آب
# ============================================================

import math
from config import (
    WORLD_SIZE_X, WORLD_SIZE_Y, WORLD_SIZE_Z,
    SUN_BRIGHTNESS, SUN_CYCLE_SPEED,
    WATER_SOUND_STRENGTH, GROUND_SOFTNESS
)


class WorldV2:
    def __init__(self):
        self.size_x = WORLD_SIZE_X
        self.size_y = WORLD_SIZE_Y
        self.size_z = WORLD_SIZE_Z
        
        self.sun_angle = 0.0
        self.sun_brightness = SUN_BRIGHTNESS
        
        self.water_position = (2, 8)
        self.water_flow = 0.0
        
        self.time = 0
        
        self.objects = {}
        self._init_objects()
        
        self.atmosphere = {
            "temperature": 22.0,
            "humidity": 0.5,
            "ambient_light": 0.6,
            "ambient_sound": 0.2
        }
        
    def _init_objects(self):
        self.objects["sun"] = {
            "type": "light_source",
            "position": (5, 5, 9),
            "intensity": SUN_BRIGHTNESS,
            "color": "warm_gold"
        }
        
        self.objects["water_stream"] = {
            "type": "water",
            "position": (2, 8, 0),
            "length": 6,
            "sound": WATER_SOUND_STRENGTH,
            "temperature": 18.0
        }
        
        for x in range(self.size_x):
            for y in range(self.size_y):
                self.objects[f"ground_{x}_{y}"] = {
                    "type": "ground",
                    "position": (x, y, 0),
                    "softness": GROUND_SOFTNESS,
                    "temperature": 20.0
                }
        
        self.objects["wall_north"] = {"type": "wall", "face": "north", "y": 0}
        self.objects["wall_south"] = {"type": "wall", "face": "south", "y": self.size_y - 1}
        self.objects["wall_east"] = {"type": "wall", "face": "east", "x": self.size_x - 1}
        self.objects["wall_west"] = {"type": "wall", "face": "west", "x": 0}
        self.objects["ceiling"] = {"type": "ceiling", "z": self.size_z - 1}
        
    def step(self):
        self.time += 1
        
        self._update_sun()
        self._update_water()
        self._update_atmosphere()
        
    def _update_sun(self):
        self.sun_angle += SUN_CYCLE_SPEED
        if self.sun_angle > 2 * math.pi:
            self.sun_angle -= 2 * math.pi
        
        self.sun_brightness = SUN_BRIGHTNESS * (0.5 + 0.5 * math.sin(self.sun_angle))
        self.sun_brightness = max(0.1, self.sun_brightness)
        
        sun_x = 5 + 4 * math.cos(self.sun_angle)
        sun_y = 5 + 4 * math.sin(self.sun_angle)
        sun_z = 5 + 2 * math.sin(self.sun_angle * 0.5)
        self.objects["sun"]["position"] = (sun_x, sun_y, sun_z)
        self.objects["sun"]["intensity"] = self.sun_brightness
        
    def _update_water(self):
        self.water_flow += 0.1
        sound = WATER_SOUND_STRENGTH * (0.7 + 0.3 * math.sin(self.water_flow))
        self.objects["water_stream"]["sound"] = sound
        
    def _update_atmosphere(self):
        self.atmosphere["ambient_light"] = self.sun_brightness * 0.6 + 0.1
        self.atmosphere["temperature"] = 20.0 + self.sun_brightness * 8.0
        self.atmosphere["ambient_sound"] = self.objects["water_stream"]["sound"] * 0.5 + 0.1
        
    def get_light_at(self, x, y, z):
        sun_pos = self.objects["sun"]["position"]
        dx = x - sun_pos[0]
        dy = y - sun_pos[1]
        dz = z - sun_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        distance = max(1.0, distance)
        
        light = self.sun_brightness / (distance * 0.3)
        light = max(0.0, min(1.0, light))
        
        if self.objects["sun"]["position"][2] < 0:
            light *= 0.1
            
        near_wall = self._is_near_wall(x, y)
        if near_wall:
            light *= 0.7
            
        return light
        
    def get_sound_at(self, x, y, z):
        water_pos = self.objects["water_stream"]["position"]
        dx = x - water_pos[0]
        dy = y - water_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        distance = max(1.0, distance)
        
        sound = self.objects["water_stream"]["sound"] / distance
        sound = max(0.0, min(1.0, sound))
        
        return sound
        
    def get_temperature_at(self, x, y, z):
        base_temp = self.atmosphere["temperature"]
        
        near_water = self._is_near_water(x, y)
        if near_water:
            base_temp -= 2.0
            
        if z == 0:
            base_temp = self.objects[f"ground_{int(x)}_{int(y)}"]["temperature"]
        elif z > 7:
            base_temp += 1.0
            
        sun_pos = self.objects["sun"]["position"]
        dx = x - sun_pos[0]
        dy = y - sun_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < 3:
            base_temp += 3.0 / max(1.0, distance)
            
        return base_temp
        
    def get_texture_at(self, x, y, z):
        if z == 0:
            return self.objects[f"ground_{int(x)}_{int(y)}"]["softness"]
        if self._is_near_water(x, y) and z < 2:
            return 0.3
        if self._is_near_wall(x, y):
            return 0.1
        return 0.6
        
    def _is_near_water(self, x, y):
        water_pos = self.objects["water_stream"]["position"]
        dx = abs(x - water_pos[0])
        dy = abs(y - water_pos[1])
        return dx < 1.5 and dy < 3
        
    def _is_near_wall(self, x, y):
        if y <= 0.5 or y >= self.size_y - 1.5:
            return True
        if x <= 0.5 or x >= self.size_x - 1.5:
            return True
        return False
        
    def is_inside(self, x, y, z):
        if x < 0 or x >= self.size_x:
            return False
        if y < 0 or y >= self.size_y:
            return False
        if z < 0 or z >= self.size_z:
            return False
        return True
        
    def get_world_state(self):
        return {
            "time": self.time,
            "sun_brightness": round(self.sun_brightness, 2),
            "temperature": round(self.atmosphere["temperature"], 1),
            "ambient_light": round(self.atmosphere["ambient_light"], 2),
            "ambient_sound": round(self.atmosphere["ambient_sound"], 2)
        }
        
    def save_state(self):
        return {
            "time": self.time,
            "sun_angle": round(self.sun_angle, 3),
            "sun_brightness": round(self.sun_brightness, 3),
            "water_flow": round(self.water_flow, 3),
            "atmosphere": {
                "temperature": round(self.atmosphere["temperature"], 1),
                "humidity": round(self.atmosphere["humidity"], 2),
                "ambient_light": round(self.atmosphere["ambient_light"], 2),
                "ambient_sound": round(self.atmosphere["ambient_sound"], 2)
            }
        }
        
    def restore_state(self, state):
        self.time = state.get("time", 0)
        self.sun_angle = state.get("sun_angle", 0.0)
        self.sun_brightness = state.get("sun_brightness", 0.5)
        self.water_flow = state.get("water_flow", 0.0)
        atm = state.get("atmosphere", {})
        self.atmosphere["temperature"] = atm.get("temperature", 22.0)
        self.atmosphere["humidity"] = atm.get("humidity", 0.5)
        self.atmosphere["ambient_light"] = atm.get("ambient_light", 0.6)
        self.atmosphere["ambient_sound"] = atm.get("ambient_sound", 0.2)