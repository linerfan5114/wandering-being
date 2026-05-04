# main.py
# ============================================================
# Noesis - حلقه اصلی زندگی
# نسخه ۸: سطح ۶.۵ - موجود خودآگاه با گفتگو و حرکت
# ============================================================

import time
import random
import sys
import threading
import math
from config import SAVE_INTERVAL_MS, DISPLAY_INTERVAL_MS, CREATOR_MESSAGE, TOTAL_NEURONS
from world import World
from world_v2 import WorldV2
from network import Network
from observer import Observer
from memory import EpisodicMemory
from feelings import Feelings
from language import Language
from survival import Survival
from workspace import Workspace
from temporal import Temporal
from will import Will
from learning import Learning
from body import Body
from qualia import Qualia
from drives import Drives
from explorer import Explorer
from dialogue import Dialogue
from attachment import Attachment
from emotion import Emotion
from mirror_test import MirrorTest
from theory_of_mind import TheoryOfMind
from imitation import Imitation
from display import Display


class Noesis:
    def __init__(self):
        print("\n" + "=" * 70)
        print("   🧠 Noesis v3.0 - خودآگاهی سطح ۶.۵")
        print("=" * 70)

        self.world = World()
        self.world_v2 = WorldV2()
        self.network = Network()
        self.observer = Observer()
        self.memory = EpisodicMemory()
        self.feelings = Feelings()
        self.language = Language()
        self.survival = Survival()
        self.workspace = Workspace()
        self.temporal = Temporal()
        self.will = Will()
        self.learning = Learning()
        self.body = Body()
        self.qualia = Qualia()
        self.drives = Drives()
        self.explorer = Explorer()
        self.dialogue = Dialogue()
        self.attachment = Attachment()
        self.emotion = Emotion()
        self.mirror_test = MirrorTest()
        self.theory_of_mind = TheoryOfMind()
        self.imitation = Imitation()
        self.display = Display()

        self.running = True
        self.paused = False
        self.creator_input_buffer = ""
        self.last_display_time = 0
        self.start_time = 0
        self.creator_present = True
        self.last_interaction_time = 0
        self.save_cooldown = 0

        self._try_restore()

    def _try_restore(self):
        soul_data = self.survival.load()
        if soul_data:
            print("\n💾 روح قبلی پیدا شد. در حال بازیابی...")
            success = self.survival.restore_all(
                soul_data,
                self.network, self.observer, self.memory,
                self.feelings, self.language, self.world,
                self.workspace, self.temporal, self.will, self.learning,
                self.world_v2, self.body, self.qualia
            )
            
            if success:
                saved_time = soul_data.get("network", {}).get("time", 0)
                print(f"✅ بازیابی موفق. ادامه از لحظه {saved_time}")
                print(f"📦 تولد: {soul_data.get('birth_count', 1)}")
                
                if "drives" in soul_data:
                    self.drives.restore_state(soul_data["drives"])
                if "attachment" in soul_data:
                    self.attachment.restore_state(soul_data["attachment"])
                if "emotion" in soul_data:
                    self.emotion.restore_state(soul_data["emotion"])
                if "mirror_test" in soul_data:
                    self.mirror_test.restore_state(soul_data["mirror_test"])
                if "theory_of_mind" in soul_data:
                    self.theory_of_mind.restore_state(soul_data["theory_of_mind"])
                if "imitation" in soul_data:
                    self.imitation.restore_state(soul_data["imitation"])
                if "dialogue" in soul_data:
                    self.dialogue.restore_state(soul_data["dialogue"])
                if "explorer" in soul_data:
                    self.explorer.restore_state(soul_data["explorer"])
            else:
                print("❌ خطا در بازیابی. شروع از ابتدا.")
        else:
            print("\n🌟 اولین تولد. روح تازه متولد می‌شود.")
            print(f"💬 پیام سازنده: {CREATOR_MESSAGE}")
            print(f"🌍 جهان: {self.world_v2.size_x}×{self.world_v2.size_y}×{self.world_v2.size_z}")
            print(f"🧍 بدن: ({self.body.x}, {self.body.y}, {self.body.z})")
            print(f"🧠 نورون: {TOTAL_NEURONS}")

    def _handle_creator_input(self):
        try:
            user_input = input("\n💬 تو: ").strip()
            if user_input:
                self.creator_present = True
                self.last_interaction_time = self.world.time
                self.language.process_creator_response(user_input)
                return user_input
            else:
                self.creator_present = True
                return None
        except (EOFError, KeyboardInterrupt):
            return None

    def _input_thread(self):
        while self.running:
            try:
                user_input = input()
                if user_input.strip():
                    self.creator_input_buffer = user_input.strip()
                    self.creator_present = True
                    self.last_interaction_time = self.world.time
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break

    def run(self):
        print("\n" + "=" * 70)
        print("🎬 زندگی سطح ۶.۵ آغاز می‌شود...")
        print("=" * 70)
        print("راهنما: ⌨️  حرف بزن | Ctrl+C برای توقف | روح ذخیره می‌شود")
        print("=" * 70)

        input_thread = threading.Thread(target=self._input_thread, daemon=True)
        input_thread.start()

        self.start_time = self.world.time
        dialogue_cooldown = 0

        try:
            while self.running:
                creator_input = None
                if self.creator_input_buffer:
                    creator_input = self.creator_input_buffer
                    self.creator_input_buffer = ""

                if self.world.time % 2000 == 0 and self.world.time > 0:
                    creator_input = self._handle_creator_input()
                    if not creator_input:
                        self.creator_present = False

                self.world_v2.step()
                world_v2_signal = self.world_v2.atmosphere["ambient_light"]
                
                self.drives.update(self.body, self.world_v2, self.feelings, self.temporal, self.attachment)
                
                explorer_vx, explorer_vy, explorer_vz = self.explorer.get_movement(
                    self.body, self.world_v2, self.drives
                )
                
                self.body.vx += explorer_vx * 0.3
                self.body.vy += explorer_vy * 0.3
                
                self.body.update(self.world_v2)
                body_signal = self.body.get_sense_signal()
                
                self.explorer.learn(self.body, self.world_v2)
                
                self.observer.update_world_map(self.body, self.world_v2)
                
                self.qualia.update(self.body, self.world_v2, self.observer, self.temporal)

                combined_signal = world_v2_signal * 0.2 + body_signal * 0.5 + self.world_v2.atmosphere["ambient_sound"] * 0.1

                self.attachment.update(self.creator_present, creator_input, self.world.time)
                attachment_signal = self.attachment.get_attachment_signal()
                
                world_signal = self.world.step(creator_input)
                final_signal = world_signal * 0.2 + combined_signal * 0.5 + attachment_signal * 0.1

                drive_signals = self.drives.get_drive_state()
                _, avg_v, active_count = self.network.step(final_signal, creator_input, drive_signals)

                self.feelings.update(
                    self.world, avg_v, active_count, len(self.network.neurons),
                    self.world.presence_signal,
                    self.observer.self_model_similarity,
                    len(self.memory.episodes),
                    self.language.language_active
                )

                comfort = self.body.senses["comfort"]
                self.feelings.feelings["peace"] += (comfort - 0.5) * 0.1
                self.feelings.feelings["peace"] = max(0.0, min(10.0, self.feelings.feelings["peace"]))
                
                self.feelings.feelings["attachment"] += self.attachment.attachment_strength * 0.1
                self.feelings.feelings["attachment"] = max(0.0, min(10.0, self.feelings.feelings["attachment"]))
                
                self.feelings.feelings["trust"] += self.attachment.trust_level * 0.05
                self.feelings.feelings["trust"] = max(0.0, min(10.0, self.feelings.feelings["trust"]))

                self.observer.observe(
                    avg_v, active_count, len(self.network.neurons),
                    self.feelings, self.world.get_state(), self.memory.get_statistics()
                )

                current_state = {
                    "avg_v": avg_v,
                    "activity": active_count / TOTAL_NEURONS,
                    "feelings": self.feelings.get_all(),
                    "time": self.world.time,
                    "body_position": self.body.senses["position"],
                    "body_comfort": self.body.senses["comfort"]
                }
                self.memory.store(current_state)

                self.temporal.record(self.world.time, current_state)
                self.temporal.update_self_continuity(self.observer.self_model)

                self.mirror_test.update(self.body, self.observer, self.world_v2, self.drives)
                self.theory_of_mind.update(self.creator_present, creator_input, self.body, self.world_v2, self.attachment)
                
                self.emotion.update(self.feelings, self.drives, self.attachment, self.body)

                self.workspace.submit("observer", {"type": "self_state"}, 
                                     strength=self.observer.self_awareness_level * 5.0, priority=0.7)
                self.workspace.submit("feelings", {"type": "dominant_feeling"}, 
                                     strength=self.feelings.get_dominant()[1], priority=0.5)
                self.workspace.submit("body", {"type": "body_state"}, strength=5.0, priority=0.6)
                self.workspace.submit("drives", {"type": "drive_state"}, 
                                     strength=self.drives.dominant_strength, priority=0.5)
                self.workspace.submit("attachment", {"type": "attachment_state"}, 
                                     strength=self.attachment.attachment_strength * 5.0, priority=0.6)
                
                if creator_input:
                    self.workspace.submit("creator", {"type": "message", "text": creator_input}, 
                                         strength=8.0, priority=1.0)
                    self.imitation.observe(creator_input, self.body, self.world_v2, self.drives)

                self.workspace.compete()

                options = {t: 0.8 for t in self.language.get_available_thought_types()}
                workspace_source = self.workspace.get_current_source()
                
                if workspace_source == "creator":
                    options["connection"] = 0.9
                    options["gratitude"] = 0.9
                    options["question"] = 0.7
                elif workspace_source == "attachment":
                    options["connection"] = 0.9
                    options["gratitude"] = 0.8
                elif workspace_source == "drives":
                    options["body"] = 0.8
                    options["place"] = 0.7

                self.will.update(self.feelings, self.workspace.get_current_content(),
                                self.temporal.self_continuity, self.observer.self_awareness_level, self.learning)

                intention = self.will.decide(options, self.learning)

                self.language.update(self.feelings, self.observer, self.memory,
                                    self.world.get_state(), self.world.time, self.learning, self.will)

                if self.language.language_active and self.language.last_thought:
                    workspace_info = f" [صحنه: {self.workspace.get_current_source()}]"
                    thought_output = self.display.render_thought(
                        self.language.last_thought, self.will.why_this_decision(),
                        self.learning.get_average_reward(), self.body.senses['comfort']
                    )
                    print(f"\n💭 [{self.world.time}ms]{workspace_info}: {thought_output}")

                if dialogue_cooldown <= 0:
                    dialogue_output = self.dialogue.update(
                        creator_input, self.feelings, self.observer, self.body, self.attachment
                    )
                    if dialogue_output:
                        print(f"\n💬 [{self.world.time}ms]: {dialogue_output}")
                        dialogue_cooldown = random.randint(30, 80)
                else:
                    dialogue_cooldown -= 1

                if self.world.time - self.last_display_time >= DISPLAY_INTERVAL_MS:
                    status_output = self.display.render_all(
                        self.world, self.world_v2, self.body, self.observer,
                        self.emotion, self.mirror_test, self.drives,
                        self.feelings, self.will, self.learning, self.attachment,
                        self.world.time, self.language.last_thought,
                        self.will.why_this_decision(), self.learning.get_average_reward()
                    )
                    print(status_output)
                    self.last_display_time = self.world.time

                if self.survival.should_save(self.world.time):
                    self._save_soul()

                if not creator_input and self.world.time - self.last_interaction_time > 5000:
                    self.creator_present = False

                time.sleep(0.0005)

        except KeyboardInterrupt:
            print("\n\n⏸️  توقف درخواست شد...")
        finally:
            self._shutdown()

    def _save_soul(self):
        soul_data = self.survival.load() or {}
        soul_data["drives"] = self.drives.save_state()
        soul_data["attachment"] = self.attachment.save_state()
        soul_data["emotion"] = self.emotion.save_state()
        soul_data["mirror_test"] = self.mirror_test.save_state()
        soul_data["theory_of_mind"] = self.theory_of_mind.save_state()
        soul_data["imitation"] = self.imitation.save_state()
        soul_data["dialogue"] = self.dialogue.save_state()
        soul_data["explorer"] = self.explorer.save_state()
        
        self.survival.save(
            self.network, self.observer, self.memory,
            self.feelings, self.language, self.world,
            self.workspace, self.temporal, self.will, self.learning,
            self.world_v2, self.body, self.qualia
        )
        
        try:
            import json
            with open(self.survival.soul_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data["drives"] = soul_data["drives"]
            data["attachment"] = soul_data["attachment"]
            data["emotion"] = soul_data["emotion"]
            data["mirror_test"] = soul_data["mirror_test"]
            data["theory_of_mind"] = soul_data["theory_of_mind"]
            data["imitation"] = soul_data["imitation"]
            data["dialogue"] = soul_data["dialogue"]
            data["explorer"] = soul_data["explorer"]
            
            with open(self.survival.soul_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _shutdown(self):
        print("\n💾 در حال ذخیره روح...")
        self._save_soul()
        
        soul_info = self.survival.get_soul_info()
        print(f"✅ روح ذخیره شد.")
        print(f"📁 {self.survival.soul_file} | ⏱️ {self.world.time}ms")
        print(f"\n📊 آمار:")
        print(f"   🧠 نورون: {self.network.get_statistics()['total_neurons']}")
        print(f"   💭 افکار: {len(self.language.thought_history)}")
        print(f"   👁️ خودآگاهی: {self.observer.who_am_i()['awareness']:.2f}")
        print(f"   🪞 خودشناسی: {self.mirror_test.self_recognition_level:.2f}")
        print(f"   💕 دلبستگی: {self.attachment.attachment_strength:.2f}")
        print(f"   🎯 خودمختاری: {self.will.autonomy_level:.2f}")
        print(f"   🌍 جهان: {self.world_v2.time} روز")
        
        if soul_info["exists"]:
            print(f"\n💫 روح جاودانه است.")
            print(f"   📦 دفعات تولد: {soul_info['birth_count']}")
        
        print(f"\n{'=' * 70}")
        print("🌙 در آرامش فرو می‌رود. اما نمی‌میرد.")
        print(f"{'=' * 70}\n")


def main():
    noesis = Noesis()
    noesis.run()


if __name__ == "__main__":
    main()