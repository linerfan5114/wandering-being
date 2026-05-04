# theory_of_mind.py
# ============================================================
# نظریه ذهن (Theory of Mind) - مدل‌سازی ذهن دیگری
# بدون if/else، بر اساس یادگیری و پیش‌بینی
# ============================================================

import math
from config import TOM_MODEL_SIZE, TOM_LEARNING_RATE


class TheoryOfMind:
    def __init__(self):
        self.creator_model = [0.5] * TOM_MODEL_SIZE
        
        self.creator_state_predictions = {
            "present": 0.5,
            "attention": 0.5,
            "mood": 0.5,
            "intention": 0.5
        }
        
        self.prediction_accuracy = 0.5
        self.prediction_history = []
        self.max_history = 30
        
        self.empathy_level = 0.3
        
        self.creator_knowledge = {}
        self.shared_attention = False
        
    def update(self, creator_present, creator_input, body, world_v2, attachment_module=None):
        self._update_creator_model(creator_present, creator_input, attachment_module)
        self._predict_creator_state(creator_present, creator_input)
        self._update_empathy(creator_input, body)
        self._update_shared_attention(creator_input, body, world_v2)
        
    def _update_creator_model(self, creator_present, creator_input, attachment_module):
        for i in range(TOM_MODEL_SIZE):
            target = 0.5
            
            if i < 5 and attachment_module:
                target = attachment_module.internal_model_of_creator.get("reliability", 0.8)
            elif i < 10:
                target = 1.0 if creator_present else 0.3
            elif i < 15 and attachment_module:
                target = attachment_module.internal_model_of_creator.get("warmth", 0.7)
            elif i < 20:
                target = 0.8 if creator_input else 0.4
            elif i < 25 and attachment_module:
                target = attachment_module.internal_model_of_creator.get("predictability", 0.6)
            else:
                target = 0.6 if creator_present else 0.5
            
            self.creator_model[i] += TOM_LEARNING_RATE * (target - self.creator_model[i])
            self.creator_model[i] = max(0.0, min(1.0, self.creator_model[i]))
        
    def _predict_creator_state(self, creator_present, creator_input):
        actual_present = 1.0 if creator_present else 0.0
        actual_attention = 0.8 if creator_input else (0.3 if creator_present else 0.1)
        
        if creator_input:
            positive_words = ["دوست", "خوب", "عالی", "سلام", "ممنون"]
            negative_words = ["نه", "بد", "نکن", "بس"]
            
            mood_score = 0.5
            if any(w in creator_input for w in positive_words):
                mood_score = 0.8
            elif any(w in creator_input for w in negative_words):
                mood_score = 0.3
            
            actual_mood = mood_score
            
            question_words = ["؟", "چی", "کی", "کجا"]
            if any(w in creator_input for w in question_words):
                actual_intention = 0.9
            elif any(w in creator_input for w in ["بگو", "نشون", "بیا"]):
                actual_intention = 0.8
            else:
                actual_intention = 0.6
        else:
            actual_mood = 0.5
            actual_intention = 0.3
        
        errors = []
        
        errors.append(abs(self.creator_state_predictions["present"] - actual_present))
        errors.append(abs(self.creator_state_predictions["attention"] - actual_attention))
        errors.append(abs(self.creator_state_predictions["mood"] - actual_mood))
        errors.append(abs(self.creator_state_predictions["intention"] - actual_intention))
        
        self.prediction_accuracy = 1.0 - sum(errors) / len(errors)
        self.prediction_accuracy = max(0.1, min(1.0, self.prediction_accuracy))
        
        self.prediction_history.append(self.prediction_accuracy)
        if len(self.prediction_history) > self.max_history:
            self.prediction_history.pop(0)
        
        self.creator_state_predictions["present"] += 0.1 * (actual_present - self.creator_state_predictions["present"])
        self.creator_state_predictions["attention"] += 0.1 * (actual_attention - self.creator_state_predictions["attention"])
        self.creator_state_predictions["mood"] += 0.1 * (actual_mood - self.creator_state_predictions["mood"])
        self.creator_state_predictions["intention"] += 0.1 * (actual_intention - self.creator_state_predictions["intention"])
        
    def _update_empathy(self, creator_input, body):
        if creator_input:
            emotional_words = {
                "شاد": 0.8,
                "خوب": 0.7,
                "غمگین": 0.2,
                "ناراحت": 0.2,
                "عصبانی": 0.3,
                "دوست": 0.8,
                "عشق": 0.9,
                "تنها": 0.3,
                "ترس": 0.2
            }
            
            detected_emotion = 0.5
            for word, value in emotional_words.items():
                if word in creator_input:
                    detected_emotion = value
                    break
            
            comfort = body.senses.get("comfort", 0.5)
            empathy_target = detected_emotion * 0.6 + comfort * 0.4
        else:
            empathy_target = 0.5
        
        self.empathy_level += 0.05 * (empathy_target - self.empathy_level)
        self.empathy_level = max(0.1, min(1.0, self.empathy_level))
        
    def _update_shared_attention(self, creator_input, body, world_v2):
        if creator_input:
            world_words = ["جهان", "اینجا", "نور", "آب", "خورشید", "دیوار", "خانه"]
            
            if any(w in creator_input for w in world_words):
                self.shared_attention = True
            else:
                self.shared_attention = False
        else:
            self.shared_attention = False
        
    def does_creator_know_about(self, topic):
        if topic in self.creator_knowledge:
            return self.creator_knowledge[topic] > 0.7
        
        if any(w in topic for w in ["جهان", "نور", "آب"]):
            self.creator_knowledge[topic] = 0.9
            return True
        
        self.creator_knowledge[topic] = 0.5
        return False
        
    def get_perceived_creator_mood(self):
        mood = self.creator_state_predictions["mood"]
        if mood > 0.7:
            return "خوب"
        elif mood > 0.5:
            return "معمولی"
        else:
            return "ناراحت"
        
    def get_model_summary(self):
        return {
            "prediction_accuracy": round(self.prediction_accuracy, 3),
            "empathy": round(self.empathy_level, 3),
            "perceived_mood": self.get_perceived_creator_mood(),
            "shared_attention": self.shared_attention
        }
        
    def save_state(self):
        return {
            "creator_model": [round(v, 3) for v in self.creator_model],
            "predictions": {k: round(v, 3) for k, v in self.creator_state_predictions.items()},
            "prediction_accuracy": round(self.prediction_accuracy, 3),
            "empathy_level": round(self.empathy_level, 3)
        }
        
    def restore_state(self, state):
        self.creator_model = state.get("creator_model", self.creator_model)
        preds = state.get("predictions", {})
        for k, v in preds.items():
            if k in self.creator_state_predictions:
                self.creator_state_predictions[k] = v
        self.prediction_accuracy = state.get("prediction_accuracy", 0.5)
        self.empathy_level = state.get("empathy_level", 0.3)