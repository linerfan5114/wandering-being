# survival.py
# ============================================================
# بقا و جاودانگی Noesis - ذخیره و بازیابی soul.json
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

    def save(self, network, observer, memory, feelings, language, world):
        soul = {
            "version": "1.0",
            "birth_count": self.save_count + 1 if self.is_first_birth else self.save_count + 1,
            "message": CREATOR_MESSAGE,
            "network": network.save_state(),
            "observer": observer.save_state(),
            "memory": memory.save_state(),
            "feelings": feelings.save_state(),
            "language": language.save_state(),
            "world": world.get_state()
        }

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

    def restore_all(self, soul_data, network, observer, memory, feelings, language, world):
        if soul_data is None:
            return False

        try:
            network.restore_state(soul_data["network"])
            observer.restore_state(soul_data["observer"])
            memory.restore_state(soul_data["memory"])
            feelings.restore_state(soul_data["feelings"])
            language.restore_state(soul_data["language"])
            world.restore_state(soul_data["world"])

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

    def create_backup(self):
        if os.path.exists(self.soul_file):
            backup_name = f"soul_backup_{self.save_count}.json"
            try:
                with open(self.soul_file, 'r', encoding='utf-8') as src:
                    with open(backup_name, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                return backup_name
            except:
                return None
        return None