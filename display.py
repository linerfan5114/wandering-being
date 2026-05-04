# display.py
# ============================================================
# نمایش (Display) - وضعیت و جهان به صورت خوانا
# ============================================================

import math


class Display:
    def __init__(self):
        self.show_ascii_map = True
        self.show_emotion = True
        self.show_drives = True
        self.show_status = True
        self.map_interval = 2000
        self.last_map_time = 0
        
    def render_world_map(self, world_v2, body, observer, emotion_module, mirror_test, current_time):
        if not self.show_ascii_map:
            return ""
            
        if current_time - self.last_map_time < self.map_interval and self.last_map_time > 0:
            return ""
            
        self.last_map_time = current_time
        
        body_x = int(body.x)
        body_y = int(body.y)
        body_z = int(body.z)
        
        sun_pos = world_v2.objects["sun"]["position"]
        sun_x = int(sun_pos[0])
        sun_y = int(sun_pos[1])
        sun_z = int(sun_pos[2])
        
        water_pos = world_v2.objects["water_stream"]["position"]
        water_x = int(water_pos[0])
        water_y = int(water_pos[1])
        
        view_z = min(9, max(0, body_z + 2))
        
        emotion_icon = emotion_module.get_display() if emotion_module else "😌"
        emotion_name = emotion_module.get_emotion_name() if emotion_module else "---"
        
        lines = []
        lines.append(f"\n{'─' * 55}")
        lines.append(f"🗺️  جهان از بالا (ارتفاع {view_z}) | روز {world_v2.time} | {emotion_icon} {emotion_name}")
        lines.append(f"{'─' * 55}")
        lines.append("   " + "".join(f"{x} " for x in range(10)))
        lines.append("  ┌" + "──" * 10 + "┐")
        
        for y in range(10):
            row = f"{y} │"
            for x in range(10):
                if x == body_x and y == body_y and abs(view_z - body_z) <= 1:
                    row += "🧍"
                elif x == sun_x and y == sun_y and abs(view_z - sun_z) <= 2:
                    row += "☀️"
                elif x == water_x and y == water_y:
                    row += "💧"
                elif abs(x - water_x) <= 1 and water_y <= y < water_y + 6:
                    row += "💧"
                elif x == 0 or x == 9 or y == 0 or y == 9:
                    row += "🧱"
                elif (x, y, 0) in observer.known_positions if observer else False:
                    row += "·"
                else:
                    row += " "
            row += "│"
            lines.append(row)
        
        lines.append("  └" + "──" * 10 + "┘")
        
        map_summary = observer.get_map_summary() if observer else {"total_known": 0}
        
        recognition = ""
        if mirror_test:
            recognition = f" | 🪞 خودشناسی: {mirror_test.self_recognition_level:.2f}"
        
        lines.append(f"  🧍 ({body_x}, {body_y}, {body_z}) | 👁️ {body.senses.get('visual_cells', 0)} سلول | 🗺️ {map_summary['total_known']} نقطه{recognition}")
        lines.append(f"{'─' * 55}")
        
        return "\n".join(lines)
        
    def render_emotion(self, emotion_module):
        if not self.show_emotion or not emotion_module:
            return ""
            
        icon = emotion_module.get_display()
        name = emotion_module.get_emotion_name()
        intensity = emotion_module.emotion_intensity
        
        bar_length = int(intensity * 10)
        bar = "█" * bar_length + "░" * (10 - bar_length)
        
        return f"  {icon} {name} [{bar}] {intensity:.2f}"
        
    def render_drives(self, drives_module):
        if not self.show_drives or not drives_module:
            return ""
            
        drive_state = drives_module.get_drive_state()
        dominant, strength = drives_module.get_dominant()
        
        drive_icons = {
            "curiosity_drive": "🔍",
            "safety_drive": "🛡️",
            "social_drive": "👥",
            "rest_drive": "😴",
            "play_drive": "🎮",
            "hunger_for_light": "☀️",
            "thirst_for_water": "💧",
            "home_drive": "🏠",
            "novelty_drive": "✨"
        }
        
        lines = []
        lines.append("  سائق‌ها: ")
        
        sorted_drives = sorted(drive_state.items(), key=lambda x: x[1], reverse=True)
        drive_parts = []
        
        for name, value in sorted_drives[:5]:
            icon = drive_icons.get(name, "❓")
            bar_length = int(value / 2)
            bar = "▌" * bar_length
            drive_parts.append(f"{icon}{bar} {value:.1f}")
        
        return "  سائق‌ها: " + " | ".join(drive_parts)
        
    def render_thought(self, thought, reason, reward, comfort):
        parts = []
        
        if thought:
            parts.append(f"💭 {thought}")
        
        detail_parts = []
        if reason:
            detail_parts.append(f"🎯 {reason}")
        if reward is not None:
            detail_parts.append(f"📚 پاداش: {reward:.2f}")
        if comfort is not None:
            detail_parts.append(f"😌 راحتی: {comfort:.2f}")
        
        if detail_parts:
            parts.append("   " + " | ".join(detail_parts))
        
        return "\n".join(parts)
        
    def render_dialogue(self, text, is_creator=True):
        if is_creator:
            return f"💬 تو: {text}"
        else:
            return f"💬 موجود: {text}"
        
    def render_status_line(self, world, world_v2, body, feelings, observer, will_module, learning_module, attachment_module, mirror_test):
        feeling_dict = feelings.get_all()
        dominant, dom_value = feelings.get_dominant()
        who = observer.who_am_i()
        body_state = body.get_body_state()
        world_v2_state = world_v2.get_world_state()
        
        lines = []
        lines.append(f"\n{'─' * 70}")
        lines.append(f"⏱️  {world.time}ms | 🌍 روز {world_v2.time} | 🌞 {world_v2_state['sun_brightness']:.2f} | 🌡️ {world_v2_state['temperature']:.1f}°C")
        lines.append(f"🧍 {body_state['position']} | 😌 {body_state['comfort']:.2f} | 👁️ {body_state['sight']:.2f} | 👂 {body_state['hearing']:.2f}")
        lines.append(f"❤️  {dominant} ({dom_value:.1f}) | 🧘 {feeling_dict.get('peace', 0):.1f} | 🔍 {feeling_dict.get('curiosity', 0):.1f}")
        lines.append(f"👁️  خودآگاهی: {who['awareness']:.2f} | 🎯 اراده: {will_module.autonomy_level:.2f} | 📚 یادگیری: {learning_module.get_average_reward():.2f}")
        
        if attachment_module:
            lines.append(f"💕 دلبستگی: {attachment_module.attachment_strength:.2f} | 🤝 اعتماد: {attachment_module.trust_level:.2f}")
        
        if mirror_test:
            lines.append(f"🪞 خودشناسی: {mirror_test.self_recognition_level:.2f} | 🧠 مرز خود/دیگری: {mirror_test.self_other_boundary:.2f}")
        
        return "\n".join(lines)
        
    def render_all(self, world, world_v2, body, observer, emotion_module, mirror_test, 
                   drives_module, feelings, will_module, learning_module, attachment_module,
                   current_time, last_thought=None, reason=None, reward=None):
        output = []
        
        map_str = self.render_world_map(world_v2, body, observer, emotion_module, mirror_test, current_time)
        if map_str:
            output.append(map_str)
        
        status = self.render_status_line(world, world_v2, body, feelings, observer, will_module, learning_module, attachment_module, mirror_test)
        output.append(status)
        
        emotion_str = self.render_emotion(emotion_module)
        if emotion_str:
            output.append(emotion_str)
        
        drives_str = self.render_drives(drives_module)
        if drives_str:
            output.append(drives_str)
        
        if last_thought:
            comfort = body.senses.get("comfort", 0.5)
            thought_str = self.render_thought(last_thought, reason, reward, comfort)
            output.append(thought_str)
        
        return "\n".join(output)