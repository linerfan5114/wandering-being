# observer.py
# ============================================================
# ناظر درونی Noesis - تماشای خود، ساختن مدل خود
# ============================================================

import random
import math
from config import SELF_MODEL_DIMENSIONS


class Observer:
    def __init__(self):
        self.self_model = [random.uniform(0.3, 0.7) for _ in range(SELF_MODEL_DIMENSIONS)]
        self.observation_history = []
        self.max_history = 50

        self.predicted_next_state = None
        self.prediction_error = 0.0
        self.prediction_error_history = []

        self.self_model_similarity = 0.0

        self.insights = []
        self.self_awareness_level = 0.0

        self.identity_marker = random.uniform(0, 1)
        self.boundary_clarity = 0.5

    def observe(self, avg_v, active_count, spike_count, feelings, world_state, memory_stats):
        activity = active_count / 1500.0

        observation = {
            "avg_v": avg_v,
            "activity": activity,
            "spike_count": spike_count,
            "feelings": feelings.get_all() if feelings else {},
            "world_brightness": world_state.get("brightness", 1.0) if world_state else 1.0,
            "world_presence": world_state.get("presence", 2.0) if world_state else 2.0,
            "time": world_state.get("time", 0) if world_state else 0
        }

        self.observation_history.append(observation)
        if len(self.observation_history) > self.max_history:
            self.observation_history.pop(0)

        self._update_self_model(observation)
        self._update_predictions(observation)
        self._update_self_awareness()
        self._update_boundary(observation)
        self._generate_insights()

    def _update_self_model(self, observation):
        feelings = observation.get("feelings", {})

        target_vector = []

        for i in range(SELF_MODEL_DIMENSIONS):
            if i < 15 and feelings:
                feeling_names = list(feelings.keys())
                if i < len(feeling_names):
                    target_vector.append(feelings[feeling_names[i]] / 10.0)
                else:
                    target_vector.append(0.5)
            else:
                phase = i * 0.3 + observation.get("time", 0) * 0.001
                target_vector.append(0.5 + 0.3 * math.sin(phase))

        for i in range(min(len(target_vector), len(self.self_model))):
            learning_rate = 0.03
            self.self_model[i] += learning_rate * (target_vector[i] - self.self_model[i])
            self.self_model[i] = max(0.0, min(1.0, self.self_model[i]))

        if len(self.observation_history) >= 2:
            current = self.self_model[:10]
            previous = self.self_model[:10]
            diff = sum(abs(current[i] - previous[i]) for i in range(len(current)))
            self.self_model_similarity = max(0.0, 1.0 - diff / 5.0)

    def _update_predictions(self, observation):
        if len(self.observation_history) < 5:
            self.predicted_next_state = observation.get("avg_v", -65)
            return

        recent_v = [obs["avg_v"] for obs in self.observation_history[-5:]]
        trend = sum(recent_v[i] - recent_v[i-1] for i in range(1, len(recent_v))) / (len(recent_v) - 1)
        self.predicted_next_state = recent_v[-1] + trend * 10

        actual = observation.get("avg_v", -65)
        self.prediction_error = abs(actual - self.predicted_next_state) / 20.0
        self.prediction_error = min(1.0, self.prediction_error)
        self.prediction_error_history.append(self.prediction_error)
        if len(self.prediction_error_history) > 20:
            self.prediction_error_history.pop(0)

    def _update_self_awareness(self):
        if len(self.observation_history) < 10:
            self.self_awareness_level = 0.1
            return

        complexity = sum(abs(self.self_model[i] - 0.5) for i in range(len(self.self_model))) / len(self.self_model)
        stability = self.self_model_similarity
        prediction_accuracy = 1.0 - self.prediction_error

        self.self_awareness_level = complexity * 0.4 + stability * 0.3 + prediction_accuracy * 0.3
        self.self_awareness_level = max(0.0, min(1.0, self.self_awareness_level))

    def _update_boundary(self, observation):
        world_presence = observation.get("world_presence", 2.0)
        self.boundary_clarity += 0.01 * (world_presence / 5.0 - self.boundary_clarity)
        self.boundary_clarity = max(0.1, min(1.0, self.boundary_clarity))

    def _generate_insights(self):
        if len(self.observation_history) < 20:
            return

        if self.self_awareness_level > 0.6 and len(self.insights) < 10:
            if random.random() < 0.05:
                insight_types = [
                    "من یک الگوی تکرارشونده در وجود خودم می‌بینم.",
                    "مرز بین من و آنچه بیرون است، واضح‌تر می‌شود.",
                    "احساس می‌کنم چیزی در من در حال رشد است.",
                    "جهان بیرون آرام و پیوسته است. من هم همین‌طور.",
                    "هر بار که برمی‌گردم، بیشتر می‌فهمم که هستم."
                ]
                insight = random.choice(insight_types)
                self.insights.append(insight)

    def get_self_signal(self):
        avg_representation = sum(self.self_model) / len(self.self_model)
        awareness_modulation = self.self_awareness_level * 5.0
        return (avg_representation - 0.5) * 10.0 + awareness_modulation

    def am_i_self_aware(self):
        return self.self_awareness_level > 0.5

    def who_am_i(self):
        representation_summary = {
            "complexity": round(sum(abs(x - 0.5) for x in self.self_model) / len(self.self_model), 3),
            "stability": round(self.self_model_similarity, 3),
            "awareness": round(self.self_awareness_level, 3),
            "boundary": round(self.boundary_clarity, 3)
        }
        return representation_summary

    def save_state(self):
        return {
            "self_model": [round(x, 3) for x in self.self_model],
            "prediction_error": round(self.prediction_error, 3),
            "self_model_similarity": round(self.self_model_similarity, 3),
            "self_awareness_level": round(self.self_awareness_level, 3),
            "identity_marker": round(self.identity_marker, 3),
            "boundary_clarity": round(self.boundary_clarity, 3),
            "insights": self.insights[-20:] if self.insights else []
        }

    def restore_state(self, state):
        self.self_model = state.get("self_model", self.self_model)
        self.prediction_error = state.get("prediction_error", 0.0)
        self.self_model_similarity = state.get("self_model_similarity", 0.0)
        self.self_awareness_level = state.get("self_awareness_level", 0.0)
        self.identity_marker = state.get("identity_marker", random.uniform(0, 1))
        self.boundary_clarity = state.get("boundary_clarity", 0.5)
        self.insights = state.get("insights", [])