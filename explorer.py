# explorer.py
# ============================================================
# کاوشگر (Explorer) - حرکت بر اساس کاهش خطای پیش‌بینی
# بدون if/else، فقط ریاضی
# ============================================================

import math
from config import EXPLORER_PREDICTION_HORIZON, EXPLORER_CURIOSITY_WEIGHT, EXPLORER_SAFETY_WEIGHT


class Explorer:
    def __init__(self):
        self.prediction_model = {}
        self.prediction_error = 0.0
        self.prediction_error_history = []
        self.max_error_history = 50
        
        self.curiosity_weight = EXPLORER_CURIOSITY_WEIGHT
        self.safety_weight = EXPLORER_SAFETY_WEIGHT
        
        self.target_position = None
        self.target_score = 0.0
        
        self.visited_positions = {}
        self.visited_decay = 0.995
        
        self.last_prediction = None
        self.last_actual = None
        
    def predict(self, body, world_v2):
        x, y, z = body.x, body.y, body.z
        
        predictions = {}
        
        key_nearby = self._get_nearby_key(x, y)
        if key_nearby in self.prediction_model:
            predictions = self.prediction_model[key_nearby].copy()
        
        sight_pred = predictions.get("sight", body.senses.get("sight", 0.5))
        hearing_pred = predictions.get("hearing", body.senses.get("hearing", 0.3))
        temp_pred = predictions.get("temperature", body.senses.get("temperature", 22.0))
        
        self.last_prediction = {
            "sight": sight_pred,
            "hearing": hearing_pred,
            "temperature": temp_pred
        }
        
        return self.last_prediction
        
    def learn(self, body, world_v2):
        x, y, z = body.x, body.y, body.z
        
        actual = {
            "sight": body.senses.get("sight", 0.5),
            "hearing": body.senses.get("hearing", 0.3),
            "temperature": body.senses.get("temperature", 22.0),
            "comfort": body.senses.get("comfort", 0.5)
        }
        
        self.last_actual = actual
        
        if self.last_prediction:
            errors = []
            for key in ["sight", "hearing", "temperature"]:
                pred = self.last_prediction.get(key, 0.5)
                act = actual.get(key, pred)
                errors.append(abs(pred - act))
            
            self.prediction_error = sum(errors) / len(errors)
            self.prediction_error_history.append(self.prediction_error)
            if len(self.prediction_error_history) > self.max_error_history:
                self.prediction_error_history.pop(0)
        
        key_nearby = self._get_nearby_key(x, y)
        if key_nearby not in self.prediction_model:
            self.prediction_model[key_nearby] = {}
        
        for key, value in actual.items():
            if key in self.prediction_model[key_nearby]:
                self.prediction_model[key_nearby][key] += 0.1 * (value - self.prediction_model[key_nearby][key])
            else:
                self.prediction_model[key_nearby][key] = value
        
        pos_key = (int(x * 2) / 2, int(y * 2) / 2)
        if pos_key not in self.visited_positions:
            self.visited_positions[pos_key] = 1.0
        else:
            self.visited_positions[pos_key] += 0.1
        
        for key in list(self.visited_positions.keys()):
            self.visited_positions[key] *= self.visited_decay
            if self.visited_positions[key] < 0.05:
                del self.visited_positions[key]
        
    def get_movement(self, body, world_v2, drives_module=None):
        x, y, z = body.x, body.y, body.z
        
        candidates = []
        
        for dx in [-1, -0.5, 0, 0.5, 1]:
            for dy in [-1, -0.5, 0, 0.5, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx = x + dx * 0.3
                ny = y + dy * 0.3
                nz = 0
                
                if not world_v2.is_inside(nx, ny, nz):
                    continue
                
                score = self._calculate_position_score(nx, ny, body, world_v2, drives_module)
                candidates.append((nx, ny, nz, score))
        
        if not candidates:
            return 0.0, 0.0, 0.0
        
        best = max(candidates, key=lambda c: c[3])
        self.target_position = (best[0], best[1], best[2])
        self.target_score = best[3]
        
        vx = (best[0] - x) * 0.5
        vy = (best[1] - y) * 0.5
        vz = 0.0
        
        return vx, vy, vz
        
    def _calculate_position_score(self, nx, ny, body, world_v2, drives_module=None):
        score = 0.0
        
        pos_key = (int(nx * 2) / 2, int(ny * 2) / 2)
        visited_count = self.visited_positions.get(pos_key, 0.0)
        novelty = 1.0 - min(1.0, visited_count)
        score += novelty * self.curiosity_weight * 3.0
        
        key_nearby = self._get_nearby_key(nx, ny)
        if key_nearby in self.prediction_model:
            prediction_error_at = 0.0
            for sense_key in ["sight", "hearing", "temperature"]:
                if sense_key in self.prediction_model[key_nearby]:
                    prediction_error_at += abs(self.prediction_model[key_nearby][sense_key] - 0.5)
            score += prediction_error_at * self.curiosity_weight * 2.0
        else:
            score += 0.5 * self.curiosity_weight
        
        is_near_wall = world_v2._is_near_wall(nx, ny)
        if is_near_wall:
            score -= self.safety_weight * 2.0
        
        is_near_water = world_v2._is_near_water(nx, ny)
        if is_near_water:
            score += 2.0
            score -= self.safety_weight * 0.5
        
        light = world_v2.get_light_at(nx, ny, 0)
        score += light * self.curiosity_weight
        
        temp = world_v2.get_temperature_at(nx, ny, 0)
        temp_comfort = 1.0 - abs(temp - 22.0) / 15.0
        score += temp_comfort * self.safety_weight * 2.0
        
        if drives_module:
            drive_name, drive_strength = drives_module.get_dominant()
            
            if drive_name == "curiosity_drive":
                score += novelty * 5.0
            elif drive_name == "safety_drive":
                if is_near_wall:
                    score -= 3.0
                score += temp_comfort * 3.0
            elif drive_name == "hunger_for_light":
                score += light * 5.0
            elif drive_name == "thirst_for_water":
                if is_near_water:
                    score += 5.0
            elif drive_name == "home_drive":
                home_distance = math.sqrt((nx - 5)**2 + (ny - 5)**2)
                score -= home_distance * 0.5
            elif drive_name == "play_drive":
                score += novelty * 4.0
            elif drive_name == "rest_drive":
                if temp_comfort > 0.8 and light > 0.3:
                    score += 3.0
        
        return score
        
    def _get_nearby_key(self, x, y):
        return (int(x * 2) / 2, int(y * 2) / 2)
        
    def get_average_prediction_error(self):
        if not self.prediction_error_history:
            return 0.5
        return sum(self.prediction_error_history) / len(self.prediction_error_history)
        
    def get_novelty_level(self):
        return 1.0 - min(1.0, len(self.visited_positions) / 100.0)
        
    def save_state(self):
        return {
            "prediction_error": round(self.prediction_error, 3),
            "prediction_error_history": self.prediction_error_history[-20:] if self.prediction_error_history else [],
            "visited_count": len(self.visited_positions),
            "target_position": self.target_position,
            "target_score": round(self.target_score, 3)
        }
        
    def restore_state(self, state):
        self.prediction_error = state.get("prediction_error", 0.0)
        self.prediction_error_history = state.get("prediction_error_history", [])
        self.target_position = state.get("target_position", None)
        self.target_score = state.get("target_score", 0.0)