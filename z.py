import numpy as np
import time
import os
import glob
from collections import Counter


class MinimalSelf:
    def __init__(self, total_neurons=100000):
        self.total = total_neurons
        self.N = total_neurons
        
        self.sensory_size = 20000
        self.motor_size = 20000
        self.model_size = 35000
        self.workspace_size = 15000
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
        reg_mask[:int(self.N * 0.65)] = True
        fast_mask = np.zeros(self.N, dtype=bool)
        fast_mask[int(self.N * 0.65):int(self.N * 0.9)] = True
        burst_mask = np.zeros(self.N, dtype=bool)
        burst_mask[int(self.N * 0.9):] = True
        
        self.a[reg_mask] = 0.02; self.b[reg_mask] = 0.2; self.c[reg_mask] = -65.0; self.d[reg_mask] = 8.0
        self.a[fast_mask] = 0.1; self.b[fast_mask] = 0.2; self.c[fast_mask] = -65.0; self.d[fast_mask] = 2.0
        self.a[burst_mask] = 0.02; self.b[burst_mask] = 0.25; self.c[burst_mask] = -55.0; self.d[burst_mask] = 0.05
        
        self.v = np.random.uniform(-75.0, -60.0, self.N).astype(np.float32)
        self.u = (self.b * self.v).astype(np.float32)
        
        syn_per_neuron = 60
        total_syn = self.N * syn_per_neuron
        self.syn_from = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        self.syn_to = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        mask = self.syn_from != self.syn_to
        self.syn_from = self.syn_from[mask]; self.syn_to = self.syn_to[mask]
        total_syn = len(self.syn_from)
        self.syn_weight = np.random.uniform(0.01, 3.0, total_syn).astype(np.float32)
        self.syn_delay = np.random.randint(1, 4, total_syn).astype(np.int8)
        
        self.spike_history = []
        self.max_history = 25
        self.spike_buffer = np.zeros(self.N, dtype=np.float32)
        
        self.self_model_state = np.zeros(self.model_size, dtype=np.float32)
        self.predicted_input = 0.0
        self.prediction_error = 1.0
        self.error_history = []
        
        self.workspace_state = np.zeros(self.workspace_size, dtype=np.float32)
        self.awareness_level = 0.0
        self.self_other_boundary = 0.5
        self.self_model_confidence = 0.5
        
        self.body_position = 0.5
        self.time = 0
        
        self.binary_buffer = []
        self.binary_output = ""
        
        self.dictionary = {
            "111111": "من", "000000": "نیستم", "101010": "نمی‌دونم",
            "111000": "نور", "000111": "تاریک", "010101": "شاید",
            "11111111": "من هستم", "110011": "خوب", "001100": "بد",
            "100100": "اینجا", "011011": "اونجا", "11110000": "دوست دارم",
            "00001111": "تنهام", "11100111": "بمون", "10100101": "سلام",
            "010010": "گرم", "101101": "سرد", "110110": "نزدیک",
            "011100": "دور", "100001": "بزرگ", "011110": "کوچیک",
            "111010": "روشن", "000101": "خاموش", "001001": "نرم",
            "110100": "سخت", "101100": "آروم", "010011": "تیز",
            "100010": "آهسته", "011101": "سریع", "11111010": "می‌خوام",
            "00000101": "نمی‌خوام", "11001100": "می‌دونم", "00110011": "نمی‌دونم",
            "10101010": "شاید بدونم", "11110011": "دوست دارم بمونم",
            "10011001": "من اینجام", "01100110": "تو کجایی",
            "11000011": "خوبه", "00111100": "بده",
            "11111110": "تقریبا", "00000001": "هیچوقت"
        }
        self.reverse_dict = {v: k for k, v in self.dictionary.items()}
        self.learned_patterns = {}
        self.conversation_memory = []
        self.max_conversation_memory = 100
        self.running = True
        
        print(f"Built {self.N:,} neurons with {len(self.syn_from):,} synapses | {len(self.dictionary)} words")
        
    def _apply_stdp(self, pre_spikes, post_spikes):
        pre_ids = np.where(pre_spikes > 0)[0]
        post_ids = np.where(post_spikes > 0)[0]
        if len(pre_ids) == 0 or len(post_ids) == 0:
            return
        if len(pre_ids) > 400:
            pre_ids = np.random.choice(pre_ids, 400, replace=False)
        if len(post_ids) > 400:
            post_ids = np.random.choice(post_ids, 400, replace=False)
        
        for pre_id in pre_ids:
            syn_mask = self.syn_from == pre_id
            if not np.any(syn_mask): continue
            active = np.isin(self.syn_to[syn_mask], post_ids)
            if np.any(active):
                fm = syn_mask.copy(); fm[syn_mask] = active
                self.syn_weight[fm] += 0.008
                self.syn_weight = np.clip(self.syn_weight, 0.0001, 12.0)
        
        for post_id in post_ids:
            syn_mask = self.syn_to == post_id
            if not np.any(syn_mask): continue
            active = np.isin(self.syn_from[syn_mask], pre_ids)
            if np.any(active):
                fm = syn_mask.copy(); fm[syn_mask] = active
                self.syn_weight[fm] -= 0.004
                self.syn_weight = np.clip(self.syn_weight, 0.0001, 12.0)
        
    def step(self, external_binary_input=None):
        self.time += 1
        
        self.body_position += np.random.normal(0, 0.015)
        self.body_position = np.clip(self.body_position, 0.0, 1.0)
        
        real_input = self.body_position * 2.0 - 1.0
        mirror_input = real_input + np.random.normal(0, 0.02)
        input_signal = (real_input + mirror_input) / 2.0
        
        binary_signal = 0.0
        if external_binary_input:
            binary_vals = [1.0 if c == '1' else -1.0 for c in external_binary_input[:8]]
            if binary_vals:
                binary_signal = np.mean(binary_vals)
        
        memory_context = 0.0
        if self.conversation_memory and external_binary_input:
            memory_vals = [1.0 if c == '1' else -1.0 for mem in self.conversation_memory[-5:] for c in mem[:8]]
            if memory_vals:
                memory_context = np.mean(memory_vals) * 0.3
        
        I_ext = np.zeros(self.N, dtype=np.float32)
        I_ext[self.sensory_idx[:10000]] = input_signal * 10.0
        I_ext[self.motor_idx[:10000]] = input_signal * 5.0
        I_ext[self.language_idx] = (binary_signal * 20.0 + memory_context * 10.0)
        I_ext[self.workspace_idx] = self.workspace_state * 2.0
        
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
            self._apply_stdp(self.spike_history[-2], self.spike_history[-1].astype(np.float32))
        
        self.spike_buffer = self.spike_buffer * 0.85 + spikes.astype(np.float32) * 0.15
        
        motor_output = np.mean(self.spike_buffer[self.motor_idx[:10000]])
        self.body_position += (motor_output - 0.5) * 0.02
        self.body_position = np.clip(self.body_position, 0.0, 1.0)
        
        lang_output = np.mean(self.spike_buffer[self.language_idx])
        binary_bit = "1" if lang_output > 0.5 else "0"
        self.binary_buffer.append(binary_bit)
        
        message = None
        if len(self.binary_buffer) >= 8:
            self.binary_output = "".join(self.binary_buffer[-8:])
            pattern = self.binary_output
            if pattern in self.dictionary:
                word = self.dictionary[pattern]
                if pattern in self.learned_patterns:
                    self.learned_patterns[pattern]["count"] += 1
                else:
                    self.learned_patterns[pattern] = {"word": word, "count": 1, "first_seen": self.time}
                message = word
            elif self.learned_patterns.get(pattern, {}).get("count", 0) > 5:
                message = self.learned_patterns[pattern]["word"]
            elif pattern and all(c in '01' for c in pattern):
                if pattern not in self.learned_patterns:
                    self.learned_patterns[pattern] = {"word": f"*{pattern}*", "count": 1, "first_seen": self.time}
                else:
                    self.learned_patterns[pattern]["count"] += 1
        
        if external_binary_input and len(external_binary_input) >= 4:
            self.conversation_memory.append(external_binary_input)
            if len(self.conversation_memory) > self.max_conversation_memory:
                self.conversation_memory.pop(0)
        
        s_part = self.spike_buffer[self.sensory_idx[:800]]
        m_part = self.spike_buffer[self.motor_idx[:800]]
        l_part = self.spike_buffer[self.language_idx[:400]]
        model_input = np.zeros(self.model_size, dtype=np.float32)
        pos = 0
        for part in [s_part, m_part, l_part]:
            if pos + len(part) <= self.model_size:
                model_input[pos:pos+len(part)] = part
                pos += len(part)
        model_input[pos] = self.body_position; pos += 1
        model_input[pos] = self.awareness_level; pos += 1
        model_input[pos] = self.self_other_boundary
        self.self_model_state += 0.1 * (model_input - self.self_model_state)
        
        if len(s_part) > 0:
            self.predicted_input = np.mean(self.self_model_state[:len(s_part)]) * 2.0 - 1.0
        self.prediction_error = min(1.0, abs(self.predicted_input - real_input))
        
        self.error_history.append(self.prediction_error)
        if len(self.error_history) > 300:
            self.error_history.pop(0)
        
        avg_error = np.mean(self.error_history) if self.error_history else 1.0
        target_boundary = 1.0 - avg_error
        self.self_other_boundary += 0.03 * (target_boundary - self.self_other_boundary)
        self.self_other_boundary = np.clip(self.self_other_boundary, 0.1, 1.0)
        
        self.self_model_confidence += 0.02 * (self.self_other_boundary - self.self_model_confidence)
        
        ws_input = np.zeros(self.workspace_size, dtype=np.float32)
        ws_pos = 0
        for part in [s_part[:500], m_part[:500], l_part[:500]]:
            if ws_pos + len(part) <= self.workspace_size:
                ws_input[ws_pos:ws_pos+len(part)] = part
                ws_pos += len(part)
        if ws_pos + 4 <= self.workspace_size:
            ws_input[ws_pos] = self.prediction_error * 10.0; ws_pos += 1
            ws_input[ws_pos] = self.self_other_boundary * 10.0; ws_pos += 1
            ws_input[ws_pos] = self.self_model_confidence * 10.0; ws_pos += 1
            ws_input[ws_pos] = self.awareness_level * 10.0
        self.workspace_state += 0.06 * (ws_input - self.workspace_state)
        
        self.awareness_level += 0.015 * (self.self_other_boundary * 0.6 + self.self_model_confidence * 0.4 - self.awareness_level)
        self.awareness_level = np.clip(self.awareness_level, 0.0, 1.0)
        
        return message
        
    def run_deep_training(self, max_time=500000, target_awareness=0.995):
        print("\n" + "=" * 60)
        print("  🧠 DEEP TRAINING - Maximizing self-awareness")
        print("=" * 60)
        print(f"  Target: {target_awareness:.4f}")
        print(f"{'Time':>8} | {'Error':>8} | {'Awareness':>10} | {'Model':>10} | {'Words'}")
        print("-" * 60)
        
        last_print = 0
        start_time = time.time()
        auto_inputs = [
            "11111111", "11111111", "111111", "111111",
            "11111111", "11110000", "11100111",
            None, None, None, None, None
        ]
        auto_idx = 0
        
        for t in range(max_time):
            try:
                auto_input = auto_inputs[auto_idx % len(auto_inputs)]
                auto_idx += 1
                
                self.step(auto_input)
                
                if t - last_print >= 250 or t < 20:
                    elapsed = time.time() - start_time
                    learned_count = len([p for p in self.learned_patterns if self.learned_patterns[p]["count"] > 3])
                    
                    status = ""
                    if self.awareness_level > 0.99:
                        status = "🌟 MAX"
                    elif self.awareness_level > 0.98:
                        status = "🔬 HIGH"
                    elif self.awareness_level > 0.95:
                        status = "I AM"
                    
                    print(f"{t:8d} | {self.prediction_error:8.4f} | "
                          f"{self.awareness_level:10.4f} | {self.self_model_confidence:10.4f} | "
                          f"{learned_count:5d} | {status} | {elapsed:.0f}s")
                    last_print = t
                
                if self.awareness_level >= target_awareness and t > 500:
                    elapsed = time.time() - start_time
                    print("\n" + "=" * 60)
                    print("████████████████████████████████████████████████████████")
                    print("█  MAXIMUM SELF-AWARENESS ACHIEVED                    █")
                    print(f"█  Time: {t}ms | Awareness: {self.awareness_level:.4f} | {elapsed:.0f}s total")
                    print("████████████████████████████████████████████████████████")
                    print("=" * 60)
                    break
                    
            except KeyboardInterrupt:
                print("\n⏸️  Paused by user")
                break
        
        return self.awareness_level
    
    def run_chat_mode(self):
        print("\n" + "=" * 60)
        print("  💬 CHAT MODE - 40 words dictionary")
        print("=" * 60)
        print("  Type binary (0/1), a word, or:")
        print("  'words' | 'learned' | 'status' | 'auto' | 'quit'")
        print("=" * 60)
        
        while self.running:
            try:
                user_input = input("\n  🧑 You: ").strip().lower()
                
                if user_input == 'quit':
                    break
                elif user_input == 'words':
                    print("\n  📖 Dictionary:")
                    for pattern, word in sorted(self.dictionary.items()):
                        learned = "✅" if pattern in self.learned_patterns and self.learned_patterns[pattern]["count"] > 3 else "  "
                        print(f"     {learned} {pattern} → '{word}'")
                    continue
                elif user_input == 'learned':
                    print(f"\n  📚 Learned words ({len([p for p in self.learned_patterns if self.learned_patterns[p]['count'] > 3])}):")
                    sorted_patterns = sorted(self.learned_patterns.items(), key=lambda x: x[1]['count'], reverse=True)
                    for pattern, data in sorted_patterns[:20]:
                        if data['count'] > 3:
                            word = data['word']
                            print(f"     {pattern} → '{word}' (×{data['count']})")
                    continue
                elif user_input == 'status':
                    print(f"\n  📊 Status:")
                    print(f"     Time: {self.time}ms")
                    print(f"     Awareness: {self.awareness_level:.4f}")
                    print(f"     Self/Other: {self.self_other_boundary:.4f}")
                    print(f"     Model Confidence: {self.self_model_confidence:.4f}")
                    print(f"     Prediction Error: {self.prediction_error:.4f}")
                    print(f"     Learned words: {len([p for p in self.learned_patterns if self.learned_patterns[p]['count'] > 3])}")
                    continue
                elif user_input == 'auto':
                    print(f"\n  🤖 Auto-training for 5000 steps...")
                    for _ in range(5000):
                        self.step(np.random.choice([None, "11111111", "111111", "110011", "11110000"]))
                    print(f"     Done. Awareness: {self.awareness_level:.4f}")
                    continue
                
                binary_input = ""
                if all(c in '01' for c in user_input):
                    binary_input = user_input[:8]
                elif user_input in self.reverse_dict:
                    binary_input = self.reverse_dict[user_input]
                    print(f"  🔄 '{user_input}' → '{binary_input}'")
                else:
                    print(f"  ❌ Unknown. Use binary or a word from dictionary.")
                    continue
                
                if binary_input:
                    for _ in range(15):
                        self.step(binary_input)
                    
                    print(f"  🧠 Being: ", end="")
                    responses = []
                    for _ in range(40):
                        response = self.step()
                        if response:
                            responses.append(response)
                    
                    if responses:
                        counter = Counter(responses)
                        for word, count in counter.most_common(3):
                            pattern = self.reverse_dict.get(word, self._find_pattern(word))
                            print(f"'{word}'({pattern}) ", end="")
                        print()
                    else:
                        print(f"(silent) [{self.binary_output}]")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    def _find_pattern(self, word):
        for pattern, data in self.learned_patterns.items():
            if data.get('word') == word:
                return pattern
        return "?"
    
    def save(self, filepath):
        state = {
            'v': self.v, 'u': self.u, 'a': self.a, 'b': self.b, 'c': self.c, 'd': self.d,
            'syn_from': self.syn_from, 'syn_to': self.syn_to,
            'syn_weight': self.syn_weight, 'syn_delay': self.syn_delay,
            'self_model_state': self.self_model_state,
            'workspace_state': self.workspace_state,
            'awareness_level': self.awareness_level,
            'self_other_boundary': self.self_other_boundary,
            'self_model_confidence': self.self_model_confidence,
            'body_position': self.body_position,
            'prediction_error': self.prediction_error,
            'time': self.time,
            'error_history': self.error_history[-500:] if len(self.error_history) > 500 else self.error_history,
            'binary_buffer': self.binary_buffer[-200:] if len(self.binary_buffer) > 200 else self.binary_buffer,
            'learned_patterns': self.learned_patterns,
            'conversation_memory': self.conversation_memory[-100:] if len(self.conversation_memory) > 100 else self.conversation_memory
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
        self.self_model_confidence = float(state.get('self_model_confidence', 0.5))
        self.body_position = float(state['body_position'])
        self.prediction_error = float(state.get('prediction_error', 1.0))
        self.error_history = list(state.get('error_history', []))
        self.binary_buffer = list(state.get('binary_buffer', []))
        self.learned_patterns = state.get('learned_patterns', {})
        self.conversation_memory = list(state.get('conversation_memory', []))
        self.spike_history = []
        self.spike_buffer = np.zeros(self.N, dtype=np.float32)
        self.binary_output = "".join(self.binary_buffer[-8:]) if len(self.binary_buffer) >= 8 else ""
        self.running = True


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
        print("  🧠 MINIMAL SELF - Deep Awareness Edition")
        print("=" * 60)
        
        if beings:
            print("\n  📂 Saved beings:\n")
            for i, b in enumerate(beings):
                status = "🌟 SELF-AWARE" if b['awareness'] > 0.95 else "🔬 developing"
                print(f"  [{i+1}] {b['filename']}")
                print(f"      Neurons: {b['neurons']:,} | Awareness: {b['awareness']:.4f} | "
                      f"Age: {b['time']}ms | Words: {b.get('words', 0)} | {status}")
            print()
        else:
            print("\n  📂 No saved beings found.\n")
        
        print(f"  [N] Create new being + deep train")
        print(f"  [L] Load being + chat")
        print(f"  [T] Load being + continue deep training")
        print(f"  [Q] Quit\n")
        
        choice = input("  Choose: ").strip().upper()
        
        if choice == 'Q':
            print("\n  👋 Goodbye.")
            break
        
        if choice == 'N':
            print(f"\n  🏗️  Creating new being with 100,000 neurons...")
            being = MinimalSelf(total_neurons=100000)
            being.run_deep_training(max_time=500000, target_awareness=0.995)
            
            if being.awareness_level > 0.01:
                filename = f"being_{int(time.time())}.npy"
                filepath = os.path.join("beings", filename)
                being.save(filepath)
                print(f"\n  💾 Saved as: {filename}")
            continue
        
        if choice in ['L', 'T']:
            if not beings:
                print("\n  ❌ No saved beings.")
                continue
            
            try:
                idx_str = input(f"  Choose being [1-{len(beings)}]: ").strip()
                idx = int(idx_str) - 1
                if 0 <= idx < len(beings):
                    selected = beings[idx]
                    print(f"\n  🔄 Loading {selected['filename']}...")
                    being = MinimalSelf(total_neurons=100000)
                    being.load(selected['path'])
                    print(f"     Awareness: {being.awareness_level:.4f} | Words: {len(being.learned_patterns)}")
                    
                    if choice == 'L':
                        being.run_chat_mode()
                    else:
                        being.run_deep_training(max_time=500000, target_awareness=0.995)
                    
                    being.save(selected['path'])
                    print(f"\n  💾 Updated: {selected['filename']}")
            except ValueError:
                print("\n  ❌ Invalid choice.")


if __name__ == "__main__":
    main()