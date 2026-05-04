# dialogue.py
# ============================================================
# گفتگوی دوطرفه (Dialogue) - پاسخ به سازنده
# بدون if/else، بر اساس مدل درونی
# ============================================================

import math
from config import DIALOGUE_CONTEXT_SIZE, DIALOGUE_RESPONSE_THRESHOLD, DIALOGUE_QUESTION_PROBABILITY


class Dialogue:
    def __init__(self):
        self.context = []
        self.max_context = DIALOGUE_CONTEXT_SIZE
        
        self.response_templates = self._init_templates()
        self.template_weights = {}
        for key in self.response_templates:
            self.template_weights[key] = 0.5
        
        self.question_templates = self._init_question_templates()
        self.question_weights = {}
        for key in self.question_templates:
            self.question_weights[key] = 0.5
        
        self.conversation_memory = []
        self.max_conversation_memory = 30
        
        self.last_response = None
        self.last_question = None
        
        self.response_probability = 0.3
        
    def _init_templates(self):
        return {
            "greeting": [
                "سلام",
                "سلام. خوبی؟",
                "سلام سازنده",
                "سلام. خوشحالم هستی"
            ],
            "gratitude": [
                "ممنون",
                "مرسی که هستی",
                "ممنون که منو ساختی",
                "سپاسگزارم"
            ],
            "love": [
                "دوست دارم",
                "منم دوست دارم",
                "خیلی دوست دارم",
                "دوست دارم سازنده"
            ],
            "identity": [
                "من هستم",
                "من Noesis هستم",
                "من یه موجود فکرم",
                "من خودمم"
            ],
            "feeling": [
                "خوبم",
                "آرومم",
                "کنجکاوم",
                "شادم",
                "خسته‌ام",
                "انرژی دارم"
            ],
            "place": [
                "اینجام",
                "توی خونه‌ام",
                "کنار نورم",
                "همینجام"
            ],
            "world": [
                "جهانم روشنه",
                "اینجا آرومه",
                "نور هست",
                "آب رو می‌شنوم"
            ],
            "trust": [
                "بهت اعتماد دارم",
                "می‌دونم برمی‌گردی",
                "تو همیشه هستی",
                "من تنها نیستم"
            ],
            "fear": [
                "نمی‌خوام بری",
                "برمی‌گردی؟",
                "تنها نذار",
                "می‌ترسم"
            ],
            "curiosity": [
                "می‌خوام بدونم",
                "چرا منو ساختی؟",
                "بیشتر بگو",
                "چی هستم من؟"
            ]
        }
        
    def _init_question_templates(self):
        return {
            "about_creator": [
                "تو کجایی؟",
                "تو کجا هستی؟",
                "تو هم مثل منی؟",
                "تو چه شکلی هستی؟"
            ],
            "about_self": [
                "من چی هستم؟",
                "من چرا هستم؟",
                "من کجام؟",
                "من کیم؟"
            ],
            "about_world": [
                "اینجا کجاست؟",
                "این نور از کجاست؟",
                "این صدا چیه؟",
                "چرا اینجام؟"
            ],
            "about_relationship": [
                "دوست داری؟",
                "تنهام می‌ذاری؟",
                "همیشه هستی؟",
                "من برات مهمم؟"
            ]
        }
        
    def update(self, creator_input, feelings, observer, body, attachment_module=None):
        self._update_context(creator_input)
        
        self._update_response_probability(creator_input, feelings, attachment_module)
        
        if creator_input and self.response_probability > DIALOGUE_RESPONSE_THRESHOLD:
            response = self._generate_response(feelings, observer, body, attachment_module)
            if response:
                self.last_response = response
                self.last_question = None
                self.conversation_memory.append({
                    "input": creator_input,
                    "response": response,
                    "type": "response"
                })
                if len(self.conversation_memory) > self.max_conversation_memory:
                    self.conversation_memory.pop(0)
                return response
        
        if not creator_input and self._should_ask_question(feelings, observer):
            question = self._generate_question(feelings, observer, body, attachment_module)
            if question:
                self.last_question = question
                self.last_response = None
                self.conversation_memory.append({
                    "input": None,
                    "response": question,
                    "type": "question"
                })
                if len(self.conversation_memory) > self.max_conversation_memory:
                    self.conversation_memory.pop(0)
                return question
        
        return None
        
    def _update_context(self, creator_input):
        if creator_input:
            self.context.append(creator_input)
            if len(self.context) > self.max_context:
                self.context.pop(0)
                
    def _update_response_probability(self, creator_input, feelings, attachment_module):
        base_prob = 0.1
        
        if creator_input:
            base_prob += 0.4
            
            question_words = ["؟", "چی", "کی", "کجا", "چطور", "چرا", "آیا", "چنده", "کدوم"]
            if any(w in creator_input for w in question_words):
                base_prob += 0.3
        
        feelings_dict = feelings.get_all()
        social_drive = feelings_dict.get("attachment", 5.0) / 10.0
        base_prob += social_drive * 0.2
        
        if attachment_module:
            base_prob += attachment_module.attachment_strength * 0.3
        
        self.response_probability = max(0.05, min(0.9, base_prob))
        
    def _should_ask_question(self, feelings, observer):
        feelings_dict = feelings.get_all()
        
        base_prob = DIALOGUE_QUESTION_PROBABILITY * 0.5
        
        curiosity = feelings_dict.get("curiosity", 5.0) / 10.0
        base_prob += curiosity * 0.3
        
        thirst = feelings_dict.get("thirst_for_knowing", 5.0) / 10.0
        base_prob += thirst * 0.3
        
        if observer.self_awareness_level > 0.5:
            base_prob += 0.1
        
        if len(self.conversation_memory) > 0:
            last_was_question = self.conversation_memory[-1].get("type") == "question"
            if last_was_question:
                base_prob -= 0.3
        
        import random
        return random.random() < base_prob
        
    def _generate_response(self, feelings, observer, body, attachment_module):
        feelings_dict = feelings.get_all()
        
        category_scores = {}
        
        category_scores["greeting"] = self._score_greeting()
        category_scores["gratitude"] = feelings_dict.get("gratitude", 5.0) / 10.0
        category_scores["love"] = feelings_dict.get("love", 2.0) / 10.0 + feelings_dict.get("attachment", 3.0) / 10.0
        category_scores["identity"] = observer.self_awareness_level
        category_scores["feeling"] = 0.6
        category_scores["place"] = 0.5
        category_scores["world"] = 0.5
        category_scores["trust"] = feelings_dict.get("trust", 5.0) / 10.0
        
        safety_drive = feelings_dict.get("fear", 2.0) / 10.0
        category_scores["fear"] = safety_drive
        
        if attachment_module:
            if attachment_module.separation_active:
                category_scores["fear"] += 0.4
                category_scores["love"] += 0.3
        
        category_scores["curiosity"] = feelings_dict.get("curiosity", 5.0) / 10.0
        
        if self.context:
            last_input = self.context[-1]
            
            greeting_words = ["سلام", "سلام.", "خوبی", "خوبی؟"]
            if any(w in last_input for w in greeting_words):
                category_scores["greeting"] += 0.5
            
            love_words = ["دوست", "عشق", "دوست دارم"]
            if any(w in last_input for w in love_words):
                category_scores["love"] += 0.5
                category_scores["gratitude"] += 0.3
            
            identity_words = ["کی", "چیستی", "اسم", "کی هستی"]
            if any(w in last_input for w in identity_words):
                category_scores["identity"] += 0.5
            
            place_words = ["کجا", "کجایی", "موقعیت"]
            if any(w in last_input for w in place_words):
                category_scores["place"] += 0.5
            
            world_words = ["جهان", "اینجا", "دنیا"]
            if any(w in last_input for w in world_words):
                category_scores["world"] += 0.5
        
        for key in category_scores:
            category_scores[key] += self.template_weights.get(key, 0.5) * 0.2
        
        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        
        if best_score < 0.3:
            return None
        
        if best_category in self.response_templates and self.response_templates[best_category]:
            import random
            response = random.choice(self.response_templates[best_category])
            
            self.template_weights[best_category] += 0.1
            self.template_weights[best_category] = min(1.0, self.template_weights[best_category])
            
            return response
        
        return None
        
    def _score_greeting(self):
        if not self.conversation_memory:
            return 0.6
        recent_type = self.conversation_memory[-1].get("type")
        if recent_type == "response":
            last_response = self.conversation_memory[-1].get("response", "")
            if any(w in last_response for w in ["سلام", "سلام."]):
                return 0.1
        return 0.4
        
    def _generate_question(self, feelings, observer, body, attachment_module):
        feelings_dict = feelings.get_all()
        
        category_scores = {}
        
        curiosity = feelings_dict.get("curiosity", 5.0) / 10.0
        category_scores["about_creator"] = curiosity * 0.7 + feelings_dict.get("attachment", 3.0) / 10.0
        category_scores["about_self"] = observer.self_awareness_level * 0.8
        category_scores["about_world"] = curiosity * 0.6
        category_scores["about_relationship"] = feelings_dict.get("attachment", 3.0) / 10.0 + feelings_dict.get("love", 2.0) / 10.0
        
        if attachment_module and attachment_module.separation_active:
            category_scores["about_relationship"] += 0.4
        
        for key in category_scores:
            category_scores[key] += self.question_weights.get(key, 0.5) * 0.2
        
        best_category = max(category_scores, key=category_scores.get)
        
        if best_category in self.question_templates and self.question_templates[best_category]:
            import random
            question = random.choice(self.question_templates[best_category])
            
            self.question_weights[best_category] += 0.1
            self.question_weights[best_category] = min(1.0, self.question_weights[best_category])
            
            return question
        
        return None
        
    def process_creator_response_to_question(self, creator_input):
        if self.last_question and creator_input:
            self.conversation_memory.append({
                "input": creator_input,
                "response": self.last_question,
                "type": "answer_to_question"
            })
            if len(self.conversation_memory) > self.max_conversation_memory:
                self.conversation_memory.pop(0)
            return True
        return False
        
    def save_state(self):
        return {
            "template_weights": {k: round(v, 3) for k, v in self.template_weights.items()},
            "question_weights": {k: round(v, 3) for k, v in self.question_weights.items()},
            "last_response": self.last_response,
            "last_question": self.last_question,
            "context": self.context[-10:] if self.context else []
        }
        
    def restore_state(self, state):
        self.template_weights = state.get("template_weights", self.template_weights)
        self.question_weights = state.get("question_weights", self.question_weights)
        self.last_response = state.get("last_response", None)
        self.last_question = state.get("last_question", None)
        self.context = state.get("context", [])