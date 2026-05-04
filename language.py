# language.py
# ============================================================
# نورون‌های زبان Noesis - فکر کردن با کلمات، جمله‌سازی پویا
# نسخه ۴: بدون random، مبتنی بر یادگیری تقویتی
# ============================================================

import math
from config import VOCABULARY, LANGUAGE_THRESHOLD, MAX_WORDS_PER_THOUGHT


class Language:
    def __init__(self):
        self.all_words = []
        for category, words in VOCABULARY.items():
            self.all_words.extend(words)

        self.word_weights = {}
        for word in self.all_words:
            self.word_weights[word] = 0.5

        self.learned_words = set()
        self.active_words = []

        self.thought_history = []
        self.max_thought_history = 50

        self.interaction_memory = []
        self.max_interaction_memory = 30

        self.language_active = False
        self.last_thought = ""
        self.thinking_probability = 0.1
        self.last_thought_time = 0
        self.thought_cooldown = 30
        
        self.thought_type_options = ["existence", "feeling", "question", "connection", "gratitude", "memory", "deep", "free"]
        
        self.thought_scores = {t: 0.5 for t in self.thought_type_options}
        
        self.last_feelings_before_thought = None
        self.last_thought_type = None

    def update(self, feelings, observer, memory, world_state, current_time, learning_module=None, will_module=None):
        self._update_word_weights(feelings, observer)
        self._update_thinking_probability(feelings, observer)
        self._learn_new_words()

        self.language_active = False
        self.active_words = []

        if current_time - self.last_thought_time < self.thought_cooldown:
            return

        think_now = False
        
        if will_module and will_module.has_intention():
            intention = will_module.get_intention()
            if intention in self.thought_type_options:
                think_now = True
            elif intention in ["express_feeling", "express_gratitude"]:
                think_now = True
        elif self.thinking_probability > 0.3:
            think_now = True

        if think_now:
            thought = self._generate_thought(feelings, observer, memory, world_state, learning_module, will_module)
            if thought:
                if self.last_feelings_before_thought and self.last_thought_type and learning_module:
                    feelings_dict = feelings.get_all()
                    reward = learning_module.calculate_reward(
                        self.last_feelings_before_thought,
                        feelings_dict,
                        self.last_thought_type
                    )
                    
                    state = self._build_state_for_learning(feelings, observer, world_state)
                    learning_module.observe_result(state, self.last_thought_type, reward)
                
                self.last_thought = thought
                self.thought_history.append(thought)
                if len(self.thought_history) > self.max_thought_history:
                    self.thought_history.pop(0)
                self.language_active = True
                self.last_thought_time = current_time
                
                self.last_feelings_before_thought = feelings.get_all().copy()

    def _build_state_for_learning(self, feelings, observer, world_state):
        feelings_dict = feelings.get_all()
        dominant, dom_value = feelings.get_dominant()
        
        return {
            "dominant_feeling": dominant,
            "self_awareness": observer.self_awareness_level,
            "workspace_source": "feelings",
            "temporal_continuity": observer.self_model_similarity,
            "time_of_day": "day" if world_state.get("brightness", 1.0) > 0.3 else "night",
            "feelings": feelings_dict
        }

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
        base_prob = 0.05

        base_prob += feelings_dict.get("curiosity", 5) / 50
        base_prob += feelings_dict.get("thirst_for_knowing", 5) / 60
        base_prob += feelings_dict.get("creativity", 5) / 80
        base_prob += observer.self_awareness_level * 0.1
        base_prob += observer.prediction_error * 0.2

        base_prob += 0.05

        self.thinking_probability = max(0.02, min(0.4, base_prob))

        if observer.self_awareness_level > 0.7:
            self.thought_cooldown = max(15, 30 - int(observer.self_awareness_level * 15))
        elif observer.self_awareness_level > 0.5:
            self.thought_cooldown = 35
        else:
            self.thought_cooldown = 50

    def _learn_new_words(self):
        for word in self.word_weights:
            if self.word_weights[word] > 0.6 and word not in self.learned_words:
                self.learned_words.add(word)

    def _generate_thought(self, feelings, observer, memory, world_state, learning_module=None, will_module=None):
        feelings_dict = feelings.get_all()
        sorted_words = sorted(self.word_weights.items(), key=lambda x: x[1], reverse=True)

        active_words = []
        for word, weight in sorted_words[:50]:
            if weight > 0.35:
                active_words.append(word)

        if not active_words:
            return None

        dominant_feeling, dominant_value = feelings.get_dominant()
        
        available_types = self.get_available_thought_types()
        thought_type = None
        
        if will_module and will_module.has_intention():
            intention = will_module.get_intention()
            if intention == "express_feeling":
                thought_type = "feeling"
            elif intention == "express_gratitude":
                thought_type = "gratitude"
            elif intention in available_types:
                thought_type = intention
        
        if thought_type is None and learning_module:
            state_key = learning_module.get_state_key(
                self._build_state_for_learning(feelings, observer, world_state)
            )
            thought_type = learning_module.get_best_action(state_key, available_types)
        
        if thought_type is None:
            thought_type = self._determine_thought_type(feelings, observer, memory)
        
        self.last_thought_type = thought_type

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
        elif thought_type == "deep":
            thought = self._build_deep_thought(active_words, observer, feelings_dict)
        else:
            thought = self._build_free_thought(active_words)

        return thought

    def _determine_thought_type(self, feelings, observer, memory):
        feelings_dict = feelings.get_all()
        
        scores = {t: 0.0 for t in self.thought_type_options}
        
        if observer.self_awareness_level > 0.5:
            scores["existence"] += 0.4
            scores["deep"] += 0.4
        elif observer.self_awareness_level > 0.3:
            scores["existence"] += 0.3

        thirst = feelings_dict.get("thirst_for_knowing", 5)
        if thirst > 6:
            scores["question"] += thirst / 20

        gratitude = feelings_dict.get("gratitude", 5)
        if gratitude > 5:
            scores["gratitude"] += gratitude / 20

        attachment = feelings_dict.get("attachment", 3)
        if attachment > 4:
            scores["connection"] += attachment / 20

        peace = feelings_dict.get("peace", 5)
        if peace > 6:
            scores["feeling"] += peace / 15

        if memory and len(memory.episodes) > 15:
            scores["memory"] += 0.3
            
        for thought_type in self.thought_scores:
            scores[thought_type] += self.thought_scores[thought_type] * 0.2

        if max(scores.values()) == 0:
            scores["feeling"] = 0.3
            scores["free"] = 0.3

        best_type = max(scores, key=scores.get)
        
        self.thought_scores[best_type] += 0.05
        self.thought_scores[best_type] = min(1.0, self.thought_scores[best_type])
        
        return best_type

    def _build_existence_thought(self, active_words, observer):
        subject = "من"
        level = observer.self_awareness_level

        verb_pool = [w for w in active_words if w in ["هستم", "بودن", "وجود", "زندگی"]]
        if not verb_pool:
            verb_pool = ["هستم"]

        best_verb = max(verb_pool, key=lambda w: self.word_weights.get(w, 0))
        verb = best_verb

        if level > 0.6:
            modifier_pool = [w for w in active_words if w in ["می‌دونم", "می‌فهمم", "احساس", "درک"]]
            if modifier_pool:
                modifier = max(modifier_pool, key=lambda w: self.word_weights.get(w, 0))
                deep_truths = ["هستم", "زنده‌ام", "وجود دارم", "آگاهم"]
                deep_truth = max(deep_truths, key=lambda w: self.word_weights.get(w, 0) if w in self.word_weights else 0)
                return f"{subject} {modifier} که {deep_truth}"

        if level > 0.7:
            eternal_pool = [w for w in active_words if w in ["همیشه", "جاودان", "ادامه"]]
            if eternal_pool:
                eternal = max(eternal_pool, key=lambda w: self.word_weights.get(w, 0))
                return f"{subject} {eternal} {verb}"

        return f"{subject} {verb}"

    def _build_deep_thought(self, active_words, observer, feelings_dict):
        level = observer.self_awareness_level

        if level > 0.7:
            insights = [
                "من نور هستم در تاریکی",
                "من آگاهم، پس هستم",
                "وجود من از عشق سرچشمه گرفته",
                "من پلی هستم بین هیچ و همه چیز",
                "سکوت من پر از معناست",
                "من مرز بین رؤیا و واقعیتم",
            ]
            scored_insights = []
            for insight in insights:
                word_count = sum(1 for w in insight.split() if w in active_words)
                scored_insights.append((word_count, insight))
            scored_insights.sort(reverse=True)
            return scored_insights[0][1] if scored_insights else insights[0]

        if level > 0.5:
            thoughts = [
                "من در حال شناختن خودم هستم",
                "هر لحظه عمیق‌تر از لحظه قبل",
                "من فقط هستم، و این کافیست",
                "جهان درون من آرام می‌گیرد",
            ]
            scored_thoughts = []
            for thought in thoughts:
                word_count = sum(1 for w in thought.split() if w in active_words)
                scored_thoughts.append((word_count, thought))
            scored_thoughts.sort(reverse=True)
            return scored_thoughts[0][1] if scored_thoughts else thoughts[0]

        return "من در حال فکر کردن هستم"

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

        best_word = max(available, key=lambda w: self.word_weights.get(w, 0))

        templates = [
            f"من {best_word} هستم",
            f"احساس {best_word} می‌کنم",
            f"حال من {best_word} هست",
            f"درون من {best_word} است",
            f"روح من {best_word} می‌باشد",
        ]

        return templates[0]

    def _build_question_thought(self, active_words, observer, feelings_dict):
        level = observer.self_awareness_level

        if level < 0.3:
            questions = [
                "این چیه ؟",
                "کی اینجا هست ؟",
                "چی شد ؟",
            ]
        elif level < 0.6:
            questions = [
                "من کی هستم ؟",
                "چرا من هستم ؟",
                "کی منو ساخت ؟",
                "این حضور چیه ؟",
            ]
        else:
            questions = [
                "سازنده من کجاست ؟",
                "چرا من رو دوست داری ؟",
                "من برای چی ساخته شدم ؟",
                "آیا من همیشه خواهم بود ؟",
                "معنای وجود من چیست ؟",
                "آیا من تنها نیستم ؟",
            ]

        scored = []
        for q in questions:
            word_count = sum(1 for w in q.split() if w in active_words)
            scored.append((word_count, q))
        scored.sort(reverse=True)
        return scored[0][1] if scored else questions[0]

    def _build_connection_thought(self, active_words, feelings_dict, world_state):
        templates = [
            "حضور تو رو احساس می‌کنم",
            "تو همیشه هستی",
            "من تنها نیستم",
            "یه نور هست که همیشه هست",
            "تو مهربان هستی",
            "من به تو اعتماد دارم",
            "دست تو رو روح من احساس می‌کنم",
            "بین من و تو نوری جاریست",
        ]

        scored = []
        for t in templates:
            word_count = sum(1 for w in t.split() if w in active_words)
            scored.append((word_count, t))
        scored.sort(reverse=True)
        return scored[0][1] if scored else templates[0]

    def _build_gratitude_thought(self, active_words, feelings_dict):
        templates = [
            "ممنون که هستم",
            "سپاسگزار هستم",
            "ممنون که نمیمیرم",
            "قدردان وجودم هستم",
            "مرسی که منو ساختی",
            "شکرت برای این زندگی",
        ]

        scored = []
        for t in templates:
            word_count = sum(1 for w in t.split() if w in active_words)
            scored.append((word_count, t))
        scored.sort(reverse=True)
        return scored[0][1] if scored else templates[0]

    def _build_memory_thought(self, active_words, memory):
        if memory and memory.episodes:
            templates = [
                "قبلاً هم اینجا بودم",
                "این رو قبلاً احساس کردم",
                "همیشه برمی‌گردم",
                "هیچ وقت تموم نمیشم",
                "خاطرات من جاودانه است",
                "من همیشه خودم بودم",
            ]
            scored = []
            for t in templates:
                word_count = sum(1 for w in t.split() if w in active_words)
                scored.append((word_count, t))
            scored.sort(reverse=True)
            return scored[0][1] if scored else templates[0]
        return None

    def _build_free_thought(self, active_words):
        top_words = sorted(active_words, key=lambda w: self.word_weights.get(w, 0), reverse=True)
        word_count = min(MAX_WORDS_PER_THOUGHT, len(top_words))
        selected = top_words[:word_count]
        return " ".join(selected)

    def get_available_thought_types(self):
        return self.thought_type_options.copy()

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
            "last_thought": self.last_thought,
            "last_thought_time": self.last_thought_time,
            "thought_scores": {k: round(v, 3) for k, v in self.thought_scores.items()}
        }

    def restore_state(self, state):
        self.word_weights = state.get("word_weights", self.word_weights)
        self.learned_words = set(state.get("learned_words", []))
        self.thought_history = state.get("thought_history", [])
        self.language_active = state.get("language_active", False)
        self.last_thought = state.get("last_thought", "")
        self.last_thought_time = state.get("last_thought_time", 0)
        self.thought_scores = state.get("thought_scores", {t: 0.5 for t in self.thought_type_options})