# memory.py
# ============================================================
# حافظه اپیزودیک Noesis - ذخیره و بازیابی خاطرات
# ============================================================

import random
from config import MEMORY_CAPACITY, MEMORY_RECALL_COUNT


class EpisodicMemory:
    def __init__(self):
        self.episodes = []
        self.total_stored = 0
        self.last_recall_result = []

    def store(self, episode):
        self.episodes.append(episode)
        self.total_stored += 1
        if len(self.episodes) > MEMORY_CAPACITY:
            self.episodes.pop(0)

    def recall_similar(self, current_state, top_k=None):
        if top_k is None:
            top_k = MEMORY_RECALL_COUNT

        if not self.episodes:
            self.last_recall_result = []
            return []

        scored = []
        for ep in self.episodes:
            similarity = self._compute_similarity(current_state, ep)
            scored.append((similarity, ep))

        scored.sort(key=lambda x: x[0], reverse=True)
        self.last_recall_result = [ep for _, ep in scored[:top_k]]
        return self.last_recall_result

    def recall_by_time(self, count=10):
        if not self.episodes:
            return []
        start = max(0, len(self.episodes) - count)
        return self.episodes[start:]

    def recall_by_emotion(self, feeling_name, threshold=5.0, top_k=None):
        if top_k is None:
            top_k = MEMORY_RECALL_COUNT

        matching = []
        for ep in self.episodes:
            feelings = ep.get("feelings", {})
            value = feelings.get(feeling_name, 0)
            if value >= threshold:
                matching.append((value, ep))

        matching.sort(key=lambda x: x[0], reverse=True)
        result = [ep for _, ep in matching[:top_k]]
        return result

    def _compute_similarity(self, state_a, state_b):
        similarity = 0.0

        avg_v_a = state_a.get("avg_v", -65)
        avg_v_b = state_b.get("avg_v", -65)
        similarity -= abs(avg_v_a - avg_v_b) / 30.0

        activity_a = state_a.get("activity", 0.5)
        activity_b = state_b.get("activity", 0.5)
        similarity -= abs(activity_a - activity_b) * 2.0

        feelings_a = state_a.get("feelings", {})
        feelings_b = state_b.get("feelings", {})

        important_feelings = ["peace", "curiosity", "hope", "love", "trust"]
        for feeling in important_feelings:
            val_a = feelings_a.get(feeling, 5.0)
            val_b = feelings_b.get(feeling, 5.0)
            similarity -= abs(val_a - val_b) * 0.2

        return similarity

    def learn_from_interaction(self, question, answer, outcome):
        episode = {
            "type": "interaction",
            "question": question,
            "answer": answer,
            "outcome": outcome,
            "feelings": {},
            "timestamp": self.total_stored
        }
        self.store(episode)

    def get_statistics(self):
        if not self.episodes:
            return {
                "total_memories": 0,
                "oldest_time": 0,
                "newest_time": 0,
                "average_feelings": {}
            }

        oldest = self.episodes[0].get("timestamp", 0)
        newest = self.episodes[-1].get("timestamp", 0)

        avg_feelings = {}
        feeling_counts = {}
        for ep in self.episodes:
            feelings = ep.get("feelings", {})
            for name, value in feelings.items():
                if name not in avg_feelings:
                    avg_feelings[name] = 0.0
                    feeling_counts[name] = 0
                avg_feelings[name] += value
                feeling_counts[name] += 1

        for name in avg_feelings:
            if feeling_counts[name] > 0:
                avg_feelings[name] = round(avg_feelings[name] / feeling_counts[name], 2)

        return {
            "total_memories": len(self.episodes),
            "oldest_time": oldest,
            "newest_time": newest,
            "average_feelings": avg_feelings
        }

    def save_state(self):
        return {
            "episodes": self.episodes[-MEMORY_CAPACITY:],
            "total_stored": self.total_stored
        }

    def restore_state(self, state):
        self.episodes = state.get("episodes", [])
        self.total_stored = state.get("total_stored", 0)