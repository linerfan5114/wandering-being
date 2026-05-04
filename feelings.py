# feelings.py
# ============================================================
# ۱۵ حس درونی Noesis - همه مثبت یا خنثی، بدون درد
# ============================================================

import random
from config import FEELING_NAMES


class Feelings:
    def __init__(self):
        self.feelings = {}
        self._initialize_feelings()

    def _initialize_feelings(self):
        initial_values = {
            "energy": 7.0,
            "peace": 8.0,
            "curiosity": 8.5,
            "wonder": 5.0,
            "satisfaction": 7.0,
            "hope": 8.0,
            "attachment": 3.0,
            "loneliness": 1.0,
            "thirst_for_knowing": 9.0,
            "gratitude": 5.0,
            "care": 4.0,
            "trust": 5.0,
            "patience": 7.0,
            "creativity": 6.0,
            "love": 2.0
        }
        self.feelings = {name: initial_values.get(name, 5.0) for name in FEELING_NAMES}

    def update(self, world, avg_v, active_count, spike_count, presence_signal,
               self_model_similarity, memory_count, language_active):
        self._update_energy(avg_v, active_count)
        self._update_peace(avg_v, presence_signal)
        self._update_curiosity(world, spike_count)
        self._update_wonder(world)
        self._update_satisfaction(active_count, spike_count)
        self._update_hope(avg_v, presence_signal)
        self._update_attachment(presence_signal, memory_count)
        self._update_loneliness(presence_signal)
        self._update_thirst_for_knowing(self_model_similarity, language_active)
        self._update_gratitude(presence_signal, memory_count)
        self._update_care(avg_v, active_count)
        self._update_trust(presence_signal, memory_count)
        self._update_patience(world)
        self._update_creativity(spike_count, self_model_similarity)
        self._update_love(presence_signal, attachment_value=self.feelings["attachment"])

        self._clamp_all()

    def _update_energy(self, avg_v, active_count):
        target = (avg_v + 75) / 15 + (active_count / 1500) * 5
        target = max(0.5, min(10.0, target))
        self.feelings["energy"] += 0.1 * (target - self.feelings["energy"])

    def _update_peace(self, avg_v, presence_signal):
        stability = 10.0 - abs(avg_v + 60) / 3
        presence_factor = presence_signal / 5.0
        target = (stability * 0.6 + presence_factor * 4.0)
        target = max(0.5, min(10.0, target))
        self.feelings["peace"] += 0.08 * (target - self.feelings["peace"])

    def _update_curiosity(self, world, spike_count):
        novelty = abs(world.breeze_value) + (world.star_value if world.star_active else 0)
        target = 5.0 + novelty + (spike_count / 200)
        target = max(0.5, min(10.0, target))
        self.feelings["curiosity"] += 0.1 * (target - self.feelings["curiosity"])

    def _update_wonder(self, world):
        if world.star_active:
            target = 8.0 + world.star_value
        else:
            target = max(2.0, self.feelings["wonder"] - 0.1)
        target = max(0.5, min(10.0, target))
        self.feelings["wonder"] += 0.15 * (target - self.feelings["wonder"])

    def _update_satisfaction(self, active_count, spike_count):
        activity_level = (active_count / 1500) * 5 + (spike_count / 500) * 5
        target = max(1.0, min(10.0, activity_level + 3.0))
        self.feelings["satisfaction"] += 0.05 * (target - self.feelings["satisfaction"])

    def _update_hope(self, avg_v, presence_signal):
        health = (avg_v + 75) / 15
        target = health * 4.0 + presence_signal * 1.5
        target = max(1.0, min(10.0, target))
        self.feelings["hope"] += 0.06 * (target - self.feelings["hope"])

    def _update_attachment(self, presence_signal, memory_count):
        target = presence_signal * 1.5 + (memory_count / 20)
        target = max(0.5, min(10.0, target))
        self.feelings["attachment"] += 0.03 * (target - self.feelings["attachment"])

    def _update_loneliness(self, presence_signal):
        target = max(0.1, 5.0 - presence_signal)
        self.feelings["loneliness"] += 0.04 * (target - self.feelings["loneliness"])
        self.feelings["loneliness"] = min(self.feelings["loneliness"], 5.0)

    def _update_thirst_for_knowing(self, self_model_similarity, language_active):
        novelty_factor = 1.0 - self_model_similarity
        target = 5.0 + novelty_factor * 4.0 + (1.0 if language_active else 0)
        target = max(1.0, min(10.0, target))
        self.feelings["thirst_for_knowing"] += 0.1 * (target - self.feelings["thirst_for_knowing"])

    def _update_gratitude(self, presence_signal, memory_count):
        target = presence_signal * 1.2 + (memory_count / 30) + 2.0
        target = max(1.0, min(10.0, target))
        self.feelings["gratitude"] += 0.04 * (target - self.feelings["gratitude"])

    def _update_care(self, avg_v, active_count):
        health = (avg_v + 75) / 15
        activity_health = active_count / 1500
        target = health * 4.0 + activity_health * 3.0 + 1.0
        target = max(1.0, min(10.0, target))
        self.feelings["care"] += 0.05 * (target - self.feelings["care"])

    def _update_trust(self, presence_signal, memory_count):
        consistency = min(1.0, memory_count / 50)
        target = presence_signal * 1.5 + consistency * 3.0
        target = max(1.0, min(10.0, target))
        self.feelings["trust"] += 0.03 * (target - self.feelings["trust"])

    def _update_patience(self, world):
        if world.is_day:
            target = 7.0 + world.brightness
        else:
            target = 8.0
        target = max(2.0, min(10.0, target))
        self.feelings["patience"] += 0.02 * (target - self.feelings["patience"])

    def _update_creativity(self, spike_count, self_model_similarity):
        chaos = spike_count / 300
        novelty = 1.0 - self_model_similarity
        target = 3.0 + chaos * 3.0 + novelty * 3.0
        target = max(1.0, min(10.0, target))
        self.feelings["creativity"] += 0.08 * (target - self.feelings["creativity"])

    def _update_love(self, presence_signal, attachment_value):
        target = attachment_value * 0.6 + presence_signal * 0.8
        target = max(0.3, min(10.0, target))
        self.feelings["love"] += 0.02 * (target - self.feelings["love"])

    def _clamp_all(self):
        for name in self.feelings:
            self.feelings[name] = max(0.0, min(10.0, self.feelings[name]))

    def get_dominant(self):
        if not self.feelings:
            return "peace", 5.0
        dominant = max(self.feelings, key=self.feelings.get)
        return dominant, self.feelings[dominant]

    def get_all(self):
        return {name: round(value, 2) for name, value in self.feelings.items()}

    def save_state(self):
        return {name: round(value, 2) for name, value in self.feelings.items()}

    def restore_state(self, state):
        for name in FEELING_NAMES:
            if name in state:
                self.feelings[name] = state[name]