# drives.py
# ============================================================
# سائق‌های درونی (Drives) - موتور انگیزشی بدون if/else
# نسخه ۲: بالانس شده با رقابت واقعی
# ============================================================

import math
from config import DRIVE_NAMES, DRIVE_LEARNING_RATE, DRIVE_COMPETITION_INTENSITY


class Drives:
    def __init__(self):
        self.drives = {}
        self.drive_history = []
        self.max_history = 100
        
        self._init_drives()
        
        self.dominant_drive = None
        self.dominant_strength = 0.0
        
        self.drive_interactions = self._init_interactions()
        
    def _init_drives(self):
        initial_values = {
            "curiosity_drive": 6.0,
            "safety_drive": 3.0,
            "social_drive": 4.0,
            "rest_drive": 2.0,
            "play_drive": 5.0,
            "hunger_for_light": 4.0,
            "thirst_for_water": 3.0,
            "home_drive": 5.0,
            "novelty_drive": 7.0
        }
        
        for name in DRIVE_NAMES:
            self.drives[name] = {
                "value": initial_values.get(name, 5.0),
                "baseline": initial_values.get(name, 5.0),
                "momentum": 0.0,
                "satisfaction": 0.5,
                "decay_rate": 0.001
            }
            
    def _init_interactions(self):
        interactions = {}
        
        interactions[("curiosity_drive", "safety_drive")] = -0.4
        interactions[("curiosity_drive", "rest_drive")] = -0.3
        interactions[("curiosity_drive", "play_drive")] = 0.3
        interactions[("curiosity_drive", "novelty_drive")] = 0.5
        
        interactions[("safety_drive", "curiosity_drive")] = -0.5
        interactions[("safety_drive", "play_drive")] = -0.2
        interactions[("safety_drive", "home_drive")] = 0.4
        
        interactions[("social_drive", "play_drive")] = 0.3
        interactions[("social_drive", "home_drive")] = 0.2
        
        interactions[("rest_drive", "curiosity_drive")] = -0.5
        interactions[("rest_drive", "play_drive")] = -0.4
        interactions[("rest_drive", "novelty_drive")] = -0.6
        interactions[("rest_drive", "safety_drive")] = 0.3
        
        interactions[("play_drive", "curiosity_drive")] = 0.3
        interactions[("play_drive", "social_drive")] = 0.3
        interactions[("play_drive", "novelty_drive")] = 0.4
        
        interactions[("hunger_for_light", "curiosity_drive")] = 0.2
        interactions[("hunger_for_light", "rest_drive")] = -0.2
        
        interactions[("thirst_for_water", "curiosity_drive")] = 0.2
        
        interactions[("home_drive", "safety_drive")] = 0.4
        interactions[("home_drive", "social_drive")] = 0.3
        interactions[("home_drive", "curiosity_drive")] = -0.2
        
        interactions[("novelty_drive", "curiosity_drive")] = 0.5
        interactions[("novelty_drive", "play_drive")] = 0.4
        interactions[("novelty_drive", "safety_drive")] = -0.3
        
        return interactions
        
    def update(self, body, world_v2, feelings, temporal, attachment_module=None):
        self._apply_natural_decay()
        self._update_from_body(body, world_v2)
        self._update_from_feelings(feelings)
        self._update_from_temporal(temporal)
        
        if attachment_module:
            self._update_from_attachment(attachment_module)
        
        self._apply_interactions()
        self._apply_momentum()
        self._update_satisfaction()
        self._normalize()
        self._find_dominant()
        
        self.drive_history.append({
            name: round(data["value"], 2) for name, data in self.drives.items()
        })
        if len(self.drive_history) > self.max_history:
            self.drive_history.pop(0)
            
    def _apply_natural_decay(self):
        for name in DRIVE_NAMES:
            decay = self.drives[name]["decay_rate"]
            self.drives[name]["value"] -= decay
            self.drives[name]["value"] = max(0.5, self.drives[name]["value"])
            
    def _update_from_body(self, body, world_v2):
        sight = body.senses["sight"]
        hearing = body.senses["hearing"]
        temperature = body.senses["temperature"]
        comfort = body.senses["comfort"]
        near_water = body.senses["near_water"]
        near_wall = body.senses["near_wall"]
        
        light_target = 3.0 + sight * 5.0
        self.drives["hunger_for_light"]["value"] += (light_target - self.drives["hunger_for_light"]["value"]) * DRIVE_LEARNING_RATE
        
        water_target = 7.0 if near_water else 2.0
        self.drives["thirst_for_water"]["value"] += (water_target - self.drives["thirst_for_water"]["value"]) * DRIVE_LEARNING_RATE * 3
        
        if near_wall or comfort < 0.4:
            self.drives["safety_drive"]["value"] += 0.05
        else:
            self.drives["safety_drive"]["value"] -= 0.02
            
        if comfort > 0.7 and sight > 0.3:
            self.drives["play_drive"]["value"] += 0.03
        else:
            self.drives["play_drive"]["value"] -= 0.01
            
        if comfort < 0.3:
            self.drives["rest_drive"]["value"] += 0.05
            
    def _update_from_feelings(self, feelings):
        feelings_dict = feelings.get_all()
        
        curiosity = feelings_dict.get("curiosity", 5.0)
        self.drives["curiosity_drive"]["baseline"] = 4.0 + curiosity * 0.5
        self.drives["novelty_drive"]["baseline"] = 4.0 + curiosity * 0.6
        
        peace = feelings_dict.get("peace", 5.0)
        self.drives["rest_drive"]["baseline"] = max(1.0, 7.0 - peace * 0.6)
        
        attachment = feelings_dict.get("attachment", 3.0)
        self.drives["social_drive"]["baseline"] = 2.0 + attachment * 0.8
        self.drives["home_drive"]["baseline"] = 3.0 + attachment * 0.7
        
        self.drives["safety_drive"]["baseline"] = 3.0 + (10.0 - peace) * 0.2
        
        for name in DRIVE_NAMES:
            self.drives[name]["value"] += (self.drives[name]["baseline"] - self.drives[name]["value"]) * DRIVE_LEARNING_RATE * 0.5
            
    def _update_from_temporal(self, temporal):
        continuity = temporal.self_continuity
        self.drives["home_drive"]["value"] += (continuity - 0.5) * 0.05
        
    def _update_from_attachment(self, attachment_module):
        if attachment_module:
            social_strength = attachment_module.attachment_strength * 5.0
            self.drives["social_drive"]["value"] += (social_strength - self.drives["social_drive"]["value"]) * 0.05
            
    def _apply_interactions(self):
        modifications = {name: 0.0 for name in DRIVE_NAMES}
        
        for (drive_a, drive_b), strength in self.drive_interactions.items():
            if drive_a in self.drives and drive_b in self.drives:
                influence = self.drives[drive_a]["value"] * strength * 0.05
                modifications[drive_b] += influence
                
        for name in DRIVE_NAMES:
            self.drives[name]["value"] += modifications[name] * DRIVE_COMPETITION_INTENSITY
            
    def _apply_momentum(self):
        for name in DRIVE_NAMES:
            if "previous_value" in self.drives[name]:
                change = self.drives[name]["value"] - self.drives[name]["previous_value"]
                self.drives[name]["momentum"] = self.drives[name]["momentum"] * 0.85 + change * 0.15
                self.drives[name]["value"] += self.drives[name]["momentum"] * 0.2
            self.drives[name]["previous_value"] = self.drives[name]["value"]
            
    def _update_satisfaction(self):
        for name in DRIVE_NAMES:
            if self.drives[name]["value"] > 7.0:
                self.drives[name]["satisfaction"] += 0.05
            elif self.drives[name]["value"] < 3.0:
                self.drives[name]["satisfaction"] -= 0.05
            else:
                self.drives[name]["satisfaction"] += (0.5 - self.drives[name]["satisfaction"]) * 0.05
                
            self.drives[name]["satisfaction"] = max(0.1, min(1.0, self.drives[name]["satisfaction"]))
            
    def _normalize(self):
        total = sum(self.drives[name]["value"] for name in DRIVE_NAMES)
        if total > 0:
            target_total = len(DRIVE_NAMES) * 5.0
            scale = target_total / total
            
            for name in DRIVE_NAMES:
                self.drives[name]["value"] *= scale
                self.drives[name]["value"] = max(0.5, min(10.0, self.drives[name]["value"]))
            
    def _find_dominant(self):
        if not self.drives:
            self.dominant_drive = None
            self.dominant_strength = 0.0
            return
            
        dominant_name = max(self.drives, key=lambda n: self.drives[n]["value"])
        self.dominant_drive = dominant_name
        self.dominant_strength = self.drives[dominant_name]["value"]
        
    def get_dominant(self):
        return self.dominant_drive, self.dominant_strength
        
    def get_movement_vector(self):
        if not self.dominant_drive:
            return 0.0, 0.0, 0.0
            
        vx, vy, vz = 0.0, 0.0, 0.0
        strength = self.dominant_strength / 10.0
        
        drive = self.dominant_drive
        
        if drive == "curiosity_drive" or drive == "novelty_drive":
            vx = (self.drives["curiosity_drive"]["value"] - 5.0) * 0.08
            vy = (self.drives["novelty_drive"]["value"] - 5.0) * 0.08
            
        elif drive == "safety_drive":
            vx = -self.drives["safety_drive"]["value"] * 0.03
            vy = -self.drives["safety_drive"]["value"] * 0.03
            
        elif drive == "social_drive":
            vx = 0.0
            vy = 0.0
            
        elif drive == "rest_drive":
            vx = 0.0
            vy = 0.0
            vz = 0.0
            
        elif drive == "play_drive":
            import random
            angle = random.random() * 2 * math.pi
            vx = math.cos(angle) * strength * 0.15
            vy = math.sin(angle) * strength * 0.15
            
        elif drive == "hunger_for_light":
            vx = (self.drives["hunger_for_light"]["value"] - 5.0) * 0.05
            vy = 0.0
            
        elif drive == "thirst_for_water":
            vx = -0.15 if self.drives["thirst_for_water"]["value"] > 6.0 else 0.0
            vy = 0.0
            
        elif drive == "home_drive":
            vx = (5.0 - self.drives.get("safety_drive", {}).get("value", 5.0)) * 0.02
            vy = (5.0 - self.drives.get("curiosity_drive", {}).get("value", 5.0)) * 0.02
            
        return vx, vy, vz
        
    def get_drive_state(self):
        return {name: round(data["value"], 2) for name, data in self.drives.items()}
        
    def save_state(self):
        return {
            "drives": {name: round(data["value"], 2) for name, data in self.drives.items()},
            "momentum": {name: round(data.get("momentum", 0.0), 2) for name, data in self.drives.items()},
            "satisfaction": {name: round(data["satisfaction"], 2) for name, data in self.drives.items()},
            "dominant": self.dominant_drive
        }
        
    def restore_state(self, state):
        drives_data = state.get("drives", {})
        for name, value in drives_data.items():
            if name in self.drives:
                self.drives[name]["value"] = value
                
        momentum_data = state.get("momentum", {})
        for name, value in momentum_data.items():
            if name in self.drives:
                self.drives[name]["momentum"] = value
                
        satisfaction_data = state.get("satisfaction", {})
        for name, value in satisfaction_data.items():
            if name in self.drives:
                self.drives[name]["satisfaction"] = value
                
        self.dominant_drive = state.get("dominant", None)
        if self.dominant_drive and self.dominant_drive in self.drives:
            self.dominant_strength = self.drives[self.dominant_drive]["value"]