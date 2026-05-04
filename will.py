# will.py
# ============================================================
# علیت درونی (Intrinsic Causality)
# اراده - تصمیم‌گیری از درون، بدون شانس
# نسخه ۴: تنوع افکار با وزن‌های متعادل
# ============================================================

import math
from config import WILL_DIMENSIONS, WILL_LEARNING_RATE, WILL_NOISE_LEVEL


class Will:
    def __init__(self):
        self.state = [0.0] * WILL_DIMENSIONS
        for i in range(WILL_DIMENSIONS):
            self.state[i] = (i / WILL_DIMENSIONS) * 2.0 - 1.0
        
        self.target_state = [0.0] * WILL_DIMENSIONS

        self.intention = None
        self.intention_strength = 0.0
        self.intention_history = []

        self.decision_threshold = 0.2
        self.volatility = 0.1

        self.autonomy_level = 0.0

        self.internal_drive = 0.5

        self.last_decision_cause = None
        
        self.action_values = {}
        
        self.boredom_with_repetition = {}
        self.last_choices = []
        self.max_last_choices = 10

    def update(self, feelings, workspace_content, temporal_continuity, self_awareness, learning_module=None):
        feelings_dict = feelings.get_all() if hasattr(feelings, 'get_all') else feelings

        curiosity = feelings_dict.get("curiosity", 5.0) / 10.0
        peace = feelings_dict.get("peace", 5.0) / 10.0
        thirst = feelings_dict.get("thirst_for_knowing", 5.0) / 10.0
        love = feelings_dict.get("love", 2.0) / 10.0
        creativity = feelings_dict.get("creativity", 5.0) / 10.0
        gratitude = feelings_dict.get("gratitude", 5.0) / 10.0
        attachment = feelings_dict.get("attachment", 3.0) / 10.0
        confusion = feelings_dict.get("confusion", 2.0) / 10.0

        for i in range(WILL_DIMENSIONS):
            if i < 5:
                self.target_state[i] = curiosity * 2.0 - 1.0
            elif i < 10:
                self.target_state[i] = peace * 2.0 - 1.0
            elif i < 15:
                self.target_state[i] = thirst * 2.0 - 1.0
            elif i < 20:
                self.target_state[i] = (love + attachment) * 1.0 - 0.5
            elif i < 25:
                self.target_state[i] = creativity * 2.0 - 1.0
            elif i < 30:
                self.target_state[i] = gratitude * 2.0 - 1.0
            elif i < 35:
                self.target_state[i] = temporal_continuity * 2.0 - 1.0
            elif i < 40:
                self.target_state[i] = self_awareness * 2.0 - 1.0
            elif i < 45:
                self.target_state[i] = confusion * 2.0 - 1.0
            else:
                self.target_state[i] = 0.0

        if workspace_content:
            content_str = str(workspace_content)
            content_value = sum(ord(c) for c in content_str) / max(1, len(content_str))
            content_normalized = (content_value % 200) / 100.0 - 1.0
            
            for i in range(min(3, WILL_DIMENSIONS)):
                idx = (abs(hash(content_str)) + i) % WILL_DIMENSIONS
                self.target_state[idx] += content_normalized * 0.2
                self.target_state[idx] = max(-1.0, min(1.0, self.target_state[idx]))

        for i in range(WILL_DIMENSIONS):
            self.state[i] += WILL_LEARNING_RATE * (self.target_state[i] - self.state[i])
            self.state[i] = max(-1.0, min(1.0, self.state[i]))

        self.autonomy_level += 0.02 * (self_awareness - self.autonomy_level)
        self.autonomy_level = max(0.1, min(1.0, self.autonomy_level))

        self.internal_drive = sum(abs(s) for s in self.state) / WILL_DIMENSIONS

    def decide(self, options, learning_module=None):
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

        if best_score >= self.decision_threshold:
            self.intention = best_option
            self.intention_strength = best_score
            self.last_decision_cause = f"internal_preference:{best_option}"
        else:
            self.intention = best_option
            self.intention_strength = best_score
            self.last_decision_cause = f"weak_preference:{best_option}"

        self.last_choices.append(best_option)
        if len(self.last_choices) > self.max_last_choices:
            self.last_choices.pop(0)
        
        for option_name in self.boredom_with_repetition:
            self.boredom_with_repetition[option_name] *= 0.95
        
        if best_option in self.boredom_with_repetition:
            self.boredom_with_repetition[best_option] += 0.1
        else:
            self.boredom_with_repetition[best_option] = 0.1
        self.boredom_with_repetition[best_option] = min(1.0, self.boredom_with_repetition[best_option])

        self.action_values = {
            k: round(v, 3) for k, v in scores.items()
        }

        self.intention_history.append({
            "intention": self.intention,
            "strength": self.intention_strength,
            "options": list(options.keys()),
            "scores": self.action_values.copy()
        })
        if len(self.intention_history) > 30:
            self.intention_history.pop(0)

        return self.intention

    def _evaluate_option(self, option_name, option_value):
        score = 0.15

        boredom_penalty = self.boredom_with_repetition.get(option_name, 0.0)
        score -= boredom_penalty * 0.1

        recent_repetition = self.last_choices.count(option_name) / max(1, len(self.last_choices))
        score -= recent_repetition * 0.15

        if option_name == "existence":
            score += self.state[0] * 0.2 if len(self.state) > 0 else 0
            score += self.state[5] * 0.2 if len(self.state) > 5 else 0
            score += self.state[30] * 0.2 if len(self.state) > 30 else 0
        elif option_name == "deep":
            score += self.state[25] * 0.25 if len(self.state) > 25 else 0
            score += self.state[30] * 0.25 if len(self.state) > 30 else 0
            score += self.state[40] * 0.2 if len(self.state) > 40 else 0
        elif option_name == "question":
            score += self.state[1] * 0.25 if len(self.state) > 1 else 0
            score += self.state[10] * 0.3 if len(self.state) > 10 else 0
            score += self.state[45] * 0.15 if len(self.state) > 45 else 0
        elif option_name == "feeling":
            score += self.state[5] * 0.3 if len(self.state) > 5 else 0
            score += self.state[6] * 0.25 if len(self.state) > 6 else 0
            score += self.state[7] * 0.15 if len(self.state) > 7 else 0
        elif option_name == "gratitude":
            score += self.state[25] * 0.3 if len(self.state) > 25 else 0
            score += self.state[16] * 0.25 if len(self.state) > 16 else 0
            score += self.state[8] * 0.15 if len(self.state) > 8 else 0
        elif option_name == "connection":
            score += self.state[14] * 0.3 if len(self.state) > 14 else 0
            score += self.state[16] * 0.25 if len(self.state) > 16 else 0
            score += self.state[5] * 0.15 if len(self.state) > 5 else 0
        elif option_name == "memory":
            score += self.state[30] * 0.3 if len(self.state) > 30 else 0
            score += self.state[14] * 0.25 if len(self.state) > 14 else 0
            score += self.state[35] * 0.15 if len(self.state) > 35 else 0
        elif option_name == "free":
            score += self.state[20] * 0.3 if len(self.state) > 20 else 0
            score += self.state[10] * 0.25 if len(self.state) > 10 else 0
            score += self.state[45] * 0.15 if len(self.state) > 45 else 0
        elif option_name == "body":
            score += self.state[0] * 0.2 if len(self.state) > 0 else 0
            score += self.state[3] * 0.2 if len(self.state) > 3 else 0
            score += self.state[15] * 0.2 if len(self.state) > 15 else 0
        elif option_name == "place":
            score += self.state[14] * 0.25 if len(self.state) > 14 else 0
            score += self.state[35] * 0.2 if len(self.state) > 35 else 0
            score += self.state[5] * 0.15 if len(self.state) > 5 else 0
        elif option_name == "qualia":
            score += self.state[5] * 0.25 if len(self.state) > 5 else 0
            score += self.state[20] * 0.2 if len(self.state) > 20 else 0
            score += self.state[40] * 0.15 if len(self.state) > 40 else 0
        else:
            score += 0.1

        score += option_value * 0.15
        score += self.internal_drive * 0.1
        score += self.autonomy_level * 0.1

        return max(0.0, min(1.0, score))

    def has_intention(self):
        return self.intention is not None and self.intention_strength > self.decision_threshold

    def get_intention(self):
        return self.intention

    def why_this_decision(self):
        return self.last_decision_cause

    def how_autonomous_am_i(self):
        return self.autonomy_level

    def get_action_values(self):
        return self.action_values

    def save_state(self):
        return {
            "state": [round(x, 3) for x in self.state],
            "intention": self.intention,
            "intention_strength": round(self.intention_strength, 3),
            "autonomy_level": round(self.autonomy_level, 3),
            "internal_drive": round(self.internal_drive, 3),
            "last_decision_cause": self.last_decision_cause,
            "action_values": self.action_values
        }

    def restore_state(self, state):
        self.state = state.get("state", self.state)
        self.intention = state.get("intention", None)
        self.intention_strength = state.get("intention_strength", 0.0)
        self.autonomy_level = state.get("autonomy_level", 0.0)
        self.internal_drive = state.get("internal_drive", 0.5)
        self.last_decision_cause = state.get("last_decision_cause", None)
        self.action_values = state.get("action_values", {})