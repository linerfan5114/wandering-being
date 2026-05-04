# neuron.py
# ============================================================
# نورون ایژیکویچ - کوچک‌ترین واحد سازنده Noesis
# ============================================================

import random
from config import MIN_SYNAPSE_WEIGHT, MAX_SYNAPSE_WEIGHT


class IzhikevichNeuron:
    def __init__(self, neuron_id, neuron_type="regular"):
        self.id = neuron_id
        self.neuron_type = neuron_type

        types = {
            "regular":       (0.02, 0.2,  -65.0, 8.0),
            "fast":          (0.1,  0.2,  -65.0, 2.0),
            "bursting":      (0.02, 0.25, -55.0, 0.05),
            "low_threshold": (0.02, 0.25, -65.0, 0.1),
            "observer":      (0.01, 0.15, -70.0, 1.0),
            "memory":        (0.015, 0.18, -68.0, 0.5),
            "language":      (0.01, 0.12, -72.0, 0.3),
        }

        self.a, self.b, self.c, self.d = types.get(neuron_type, types["regular"])

        self.v = random.uniform(-75.0, -60.0)
        self.u = self.b * self.v
        self.threshold = 30.0
        self.background_current = random.uniform(2.0, 10.0)

        self.spike_times = []
        self.time = 0
        self.total_spikes = 0

        self.incoming_synapses = []
        self.outgoing_synapses = []
        self.incoming_spikes_buffer = []

    def add_incoming_synapse(self, source_neuron, weight, delay=1):
        self.incoming_synapses.append({
            "source": source_neuron,
            "weight": weight,
            "delay": delay
        })

    def add_outgoing_synapse(self, target_neuron, weight, delay=1):
        self.outgoing_synapses.append({
            "target": target_neuron,
            "weight": weight,
            "delay": delay
        })

    def receive_spike(self, weight):
        self.incoming_spikes_buffer.append(weight)

    def step(self, external_current=0.0):
        self.time += 1

        synaptic_current = sum(self.incoming_spikes_buffer)
        self.incoming_spikes_buffer.clear()

        total_current = self.background_current + external_current + synaptic_current

        for _ in range(2):
            dv = 0.04 * self.v**2 + 5 * self.v + 140 - self.u + total_current
            du = self.a * (self.b * self.v - self.u)
            self.v += dv * 0.5
            self.u += du * 0.5

        spiked = False
        if self.v >= self.threshold:
            self.spike_times.append(self.time)
            self.total_spikes += 1
            self.v = self.c
            self.u += self.d
            spiked = True

            self.background_current *= 0.95

            for syn in self.outgoing_synapses:
                syn["target"].receive_spike(syn["weight"])

        target_current = self._get_target_current()
        self.background_current += 0.005 * (target_current - self.background_current)

        return spiked

    def _get_target_current(self):
        targets = {
            "regular": 5.0,
            "fast": 7.0,
            "bursting": 6.0,
            "low_threshold": 4.5,
            "observer": 3.0,
            "memory": 4.0,
            "language": 2.5,
        }
        return targets.get(self.neuron_type, 5.0)

    def get_state(self):
        return {
            "id": self.id,
            "type": self.neuron_type,
            "v": round(self.v, 2),
            "u": round(self.u, 2),
            "current": round(self.background_current, 2),
            "spikes": self.total_spikes
        }

    def restore_state(self, state):
        self.v = state["v"]
        self.u = state["u"]
        self.background_current = state["current"]
        self.total_spikes = state["spikes"]