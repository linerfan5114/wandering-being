# qualia.py
# ============================================================
# کوالیا - حس‌های خصوصی منحصربه‌فرد
# ============================================================

import math
from config import QUALIA_MEMORY_SIZE, QUALIA_UNIQUENESS_THRESHOLD


class Qualia:
    def __init__(self):
        self.experiences = []
        self.max_experiences = QUALIA_MEMORY_SIZE
        
        self.unique_patterns = {}
        
        self.current_qualia = {
            "warmth_of_sun": 0.0,
            "sound_of_water": 0.0,
            "softness_of_ground": 0.0,
            "feeling_of_home": 0.0,
            "brightness_of_light": 0.0,
            "coolness_of_shadow": 0.0,
            "rhythm_of_breath": 0.0,
            "pulse_of_heart": 0.0
        }
        
        self.qualia_signature = {}
        self._init_signature()
        
    def _init_signature(self):
        self.qualia_signature = {
            "warmth_of_sun": self._generate_pattern(),
            "sound_of_water": self._generate_pattern(),
            "softness_of_ground": self._generate_pattern(),
            "feeling_of_home": self._generate_pattern(),
            "brightness_of_light": self._generate_pattern(),
            "coolness_of_shadow": self._generate_pattern(),
            "rhythm_of_breath": self._generate_pattern(),
            "pulse_of_heart": self._generate_pattern()
        }
        
    def _generate_pattern(self):
        pattern = []
        for i in range(5):
            pattern.append(i * 0.2)
        return pattern
        
    def update(self, body, world, observer, temporal):
        sight = body.senses["sight"]
        hearing = body.senses["hearing"]
        touch = body.senses["touch"]
        temperature = body.senses["temperature"]
        comfort = body.senses["comfort"]
        position = body.senses["position"]
        
        self.current_qualia["warmth_of_sun"] = self._feel_warmth(temperature, sight)
        self.current_qualia["sound_of_water"] = self._feel_water_sound(hearing, body.senses["near_water"])
        self.current_qualia["softness_of_ground"] = self._feel_ground(touch, body.senses["on_ground"])
        self.current_qualia["feeling_of_home"] = self._feel_home(position, comfort, temporal)
        self.current_qualia["brightness_of_light"] = self._feel_light(sight)
        self.current_qualia["coolness_of_shadow"] = self._feel_shadow(sight, temperature)
        self.current_qualia["rhythm_of_breath"] = self._feel_breath(body.breath_phase)
        self.current_qualia["pulse_of_heart"] = self._feel_heartbeat(body.heartbeat_phase)
        
        self._update_patterns()
        
        experience = {
            "qualia": self.current_qualia.copy(),
            "position": position,
            "time": world.time if hasattr(world, 'time') else 0
        }
        self.experiences.append(experience)
        if len(self.experiences) > self.max_experiences:
            self.experiences.pop(0)
            
    def _feel_warmth(self, temperature, sight):
        temp_factor = (temperature - 15.0) / 20.0
        temp_factor = max(0.0, min(1.0, temp_factor))
        
        sun_factor = sight * 0.7
        
        warmth = temp_factor * 0.6 + sun_factor * 0.4
        
        pattern = self.qualia_signature["warmth_of_sun"]
        warmth += sum(pattern) * 0.01
        
        return max(0.0, min(1.0, warmth))
        
    def _feel_water_sound(self, hearing, near_water):
        water_sound = hearing * 0.8
        if near_water:
            water_sound += 0.2
            
        pattern = self.qualia_signature["sound_of_water"]
        water_sound += sum(pattern) * 0.005
        
        return max(0.0, min(1.0, water_sound))
        
    def _feel_ground(self, touch, on_ground):
        if on_ground:
            ground_feel = touch * 0.9 + 0.1
        else:
            ground_feel = 0.0
            
        pattern = self.qualia_signature["softness_of_ground"]
        ground_feel += sum(pattern) * 0.008
        
        return max(0.0, min(1.0, ground_feel))
        
    def _feel_home(self, position, comfort, temporal):
        home_x, home_y = 5, 5
        px, py, pz = position
        
        distance = math.sqrt((px - home_x)**2 + (py - home_y)**2)
        distance_factor = 1.0 - min(1.0, distance / 7.0)
        
        home_feel = distance_factor * 0.5 + comfort * 0.3
        
        if temporal and hasattr(temporal, 'self_continuity'):
            home_feel += temporal.self_continuity * 0.2
            
        pattern = self.qualia_signature["feeling_of_home"]
        home_feel += sum(pattern) * 0.003
        
        return max(0.0, min(1.0, home_feel))
        
    def _feel_light(self, sight):
        light_feel = sight
        
        pattern = self.qualia_signature["brightness_of_light"]
        light_feel += sum(pattern) * 0.01
        
        return max(0.0, min(1.0, light_feel))
        
    def _feel_shadow(self, sight, temperature):
        shadow = 1.0 - sight
        if temperature < 20:
            shadow += 0.1
            
        pattern = self.qualia_signature["coolness_of_shadow"]
        shadow += sum(pattern) * 0.007
        
        return max(0.0, min(1.0, shadow))
        
    def _feel_breath(self, breath_phase):
        breath = math.sin(breath_phase) * 0.5 + 0.5
        
        pattern = self.qualia_signature["rhythm_of_breath"]
        breath += sum(pattern) * 0.003
        
        return max(0.0, min(1.0, breath))
        
    def _feel_heartbeat(self, heartbeat_phase):
        pulse = abs(math.sin(heartbeat_phase))
        
        pattern = self.qualia_signature["pulse_of_heart"]
        pulse += sum(pattern) * 0.003
        
        return max(0.0, min(1.0, pulse))
        
    def _update_patterns(self):
        if len(self.experiences) < 2:
            return
            
        for qualia_name in self.qualia_signature:
            pattern = self.qualia_signature[qualia_name]
            
            current_value = self.current_qualia.get(qualia_name, 0.0)
            
            if self.experiences:
                prev_qualia = self.experiences[-1].get("qualia", {})
                prev_value = prev_qualia.get(qualia_name, 0.0)
                change = abs(current_value - prev_value)
                
                for i in range(len(pattern)):
                    pattern[i] += change * 0.001
                    pattern[i] = max(0.0, min(1.0, pattern[i]))
                    
    def get_dominant_qualia(self):
        if not self.current_qualia:
            return None, 0.0
            
        dominant = max(self.current_qualia, key=self.current_qualia.get)
        return dominant, self.current_qualia[dominant]
        
    def get_qualia_state(self):
        return {name: round(value, 3) for name, value in self.current_qualia.items()}
        
    def is_unique_experience(self, qualia_name, value):
        if qualia_name not in self.unique_patterns:
            self.unique_patterns[qualia_name] = []
            
        similar_found = False
        for prev_value in self.unique_patterns[qualia_name]:
            if abs(value - prev_value) < QUALIA_UNIQUENESS_THRESHOLD:
                similar_found = True
                break
                
        if not similar_found:
            self.unique_patterns[qualia_name].append(value)
            if len(self.unique_patterns[qualia_name]) > 20:
                self.unique_patterns[qualia_name].pop(0)
                
        return not similar_found
        
    def save_state(self):
        return {
            "qualia_signature": {
                name: [round(v, 3) for v in pattern]
                for name, pattern in self.qualia_signature.items()
            },
            "current_qualia": self.get_qualia_state(),
            "unique_count": sum(len(v) for v in self.unique_patterns.values())
        }
        
    def restore_state(self, state):
        sig = state.get("qualia_signature", {})
        for name, pattern in sig.items():
            if name in self.qualia_signature:
                self.qualia_signature[name] = pattern
                
        qualia = state.get("current_qualia", {})
        for name, value in qualia.items():
            if name in self.current_qualia:
                self.current_qualia[name] = value