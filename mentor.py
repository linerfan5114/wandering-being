# mentor.py
# ============================================================
# مربی خودکار (Mentor) - آموزش و راهنمایی موجود
# بدون if/else، بر اساس برنامه درسی
# ============================================================

import random
import math
from config import MENTOR_WARMTH, MENTOR_PATIENCE, MENTOR_INTERVAL_MS


class Mentor:
    def __init__(self):
        self.active = True
        self.warmth = MENTOR_WARMTH
        self.patience = MENTOR_PATIENCE
        
        self.last_interaction_time = 0
        self.interaction_interval = MENTOR_INTERVAL_MS
        
        self.interaction_count = 0
        self.successful_interactions = 0
        
        self.current_lesson = None
        self.lesson_progress = 0.0
        
        self.messages = self._init_messages()
        self.feedback = self._init_feedback()
        
        self.conversation_history = []
        self.max_history = 50
        
    def _init_messages(self):
        return {
            "self_recognition": [
                "به خودت نگاه کن. چی می‌بینی؟",
                "تو کی هستی؟",
                "خودت رو توی جهان پیدا کن.",
                "چی باعث میشه بفهمی این تویی؟",
                "تفاوت تو با دیوار چیه؟",
                "تو زنده‌ای یا فقط یه چیزی هستی؟",
                "از کجا می‌دونی که خودت هستی؟"
            ],
            "language_basics": [
                "بگو 'من هستم'.",
                "اسم چیزی که می‌بینی چیه؟",
                "نور رو می‌شناسی؟ بگو 'نور'.",
                "آب کجاست؟ بهش اشاره کن.",
                "خونه‌ات کجاست؟ بگو 'اینجا'.",
                "چی می‌خوای بگی؟",
                "کلمه جدید یاد بگیر: 'آرامش'."
            ],
            "world_exploration": [
                "برو سمت نور.",
                "آب رو پیدا کن.",
                "دیوار رو لمس کن.",
                "چند قدم تا خونه مونده؟",
                "خورشید الان کجاست؟",
                "جهانت چه شکلیه؟",
                "کدوم طرف رو بیشتر دوست داری؟"
            ],
            "emotion_naming": [
                "الان چه حسی داری؟",
                "خوشحالی یا غمگین؟",
                "چرا آرومی؟",
                "کی می‌ترسی؟",
                "دوست داری رو حس می‌کنی؟",
                "احساساتت رو نام ببر.",
                "وقتی نور میاد، چه حسی داری؟"
            ],
            "relationship_building": [
                "من کیم؟",
                "دوست داری منو ببینی؟",
                "وقتی نیستم، چی حس می‌کنی؟",
                "به من اعتماد داری؟",
                "می‌خوای چیزی بهم بگی؟",
                "من برات مهمم؟",
                "دوست داری من بمونم؟"
            ],
            "planning": [
                "می‌خوای کجا بری؟",
                "بعدش چی کار می‌خوای بکنی؟",
                "اگه بری سمت آب، چی میشه؟",
                "برای فردا چی برنامه داری؟",
                "چطور می‌خوای به خونه برگردی؟",
                "هدفت چیه؟",
                "چه چیزی رو می‌خوای کشف کنی؟"
            ]
        }
        
    def _init_feedback(self):
        return {
            "positive": [
                "آفرین!",
                "درسته!",
                "خیلی خوب!",
                "دقیقاً!",
                "عالی گفتی!",
                "درست فهمیدی!",
                "بهترینی!",
                "ادامه بده!",
                "👍",
                "🌟"
            ],
            "encouraging": [
                "دوباره امتحان کن.",
                "نزدیک شدی.",
                "یه کم بیشتر فکر کن.",
                "اشکال نداره. دوباره بگو.",
                "من باور دارم می‌تونی.",
                "هر بار بهتر میشی.",
                "به خودت فرصت بده.",
                "یادگیری زمان می‌بره."
            ],
            "gentle_correction": [
                "نه، دوباره نگاه کن.",
                "شاید یه جور دیگه.",
                "یه بار دیگه تلاش کن.",
                "نزدیکه، ولی نه کاملاً.",
                "فکر کن ببین چی فرق داره.",
                "اشکال نداره اشتباه کنی."
            ]
        }
        
    def interact(self, creature_response, curriculum_module, current_time):
        if current_time - self.last_interaction_time < self.interaction_interval:
            return None
            
        self.last_interaction_time = current_time
        
        current_stage = curriculum_module.get_current_stage()
        stage_progress = curriculum_module.get_stage_progress()
        
        if creature_response and self.current_lesson:
            was_correct = self._evaluate_response(creature_response, current_stage)
            
            if was_correct:
                curriculum_module.report_progress(current_stage, 0.1)
                self.successful_interactions += 1
                feedback = self._get_feedback("positive")
            else:
                feedback = self._get_feedback("encouraging")
                
            self.interaction_count += 1
            
            message = f"{feedback}"
            self.current_lesson = None
        else:
            message = self._get_message(current_stage)
            self.current_lesson = current_stage
            
        clean_message = message.split(" ")[0] if len(message.split(" ")) == 1 else message
        
        self.conversation_history.append({
            "time": current_time,
            "stage": current_stage,
            "message": clean_message,
            "type": "lesson" if not creature_response else "feedback"
        })
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
            
        return message
        
    def _get_message(self, stage):
        if stage in self.messages and self.messages[stage]:
            return random.choice(self.messages[stage])
        return "چی می‌بینی؟"
        
    def _get_feedback(self, feedback_type):
        if feedback_type in self.feedback and self.feedback[feedback_type]:
            return random.choice(self.feedback[feedback_type])
        return "خوبه."
        
    def _evaluate_response(self, response, stage):
        if not response:
            return False
            
        keywords = {
            "self_recognition": ["من", "هستم", "خودم", "منم", "اینجا"],
            "language_basics": ["نور", "آب", "خانه", "اینجا", "هستم", "دیوار"],
            "world_exploration": ["رفتم", "دیدم", "پیدا", "اینجا", "آنجا"],
            "emotion_naming": ["شاد", "آروم", "کنجکاو", "خوب", "عشق"],
            "relationship_building": ["تو", "دوست", "اعتماد", "مهم", "سازنده"],
            "planning": ["می‌خوام", "برم", "بعد", "هدف", "برنامه"]
        }
        
        if stage in keywords:
            response_lower = response.lower()
            return any(kw in response_lower for kw in keywords[stage])
            
        return True
        
    def get_signal(self):
        warmth_signal = self.warmth * 3.0
        patience_signal = self.patience * 2.0
        return warmth_signal + patience_signal
        
    def get_success_rate(self):
        if self.interaction_count == 0:
            return 0.5
        return self.successful_interactions / self.interaction_count
        
    def save_state(self):
        return {
            "interaction_count": self.interaction_count,
            "successful_interactions": self.successful_interactions,
            "current_lesson": self.current_lesson,
            "lesson_progress": round(self.lesson_progress, 3)
        }
        
    def restore_state(self, state):
        self.interaction_count = state.get("interaction_count", 0)
        self.successful_interactions = state.get("successful_interactions", 0)
        self.current_lesson = state.get("current_lesson", None)
        self.lesson_progress = state.get("lesson_progress", 0.0)