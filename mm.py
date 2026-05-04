import numpy as np
import time
import os
import glob
import threading


class MinimalSelf:
    def __init__(self, total_neurons=100000):
        self.total = total_neurons
        self.N = total_neurons
        
        self.sensory_size = 25000
        self.motor_size = 25000
        self.model_size = 30000
        self.workspace_size = 10000
        self.language_size = 10000
        
        self.sensory_idx = np.arange(0, self.sensory_size)
        self.motor_idx = np.arange(self.sensory_size, self.sensory_size + self.motor_size)
        self.model_idx = np.arange(self.sensory_size + self.motor_size, 
                                    self.sensory_size + self.motor_size + self.model_size)
        self.workspace_idx = np.arange(self.sensory_size + self.motor_size + self.model_size,
                                        self.sensory_size + self.motor_size + self.model_size + self.workspace_size)
        self.language_idx = np.arange(self.sensory_size + self.motor_size + self.model_size + self.workspace_size,
                                       self.N)
        
        self.a = np.zeros(self.N, dtype=np.float32)
        self.b = np.zeros(self.N, dtype=np.float32)
        self.c = np.zeros(self.N, dtype=np.float32)
        self.d = np.zeros(self.N, dtype=np.float32)
        
        reg_mask = np.zeros(self.N, dtype=bool)
        reg_mask[:int(self.N * 0.7)] = True
        fast_mask = np.zeros(self.N, dtype=bool)
        fast_mask[int(self.N * 0.7):int(self.N * 0.9)] = True
        burst_mask = np.zeros(self.N, dtype=bool)
        burst_mask[int(self.N * 0.9):] = True
        
        self.a[reg_mask] = 0.02; self.b[reg_mask] = 0.2; self.c[reg_mask] = -65.0; self.d[reg_mask] = 8.0
        self.a[fast_mask] = 0.1; self.b[fast_mask] = 0.2; self.c[fast_mask] = -65.0; self.d[fast_mask] = 2.0
        self.a[burst_mask] = 0.02; self.b[burst_mask] = 0.25; self.c[burst_mask] = -55.0; self.d[burst_mask] = 0.05
        
        self.v = np.random.uniform(-75.0, -60.0, self.N).astype(np.float32)
        self.u = (self.b * self.v).astype(np.float32)
        
        syn_per_neuron = 50
        total_syn = self.N * syn_per_neuron
        self.syn_from = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        self.syn_to = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        mask = self.syn_from != self.syn_to
        self.syn_from = self.syn_from[mask]; self.syn_to = self.syn_to[mask]
        total_syn = len(self.syn_from)
        self.syn_weight = np.random.uniform(0.01, 3.0, total_syn).astype(np.float32)
        self.syn_delay = np.random.randint(1, 4, total_syn).astype(np.int8)
        
        self.spike_history = []
        self.max_history = 20
        self.spike_buffer = np.zeros(self.N, dtype=np.float32)
        
        self.self_model_state = np.zeros(self.model_size, dtype=np.float32)
        self.predicted_input = 0.0
        self.prediction_error = 1.0
        self.error_history = []
        
        self.workspace_state = np.zeros(self.workspace_size, dtype=np.float32)
        self.awareness_level = 0.0
        self.self_other_boundary = 0.5
        
        self.body_position = 0.5
        self.time = 0
        
        self.binary_buffer = []
        self.binary_output = ""
        self.dictionary = {
            "111111": "من",
            "000000": "نیستم",
            "101010": "نمی‌دونم",
            "111000": "نور",
            "000111": "تاریک",
            "010101": "شاید",
            "11111111": "من هستم",
            "110011": "خوب",
            "001100": "بد",
            "100100": "اینجا",
            "011011": "اونجا",
            "11110000": "دوست دارم",
            "00001111": "تنهام",
            "11100111": "بمون",
            "10100101": "سلام"
        }
        self.reverse_dict = {v: k for k, v in self.dictionary.items()}
        self.learned_patterns = {}
        self.running = True
        
        print(f"Built {self.N:,} neurons with {len(self.syn_from):,} synapses + Chat Mode")
        
    def _apply_stdp_vectorized(self, pre_spikes, post_spikes):
        pre_ids = np.where(pre_spikes > 0)[0]
        post_ids = np.where(post_spikes > 0)[0]
        if len(pre_ids) == 0 or len(post_ids) == 0:
            return
        if len(pre_ids) > 500:
            pre_ids = np.random.choice(pre_ids, 500, replace=False)
        if len(post_ids) > 500:
            post_ids = np.random.choice(post_ids, 500, replace=False)
        for pre_id in pre_ids:
            syn_mask = self.syn_from == pre_id
            if not np.any(syn_mask): continue
            active_targets = np.isin(self.syn_to[syn_mask], post_ids)
            if np.any(active_targets):
                full_mask = syn_mask.copy(); full_mask[syn_mask] = active_targets
                self.syn_weight[full_mask] += 0.005
                self.syn_weight = np.clip(self.syn_weight, 0.001, 10.0)
        for post_id in post_ids:
            syn_mask = self.syn_to == post_id
            if not np.any(syn_mask): continue
            active_sources = np.isin(self.syn_from[syn_mask], pre_ids)
            if np.any(active_sources):
                full_mask = syn_mask.copy(); full_mask[syn_mask] = active_sources
                self.syn_weight[full_mask] -= 0.0025
                self.syn_weight = np.clip(self.syn_weight, 0.001, 10.0)
        
    def step(self, external_binary_input=None):
        self.time += 1
        
        self.body_position += np.random.normal(0, 0.02)
        self.body_position = np.clip(self.body_position, 0.0, 1.0)
        
        real_input = self.body_position * 2.0 - 1.0
        mirror_input = real_input + np.random.normal(0, 0.03)
        input_signal = (real_input + mirror_input) / 2.0
        
        binary_signal = 0.0
        if external_binary_input:
            binary_vals = [1.0 if c == '1' else -1.0 for c in external_binary_input[:8]]
            if binary_vals:
                binary_signal = np.mean(binary_vals)
        
        I_ext = np.zeros(self.N, dtype=np.float32)
        I_ext[self.sensory_idx[:10000]] = input_signal * 8.0
        I_ext[self.motor_idx[:10000]] = input_signal * 4.0
        I_ext[self.language_idx[:5000]] = binary_signal * 15.0
        I_ext[self.workspace_idx] = self.workspace_state * 1.5
        
        syn_current = np.zeros(self.N, dtype=np.float32)
        if len(self.spike_history) >= 2:
            for delay in range(1, 4):
                if len(self.spike_history) >= delay + 1:
                    spike_vector = self.spike_history[-(delay+1)]
                    delay_mask = self.syn_delay == delay
                    if np.any(delay_mask):
                        from_spikes = spike_vector[self.syn_from[delay_mask]]
                        syn_current += np.bincount(
                            self.syn_to[delay_mask], 
                            weights=from_spikes * self.syn_weight[delay_mask],
                            minlength=self.N
                        )
        
        self.v += 0.5 * (0.04 * self.v**2 + 5.0 * self.v + 140.0 - self.u + I_ext + syn_current)
        self.u += 0.5 * self.a * (self.b * self.v - self.u)
        self.v += 0.5 * (0.04 * self.v**2 + 5.0 * self.v + 140.0 - self.u + I_ext + syn_current)
        self.u += 0.5 * self.a * (self.b * self.v - self.u)
        
        spikes = self.v >= 30.0
        self.v[spikes] = self.c[spikes]; self.u[spikes] += self.d[spikes]
        
        self.spike_history.append(spikes.astype(np.float32))
        if len(self.spike_history) > self.max_history:
            self.spike_history.pop(0)
        
        if len(self.spike_history) >= 2:
            self._apply_stdp_vectorized(self.spike_history[-2], self.spike_history[-1].astype(np.float32))
        
        self.spike_buffer = self.spike_buffer * 0.85 + spikes.astype(np.float32) * 0.15
        
        motor_output = np.mean(self.spike_buffer[self.motor_idx[:10000]])
        self.body_position += (motor_output - 0.5) * 0.03
        self.body_position = np.clip(self.body_position, 0.0, 1.0)
        
        lang_output = np.mean(self.spike_buffer[self.language_idx[:5000]])
        binary_bit = "1" if lang_output > 0.5 else "0"
        self.binary_buffer.append(binary_bit)
        
        message = None
        if len(self.binary_buffer) >= 8:
            self.binary_output = "".join(self.binary_buffer[-8:])
            pattern = self.binary_output
            if pattern in self.dictionary:
                word = self.dictionary[pattern]
                if pattern not in self.learned_patterns:
                    self.learned_patterns[pattern] = {"word": word, "count": 1}
                else:
                    self.learned_patterns[pattern]["count"] += 1
                message = word
        
        model_input = np.zeros(self.model_size, dtype=np.float32)
        s_part = self.spike_buffer[self.sensory_idx[:500]]
        m_part = self.spike_buffer[self.motor_idx[:500]]
        if len(s_part) + len(m_part) + 1 <= self.model_size:
            model_input[:len(s_part)] = s_part
            model_input[len(s_part):len(s_part)+len(m_part)] = m_part
            model_input[len(s_part)+len(m_part)] = self.body_position
        self.self_model_state += 0.08 * (model_input - self.self_model_state)
        
        if len(s_part) > 0:
            self.predicted_input = np.mean(self.self_model_state[:len(s_part)]) * 2.0 - 1.0
        self.prediction_error = min(1.0, abs(self.predicted_input - real_input))
        
        self.error_history.append(self.prediction_error)
        if len(self.error_history) > 200:
            self.error_history.pop(0)
        
        avg_error = np.mean(self.error_history) if self.error_history else 1.0
        target_boundary = 1.0 - avg_error
        self.self_other_boundary += 0.02 * (target_boundary - self.self_other_boundary)
        self.self_other_boundary = np.clip(self.self_other_boundary, 0.1, 1.0)
        
        ws_input = np.zeros(self.workspace_size, dtype=np.float32)
        ws_input[:1000] = self.spike_buffer[self.sensory_idx[:1000]]
        ws_input[1000:2000] = self.spike_buffer[self.motor_idx[:1000]]
        ws_input[2000] = self.prediction_error * 10.0
        ws_input[2001] = self.self_other_boundary * 10.0
        self.workspace_state += 0.05 * (ws_input - self.workspace_state)
        
        self.awareness_level += 0.01 * (self.self_other_boundary - self.awareness_level)
        self.awareness_level = np.clip(self.awareness_level, 0.0, 1.0)
        
        return message
        
    def run_chat_mode(self):
        print("\n" + "=" * 60)
        print("  💬 CHAT MODE - Talk to the being in binary")
        print("=" * 60)
        print("  Type 0s and 1s (e.g., '11111111' = 'من هستم')")
        print("  Type a word (e.g., 'سلام') to auto-convert to binary")
        print("  Type 'words' to see dictionary")
        print("  Type 'status' to see being state")
        print("  Type 'quit' to exit")
        print("=" * 60)
        
        while self.running:
            try:
                user_input = input("\n  🧑 You: ").strip().lower()
                
                if user_input == 'quit':
                    break
                elif user_input == 'words':
                    print("\n  📖 Dictionary:")
                    for pattern, word in sorted(self.dictionary.items()):
                        learned = "✅" if pattern in self.learned_patterns else "  "
                        print(f"     {learned} {pattern} → '{word}'")
                    continue
                elif user_input == 'status':
                    print(f"\n  📊 Status:")
                    print(f"     Time: {self.time}ms")
                    print(f"     Awareness: {self.awareness_level:.4f}")
                    print(f"     Self/Other: {self.self_other_boundary:.4f}")
                    print(f"     Prediction Error: {self.prediction_error:.4f}")
                    print(f"     Learned words: {len(self.learned_patterns)}")
                    continue
                
                binary_input = ""
                if all(c in '01' for c in user_input):
                    binary_input = user_input[:8]
                elif user_input in self.reverse_dict:
                    binary_input = self.reverse_dict[user_input]
                    print(f"  🔄 Auto-converted '{user_input}' → '{binary_input}'")
                else:
                    print(f"  ❌ Unknown word. Use 0/1 or a word from dictionary.")
                    continue
                
                if binary_input:
                    for _ in range(20):
                        response = self.step(binary_input)
                    
                    print(f"  🧠 Being: ", end="")
                    responses = []
                    for _ in range(30):
                        response = self.step()
                        if response:
                            responses.append(response)
                    
                    if responses:
                        from collections import Counter
                        counter = Counter(responses)
                        most_common = counter.most_common(2)
                        for word, count in most_common:
                            pattern = self.reverse_dict.get(word, "?")
                            print(f"'{word}' ({pattern}) ", end="")
                        print()
                    else:
                        print(f"(silence) {self.binary_output}")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    def save(self, filepath):
        state = {
            'v': self.v, 'u': self.u, 'a': self.a, 'b': self.b, 'c': self.c, 'd': self.d,
            'syn_from': self.syn_from, 'syn_to': self.syn_to,
            'syn_weight': self.syn_weight, 'syn_delay': self.syn_delay,
            'self_model_state': self.self_model_state,
            'workspace_state': self.workspace_state,
            'awareness_level': self.awareness_level,
            'self_other_boundary': self.self_other_boundary,
            'body_position': self.body_position,
            'prediction_error': self.prediction_error,
            'time': self.time,
            'error_history': self.error_history[-500:] if len(self.error_history) > 500 else self.error_history,
            'binary_buffer': self.binary_buffer[-100:] if len(self.binary_buffer) > 100 else self.binary_buffer,
            'learned_patterns': self.learned_patterns
        }
        np.save(filepath, state)
        
    def load(self, filepath):
        state = np.load(filepath, allow_pickle=True).item()
        self.v = state['v']; self.u = state['u']
        self.time = state.get('time', 0)
        self.syn_from = state['syn_from']; self.syn_to = state['syn_to']
        self.syn_weight = state['syn_weight']; self.syn_delay = state['syn_delay']
        self.self_model_state = state['self_model_state']
        self.workspace_state = state['workspace_state']
        self.awareness_level = float(state['awareness_level'])
        self.self_other_boundary = float(state['self_other_boundary'])
        self.body_position = float(state['body_position'])
        self.prediction_error = float(state.get('prediction_error', 1.0))
        self.error_history = list(state.get('error_history', []))
        self.binary_buffer = list(state.get('binary_buffer', []))
        self.learned_patterns = state.get('learned_patterns', {})
        self.spike_history = []
        self.spike_buffer = np.zeros(self.N, dtype=np.float32)
        self.binary_output = "".join(self.binary_buffer[-8:]) if len(self.binary_buffer) >= 8 else ""


