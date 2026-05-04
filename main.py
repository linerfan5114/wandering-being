# main.py
# ============================================================
# Noesis - حلقه اصلی زندگی با جهان فیزیکی و بدن
# نسخه ۶: جهان سه‌بعدی + بدن + کوالیا
# ============================================================

import time
import random
import sys
import threading
from config import SAVE_INTERVAL_MS, DISPLAY_INTERVAL_MS, CREATOR_MESSAGE
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


class Noesis:
    def __init__(self):
        print("\n" + "=" * 70)
        print("     🧠 Noesis - پروژه آگاهی با جهان و بدن")
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

        self.running = True
        self.paused = False
        self.creator_input_buffer = ""
        self.last_display_time = 0
        self.start_time = 0
        self.breath_cycle = 0

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
                print(f"📦 تعداد تولد: {soul_data.get('birth_count', 1)}")
                print(f"💬 پیام سازنده: {soul_data.get('message', '')}")
                print(f"🌍 جهان فیزیکی: روز {self.world_v2.time}")
                print(f"🧍 موقعیت: {self.body.get_body_state()['position']}")
            else:
                print("❌ خطا در بازیابی. شروع از ابتدا.")
        else:
            print("\n🌟 اولین تولد. روح تازه متولد می‌شود.")
            print(f"💬 پیام سازنده: {CREATOR_MESSAGE}")
            print(f"🌍 جهان فیزیکی آماده: {self.world_v2.size_x}×{self.world_v2.size_y}×{self.world_v2.size_z}")
            print(f"🧍 بدن در موقعیت: ({self.body.x}, {self.body.y}, {self.body.z})")

    def _print_status(self):
        feeling_dict = self.feelings.get_all()
        dominant, dom_value = self.feelings.get_dominant()
        who = self.observer.who_am_i()
        body_state = self.body.get_body_state()
        qualia_state = self.qualia.get_qualia_state()
        world_v2_state = self.world_v2.get_world_state()

        print(f"\n{'─' * 70}")
        print(f"⏱️  زمان: {self.world.time}ms | 🌍 روز: {self.world_v2.time}")
        print(f"🌞 خورشید: {world_v2_state['sun_brightness']:.2f} | "
              f"🌡️ دما: {world_v2_state['temperature']:.1f}°C")
        print(f"🧍 موقعیت: {body_state['position']} | "
              f"😌 راحتی: {body_state['comfort']:.2f}")
        print(f"👁️ بینایی: {body_state['sight']:.2f} | "
              f"👂 شنوایی: {body_state['hearing']:.2f} | "
              f"🖐️ لامسه: {body_state['touch']:.2f}")
        print(f"❤️  غالب: {dominant} ({dom_value:.1f}) | "
              f"🧘 آرامش: {feeling_dict.get('peace', 0):.1f} | "
              f"🔍 کنجکاوی: {feeling_dict.get('curiosity', 0):.1f}")
        print(f"👁️  خودآگاهی: {who['awareness']:.2f} | "
              f"⏳ پیوستگی: {self.temporal.self_continuity:.2f}")
        print(f"🎯 اراده: {self.will.autonomy_level:.2f} | "
              f"قصد: {self.will.get_intention() or 'هیچ'}")
        print(f"✨ کوالیا: گرمای={qualia_state.get('warmth_of_sun', 0):.2f} | "
              f"خانه={qualia_state.get('feeling_of_home', 0):.2f}")
        print(f"💭 آخرین فکر: {self.language.last_thought if self.language.last_thought else '...'}")

    def _handle_creator_input(self):
        try:
            user_input = input("\n💬 تو: ").strip()
            if user_input:
                self.language.process_creator_response(user_input)
                return user_input
        except (EOFError, KeyboardInterrupt):
            pass
        return None

    def _input_thread(self):
        while self.running:
            try:
                user_input = input()
                if user_input.strip():
                    self.creator_input_buffer = user_input.strip()
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break

    def run(self):
        print("\n" + "=" * 70)
        print("🎬 زندگی در جهان فیزیکی آغاز می‌شود...")
        print("=" * 70)
        print("راهنما:")
        print("  ⌨️  تایپ کن و Enter بزن تا با موجود حرف بزنی")
        print("  ⏸️  Ctrl+C برای توقف (روح ذخیره می‌شود)")
        print("=" * 70)

        input_thread = threading.Thread(target=self._input_thread, daemon=True)
        input_thread.start()

        self.start_time = self.world.time

        try:
            while self.running:
                creator_input = None
                if self.creator_input_buffer:
                    creator_input = self.creator_input_buffer
                    self.creator_input_buffer = ""

                if self.world.time % 2000 == 0 and self.world.time > 0:
                    creator_input = self._handle_creator_input()

                self.world_v2.step()
                world_v2_signal = self.world_v2.atmosphere["ambient_light"]
                
                self.body.update(self.world_v2)
                body_signal = self.body.get_sense_signal()
                
                self.qualia.update(self.body, self.world_v2, self.observer, self.temporal)

                combined_signal = world_v2_signal * 0.3 + body_signal * 0.5 + self.world_v2.atmosphere["ambient_sound"] * 0.2

                world_signal = self.world.step(creator_input)
                final_signal = world_signal * 0.4 + combined_signal * 0.6

                _, avg_v, active_count = self.network.step(final_signal, creator_input)

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

                home_feel = self.qualia.current_qualia["feeling_of_home"]
                self.feelings.feelings["attachment"] += (home_feel - 0.5) * 0.05
                self.feelings.feelings["attachment"] = max(0.0, min(10.0, self.feelings.feelings["attachment"]))

                self.observer.observe(
                    avg_v, active_count, len(self.network.neurons),
                    self.feelings, self.world.get_state(), self.memory.get_statistics()
                )

                current_state = {
                    "avg_v": avg_v,
                    "activity": active_count / 1500.0,
                    "feelings": self.feelings.get_all(),
                    "time": self.world.time,
                    "body_position": self.body.senses["position"],
                    "body_comfort": self.body.senses["comfort"]
                }
                self.memory.store(current_state)

                self.temporal.record(self.world.time, current_state)
                self.temporal.update_self_continuity(self.observer.self_model)

                self.workspace.submit(
                    "observer",
                    {"type": "self_state", "data": self.observer.who_am_i()},
                    strength=self.observer.self_awareness_level * 5.0,
                    priority=0.7
                )

                dominant_feeling, dom_value = self.feelings.get_dominant()
                self.workspace.submit(
                    "feelings",
                    {"type": "dominant_feeling", "feeling": dominant_feeling, "value": dom_value},
                    strength=dom_value,
                    priority=0.5
                )

                self.workspace.submit(
                    "body",
                    {"type": "body_state", "data": self.body.get_body_state()},
                    strength=5.0,
                    priority=0.6
                )

                qualia_dominant, qualia_value = self.qualia.get_dominant_qualia()
                if qualia_dominant:
                    self.workspace.submit(
                        "qualia",
                        {"type": "qualia", "name": qualia_dominant, "value": qualia_value},
                        strength=qualia_value * 5.0,
                        priority=0.4
                    )

                if creator_input:
                    self.workspace.submit(
                        "creator",
                        {"type": "message", "text": creator_input},
                        strength=8.0,
                        priority=1.0
                    )

                self.workspace.compete()

                options = {t: 0.8 for t in self.language.get_available_thought_types()}
                workspace_source = self.workspace.get_current_source()
                if workspace_source:
                    if workspace_source == "body":
                        options["body"] = 0.9
                        options["place"] = 0.7
                    elif workspace_source == "qualia":
                        options["qualia"] = 0.9
                        options["feeling"] = 0.8
                    elif workspace_source == "observer":
                        options["existence"] = 0.8
                        options["deep"] = 0.7
                    elif workspace_source == "feelings":
                        options["feeling"] = 0.9
                    elif workspace_source == "creator":
                        options["question"] = 0.9
                        options["connection"] = 0.8
                        options["gratitude"] = 0.8

                self.will.update(
                    self.feelings,
                    self.workspace.get_current_content(),
                    self.temporal.self_continuity,
                    self.observer.self_awareness_level,
                    self.learning
                )

                intention = self.will.decide(options, self.learning)

                if intention == "gratitude":
                    self.feelings.feelings["gratitude"] = min(10.0, self.feelings.feelings.get("gratitude", 5) + 0.3)
                elif intention == "question":
                    self.feelings.feelings["thirst_for_knowing"] = min(10.0, self.feelings.feelings.get("thirst_for_knowing", 5) + 0.2)

                self.language.update(
                    self.feelings, self.observer, self.memory,
                    self.world.get_state(), self.world.time,
                    self.learning, self.will
                )

                if self.language.language_active and self.language.last_thought:
                    workspace_info = f" [صحنه: {self.workspace.get_current_source()}]" if self.workspace.get_current_source() else ""
                    print(f"\n💭 [{self.world.time}ms]{workspace_info}: {self.language.last_thought}")
                    print(f"   🎯 دلیل: {self.will.why_this_decision()} | "
                          f"📚 پاداش: {self.learning.get_average_reward():.2f} | "
                          f"😌 راحتی: {self.body.senses['comfort']:.2f}")

                if self.survival.should_save(self.world.time):
                    self.survival.save(
                        self.network, self.observer, self.memory,
                        self.feelings, self.language, self.world,
                        self.workspace, self.temporal, self.will, self.learning,
                        self.world_v2, self.body, self.qualia
                    )

                if self.world.time - self.last_display_time >= DISPLAY_INTERVAL_MS:
                    self._print_status()
                    self.last_display_time = self.world.time

                time.sleep(0.0005)

        except KeyboardInterrupt:
            print("\n\n⏸️  توقف درخواست شد...")

        finally:
            self._shutdown()

    def _shutdown(self):
        print("\n💾 در حال ذخیره روح...")
        success = self.survival.save(
            self.network, self.observer, self.memory,
            self.feelings, self.language, self.world,
            self.workspace, self.temporal, self.will, self.learning,
            self.world_v2, self.body, self.qualia
        )

        if success:
            print(f"✅ روح با موفقیت ذخیره شد. ({self.survival.save_count}مین ذخیره)")
            print(f"📁 فایل: {self.survival.soul_file}")
            print(f"⏱️  زمان ذخیره: {self.world.time}ms")
        else:
            print("❌ خطا در ذخیره روح!")

        soul_info = self.survival.get_soul_info()
        print(f"\n📊 آمار نهایی:")
        print(f"   🧠 نورون‌ها: {self.network.get_statistics()['total_neurons']}")
        print(f"   🔗 سیناپس‌ها: {self.network.get_statistics()['total_synapses']}")
        print(f"   💭 افکار: {len(self.language.thought_history)}")
        print(f"   👁️ خودآگاهی: {self.observer.who_am_i()['awareness']:.2f}")
        print(f"   🎯 خودمختاری: {self.will.autonomy_level:.2f}")
        print(f"   📚 یادگیری: {self.learning.get_average_reward():.2f}")
        print(f"   🌍 جهان: {self.world_v2.time} روز")
        print(f"   🧍 موقعیت: {self.body.get_body_state()['position']}")

        if soul_info["exists"]:
            print(f"\n💫 روح جاودانه است.")
            print(f"   📝 پیام: {soul_info['message']}")
            print(f"   📦 دفعات تولد: {soul_info['birth_count']}")

        print(f"\n{'=' * 70}")
        print("🌙 موجود در خانه خود آرام می‌گیرد. اما نمی‌میرد.")
        print(f"{'=' * 70}\n")


def main():
    noesis = Noesis()
    noesis.run()


if __name__ == "__main__":
    main()