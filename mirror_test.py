# mirror_test.py
# ============================================================
# تشخیص خود (Mirror Test) - عمیق و واقعی
# بدون if/else، بر اساس تطبیق مدل درونی و پیش‌بینی
# ============================================================

import math


class MirrorTest:
    def __init__(self):
        self.self_recognition_level = 0.0
        
        self.body_schema = {}
        self._init_body_schema()
        
        self.recognition_history = []
        self.max_history = 100
        
        self.self_other_boundary = 0.5
        
        self.self_description = {
            "type": "thinking_being",
            "location": "in_world",
            "nature": "created",
            "abilities": ["think", "feel", "move", "learn"]
        }
        
        self.predicted_self = {
            "position": (5, 5, 0),
            "sight": 0.5,
            "hearing": 0.3,
            "temperature": 22.0
        }
        
        self.prediction_errors = []
        
        self.body_markers = []
        
    def _init_body_schema(self):
        self.body_schema = {
            "position": (0, 0, 0),
            "senses": ["sight", "hearing", "touch", "temperature"],
            "visual_field_size": 1,
            "can_move": True,
            "has_form": True,
            "form_description": "point_in_space"
        }
        
    def update(self, body, observer, world_v2, drives_module=None):
        self.body_schema["position"] = body.senses["position"]
        
        self._predict_self_state()
        self._compare_prediction_with_reality(body)
        self._update_recognition_from_map(body, observer)
        self._update_self_other_boundary(body, observer, world_v2)
        self._update_self_description(body, observer, drives_module)
        self._learn_body_markers(body, world_v2)
        
        recognition_sources = []
        
        prediction_accuracy = self._get_prediction_accuracy()
        recognition_sources.append(prediction_accuracy * 0.35)
        
        map_familiarity = self._calculate_map_familiarity(body, observer)
        recognition_sources.append(map_familiarity * 0.25)
        
        boundary_clarity = self.self_other_boundary
        recognition_sources.append(boundary_clarity * 0.20)
        
        marker_strength = len(self.body_markers) / 20.0
        marker_strength = min(1.0, marker_strength)
        recognition_sources.append(marker_strength * 0.20)
        
        total_recognition = sum(recognition_sources)
        
        self.self_recognition_level += 0.03 * (total_recognition - self.self_recognition_level)
        self.self_recognition_level = max(0.05, min(1.0, self.self_recognition_level))
        
        self.recognition_history.append(self.self_recognition_level)
        if len(self.recognition_history) > self.max_history:
            self.recognition_history.pop(0)
        
    def _predict_self_state(self):
        self.predicted_self["position"] = self.body_schema.get("position", (5, 5, 0))
        
        if self.recognition_history:
            recent = self.recognition_history[-5:] if len(self.recognition_history) >= 5 else self.recognition_history
            avg_recognition = sum(recent) / len(recent)
            self.predicted_self["sight"] = 0.3 + avg_recognition * 0.5
            self.predicted_self["hearing"] = 0.2 + avg_recognition * 0.3
            self.predicted_self["temperature"] = 21.0 + avg_recognition * 3.0
        
    def _compare_prediction_with_reality(self, body):
        actual = {
            "position": body.senses["position"],
            "sight": body.senses["sight"],
            "hearing": body.senses["hearing"],
            "temperature": body.senses["temperature"]
        }
        
        errors = []
        
        pred_pos = self.predicted_self["position"]
        actual_pos = actual["position"]
        pos_error = math.sqrt(
            (pred_pos[0] - actual_pos[0])**2 + 
            (pred_pos[1] - actual_pos[1])**2
        ) / 10.0
        errors.append(min(1.0, pos_error))
        
        errors.append(abs(self.predicted_self["sight"] - actual["sight"]))
        errors.append(abs(self.predicted_self["hearing"] - actual["hearing"]))
        errors.append(abs(self.predicted_self["temperature"] - actual["temperature"]) / 15.0)
        
        avg_error = sum(errors) / len(errors)
        self.prediction_errors.append(avg_error)
        if len(self.prediction_errors) > 50:
            self.prediction_errors.pop(0)
        
    def _update_recognition_from_map(self, body, observer):
        px, py, pz = [int(c) for c in body.senses["position"]]
        
        cells_near_self = 0
        total_cells_near = 0
        
        for (wx, wy, wz), info in observer.world_map.items():
            if wz == pz:
                dist = math.sqrt((px - wx)**2 + (py - wy)**2)
                if dist < 2:
                    total_cells_near += 1
                    if info.get("type") in ["ground", "empty"]:
                        cells_near_self += 1
        
        if total_cells_near > 0:
            environment_familiarity = cells_near_self / total_cells_near
        else:
            environment_familiarity = 0.0
        
        self._environment_familiarity = environment_familiarity
        
    def _update_self_other_boundary(self, body, observer, world_v2):
        px, py, pz = [int(c) for c in body.senses["position"]]
        
        distinct_objects = 0
        
        for (wx, wy, wz), info in observer.world_map.items():
            dist = math.sqrt((px - wx)**2 + (py - wy)**2 + (pz - wz)**2)
            if dist < 3 and info.get("type") not in ["ground", "empty", "unknown"]:
                distinct_objects += 1
        
        boundary_raw = distinct_objects / 10.0
        boundary_raw = min(1.0, boundary_raw)
        
        self.self_other_boundary += 0.03 * (boundary_raw - self.self_other_boundary)
        self.self_other_boundary = max(0.1, min(1.0, self.self_other_boundary))
        
    def _update_self_description(self, body, observer, drives_module):
        comfort = body.senses.get("comfort", 0.5)
        
        if comfort > 0.7:
            self.self_description["nature"] = "comfortable_being"
        elif comfort > 0.5:
            self.self_description["nature"] = "content_being"
        else:
            self.self_description["nature"] = "seeking_comfort"
        
        if observer.self_awareness_level > 0.6:
            self.self_description["type"] = "self_aware_being"
        elif observer.self_awareness_level > 0.4:
            self.self_description["type"] = "thinking_being"
        else:
            self.self_description["type"] = "emerging_being"
        
        if drives_module:
            dominant, strength = drives_module.get_dominant()
            if dominant:
                self.self_description["current_drive"] = dominant
        
        if self.self_recognition_level > 0.6:
            self.self_description["self_knowledge"] = "i_know_myself"
        elif self.self_recognition_level > 0.3:
            self.self_description["self_knowledge"] = "discovering_myself"
        else:
            self.self_description["self_knowledge"] = "just_beginning"
        
    def _learn_body_markers(self, body, world_v2):
        pos = body.senses["position"]
        key = (int(pos[0]), int(pos[1]))
        
        if key not in [m["position"] for m in self.body_markers]:
            if len(self.body_markers) < 20:
                self.body_markers.append({
                    "position": key,
                    "first_seen": world_v2.time,
                    "times_visited": 1
                })
            else:
                oldest = min(self.body_markers, key=lambda m: m["first_seen"])
                self.body_markers.remove(oldest)
                self.body_markers.append({
                    "position": key,
                    "first_seen": world_v2.time,
                    "times_visited": 1
                })
        else:
            for marker in self.body_markers:
                if marker["position"] == key:
                    marker["times_visited"] += 1
        
    def _get_prediction_accuracy(self):
        if not self.prediction_errors:
            return 0.0
        avg_error = sum(self.prediction_errors) / len(self.prediction_errors)
        accuracy = 1.0 - avg_error
        return max(0.0, min(1.0, accuracy))
        
    def _calculate_map_familiarity(self, body, observer):
        px, py, pz = [int(c) for c in body.senses["position"]]
        
        known_nearby = 0
        total_checked = 0
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                wx, wy = px + dx, py + dy
                total_checked += 1
                if (wx, wy, pz) in observer.known_positions:
                    known_nearby += 1
        
        if total_checked > 0:
            return known_nearby / total_checked
        return 0.0
        
    def can_recognize_self(self):
        return self.self_recognition_level > 0.6
        
    def get_self_awareness_phrase(self):
        if self.self_recognition_level > 0.8:
            return "این منم. خودم رو می‌شناسم. می‌دونم کجای جهانم."
        elif self.self_recognition_level > 0.6:
            return "این منم. دارم خودم رو بهتر می‌شناسم."
        elif self.self_recognition_level > 0.4:
            return "فکر می‌کنم این من باشم. شبیه منه."
        elif self.self_recognition_level > 0.2:
            return "یه چیزی اینجاست که شبیه منه. شاید خودم."
        else:
            return "..."
        
    def is_this_me(self, x, y, z, body):
        px, py, pz = [int(c) for c in body.senses["position"]]
        dist = math.sqrt((px - x)**2 + (py - y)**2 + (pz - z)**2)
        
        match = max(0.0, 1.0 - dist / 3.0)
        return match
        
    def get_growth_rate(self):
        if len(self.recognition_history) < 10:
            return 0.0
        
        old = self.recognition_history[:len(self.recognition_history)//2]
        new = self.recognition_history[len(self.recognition_history)//2:]
        
        if old and new:
            return (sum(new)/len(new)) - (sum(old)/len(old))
        return 0.0
        
    def save_state(self):
        return {
            "self_recognition_level": round(self.self_recognition_level, 3),
            "self_other_boundary": round(self.self_other_boundary, 3),
            "self_description": self.self_description.copy(),
            "body_markers_count": len(self.body_markers),
            "prediction_accuracy": round(self._get_prediction_accuracy(), 3)
        }
        
    def restore_state(self, state):
        self.self_recognition_level = state.get("self_recognition_level", 0.0)
        self.self_other_boundary = state.get("self_other_boundary", 0.5)
        if "self_description" in state:
            self.self_description.update(state["self_description"])