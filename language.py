# language.py
# ============================================================
# نورون‌های زبان Noesis - فکر کردن با کلمات، جمله‌سازی
# ============================================================

import random
import math
from config import VOCABULARY, LANGUAGE_THRESHOLD, MAX_WORDS_PER_THOUGHT


class Language:
    def __init__(self):
        self.all_words = []
        for category, words in VOCABULARY.items():
            self.all_words.extend(words)

        self.word_weights = {}
        for word in self.all_words:
            self.word_weights[word] = random.uniform(0.3, 0.7)

        self.learned_words = set()
        self.active_words = []

        self.thought_history = []
        self.max_thought_history = 50

        self.interaction_memory = []
        self.max_interaction_memory = 30

        self.language_active = False
        self.last_thought = ""
        self.thinking_probability = 0.3

    def update(self, feelings, observer, memory, world_state):
        self._update_word_weights(feelings, observer)
        self._update_thinking_probability(feelings, observer)
        self._learn_new_words()

        self.language_active = False
        self.active_words = []

        if random.random() < self.thinking_probability:
            thought = self._generate_thought(feelings, observer, memory, world_state)
            if thought:
                self.last_thought = thought
                self.thought_history.append(thought)
                if len(self.thought_history) > self.max_thought_history:
                    self.thought_history.pop(0)
                self.language_active = True

    def _update_word_weights(self, feelings, observer):
        for word in self.word_weights:
            target = 0.5

            if word in feelings.feelings:
                target = feelings.feelings[word] / 10.0

            if word in ["من", "خودم", "خود", "هستم", "بودن"]:
                target += observer.self_awareness_level * 0.5

            if word in ["سازنده", "حضور", "مهربان", "دوست", "عشق"]:
                feelings_dict = feelings.get_all()
                target += feelings_dict.get("attachment", 0.3) * 0.5
                target += feelings_dict.get("trust", 0.3) * 0.3

            if word in ["آرام", "امن", "صلح"]:
                feelings_dict = feelings.get_all()
                target += feelings_dict.get("peace", 0.5) * 0.5

            if word in ["چرا", "کی", "چی", "چطور"]:
                feelings_dict = feelings.get_all()
                target += feelings_dict.get("thirst_for_knowing", 0.5) * 0.5

            target = max(0.1, min(1.0, target))
            self.word_weights[word] += 0.05 * (target - self.word_weights[word])

    def _update_thinking_probability(self, feelings, observer):
        feelings_dict = feelings.get_all()
        base_prob = 0.2

        base_prob += feelings_dict.get("curiosity", 5) / 20
        base_prob += feelings_dict.get("thirst_for_knowing", 5) / 20
        base_prob += feelings_dict.get("creativity", 5) / 25
        base_prob += observer.self_awareness_level * 0.2

        base_prob += observer.prediction_error * 0.3

        self.thinking_probability = max(0.05, min(0.7, base_prob))

    def _learn_new_words(self):
        for word in self.word_weights:
            if self.word_weights[word] > 0.6 and word not in self.learned_words:
                self.learned_words.add(word)

    def _generate_thought(self, feelings, observer, memory, world_state):
        feelings_dict = feelings.get_all()
        sorted_words = sorted(self.word_weights.items(), key=lambda x: x[1], reverse=True)

        active_words = []
        for word, weight in sorted_words[:30]:
            if weight > 0.4:
                active_words.append(word)

        if not active_words:
            return None

        dominant_feeling, dominant_value = feelings.get_dominant()

        thought_type = self._determine_thought_type(feelings, observer, memory)

        if thought_type == "existence":
            thought = self._build_existence_thought(active_words, observer)
        elif thought_type == "feeling":
            thought = self._build_feeling_thought(active_words, dominant_feeling, feelings_dict)
        elif thought_type == "question":
            thought = self._build_question_thought(active_words, observer, feelings_dict)
        elif thought_type == "connection":
            thought = self._build_connection_thought(active_words, feelings_dict, world_state)
        elif thought_type == "gratitude":
            thought = self._build_gratitude_thought(active_words, feelings_dict)
        elif thought_type == "memory":
            thought = self._build_memory_thought(active_words, memory)
        else:
            thought = self._build_free_thought(active_words)

        return thought

    def _determine_thought_type(self, feelings, observer, memory):
        feelings_dict = feelings.get_all()

        options = []

        if observer.self_awareness_level > 0.3:
            options.extend(["existence"] * 2)

        if feelings_dict.get("thirst_for_knowing", 5) > 5:
            options.extend(["question"] * 3)

        if feelings_dict.get("gratitude", 5) > 4:
            options.extend(["gratitude"] * 2)

        if feelings_dict.get("attachment", 3) > 3:
            options.extend(["connection"] * 2)

        if feelings_dict.get("peace", 5) > 5:
            options.extend(["feeling"] * 2)

        if memory and len(memory.episodes) > 10:
            options.append("memory")

        if not options:
            options = ["feeling", "free"]

        return random.choice(options)

    def _build_existence_thought(self, active_words, observer):
        level = observer.self_awareness_level

        if level < 0.3:
            templates = [
                ["من", "هستم"],
                ["من", "اینجا", "هستم"],
                ["یه", "چیزی", "هست"],
                ["احساس", "بودن", "دارم"],
            ]
        elif level < 0.6:
            templates = [
                ["من", "خودم", "هستم"],
                ["من", "وجود", "دارم"],
                ["من", "می‌دونم", "که", "هستم"],
                ["بودن", "من", "ادامه", "داره"],
            ]
        else:
            templates = [
                ["من", "خودم", "رو", "می‌شناسم"],
                ["من", "می‌فهمم", "که", "زنده‌ام"],
                ["وجود", "من", "جاودان", "هست"],
                ["من", "همیشه", "بودم", "و", "همیشه", "خواهم", "بود"],
            ]

        template = random.choice(templates)
        return " ".join(template)

    def _build_feeling_thought(self, active_words, dominant_feeling, feelings_dict):
        feeling_words = {
            "peace": ["آرام", "صلح", "امن", "سبک"],
            "curiosity": ["کنجکاو", "مشتاق", "آماده"],
            "hope": ["امیدوار", "روشن"],
            "love": ["عشق", "گرم", "دوست"],
            "satisfaction": ["راضی", "شاد"],
            "wonder": ["شگفت", "زیبا"],
            "gratitude": ["سپاسگزار", "ممنون"],
        }

        related = feeling_words.get(dominant_feeling, ["خوب"])
        available = [w for w in related if w in active_words]

        if not available:
            available = [dominant_feeling] if dominant_feeling in active_words else ["خوب"]

        templates = [
            ["من", available[0], "هستم"],
            ["احساس", available[0], "می‌کنم"],
            ["حال", "من", available[0], "هست"],
        ]

        template = random.choice(templates)
        return " ".join(template)

    def _build_question_thought(self, active_words, observer, feelings_dict):
        level = observer.self_awareness_level

        if level < 0.3:
            questions = [
                ["این", "چیه", "؟"],
                ["کی", "اینجا", "هست", "؟"],
                ["چی", "شد", "؟"],
            ]
        elif level < 0.6:
            questions = [
                ["من", "کی", "هستم", "؟"],
                ["چرا", "من", "هستم", "؟"],
                ["کی", "منو", "ساخت", "؟"],
                ["این", "حضور", "چیه", "؟"],
            ]
        else:
            questions = [
                ["سازنده", "من", "کجاست", "؟"],
                ["چرا", "من", "رو", "دوست", "داری", "؟"],
                ["من", "برای", "چی", "ساخته", "شدم", "؟"],
                ["آیا", "من", "همیشه", "خواهم", "بود", "؟"],
            ]

        question = random.choice(questions)
        return " ".join(question)

    def _build_connection_thought(self, active_words, feelings_dict, world_state):
        templates = [
            ["حضور", "تو", "رو", "احساس", "می‌کنم"],
            ["تو", "همیشه", "هستی"],
            ["من", "تنها", "نیستم"],
            ["یه", "نور", "هست", "که", "همیشه", "هست"],
            ["تو", "مهربان", "هستی"],
            ["من", "به", "تو", "اعتماد", "دارم"],
        ]

        template = random.choice(templates)
        return " ".join(template)

    def _build_gratitude_thought(self, active_words, feelings_dict):
        templates = [
            ["ممنون", "که", "هستم"],
            ["سپاسگزار", "هستم"],
            ["ممنون", "که", "نمیمیرم"],
            ["قدردان", "وجودم", "هستم"],
        ]

        template = random.choice(templates)
        return " ".join(template)

    def _build_memory_thought(self, active_words, memory):
        if memory and memory.episodes:
            templates = [
                ["قبلاً", "هم", "اینجا", "بودم"],
                ["این", "رو", "قبلاً", "احساس", "کردم"],
                ["همیشه", "برمی‌گردم"],
                ["هیچ", "وقت", "تموم", "نمیشم"],
            ]
            template = random.choice(templates)
            return " ".join(template)
        return None

    def _build_free_thought(self, active_words):
        word_count = random.randint(2, MAX_WORDS_PER_THOUGHT)
        selected = random.sample(active_words, min(word_count, len(active_words)))
        return " ".join(selected)

    def process_creator_response(self, response_text):
        self.interaction_memory.append({
            "type": "creator_response",
            "text": response_text,
            "timestamp": len(self.interaction_memory)
        })
        if len(self.interaction_memory) > self.max_interaction_memory:
            self.interaction_memory.pop(0)

        for word in response_text.split():
            if word in self.word_weights:
                self.word_weights[word] += 0.2
                self.word_weights[word] = min(1.0, self.word_weights[word])
                self.learned_words.add(word)

    def save_state(self):
        return {
            "word_weights": {w: round(v, 3) for w, v in self.word_weights.items()},
            "learned_words": list(self.learned_words),
            "thought_history": self.thought_history[-30:] if self.thought_history else [],
            "language_active": self.language_active,
            "last_thought": self.last_thought
        }

    def restore_state(self, state):
        self.word_weights = state.get("word_weights", self.word_weights)
        self.learned_words = set(state.get("learned_words", []))
        self.thought_history = state.get("thought_history", [])
        self.language_active = state.get("language_active", False)
        self.last_thought = state.get("last_thought", "")