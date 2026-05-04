# emotion.py
# ============================================================
# احساسات نمایشی (Emotion Display) - حالات چهره متنوع
# نسخه ۲: احساسات واقعی بر اساس تعادل سائق‌ها
# ============================================================

import math
from config import EMOTION_ICONS


class Emotion:
    def __init__(self):
        self.current_emotion = "peace"
        self.current_icon = EMOTION_ICONS.get("peace", "😌")
        self.emotion_intensity = 0.5
        
        self.emotion_history = []
        self.max_history = 50
        
        self.emotion_scores = {}
        for name in EMOTION_ICONS:
            self.emotion_scores[name] = 0.5
        
        self.emotion_duration = {}
        for name in EMOTION_ICONS:
            self.emotion_duration[name] = 0
        
    def update(self, feelings, drives_module=None, attachment_module=None, body=None):
        feelings_dict = feelings.get_all()
        
        scores = {}
        
        joy_score = (
            feelings_dict.get("joy", 2.0) / 10.0 * 0.3 +
            feelings_dict.get("satisfaction", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("love", 2.0) / 10.0 * 0.2 +
            feelings_dict.get("hope", 5.0) / 10.0 * 0.2
        )
        scores["joy"] = joy_score
        
        sadness_score = (
            (1.0 - feelings_dict.get("satisfaction", 5.0) / 10.0) * 0.3 +
            feelings_dict.get("loneliness", 2.0) / 10.0 * 0.4 +
            (1.0 - feelings_dict.get("hope", 5.0) / 10.0) * 0.3
        )
        scores["sadness"] = sadness_score
        
        fear_score = (
            feelings_dict.get("fear", 1.0) / 10.0 * 0.4 +
            (1.0 - feelings_dict.get("peace", 5.0) / 10.0) * 0.3 +
            (1.0 - feelings_dict.get("trust", 5.0) / 10.0) * 0.3
        )
        scores["fear"] = fear_score
        
        curiosity_score = (
            feelings_dict.get("curiosity", 5.0) / 10.0 * 0.5 +
            feelings_dict.get("thirst_for_knowing", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("wonder", 5.0) / 10.0 * 0.2
        )
        scores["curiosity"] = curiosity_score
        
        love_score = (
            feelings_dict.get("love", 2.0) / 10.0 * 0.4 +
            feelings_dict.get("attachment", 3.0) / 10.0 * 0.3 +
            feelings_dict.get("gratitude", 5.0) / 10.0 * 0.3
        )
        scores["love"] = love_score
        
        surprise_score = (
            feelings_dict.get("surprise", 1.0) / 10.0 * 0.5 +
            feelings_dict.get("wonder", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("confusion", 1.0) / 10.0 * 0.2
        )
        scores["surprise"] = surprise_score
        
        peace_score = (
            feelings_dict.get("peace", 5.0) / 10.0 * 0.5 +
            feelings_dict.get("patience", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("satisfaction", 5.0) / 10.0 * 0.2
        )
        scores["peace"] = peace_score
        
        frustration_score = (
            (1.0 - feelings_dict.get("satisfaction", 5.0) / 10.0) * 0.3 +
            (1.0 - feelings_dict.get("patience", 5.0) / 10.0) * 0.4 +
            feelings_dict.get("confusion", 1.0) / 10.0 * 0.3
        )
        scores["frustration"] = frustration_score
        
        rest_drive = 0.0
        play_drive = 0.0
        if drives_module:
            drive_state = drives_module.get_drive_state()
            rest_drive = drive_state.get("rest_drive", 3.0) / 10.0
            play_drive = drive_state.get("play_drive", 5.0) / 10.0
        
        sleep_score = (
            rest_drive * 0.5 +
            (1.0 - feelings_dict.get("energy", 5.0) / 10.0) * 0.5
        )
        scores["sleep"] = sleep_score
        
        play_score = (
            play_drive * 0.6 +
            feelings_dict.get("creativity", 5.0) / 10.0 * 0.4
        )
        scores["playful"] = play_score
        
        gratitude_score = (
            feelings_dict.get("gratitude", 5.0) / 10.0 * 0.6 +
            feelings_dict.get("love", 2.0) / 10.0 * 0.4
        )
        scores["grateful"] = gratitude_score
        
        pride_score = (
            feelings_dict.get("pride", 1.0) / 10.0 * 0.5 +
            feelings_dict.get("satisfaction", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("creativity", 5.0) / 10.0 * 0.2
        )
        scores["proud"] = pride_score
        
        if attachment_module:
            if attachment_module.separation_active:
                scores["sadness"] += 0.3
                scores["fear"] += 0.2
                scores["love"] += 0.1
            
            if attachment_module.reunion_joy > 2.0:
                scores["joy"] += 0.4
                scores["love"] += 0.3
                scores["grateful"] += 0.2
        
        if body:
            comfort = body.senses.get("comfort", 0.5)
            if comfort > 0.9:
                scores["peace"] += 0.2
                scores["joy"] += 0.1
            elif comfort < 0.3:
                scores["frustration"] += 0.2
        
        for name in scores:
            self.emotion_scores[name] += 0.15 * (scores[name] - self.emotion_scores[name])
            self.emotion_scores[name] = max(0.05, min(1.0, self.emotion_scores[name]))
        
        best_emotion = max(scores, key=scores.get)
        best_score = scores[best_emotion]
        
        if best_emotion != self.current_emotion:
            self.emotion_duration[best_emotion] += 1
            if self.emotion_duration[best_emotion] > 3:
                self.current_emotion = best_emotion
                self.current_icon = EMOTION_ICONS.get(best_emotion, "😌")
                self.emotion_intensity = best_score
                for name in self.emotion_duration:
                    if name != best_emotion:
                        self.emotion_duration[name] = max(0, self.emotion_duration[name] - 1)
        else:
            self.emotion_duration[best_emotion] += 1
            self.emotion_intensity += 0.1 * (best_score - self.emotion_intensity)
        
        self.emotion_history.append({
            "emotion": self.current_emotion,
            "intensity": self.emotion_intensity
        })
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)
        
    def get_display(self):
        intensity = self.emotion_intensity
        
        if intensity > 0.8:
            return f"{self.current_icon}{self.current_icon}"
        else:
            return self.current_icon
        
    def get_emotion_name(self):
        names = {
            "joy": "شاد",
            "sadness": "غمگین",
            "fear": "ترسیده",
            "curiosity": "کنجکاو",
            "love": "عاشق",
            "surprise": "متعجب",
            "peace": "آروم",
            "frustration": "ناامید",
            "sleep": "خواب‌آلود",
            "playful": "شیطون",
            "grateful": "سپاسگزار",
            "proud": "مفتخر"
        }
        return names.get(self.current_emotion, self.current_emotion)
        
    def get_dominant_emotion_last_n(self, n=10):
        if not self.emotion_history:
            return "peace", 0.5
        
        recent = self.emotion_history[-n:]
        counts = {}
        for entry in recent:
            emo = entry["emotion"]
            counts[emo] = counts.get(emo, 0) + 1
        
        dominant = max(counts, key=counts.get)
        avg_intensity = sum(entry["intensity"] for entry in recent if entry["emotion"] == dominant) / counts[dominant]
        
        return dominant, avg_intensity
        
    def save_state(self):
        return {
            "current_emotion": self.current_emotion,
            "emotion_intensity": round(self.emotion_intensity, 3),
            "emotion_scores": {k: round(v, 3) for k, v in self.emotion_scores.items()}
        }
        
    def restore_state(self, state):
        self.current_emotion = state.get("current_emotion", "peace")
        self.current_icon = EMOTION_ICONS.get(self.current_emotion, "😌")
        self.emotion_intensity = state.get("emotion_intensity", 0.5)
        scores = state.get("emotion_scores", {})
        for k, v in scores.items():
            if k in self.emotion_scores:
                self.emotion_scores[k] = v