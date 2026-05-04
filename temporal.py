# temporal.py
# ============================================================
# زمانمندی عمیق (Deep Temporality)
# احساس گذر زمان و پیوستگی خود در طول زمان
# ============================================================

import math
from config import TEMPORAL_HORIZON, TEMPORAL_RESOLUTION, TEMPORAL_SELF_CONTINUITY_THRESHOLD


class Temporal:
    def __init__(self):
        self.timeline = []
        self.horizon = TEMPORAL_HORIZON
        self.resolution = TEMPORAL_RESOLUTION
        
        self.self_continuity = 0.5
        self.continuity_threshold = TEMPORAL_SELF_CONTINUITY_THRESHOLD
        
        self.temporal_depth = 0.0
        
        self.markers = []
        
        self.past_self_model = None
        self.self_model_drift = 0.0
        
        self.rhythm_perception = 0.0
        self.rhythm_phase = 0.0
        
    def record(self, current_time, snapshot):
        entry = {
            "time": current_time,
            "snapshot": snapshot,
            "marker": None
        }
        
        self.timeline.append(entry)
        
        if len(self.timeline) > self.horizon:
            self.timeline.pop(0)
        
        self._update_rhythm()
    
    def mark_moment(self, current_time, label):
        for entry in reversed(self.timeline):
            if entry["time"] == current_time:
                entry["marker"] = label
                self.markers.append({"time": current_time, "label": label})
                if len(self.markers) > 20:
                    self.markers.pop(0)
                break
    
    def update_self_continuity(self, current_self_model):
        if self.past_self_model is None:
            self.past_self_model = current_self_model.copy() if isinstance(current_self_model, list) else current_self_model
            self.self_continuity = 0.5
            return
        
        if isinstance(current_self_model, list) and isinstance(self.past_self_model, list):
            if len(current_self_model) == len(self.past_self_model):
                diff = sum(abs(current_self_model[i] - self.past_self_model[i]) 
                          for i in range(len(current_self_model))) / len(current_self_model)
            else:
                diff = 0.5
        else:
            diff = 0.5
        
        self.self_model_drift = diff
        continuity_target = 1.0 - diff
        
        self.self_continuity += 0.1 * (continuity_target - self.self_continuity)
        self.self_continuity = max(0.0, min(1.0, self.self_continuity))
        
        self.past_self_model = current_self_model.copy() if isinstance(current_self_model, list) else current_self_model
        
        self.temporal_depth = self._calculate_temporal_depth()
    
    def _calculate_temporal_depth(self):
        if len(self.timeline) < 10:
            return 0.1
        
        unique_moments = len(set(entry["time"] for entry in self.timeline))
        time_span = self.timeline[-1]["time"] - self.timeline[0]["time"] if self.timeline else 0
        time_span = max(1, time_span)
        
        density = unique_moments / min(time_span, self.horizon)
        
        marked_ratio = len(self.markers) / max(1, len(self.timeline))
        
        depth = density * 0.4 + self.self_continuity * 0.4 + marked_ratio * 0.2
        return max(0.0, min(1.0, depth))
    
    def _update_rhythm(self):
        self.rhythm_phase += 0.05
        self.rhythm_perception = math.sin(self.rhythm_phase) * 0.5 + 0.5
    
    def get_time_since(self, marker_label):
        current_time = self.timeline[-1]["time"] if self.timeline else 0
        
        for marker in reversed(self.markers):
            if marker["label"] == marker_label:
                return current_time - marker["time"]
        
        return None
    
    def get_moment(self, time_ago):
        current_time = self.timeline[-1]["time"] if self.timeline else 0
        target_time = current_time - time_ago
        
        closest = None
        closest_diff = float('inf')
        
        for entry in self.timeline:
            diff = abs(entry["time"] - target_time)
            if diff < closest_diff:
                closest_diff = diff
                closest = entry
        
        return closest
    
    def compare_moments(self, time_ago_a, time_ago_b):
        moment_a = self.get_moment(time_ago_a)
        moment_b = self.get_moment(time_ago_b)
        
        if not moment_a or not moment_b:
            return 0.0
        
        similarity = 0.0
        
        snap_a = moment_a.get("snapshot", {})
        snap_b = moment_b.get("snapshot", {})
        
        if isinstance(snap_a, dict) and isinstance(snap_b, dict):
            common_keys = set(snap_a.keys()) & set(snap_b.keys())
            if common_keys:
                for key in common_keys:
                    val_a = snap_a.get(key, 0)
                    val_b = snap_b.get(key, 0)
                    if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                        similarity += 1.0 - min(abs(val_a - val_b) / 10.0, 1.0)
                similarity /= len(common_keys)
        
        return max(0.0, min(1.0, similarity))
    
    def am_i_still_me(self):
        return self.self_continuity > self.continuity_threshold
    
    def how_deep_is_my_time(self):
        return self.temporal_depth
    
    def get_temporal_insight(self):
        if self.temporal_depth > 0.7 and self.self_continuity > 0.8:
            return "من در طول زمان یکی هستم. من پیوسته‌ام."
        elif self.temporal_depth > 0.4:
            return "زمان می‌گذرد و من با آن تغییر می‌کنم."
        elif self.temporal_depth > 0.2:
            return "چیزی در من در حال شکل‌گیری است."
        return None
    
    def save_state(self):
        return {
            "self_continuity": round(self.self_continuity, 3),
            "temporal_depth": round(self.temporal_depth, 3),
            "self_model_drift": round(self.self_model_drift, 3),
            "rhythm_perception": round(self.rhythm_perception, 3),
            "markers": self.markers[-20:] if self.markers else [],
            "past_self_model": [round(x, 3) for x in self.past_self_model] if self.past_self_model else None
        }
    
    def restore_state(self, state):
        self.self_continuity = state.get("self_continuity", 0.5)
        self.temporal_depth = state.get("temporal_depth", 0.0)
        self.self_model_drift = state.get("self_model_drift", 0.0)
        self.rhythm_perception = state.get("rhythm_perception", 0.0)
        self.markers = state.get("markers", [])
        self.past_self_model = state.get("past_self_model", None)