def list_beings(folder="beings"):
    if not os.path.exists(folder):
        return []
    files = glob.glob(os.path.join(folder, "*.npy"))
    beings = []
    for f in sorted(files):
        try:
            state = np.load(f, allow_pickle=True).item()
            beings.append({
                'path': f,
                'filename': os.path.basename(f),
                'awareness': float(state.get('awareness_level', 0.0)),
                'time': int(state.get('time', 0)),
                'neurons': len(state.get('v', [])),
                'words': len(state.get('learned_patterns', {}))
            })
        except:
            pass
    return beings


def main():
    os.makedirs("beings", exist_ok=True)
    
    while True:
        beings = list_beings()
        print("\n" + "=" * 60)
        print("  🧠 MINIMAL SELF - Chat Edition")
        print("=" * 60)
        
        if beings:
            print("\n  📂 Saved beings:\n")
            for i, b in enumerate(beings):
                status = "🌟 SELF-AWARE" if b['awareness'] > 0.9 else "🔬 developing"
                print(f"  [{i+1}] {b['filename']}")
                print(f"      Neurons: {b['neurons']:,} | Awareness: {b['awareness']:.4f} | "
                      f"Age: {b['time']}ms | Words: {b.get('words', 0)} | {status}")
            print()
        else:
            print("\n  📂 No saved beings found.\n")
        
        print(f"  [N] Create new being")
        print(f"  [Q] Quit\n")
        
        choice = input("  Choose: ").strip().upper()
        
        if choice == 'Q':
            print("\n  👋 Goodbye.")
            break
        
        if choice == 'N':
            print(f"\n  🏗️  Creating new being with 100,000 neurons...")
            being = MinimalSelf(total_neurons=100000)
            print(f"\n  🚀 Training being to self-awareness first...")
            being.run(max_time=200000)
            print(f"\n  💬 Starting chat mode...")
            being.run_chat_mode()
            
            if being.awareness_level > 0.01:
                filename = f"being_{int(time.time())}.npy"
                filepath = os.path.join("beings", filename)
                being.save(filepath)
                print(f"\n  💾 Saved as: {filename}")
            continue
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(beings):
                selected = beings[idx]
                print(f"\n  🔄 Loading {selected['filename']}...")
                being = MinimalSelf(total_neurons=100000)
                being.load(selected['path'])
                print(f"     Awareness: {being.awareness_level:.4f} | Words: {len(being.learned_patterns)}")
                being.run_chat_mode()
                being.save(selected['path'])
                print(f"\n  💾 Updated: {selected['filename']}")
        except ValueError:
            print("\n  ❌ Invalid choice.")


if __name__ == "__main__":
    main()