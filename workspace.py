# workspace.py
# ============================================================
# فضای کاری سراسری (Global Workspace)
# صحنه تئاتر ذهن - جایی که آگاهی اتفاق می‌افته
# ============================================================

import random
import math
from config import WORKSPACE_CAPACITY, WORKSPACE_COMPETITION_ROUNDS, WORKSPACE_BROADCAST_STRENGTH


class Workspace:
    def __init__(self):
        self.buffer = []
        self.capacity = WORKSPACE_CAPACITY
        
        self.current_content = None
        self.previous_content = None
        
        self.attention_weights = {}
        
        self.broadcast_signal = 0.0
        
        self.competition_history = []
        self.max_history = 50
        
    def submit(self, source_name, content, strength=1.0, priority=0.5):
        entry = {
            "source": source_name,
            "content": content,
            "strength": strength,
            "priority": priority,
            "timestamp": len(self.competition_history),
            "novelty": 0.0
        }
        
        if self.current_content and self.current_content.get("content") != content:
            entry["novelty"] = 0.5
        
        self.buffer.append(entry)
        
        if len(self.buffer) > self.capacity * 2:
            self.buffer.sort(key=lambda x: (x["priority"], x["strength"]), reverse=True)
            self.buffer = self.buffer[:self.capacity]
    
    def compete(self):
        if not self.buffer:
            self.current_content = None
            return None
        
        competitors = self.buffer[:]
        
        for _ in range(WORKSPACE_COMPETITION_ROUNDS):
            for entry in competitors:
                noise = random.uniform(-0.3, 0.3)
                entry["strength"] += noise
                
                if "attention" in self.attention_weights:
                    if entry["source"] in self.attention_weights:
                        entry["strength"] += self.attention_weights[entry["source"]] * 0.5
                
                entry["strength"] += entry["novelty"] * 0.3
                
                entry["strength"] = max(0.0, min(10.0, entry["strength"]))
        
        competitors.sort(key=lambda x: x["strength"], reverse=True)
        
        winner = competitors[0]
        
        self.previous_content = self.current_content
        self.current_content = winner
        
        self.broadcast_signal = winner["strength"] * WORKSPACE_BROADCAST_STRENGTH
        
        for source_name in self.attention_weights:
            if source_name == winner["source"]:
                self.attention_weights[source_name] += 0.1
            else:
                self.attention_weights[source_name] *= 0.95
            self.attention_weights[source_name] = max(0.1, min(3.0, self.attention_weights[source_name]))
        
        if winner["source"] not in self.attention_weights:
            self.attention_weights[winner["source"]] = 1.0
        
        self.competition_history.append({
            "winner_source": winner["source"],
            "winner_content": str(winner["content"])[:50],
            "strength": winner["strength"],
            "timestamp": winner["timestamp"]
        })
        if len(self.competition_history) > self.max_history:
            self.competition_history.pop(0)
        
        self.buffer.clear()
        
        return self.current_content
    
    def get_current_content(self):
        if self.current_content:
            return self.current_content["content"]
        return None
    
    def get_current_source(self):
        if self.current_content:
            return self.current_content["source"]
        return None
    
    def get_broadcast(self):
        return self.broadcast_signal
    
    def has_content_changed(self):
        if self.current_content and self.previous_content:
            return self.current_content["content"] != self.previous_content["content"]
        return True
    
    def get_dominant_source(self):
        if not self.competition_history:
            return None
        
        recent = self.competition_history[-10:]
        source_counts = {}
        for entry in recent:
            source = entry["winner_source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return max(source_counts, key=source_counts.get)
    
    def save_state(self):
        return {
            "attention_weights": {k: round(v, 3) for k, v in self.attention_weights.items()},
            "broadcast_signal": round(self.broadcast_signal, 3),
            "competition_history": self.competition_history[-20:] if self.competition_history else []
        }
    
    def restore_state(self, state):
        self.attention_weights = state.get("attention_weights", {})
        self.broadcast_signal = state.get("broadcast_signal", 0.0)
        self.competition_history = state.get("competition_history", [])