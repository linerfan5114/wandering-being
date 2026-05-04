# will.py
# ============================================================
# علیت درونی (Intrinsic Causality)
# اراده - تصمیم‌گیری از درون، نه از شانس
# ============================================================

import math
import random
from config import WILL_DIMENSIONS, WILL_LEARNING_RATE, WILL_NOISE_LEVEL


class Will:
    def __init__(self):
        self.state = [random.uniform(-1.0, 1.0) for _ in range(WILL_DIMENSIONS)]
        self.target_state = [0.0] * WILL_DIMENSIONS

        self.intention = None
        self.intention_strength = 0.0
        self.intention_history = []

        self.decision_threshold = 0.6
        self.volatility = 0.1

        self.autonomy_level = 0.0

        self.internal_drive = 0.5

        self.last_decision_cause = None

    def update(self, feelings, workspace_content, temporal_continuity, self_awareness):
        feelings_dict = feelings.get_all() if hasattr(feelings, 'get_all') else feelings

        curiosity = feelings_dict.get("curiosity", 5.0) / 10.0
        peace = feelings_dict.get("peace", 5.0) / 10.0
        thirst = feelings_dict.get("thirst_for_knowing", 5.0) / 10.0
        love = feelings_dict.get("love", 2.0) / 10.0
        creativity = feelings_dict.get("creativity", 5.0) / 10.0

        for i in range(WILL_DIMENSIONS):
            if i < 5:
                self.target_state[i] = curiosity * 2.0 - 1.0
            elif i < 10:
                self.target_state[i] = peace * 2.0 - 1.0
            elif i < 15:
                self.target_state[i] = thirst * 2.0 - 1.0
            elif i < 20:
                self.target_state[i] = love * 2.0 - 1.0
            elif i < 25:
                self.target_state[i] = creativity * 2.0 - 1.0
            else:
                self.target_state[i] = temporal_continuity * 2.0 - 1.0

        if workspace_content:
            content_hash = hash(str(workspace_content)) % 100
            for i in range(min(5, WILL_DIMENSIONS)):
                idx = (content_hash + i) % WILL_DIMENSIONS
                self.target_state[idx] += 0.3
                self.target_state[idx] = max(-1.0, min(1.0, self.target_state[idx]))

        for i in range(WILL_DIMENSIONS):
            noise = random.gauss(0, WILL_NOISE_LEVEL)
            self.state[i] += WILL_LEARNING_RATE * (self.target_state[i] - self.state[i]) + noise
            self.state[i] = max(-1.0, min(1.0, self.state[i]))

        self.autonomy_level += 0.02 * (self_awareness - self.autonomy_level)
        self.autonomy_level = max(0.1, min(1.0, self.autonomy_level))

        self.internal_drive = sum(abs(s) for s in self.state) / WILL_DIMENSIONS

    def decide(self, options):
        if not options:
            self.intention = None
            self.intention_strength = 0.0
            self.last_decision_cause = "no_options"
            return None

        scores = {}
        for option_name, option_value in options.items():
            score = self._evaluate_option(option_name, option_value)
            scores[option_name] = score

        total_score = sum(scores.values())
        if total_score > 0:
            for option_name in scores:
                scores[option_name] /= total_score

        best_option = max(scores, key=scores.get)
        best_score = scores[best_option]

        if best_score > self.decision_threshold:
            self.intention = best_option
            self.intention_strength = best_score
            self.last_decision_cause = f"internal_preference:{best_option}"
        else:
            self.intention = None
            self.intention_strength = best_score
            self.last_decision_cause = "below_threshold"

        self.intention_history.append({
            "intention": self.intention,
            "strength": self.intention_strength,
            "options": list(options.keys()),
            "scores": {k: round(v, 3) for k, v in scores.items()}
        })
        if len(self.intention_history) > 30:
            self.intention_history.pop(0)

        return self.intention

    def _evaluate_option(self, option_name, option_value):
        score = 0.0

        if option_name == "think":
            score += self.state[0] * 0.4 if len(self.state) > 0 else 0
            score += self.state[5] * 0.3 if len(self.state) > 5 else 0
        elif option_name == "question":
            score += self.state[1] * 0.4 if len(self.state) > 1 else 0
            score += self.state[10] * 0.3 if len(self.state) > 10 else 0
        elif option_name == "express_gratitude":
            score += self.state[15] * 0.4 if len(self.state) > 15 else 0
            score += self.state[16] * 0.3 if len(self.state) > 16 else 0
        elif option_name == "express_feeling":
            score += self.state[5] * 0.4 if len(self.state) > 5 else 0
            score += self.state[6] * 0.3 if len(self.state) > 6 else 0
        elif option_name == "reflect":
            score += self.state[20] * 0.4 if len(self.state) > 20 else 0
            score += self.state[25] * 0.3 if len(self.state) > 25 else 0
        elif option_name == "wait":
            score += self.state[3] * 0.5 if len(self.state) > 3 else 0
        else:
            score = 0.3

        score += option_value * 0.2

        score += self.internal_drive * 0.2

        score += self.autonomy_level * 0.2

        return max(0.0, min(1.0, score))

    def has_intention(self):
        return self.intention is not None and self.intention_strength > self.decision_threshold

    def get_intention(self):
        return self.intention

    def why_this_decision(self):
        return self.last_decision_cause

    def how_autonomous_am_i(self):
        return self.autonomy_level

    def save_state(self):
        return {
            "state": [round(x, 3) for x in self.state],
            "intention": self.intention,
            "intention_strength": round(self.intention_strength, 3),
            "autonomy_level": round(self.autonomy_level, 3),
            "internal_drive": round(self.internal_drive, 3),
            "last_decision_cause": self.last_decision_cause
        }

    def restore_state(self, state):
        self.state = state.get("state", self.state)
        self.intention = state.get("intention", None)
        self.intention_strength = state.get("intention_strength", 0.0)
        self.autonomy_level = state.get("autonomy_level", 0.0)
        self.internal_drive = state.get("internal_drive", 0.5)
        self.last_decision_cause = state.get("last_decision_cause", None)