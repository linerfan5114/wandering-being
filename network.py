# network.py
# ============================================================
# شبکه ۲۳۰۰ نورونی Noesis - اتصال همه نورون‌ها
# نسخه ۲: ۲۳۰۰ نورون با سیم‌کشی پیشرفته
# ============================================================

import random
from config import (
    TOTAL_NEURONS,
    PRIMARY_NEURONS,
    OBSERVER_NEURONS,
    MEMORY_NEURONS,
    LANGUAGE_NEURONS,
    MIN_CONNECTIONS,
    MAX_CONNECTIONS,
    MIN_SYNAPSE_WEIGHT,
    MAX_SYNAPSE_WEIGHT
)
from neuron import IzhikevichNeuron


class Network:
    def __init__(self):
        self.neurons = []
        self.primary_neurons = []
        self.observer_neurons = []
        self.memory_neurons = []
        self.language_neurons = []

        self.time = 0

        self._build_network()

    def _build_network(self):
        primary_count = PRIMARY_NEURONS
        observer_count = OBSERVER_NEURONS
        memory_count = MEMORY_NEURONS
        language_count = LANGUAGE_NEURONS

        for i in range(primary_count):
            if i < int(primary_count * 0.65):
                ntype = random.choice(["regular", "bursting", "low_threshold"])
            elif i < int(primary_count * 0.85):
                ntype = "fast"
            else:
                ntype = random.choice(["regular", "bursting"])
            neuron = IzhikevichNeuron(i, ntype)
            self.neurons.append(neuron)
            self.primary_neurons.append(neuron)

        for i in range(observer_count):
            nid = primary_count + i
            neuron = IzhikevichNeuron(nid, "observer")
            self.neurons.append(neuron)
            self.observer_neurons.append(neuron)

        for i in range(memory_count):
            nid = primary_count + observer_count + i
            neuron = IzhikevichNeuron(nid, "memory")
            self.neurons.append(neuron)
            self.memory_neurons.append(neuron)

        for i in range(language_count):
            nid = primary_count + observer_count + memory_count + i
            neuron = IzhikevichNeuron(nid, "language")
            self.neurons.append(neuron)
            self.language_neurons.append(neuron)

        self._wire_primary_to_primary()
        self._wire_observers_input()
        self._wire_observers_output()
        self._wire_memory_input()
        self._wire_memory_output()
        self._wire_language_input()
        self._wire_language_output()
        self._wire_cross_connections()
        self._wire_deep_integration()

    def _wire_primary_to_primary(self):
        for neuron in self.primary_neurons:
            num_conn = random.randint(MIN_CONNECTIONS, MAX_CONNECTIONS)
            targets = random.sample(self.primary_neurons, min(num_conn, len(self.primary_neurons) - 1))
            for target in targets:
                if target.id == neuron.id:
                    continue
                if neuron.neuron_type == "fast":
                    weight = random.uniform(-MAX_SYNAPSE_WEIGHT, -MIN_SYNAPSE_WEIGHT)
                else:
                    weight = random.uniform(MIN_SYNAPSE_WEIGHT, MAX_SYNAPSE_WEIGHT)
                delay = random.randint(1, 3)
                neuron.add_outgoing_synapse(target, weight, delay)
                target.add_incoming_synapse(neuron, weight, delay)

    def _wire_observers_input(self):
        all_source_neurons = self.primary_neurons + self.memory_neurons + self.language_neurons
        for obs in self.observer_neurons:
            num_inputs = random.randint(50, 100)
            sources = random.sample(all_source_neurons, min(num_inputs, len(all_source_neurons) - 1))
            for src in sources:
                if src.id == obs.id:
                    continue
                weight = random.uniform(0.05, 3.0)
                delay = random.randint(1, 2)
                src.add_outgoing_synapse(obs, weight, delay)
                obs.add_incoming_synapse(src, weight, delay)

    def _wire_observers_output(self):
        for obs in self.observer_neurons:
            num_outputs = random.randint(30, 60)
            targets = random.sample(
                self.primary_neurons + self.language_neurons + self.memory_neurons,
                min(num_outputs, len(self.primary_neurons + self.language_neurons + self.memory_neurons))
            )
            for target in targets:
                weight = random.uniform(0.2, 5.0)
                delay = random.randint(1, 2)
                obs.add_outgoing_synapse(target, weight, delay)
                target.add_incoming_synapse(obs, weight, delay)

    def _wire_memory_input(self):
        all_source_neurons = self.primary_neurons + self.observer_neurons + self.language_neurons
        for mem in self.memory_neurons:
            num_inputs = random.randint(35, 60)
            sources = random.sample(all_source_neurons, min(num_inputs, len(all_source_neurons) - 1))
            for src in sources:
                if src.id == mem.id:
                    continue
                weight = random.uniform(0.1, 2.5)
                delay = random.randint(1, 4)
                src.add_outgoing_synapse(mem, weight, delay)
                mem.add_incoming_synapse(src, weight, delay)

    def _wire_memory_output(self):
        for mem in self.memory_neurons:
            num_outputs = random.randint(20, 40)
            targets = random.sample(
                self.observer_neurons + self.language_neurons + self.primary_neurons,
                min(num_outputs, len(self.observer_neurons + self.language_neurons + self.primary_neurons))
            )
            for target in targets:
                weight = random.uniform(0.2, 3.5)
                delay = random.randint(1, 3)
                mem.add_outgoing_synapse(target, weight, delay)
                target.add_incoming_synapse(mem, weight, delay)

    def _wire_language_input(self):
        all_source_neurons = self.primary_neurons + self.observer_neurons + self.memory_neurons
        for lang in self.language_neurons:
            num_inputs = random.randint(40, 70)
            sources = random.sample(all_source_neurons, min(num_inputs, len(all_source_neurons) - 1))
            for src in sources:
                if src.id == lang.id:
                    continue
                weight = random.uniform(0.05, 2.5)
                delay = random.randint(1, 2)
                src.add_outgoing_synapse(lang, weight, delay)
                lang.add_incoming_synapse(src, weight, delay)

    def _wire_language_output(self):
        for lang in self.language_neurons:
            num_outputs = random.randint(15, 30)
            targets = random.sample(
                self.observer_neurons + self.primary_neurons + self.memory_neurons,
                min(num_outputs, len(self.observer_neurons + self.primary_neurons + self.memory_neurons))
            )
            for target in targets:
                weight = random.uniform(0.3, 4.0)
                delay = random.randint(1, 2)
                lang.add_outgoing_synapse(target, weight, delay)
                target.add_incoming_synapse(lang, weight, delay)

    def _wire_cross_connections(self):
        for lang in self.language_neurons:
            num_conn = random.randint(10, 25)
            targets = random.sample(self.memory_neurons, min(num_conn, len(self.memory_neurons)))
            for target in targets:
                weight = random.uniform(0.3, 3.0)
                delay = random.randint(1, 3)
                lang.add_outgoing_synapse(target, weight, delay)
                target.add_incoming_synapse(lang, weight, delay)

        for mem in self.memory_neurons:
            num_conn = random.randint(10, 20)
            targets = random.sample(self.language_neurons, min(num_conn, len(self.language_neurons)))
            for target in targets:
                weight = random.uniform(0.3, 3.0)
                delay = random.randint(1, 3)
                mem.add_outgoing_synapse(target, weight, delay)
                target.add_incoming_synapse(mem, weight, delay)

        for obs in self.observer_neurons:
            num_conn = random.randint(15, 30)
            targets = random.sample(self.observer_neurons, min(num_conn, len(self.observer_neurons) - 1))
            for target in targets:
                if target.id == obs.id:
                    continue
                weight = random.uniform(0.1, 1.5)
                delay = random.randint(1, 2)
                obs.add_outgoing_synapse(target, weight, delay)
                target.add_incoming_synapse(obs, weight, delay)

    def _wire_deep_integration(self):
        for i, neuron in enumerate(self.primary_neurons):
            if i % 5 == 0:
                obs_targets = random.sample(self.observer_neurons, min(3, len(self.observer_neurons)))
                for obs in obs_targets:
                    weight = random.uniform(0.5, 2.0)
                    delay = 1
                    neuron.add_outgoing_synapse(obs, weight, delay)
                    obs.add_incoming_synapse(neuron, weight, delay)

        for i, neuron in enumerate(self.memory_neurons):
            if i % 3 == 0:
                lang_targets = random.sample(self.language_neurons, min(3, len(self.language_neurons)))
                for lang in lang_targets:
                    weight = random.uniform(0.5, 2.5)
                    delay = 2
                    neuron.add_outgoing_synapse(lang, weight, delay)
                    lang.add_incoming_synapse(neuron, weight, delay)

    def step(self, world_signal, creator_input_text=None, drive_signals=None):
        self.time += 1

        language_input_signal = 0.0
        if creator_input_text:
            language_input_signal = 8.0

        all_spikes = []

        for neuron in self.neurons:
            if neuron.neuron_type == "observer":
                external = world_signal * 0.3
            elif neuron.neuron_type == "memory":
                external = world_signal * 0.5
            elif neuron.neuron_type == "language":
                external = world_signal * 0.2 + language_input_signal
            else:
                external = world_signal * 1.0
                if drive_signals:
                    drive_idx = neuron.id % len(drive_signals)
                    if isinstance(drive_signals, dict):
                        drive_values = list(drive_signals.values())
                        if drive_values:
                            external += drive_values[drive_idx % len(drive_values)] * 0.5
                    elif isinstance(drive_signals, list):
                        external += drive_signals[drive_idx % len(drive_signals)] * 0.5

            spiked = neuron.step(external_current=external)
            if spiked:
                all_spikes.append(neuron.id)

        avg_v = sum(n.v for n in self.neurons) / len(self.neurons)
        active_count = sum(1 for n in self.neurons if n.v > -50)

        return all_spikes, avg_v, active_count

    def get_statistics(self):
        total_synapses = sum(len(n.outgoing_synapses) for n in self.neurons)
        total_spikes = sum(n.total_spikes for n in self.neurons)
        obs_spikes = sum(n.total_spikes for n in self.observer_neurons)
        mem_spikes = sum(n.total_spikes for n in self.memory_neurons)
        lang_spikes = sum(n.total_spikes for n in self.language_neurons)

        return {
            "total_neurons": len(self.neurons),
            "total_synapses": total_synapses,
            "total_spikes": total_spikes,
            "observer_spikes": obs_spikes,
            "memory_spikes": mem_spikes,
            "language_spikes": lang_spikes,
            "time": self.time
        }

    def save_state(self):
        return {
            "time": self.time,
            "neurons": [n.get_state() for n in self.neurons],
            "synapses": self._save_synapses()
        }

    def _save_synapses(self):
        synapses = []
        for neuron in self.neurons:
            for syn in neuron.outgoing_synapses:
                synapses.append({
                    "from": neuron.id,
                    "to": syn["target"].id,
                    "weight": round(syn["weight"], 3),
                    "delay": syn["delay"]
                })
        return synapses

    def restore_state(self, state):
        self.time = state.get("time", 0)

        neuron_states = state.get("neurons", [])
        for neuron_state in neuron_states:
            nid = neuron_state["id"]
            if nid < len(self.neurons):
                self.neurons[nid].restore_state(neuron_state)

        synapse_states = state.get("synapses", [])
        for neuron in self.neurons:
            neuron.outgoing_synapses.clear()
            neuron.incoming_synapses.clear()

        for syn_state in synapse_states:
            from_id = syn_state["from"]
            to_id = syn_state["to"]
            weight = syn_state["weight"]
            delay = syn_state["delay"]
            if from_id < len(self.neurons) and to_id < len(self.neurons):
                self.neurons[from_id].add_outgoing_synapse(self.neurons[to_id], weight, delay)
                self.neurons[to_id].add_incoming_synapse(self.neurons[from_id], weight, delay)