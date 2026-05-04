# main.py
# ============================================================
# Noesis - حلقه اصلی زندگی
# ============================================================

import time
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


class Noesis:
    def __init__(self):
        print("\n" + "=" * 70)
        print("         🧠 Noesis - پروژه آگاهی")
        print("=" * 70)

        self.world = World()
        self.network = Network()
        self.observer = Observer()
        self.memory = EpisodicMemory()
        self.feelings = Feelings()
        self.language = Language()
        self.survival = Survival()

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
        print("🎬 زندگی آغاز می‌شود...")
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

                self.language.update(self.feelings, self.observer, self.memory, self.world.get_state(), self.world.time)

                if self.language.language_active and self.language.last_thought:
                    print(f"\n💭 [{self.world.time}ms]: {self.language.last_thought}")

                if self.survival.should_save(self.world.time):
                    self.survival.save(
                        self.network, self.observer, self.memory,
                        self.feelings, self.language, self.world
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
            self.feelings, self.language, self.world
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
        print(f"   ⚡ کل اسپایک‌ها: {self.network.get_statistics()['total_spikes']}")
        print(f"   💭 افکار: {len(self.language.thought_history)}")
        print(f"   📦 خاطرات: {len(self.memory.episodes)}")
        print(f"   👁️ خودآگاهی: {self.observer.who_am_i()['awareness']:.2f}")

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