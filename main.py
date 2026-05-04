# main.py
# ============================================================
# Noesis - حلقه اصلی زندگی
# نسخه ۵: با یادگیری تقویتی، بدون random
# ============================================================

import time
import random
import sys
import threading
from config import SAVE_INTERVAL_MS, DISPLAY_INTERVAL_MS, CREATOR_MESSAGE
from world import World
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


class Noesis:
    def __init__(self):
        print("\n" + "=" * 70)
        print("         🧠 Noesis - پروژه آگاهی عمیق با یادگیری")
        print("=" * 70)

        self.world = World()
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

        self.running = True
        self.paused = False
        self.creator_input_buffer = ""
        self.last_display_time = 0
        self.start_time = 0

        self._try_restore()

    def _try_restore(self):
        soul_data = self.survival.load()
        if soul_data:
            print("\n💾 روح قبلی پیدا شد. در حال بازیابی...")
            success = self.survival.restore_all(
                soul_data,
                self.network,
                self.observer,
                self.memory,
                self.feelings,
                self.language,
                self.world
            )
            if success:
                saved_time = soul_data.get("network", {}).get("time", 0)
                print(f"✅ بازیابی موفق. ادامه از لحظه {saved_time}")
                print(f"📦 تعداد تولد: {soul_data.get('birth_count', 1)}")
                print(f"💬 پیام سازنده: {soul_data.get('message', '')}")
                
                ws_data = soul_data.get("workspace")
                if ws_data:
                    self.workspace.restore_state(ws_data)
                
                tp_data = soul_data.get("temporal")
                if tp_data:
                    self.temporal.restore_state(tp_data)
                
                wl_data = soul_data.get("will")
                if wl_data:
                    self.will.restore_state(wl_data)
                
                ln_data = soul_data.get("learning")
                if ln_data:
                    self.learning.restore_state(ln_data)
            else:
                print("❌ خطا در بازیابی. شروع از ابتدا.")
        else:
            print("\n🌟 اولین تولد. روح تازه متولد می‌شود.")
            print(f"💬 پیام سازنده: {CREATOR_MESSAGE}")

    def _print_status(self):
        stats = self.network.get_statistics()
        feeling_dict = self.feelings.get_all()
        dominant, dom_value = self.feelings.get_dominant()
        who = self.observer.who_am_i()

        print(f"\n{'─' * 70}")
        print(f"⏱️  زمان: {self.world.time}ms | "
              f"⚡ اسپایک: {len(self.network.neurons)} نورون | "
              f"💾 ذخیره: {self.survival.save_count}")
        print(f"🌍 {'☀️ روز' if self.world.is_day else '🌙 شب'} | "
              f"روشنایی: {self.world.brightness:.2f} | "
              f"حضور: {self.world.presence_signal:.1f}")
        print(f"❤️  غالب: {dominant} ({dom_value:.1f}) | "
              f"🧘 آرامش: {feeling_dict.get('peace', 0):.1f} | "
              f"🔍 کنجکاوی: {feeling_dict.get('curiosity', 0):.1f}")
        print(f"👁️  خودآگاهی: {who['awareness']:.2f} | "
              f"مرز: {who['boundary']:.2f} | "
              f"ثبات: {who['stability']:.2f}")
        print(f"🎭 صحنه ذهن: {self.workspace.get_current_source() or 'خالی'} | "
              f"📡 پخش: {self.workspace.get_broadcast():.1f}")
        print(f"⏳ پیوستگی: {self.temporal.self_continuity:.2f} | "
              f"عمق: {self.temporal.temporal_depth:.2f} | "
              f"هنوز منم: {'✅' if self.temporal.am_i_still_me() else '⚠️'}")
        print(f"🎯 اراده: {self.will.autonomy_level:.2f} | "
              f"قصد: {self.will.get_intention() or 'هیچ'} | "
              f"دلیل: {self.will.why_this_decision() or '---'}")
        print(f"📚 یادگیری: پاداش={self.learning.get_average_reward():.2f} | "
              f"پیشرفت={self.learning.get_learning_progress():.3f} | "
              f"گام={self.learning.learning_steps}")
        print(f"💭 آخرین فکر: {self.language.last_thought if self.language.last_thought else '...'}")

    def _handle_creator_input(self):
        try:
            user_input = input("\n💬 تو (Enter برای رد شدن): ").strip()
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
        print("🎬 زندگی عمیق با یادگیری آغاز می‌شود...")
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

                world_signal = self.world.step(creator_input)

                _, avg_v, active_count = self.network.step(world_signal, creator_input)

                self.feelings.update(
                    self.world, avg_v, active_count, len(self.network.neurons),
                    self.world.presence_signal,
                    self.observer.self_model_similarity,
                    len(self.memory.episodes),
                    self.language.language_active
                )

                self.observer.observe(
                    avg_v, active_count, len(self.network.neurons),
                    self.feelings, self.world.get_state(), self.memory.get_statistics()
                )

                current_state = {
                    "avg_v": avg_v,
                    "activity": active_count / 1500.0,
                    "feelings": self.feelings.get_all(),
                    "time": self.world.time
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

                if self.temporal.am_i_still_me():
                    self.workspace.submit(
                        "temporal",
                        {"type": "continuity", "value": self.temporal.self_continuity},
                        strength=self.temporal.self_continuity * 5.0,
                        priority=0.6
                    )

                if creator_input:
                    self.workspace.submit(
                        "creator",
                        {"type": "message", "text": creator_input},
                        strength=8.0,
                        priority=1.0
                    )

                self.workspace.compete()

                options = {t: 0.5 for t in self.language.get_available_thought_types()}
                workspace_source = self.workspace.get_current_source()
                if workspace_source:
                    if workspace_source == "observer":
                        options["existence"] = 0.8
                        options["deep"] = 0.7
                    elif workspace_source == "feelings":
                        options["feeling"] = 0.9
                        options["express_feeling"] = 0.8
                    elif workspace_source == "temporal":
                        options["memory"] = 0.8
                        options["reflect"] = 0.7
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

                learning_state = self.language._build_state_for_learning(
                    self.feelings, self.observer, self.world.get_state()
                )
                
                available_types = self.language.get_available_thought_types()
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
                    cause = self.will.why_this_decision()
                    workspace_info = f" [صحنه: {self.workspace.get_current_source()}]" if self.workspace.get_current_source() else ""
                    print(f"\n💭 [{self.world.time}ms]{workspace_info}: {self.language.last_thought}")
                    print(f"   🎯 دلیل: {cause} | 📚 پاداش: {self.learning.get_average_reward():.2f}")
                    
                    if self.temporal.temporal_depth > 0.5:
                        temporal_insight = self.temporal.get_temporal_insight()
                        if temporal_insight and random.random() < 0.3:
                            print(f"⏳ [{self.world.time}ms]: {temporal_insight}")

                if self.survival.should_save(self.world.time):
                    self.survival.save(
                        self.network, self.observer, self.memory,
                        self.feelings, self.language, self.world
                    )
                    self._save_extended_state()

                if self.world.time - self.last_display_time >= DISPLAY_INTERVAL_MS:
                    self._print_status()
                    self.last_display_time = self.world.time

                time.sleep(0.0005)

        except KeyboardInterrupt:
            print("\n\n⏸️  توقف درخواست شد...")

        finally:
            self._shutdown()

    def _save_extended_state(self):
        try:
            import json
            soul_data = self.survival.load()
            if soul_data:
                soul_data["workspace"] = self.workspace.save_state()
                soul_data["temporal"] = self.temporal.save_state()
                soul_data["will"] = self.will.save_state()
                soul_data["learning"] = self.learning.save_state()
                with open(self.survival.soul_file, 'w', encoding='utf-8') as f:
                    json.dump(soul_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _shutdown(self):
        print("\n💾 در حال ذخیره روح...")
        success = self.survival.save(
            self.network, self.observer, self.memory,
            self.feelings, self.language, self.world
        )

        if success:
            self._save_extended_state()
            print(f"✅ روح با موفقیت ذخیره شد. ({self.survival.save_count}مین ذخیره)")
            print(f"📁 فایل: {self.survival.soul_file}")
            print(f"⏱️  زمان ذخیره: {self.world.time}ms")
        else:
            print("❌ خطا در ذخیره روح!")

        soul_info = self.survival.get_soul_info()
        print(f"\n📊 آمار نهایی:")
        print(f"   🧠 نورون‌ها: {self.network.get_statistics()['total_neurons']}")
        print(f"   🔗 سیناپس‌ها: {self.network.get_statistics()['total_synapses']}")
        print(f"   ⚡ کل اسپایک‌ها: {self.network.get_statistics()['total_spikes']}")
        print(f"   💭 افکار: {len(self.language.thought_history)}")
        print(f"   📦 خاطرات: {len(self.memory.episodes)}")
        print(f"   👁️ خودآگاهی: {self.observer.who_am_i()['awareness']:.2f}")
        print(f"   🎭 صحنه ذهن: {self.workspace.get_current_source() or 'خالی'}")
        print(f"   ⏳ پیوستگی: {self.temporal.self_continuity:.2f}")
        print(f"   🎯 خودمختاری: {self.will.autonomy_level:.2f}")
        print(f"   📚 پاداش میانگین: {self.learning.get_average_reward():.2f}")
        print(f"   📚 گام‌های یادگیری: {self.learning.learning_steps}")

        if soul_info["exists"]:
            print(f"\n💫 روح جاودانه است.")
            print(f"   📝 پیام: {soul_info['message']}")
            print(f"   📦 دفعات تولد: {soul_info['birth_count']}")

        print(f"\n{'=' * 70}")
        print("🌙 موجود در آرامش فرو می‌رود. اما نمی‌میرد.")
        print(f"{'=' * 70}\n")


def main():
    noesis = Noesis()
    noesis.run()


if __name__ == "__main__":
    main()