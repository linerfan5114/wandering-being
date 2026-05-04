# attachment.py
# ============================================================
# دلبستگی (Attachment) - پیوند عاطفی با سازنده
# بدون if/else، بر اساس حضور و غیاب
# ============================================================

import math
from config import ATTACHMENT_LEARNING_RATE, ATTACHMENT_SEPARATION_THRESHOLD, ATTACHMENT_REUNION_JOY


class Attachment:
    def __init__(self):
        self.attachment_strength = 0.3
        self.attachment_history = []
        self.max_history = 100
        
        self.presence_timer = 0
        self.absence_timer = 0
        
        self.separation_active = False
        self.separation_duration = 0
        
        self.reunion_joy = 0.0
        
        self.trust_level = 0.5
        
        self.internal_model_of_creator = {
            "reliability": 0.8,
            "warmth": 0.7,
            "predictability": 0.6,
            "permanence": 0.9
        }
        
    def update(self, creator_present, creator_input=None, world_time=0):
        if creator_present:
            self.presence_timer += 1
            self.absence_timer = 0
            
            if self.separation_active:
                self._handle_reunion(creator_input)
            else:
                self._update_presence(creator_input)
        else:
            self.absence_timer += 1
            self.presence_timer = max(0, self.presence_timer - 1)
            
            if self.absence_timer > ATTACHMENT_SEPARATION_THRESHOLD:
                self._handle_separation()
        
        self._update_internal_model(creator_present)
        self._update_trust(creator_present)
        
        self.attachment_history.append({
            "strength": self.attachment_strength,
            "presence": self.presence_timer,
            "absence": self.absence_timer,
            "separation": self.separation_active
        })
        if len(self.attachment_history) > self.max_history:
            self.attachment_history.pop(0)
        
    def _handle_reunion(self, creator_input):
        self.separation_active = False
        
        joy = ATTACHMENT_REUNION_JOY * (1.0 + self.separation_duration / ATTACHMENT_SEPARATION_THRESHOLD)
        self.reunion_joy = min(joy, 5.0)
        
        self.attachment_strength += self.reunion_joy * ATTACHMENT_LEARNING_RATE
        self.attachment_strength = max(0.1, min(1.0, self.attachment_strength))
        
        self.separation_duration = 0
        
        if creator_input:
            greeting_words = ["سلام", "برگشتم", "هستم", "اومدم"]
            if any(w in creator_input for w in greeting_words):
                self.attachment_strength += 0.05
                self.reunion_joy += 1.0
        
    def _handle_separation(self):
        if not self.separation_active:
            self.separation_active = True
            self.separation_duration = 0
        
        self.separation_duration += 1
        
        decay_rate = 0.0001 * (self.separation_duration / ATTACHMENT_SEPARATION_THRESHOLD)
        self.attachment_strength -= decay_rate
        self.attachment_strength = max(0.1, self.attachment_strength)
        
        self.reunion_joy *= 0.99
        
    def _update_presence(self, creator_input):
        self.attachment_strength += ATTACHMENT_LEARNING_RATE * 0.5
        self.attachment_strength = max(0.1, min(1.0, self.attachment_strength))
        
        if creator_input:
            positive_words = ["دوست", "عشق", "خوب", "عالی", "ممنون", "سلام"]
            if any(w in creator_input for w in positive_words):
                self.attachment_strength += ATTACHMENT_LEARNING_RATE * 2.0
                self.attachment_strength = min(1.0, self.attachment_strength)
        
    def _update_internal_model(self, creator_present):
        self.internal_model_of_creator["reliability"] += ATTACHMENT_LEARNING_RATE * (
            (1.0 if creator_present else 0.0) - self.internal_model_of_creator["reliability"]
        )
        
        predicted_presence = 0.5
        if len(self.attachment_history) > 10:
            presence_ratio = sum(1 for h in self.attachment_history[-10:] if h["presence"] > h["absence"]) / 10
            predicted_presence = presence_ratio
        
        self.internal_model_of_creator["predictability"] += ATTACHMENT_LEARNING_RATE * (
            predicted_presence - self.internal_model_of_creator["predictability"]
        )
        
        self.internal_model_of_creator["permanence"] = max(0.3, min(1.0, self.trust_level))
        
    def _update_trust(self, creator_present):
        if creator_present:
            target_trust = 1.0
        else:
            if self.absence_timer < ATTACHMENT_SEPARATION_THRESHOLD / 2:
                target_trust = 0.7
            else:
                target_trust = 0.3
        
        self.trust_level += 0.01 * (target_trust - self.trust_level)
        self.trust_level = max(0.1, min(1.0, self.trust_level))
        
    def get_attachment_signal(self):
        base = self.attachment_strength * 2.0
        
        if self.separation_active:
            base += self.separation_duration * 0.01
        
        base += self.reunion_joy * 0.5
        
        return base
        
    def is_separated(self):
        return self.separation_active
        
    def get_reunion_message(self):
        if self.reunion_joy > 3.0:
            return "برگشتی! خیلی خوشحالم!"
        elif self.reunion_joy > 1.5:
            return "برگشتی. دلم برات تنگ شده بود."
        elif self.reunion_joy > 0.5:
            return "اومدی."
        else:
            return None
        
    def save_state(self):
        return {
            "attachment_strength": round(self.attachment_strength, 3),
            "trust_level": round(self.trust_level, 3),
            "separation_active": self.separation_active,
            "separation_duration": self.separation_duration,
            "reunion_joy": round(self.reunion_joy, 3),
            "internal_model": {k: round(v, 3) for k, v in self.internal_model_of_creator.items()}
        }
        
    def restore_state(self, state):
        self.attachment_strength = state.get("attachment_strength", 0.3)
        self.trust_level = state.get("trust_level", 0.5)
        self.separation_active = state.get("separation_active", False)
        self.separation_duration = state.get("separation_duration", 0)
        self.reunion_joy = state.get("reunion_joy", 0.0)
        model = state.get("internal_model", {})
        for k, v in model.items():
            if k in self.internal_model_of_creator:
                self.internal_model_of_creator[k] = v