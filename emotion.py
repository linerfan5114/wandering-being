# emotion.py
# ============================================================
# احساسات نمایشی (Emotion Display) - حالات چهره
# بر اساس وضعیت درونی، بدون if/else
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
        
    def update(self, feelings, drives_module=None, attachment_module=None, body=None):
        feelings_dict = feelings.get_all()
        
        scores = {}
        
        joy_score = (
            feelings_dict.get("joy", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("satisfaction", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("love", 3.0) / 10.0 * 0.2 +
            feelings_dict.get("hope", 5.0) / 10.0 * 0.2
        )
        scores["joy"] = joy_score
        
        sadness_score = (
            (10.0 - feelings_dict.get("satisfaction", 5.0)) / 10.0 * 0.3 +
            feelings_dict.get("loneliness", 2.0) / 10.0 * 0.4 +
            (10.0 - feelings_dict.get("hope", 5.0)) / 10.0 * 0.3
        )
        scores["sadness"] = sadness_score
        
        fear_score = (
            feelings_dict.get("fear", 2.0) / 10.0 * 0.4 +
            (10.0 - feelings_dict.get("peace", 5.0)) / 10.0 * 0.3 +
            (10.0 - feelings_dict.get("trust", 5.0)) / 10.0 * 0.3
        )
        scores["fear"] = fear_score
        
        curiosity_score = (
            feelings_dict.get("curiosity", 5.0) / 10.0 * 0.5 +
            feelings_dict.get("thirst_for_knowing", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("wonder", 5.0) / 10.0 * 0.2
        )
        scores["curiosity"] = curiosity_score
        
        love_score = (
            feelings_dict.get("love", 3.0) / 10.0 * 0.4 +
            feelings_dict.get("attachment", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("gratitude", 5.0) / 10.0 * 0.3
        )
        scores["love"] = love_score
        
        surprise_score = (
            feelings_dict.get("surprise", 2.0) / 10.0 * 0.5 +
            feelings_dict.get("wonder", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("confusion", 2.0) / 10.0 * 0.2
        )
        scores["surprise"] = surprise_score
        
        peace_score = (
            feelings_dict.get("peace", 5.0) / 10.0 * 0.5 +
            feelings_dict.get("patience", 5.0) / 10.0 * 0.3 +
            feelings_dict.get("satisfaction", 5.0) / 10.0 * 0.2
        )
        scores["peace"] = peace_score
        
        frustration_score = (
            (10.0 - feelings_dict.get("satisfaction", 5.0)) / 10.0 * 0.3 +
            (10.0 - feelings_dict.get("patience", 5.0)) / 10.0 * 0.4 +
            feelings_dict.get("confusion", 2.0) / 10.0 * 0.3
        )
        scores["frustration"] = frustration_score
        
        rest_drive = 0.0
        if drives_module:
            drive_state = drives_module.get_drive_state()
            rest_drive = drive_state.get("rest_drive", 5.0) / 10.0
        
        sleep_score = (
            rest_drive * 0.5 +
            (10.0 - feelings_dict.get("energy", 5.0)) / 10.0 * 0.5
        )
        scores["sleep"] = sleep_score
        
        play_score = 0.0
        if drives_module:
            drive_state = drives_module.get_drive_state()
            play_drive = drive_state.get("play_drive", 5.0) / 10.0
            play_score = play_drive * 0.6 + feelings_dict.get("creativity", 5.0) / 10.0 * 0.4
        scores["playful"] = play_score
        
        gratitude_score = (
            feelings_dict.get("gratitude", 5.0) / 10.0 * 0.6 +
            feelings_dict.get("love", 3.0) / 10.0 * 0.4
        )
        scores["grateful"] = gratitude_score
        
        pride_score = (
            feelings_dict.get("pride", 2.0) / 10.0 * 0.5 +
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
        
        for name in scores:
            self.emotion_scores[name] += 0.1 * (scores[name] - self.emotion_scores[name])
            self.emotion_scores[name] = max(0.1, min(1.0, self.emotion_scores[name]))
        
        best_emotion = max(scores, key=scores.get)
        best_score = scores[best_emotion]
        
        self.current_emotion = best_emotion
        self.current_icon = EMOTION_ICONS.get(best_emotion, "😌")
        self.emotion_intensity = best_score
        
        self.emotion_history.append({
            "emotion": best_emotion,
            "intensity": best_score
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