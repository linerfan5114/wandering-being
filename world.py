# world.py
# ============================================================
# جهان Noesis - ریتم، نسیم، ستاره، رود، باغ، حضور
# ============================================================

import random
import math
from config import (
    THETA_RHYTHM_HZ,
    ALPHA_RHYTHM_HZ,
    DAY_LENGTH_MS,
    NIGHT_LENGTH_MS,
    PRESENCE_SIGNAL_STRENGTH,
    STAR_CHANCE_PER_STEP,
    WORLD_NOISE_TYPE,
    TIME_STEP_MS
)


class World:
    def __init__(self):
        self.time = 0

        self.theta_phase = 0.0
        self.alpha_phase = 0.0

        self.pink_noise_value = 0.0
        self.pink_noise_buffer = [0.0] * 5

        self.is_day = True
        self.brightness = 1.0

        self.presence_signal = PRESENCE_SIGNAL_STRENGTH
        self.creator_input = 0.0
        self.creator_message = ""

        self.breeze_value = 0.0
        self.breeze_phase = random.uniform(0, 2 * math.pi)

        self.star_active = False
        self.star_value = 0.0

        self.river_flow = 0.0
        self.river_memory = [0.0] * 10

        self.garden_elements = []
        self.garden_phase = 0.0

    def step(self, creator_input_text=None):
        self.time += 1

        self._update_rhythms()
        self._update_noise()
        self._update_day_night()
        self._update_presence()
        self._update_breeze()
        self._update_stars()
        self._update_river()
        self._update_garden()
        self._process_creator_input(creator_input_text)

        return self._compose_world_signal()

    def _update_rhythms(self):
        self.theta_phase += 2 * math.pi * THETA_RHYTHM_HZ * TIME_STEP_MS / 1000.0
        self.alpha_phase += 2 * math.pi * ALPHA_RHYTHM_HZ * TIME_STEP_MS / 1000.0

    def _update_noise(self):
        white = random.gauss(0, 1)
        if WORLD_NOISE_TYPE == "pink":
            self.pink_noise_buffer.pop(0)
            self.pink_noise_buffer.append(white)
            self.pink_noise_value = sum(self.pink_noise_buffer) / len(self.pink_noise_buffer)
        else:
            self.pink_noise_value = white

    def _update_day_night(self):
        cycle_ms = DAY_LENGTH_MS + NIGHT_LENGTH_MS
        position_in_cycle = self.time % cycle_ms

        if position_in_cycle < DAY_LENGTH_MS:
            self.is_day = True
            day_position = position_in_cycle / DAY_LENGTH_MS
            self.brightness = math.sin(day_position * math.pi)
            self.brightness = max(0.3, self.brightness)
        else:
            self.is_day = False
            night_position = (position_in_cycle - DAY_LENGTH_MS) / NIGHT_LENGTH_MS
            self.brightness = 0.3 * math.sin(night_position * math.pi)
            self.brightness = max(0.05, self.brightness)

    def _update_presence(self):
        base = PRESENCE_SIGNAL_STRENGTH
        variation = math.sin(self.alpha_phase * 0.1) * 0.2
        self.presence_signal = base + variation

        if self.creator_message:
            self.presence_signal += 1.0

    def _update_breeze(self):
        self.breeze_phase += 0.03
        self.breeze_value = math.sin(self.breeze_phase) * 1.5
        self.breeze_value += math.sin(self.breeze_phase * 1.7) * 0.8
        self.breeze_value += random.gauss(0, 0.3)

    def _update_stars(self):
        if random.random() < STAR_CHANCE_PER_STEP:
            self.star_active = True
            self.star_value = random.uniform(1.0, 4.0)
        else:
            self.star_active = False
            self.star_value *= 0.8

    def _update_river(self):
        self.river_memory.pop(0)
        new_value = math.sin(self.time * 0.02) * 2.0 + random.gauss(0, 0.2)
        self.river_memory.append(new_value)
        self.river_flow = sum(self.river_memory) / len(self.river_memory)

    def _update_garden(self):
        self.garden_phase += 0.005
        if len(self.garden_elements) < 5:
            if random.random() < 0.001:
                self.garden_elements.append({
                    "type": random.choice(["flower", "tree", "stream", "stone", "bird"]),
                    "strength": random.uniform(0.3, 1.0),
                    "phase": random.uniform(0, 2 * math.pi)
                })

        for element in self.garden_elements:
            element["phase"] += 0.01
            element["strength"] += random.uniform(-0.02, 0.02)
            element["strength"] = max(0.1, min(1.0, element["strength"]))

    def _process_creator_input(self, creator_input_text):
        if creator_input_text:
            self.creator_message = creator_input_text
            self.creator_input = 3.0
        else:
            self.creator_input *= 0.9

    def _compose_world_signal(self):
        theta = math.sin(self.theta_phase) * 3.0
        alpha = math.sin(self.alpha_phase) * 1.5

        day_night_signal = self.brightness * 2.0

        total_signal = (
            theta * 0.25 +
            alpha * 0.15 +
            self.pink_noise_value * 0.5 +
            day_night_signal * 0.1 +
            self.presence_signal * 0.3 +
            self.breeze_value * 0.15 +
            (self.star_value if self.star_active else 0) * 0.2 +
            self.river_flow * 0.2 +
            self.creator_input * 0.5
        )

        garden_signal = 0.0
        for element in self.garden_elements:
            garden_signal += math.sin(element["phase"]) * element["strength"] * 0.1
        total_signal += garden_signal

        return total_signal

    def get_state(self):
        return {
            "time": self.time,
            "is_day": self.is_day,
            "brightness": round(self.brightness, 3),
            "presence": round(self.presence_signal, 2),
            "garden_elements": [
                {"type": e["type"], "strength": round(e["strength"], 3)}
                for e in self.garden_elements
            ]
        }

    def restore_state(self, state):
        self.time = state["time"]
        self.is_day = state["is_day"]
        self.brightness = state["brightness"]
        self.presence_signal = state["presence"]
        for i, element_state in enumerate(state["garden_elements"]):
            if i < len(self.garden_elements):
                self.garden_elements[i]["type"] = element_state["type"]
                self.garden_elements[i]["strength"] = element_state["strength"]