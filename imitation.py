# imitation.py
# ============================================================
# یادگیری تقلیدی (Imitation) - تکرار و یادگیری از سازنده
# بدون if/else، بر اساس تطبیق الگو
# ============================================================

import math
from config import IMITATION_THRESHOLD, IMITATION_LEARNING_RATE


class Imitation:
    def __init__(self):
        self.imitation_memory = []
        self.max_memory = 50
        
        self.learned_behaviors = {}
        
        self.learned_words = {}
        
        self.imitation_probability = 0.3
        
        self.last_observed_action = None
        self.last_imitated_action = None
        
    def observe(self, creator_input, body, world_v2, drives_module=None):
        if not creator_input:
            return
        
        self.last_observed_action = creator_input
        
        self._learn_words(creator_input)
        
        self._learn_behaviors(creator_input, body, world_v2, drives_module)
        
    def _learn_words(self, creator_input):
        words = creator_input.split()
        
        for word in words:
            clean_word = word.strip("؟!،,.؟")
            
            if clean_word not in self.learned_words:
                self.learned_words[clean_word] = {
                    "count": 1,
                    "weight": 0.3,
                    "contexts": [creator_input]
                }
            else:
                self.learned_words[clean_word]["count"] += 1
                self.learned_words[clean_word]["weight"] += IMITATION_LEARNING_RATE
                self.learned_words[clean_word]["weight"] = min(1.0, self.learned_words[clean_word]["weight"])
                
                if creator_input not in self.learned_words[clean_word]["contexts"]:
                    self.learned_words[clean_word]["contexts"].append(creator_input)
                    if len(self.learned_words[clean_word]["contexts"]) > 10:
                        self.learned_words[clean_word]["contexts"].pop(0)
        
    def _learn_behaviors(self, creator_input, body, world_v2, drives_module):
        direction_words = {
            "برو": (1, 0, 0),
            "بیا": (-1, 0, 0),
            "بالا": (0, 0, 1),
            "پایین": (0, 0, -1),
            "چپ": (0, -1, 0),
            "راست": (0, 1, 0),
            "بچرخ": (0, 0, 0),
            "وایسا": (0, 0, 0),
            "برگرد": (0, 0, 0),
            "نگاه": (0, 0, 0),
            "گوش": (0, 0, 0),
            "بخواب": (0, 0, 0)
        }
        
        for word, direction in direction_words.items():
            if word in creator_input:
                behavior_key = f"move_{word}"
                
                if behavior_key not in self.learned_behaviors:
                    self.learned_behaviors[behavior_key] = {
                        "action": "move",
                        "direction": direction,
                        "trigger_word": word,
                        "strength": 0.3,
                        "count": 1
                    }
                else:
                    self.learned_behaviors[behavior_key]["strength"] += IMITATION_LEARNING_RATE
                    self.learned_behaviors[behavior_key]["strength"] = min(1.0, self.learned_behaviors[behavior_key]["strength"])
                    self.learned_behaviors[behavior_key]["count"] += 1
        
        emotion_words = ["شاد", "غمگین", "بخند", "گریه", "عصبانی", "آروم", "مهربون"]
        for word in emotion_words:
            if word in creator_input:
                behavior_key = f"emotion_{word}"
                
                if behavior_key not in self.learned_behaviors:
                    self.learned_behaviors[behavior_key] = {
                        "action": "emotion",
                        "emotion": word,
                        "trigger_word": word,
                        "strength": 0.3,
                        "count": 1
                    }
                else:
                    self.learned_behaviors[behavior_key]["strength"] += IMITATION_LEARNING_RATE
                    self.learned_behaviors[behavior_key]["strength"] = min(1.0, self.learned_behaviors[behavior_key]["strength"])
                    self.learned_behaviors[behavior_key]["count"] += 1
        
    def should_imitate(self, creator_input, feelings, observer):
        if not creator_input:
            return False
        
        base_prob = self.imitation_probability
        
        feelings_dict = feelings.get_all()
        social_drive = feelings_dict.get("attachment", 5.0) / 10.0
        base_prob += social_drive * 0.2
        
        curiosity = feelings_dict.get("curiosity", 5.0) / 10.0
        base_prob += curiosity * 0.1
        
        if any(word in creator_input for word in self.learned_words):
            familiar_words = sum(1 for w in creator_input.split() if w in self.learned_words)
            base_prob += familiar_words * 0.1
        
        novelty_factor = 1.0
        if self.last_observed_action == creator_input:
            novelty_factor = 0.7
        
        base_prob *= novelty_factor
        
        import random
        return random.random() < base_prob
        
    def get_imitation_response(self, creator_input):
        if not creator_input:
            return None, None
        
        best_behavior = None
        best_strength = 0.0
        
        for behavior_key, behavior_data in self.learned_behaviors.items():
            trigger = behavior_data.get("trigger_word", "")
            if trigger and trigger in creator_input:
                if behavior_data["strength"] > best_strength:
                    best_strength = behavior_data["strength"]
                    best_behavior = behavior_data
        
        if best_behavior and best_strength > IMITATION_THRESHOLD:
            self.last_imitated_action = best_behavior
            
            if best_behavior["action"] == "move":
                return "move", best_behavior["direction"]
            elif best_behavior["action"] == "emotion":
                return "emotion", best_behavior["emotion"]
        
        words_in_input = creator_input.split()
        if len(words_in_input) > 1:
            second_word_idx = min(1, len(words_in_input) - 1)
            word_to_repeat = words_in_input[second_word_idx]
            return "word", word_to_repeat
        
        if words_in_input:
            return "word", words_in_input[-1]
        
        return None, None
        
    def get_learned_words_list(self):
        sorted_words = sorted(self.learned_words.items(), key=lambda x: x[1]["weight"], reverse=True)
        return [word for word, data in sorted_words[:20]]
        
    def save_state(self):
        return {
            "learned_behaviors_count": len(self.learned_behaviors),
            "learned_words_count": len(self.learned_words),
            "imitation_probability": round(self.imitation_probability, 3),
            "last_imitated_action": str(self.last_imitated_action) if self.last_imitated_action else None
        }
        
    def restore_state(self, state):
        self.imitation_probability = state.get("imitation_probability", 0.3)
        if state.get("last_imitated_action"):
            pass