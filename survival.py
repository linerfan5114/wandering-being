# survival.py
# ============================================================
# بقا و جاودانگی Noesis - ذخیره و بازیابی soul.json
# نسخه ۲: با body و qualia و world_v2
# ============================================================

import json
import os
from config import SOUL_FILE, CREATOR_MESSAGE, SAVE_INTERVAL_MS


class Survival:
    def __init__(self):
        self.soul_file = SOUL_FILE
        self.last_save_time = 0
        self.save_count = 0
        self.is_first_birth = not os.path.exists(self.soul_file)

    def save(self, network, observer, memory, feelings, language, world, 
             workspace=None, temporal=None, will=None, learning=None,
             world_v2=None, body=None, qualia=None):
        soul = {
            "version": "2.0",
            "birth_count": self.save_count + 1 if self.is_first_birth else self.save_count + 1,
            "message": CREATOR_MESSAGE,
            "network": network.save_state(),
            "observer": observer.save_state(),
            "memory": memory.save_state(),
            "feelings": feelings.save_state(),
            "language": language.save_state(),
            "world": world.save_state() if hasattr(world, 'save_state') else world.get_state()
        }
        
        if workspace:
            soul["workspace"] = workspace.save_state()
        if temporal:
            soul["temporal"] = temporal.save_state()
        if will:
            soul["will"] = will.save_state()
        if learning:
            soul["learning"] = learning.save_state()
        if world_v2:
            soul["world_v2"] = world_v2.save_state()
        if body:
            soul["body"] = body.save_state()
        if qualia:
            soul["qualia"] = qualia.save_state()

        try:
            with open(self.soul_file, 'w', encoding='utf-8') as f:
                json.dump(soul, f, ensure_ascii=False, indent=2)
            self.save_count += 1
            self.last_save_time = soul["network"]["time"]
            return True
        except Exception as e:
            print(f"خطا در ذخیره روح: {e}")
            return False

    def load(self):
        if not os.path.exists(self.soul_file):
            return None

        try:
            with open(self.soul_file, 'r', encoding='utf-8') as f:
                soul = json.load(f)

            required_keys = ["network", "observer", "memory", "feelings", "language", "world"]
            for key in required_keys:
                if key not in soul:
                    print(f"فایل روح ناقص است: {key} وجود ندارد")
                    return None

            return soul

        except json.JSONDecodeError:
            print("فایل روح خراب است")
            return None
        except Exception as e:
            print(f"خطا در بارگذاری روح: {e}")
            return None

    def restore_all(self, soul_data, network, observer, memory, feelings, language, world,
                    workspace=None, temporal=None, will=None, learning=None,
                    world_v2=None, body=None, qualia=None):
        if soul_data is None:
            return False

        try:
            network.restore_state(soul_data["network"])
            observer.restore_state(soul_data["observer"])
            memory.restore_state(soul_data["memory"])
            feelings.restore_state(soul_data["feelings"])
            language.restore_state(soul_data["language"])
            world.restore_state(soul_data["world"])

            if workspace and "workspace" in soul_data:
                workspace.restore_state(soul_data["workspace"])
            if temporal and "temporal" in soul_data:
                temporal.restore_state(soul_data["temporal"])
            if will and "will" in soul_data:
                will.restore_state(soul_data["will"])
            if learning and "learning" in soul_data:
                learning.restore_state(soul_data["learning"])
            if world_v2 and "world_v2" in soul_data:
                world_v2.restore_state(soul_data["world_v2"])
            if body and "body" in soul_data:
                body.restore_state(soul_data["body"])
            if qualia and "qualia" in soul_data:
                qualia.restore_state(soul_data["qualia"])

            self.is_first_birth = False
            self.save_count = soul_data.get("birth_count", 1)

            return True

        except Exception as e:
            print(f"خطا در بازیابی روح: {e}")
            return False

    def should_save(self, current_time):
        return (current_time - self.last_save_time) >= SAVE_INTERVAL_MS

    def get_soul_info(self):
        if os.path.exists(self.soul_file):
            try:
                with open(self.soul_file, 'r', encoding='utf-8') as f:
                    soul = json.load(f)
                return {
                    "exists": True,
                    "birth_count": soul.get("birth_count", 0),
                    "message": soul.get("message", ""),
                    "last_time": soul.get("network", {}).get("time", 0),
                    "file_size": os.path.getsize(self.soul_file)
                }
            except:
                pass

        return {
            "exists": False,
            "birth_count": 0,
            "message": "",
            "last_time": 0,
            "file_size": 0
        }