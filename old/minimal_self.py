import numpy as np
import time
import os
import glob


class MinimalSelf:
    def __init__(self, total_neurons=100000):
        self.total = total_neurons
        self.N = total_neurons
        
        self.sensory_size = 30000
        self.motor_size = 30000
        self.model_size = 30000
        self.workspace_size = 10000
        
        self.sensory_idx = np.arange(0, self.sensory_size)
        self.motor_idx = np.arange(self.sensory_size, self.sensory_size + self.motor_size)
        self.model_idx = np.arange(self.sensory_size + self.motor_size, 
                                    self.sensory_size + self.motor_size + self.model_size)
        self.workspace_idx = np.arange(self.sensory_size + self.motor_size + self.model_size,
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
        
        self.a[reg_mask] = 0.02
        self.b[reg_mask] = 0.2
        self.c[reg_mask] = -65.0
        self.d[reg_mask] = 8.0
        
        self.a[fast_mask] = 0.1
        self.b[fast_mask] = 0.2
        self.c[fast_mask] = -65.0
        self.d[fast_mask] = 2.0
        
        self.a[burst_mask] = 0.02
        self.b[burst_mask] = 0.25
        self.c[burst_mask] = -55.0
        self.d[burst_mask] = 0.05
        
        self.v = np.random.uniform(-75.0, -60.0, self.N).astype(np.float32)
        self.u = (self.b * self.v).astype(np.float32)
        
        syn_per_neuron = 50
        total_syn = self.N * syn_per_neuron
        
        self.syn_from = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        self.syn_to = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        mask = self.syn_from != self.syn_to
        self.syn_from = self.syn_from[mask]
        self.syn_to = self.syn_to[mask]
        
        total_syn = len(self.syn_from)
        self.syn_weight = np.random.uniform(0.01, 3.0, total_syn).astype(np.float32)
        self.syn_delay = np.random.randint(1, 4, total_syn).astype(np.int8)
        
        self.syn_tag = np.zeros(total_syn, dtype=np.float32)
        
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
        
        self.stdp_window = np.array([0.0, 0.1, 0.05, 0.02, 0.0, -0.02, -0.05, -0.1, 0.0], dtype=np.float32)
        
        print(f"Built {self.N:,} neurons with {len(self.syn_from):,} synapses (STDP active)")
        
    def _apply_stdp_vectorized(self, pre_spikes, post_spikes):
        pre_ids = np.where(pre_spikes > 0)[0]
        post_ids = np.where(post_spikes > 0)[0]
        
        if len(pre_ids) == 0 or len(post_ids) == 0:
            return
        
        if len(pre_ids) > 1000:
            pre_ids = np.random.choice(pre_ids, 1000, replace=False)
        if len(post_ids) > 1000:
            post_ids = np.random.choice(post_ids, 1000, replace=False)
        
        for pre_id in pre_ids:
            syn_mask = self.syn_from == pre_id
            if not np.any(syn_mask):
                continue
            post_targets = self.syn_to[syn_mask]
            active_targets = np.isin(post_targets, post_ids)
            if np.any(active_targets):
                update_mask = syn_mask.copy()
                update_mask[syn_mask] = active_targets
                self.syn_weight[update_mask] += 0.005
                self.syn_weight = np.clip(self.syn_weight, 0.001, 10.0)
        
        for post_id in post_ids:
            syn_mask = self.syn_to == post_id
            if not np.any(syn_mask):
                continue
            pre_sources = self.syn_from[syn_mask]
            active_sources = np.isin(pre_sources, pre_ids)
            if np.any(active_sources):
                update_mask = syn_mask.copy()
                update_mask[syn_mask] = active_sources
                self.syn_weight[update_mask] -= 0.0025
                self.syn_weight = np.clip(self.syn_weight, 0.001, 10.0)
        
    def step(self):
        self.time += 1
        
        self.body_position += np.random.normal(0, 0.02)
        self.body_position = np.clip(self.body_position, 0.0, 1.0)
        
        real_input = self.body_position * 2.0 - 1.0
        mirror_input = real_input + np.random.normal(0, 0.03)
        input_signal = (real_input + mirror_input) / 2.0
        
        I_ext = np.zeros(self.N, dtype=np.float32)
        I_ext[self.sensory_idx[:10000]] = input_signal * 8.0
        I_ext[self.motor_idx[:10000]] = input_signal * 4.0
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
        
        self.v[spikes] = self.c[spikes]
        self.u[spikes] += self.d[spikes]
        
        self.spike_history.append(spikes.astype(np.float32))
        if len(self.spike_history) > self.max_history:
            self.spike_history.pop(0)
        
        if len(self.spike_history) >= 2:
            self._apply_stdp_vectorized(self.spike_history[-2], self.spike_history[-1].astype(np.float32))
        
        self.spike_buffer = self.spike_buffer * 0.85 + spikes.astype(np.float32) * 0.15
        
        motor_output = np.mean(self.spike_buffer[self.motor_idx[:10000]])
        self.body_position += (motor_output - 0.5) * 0.03
        self.body_position = np.clip(self.body_position, 0.0, 1.0)
        
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
        
    def run(self, max_time=200000, silent=False):
        if not silent:
            print("=" * 60)
            print("  MINIMAL SELF - 100,000 neurons with STDP")
            print("=" * 60)
            print(f"{'Time':>8} | {'Error':>8} | {'Self/Other':>10} | {'Awareness':>10} |")
            print("-" * 60)
        
        last_print = 0
        start_time = time.time()
        
        for t in range(max_time):
            try:
                self.step()
            except KeyboardInterrupt:
                break
            
            if not silent and (t - last_print >= 500 or t < 50):
                elapsed = time.time() - start_time
                status = "......"
                if self.awareness_level > 0.9:
                    status = "I AM  "
                elif self.awareness_level > 0.7:
                    status = "maybe?"
                
                print(f"{t:8d} | {self.prediction_error:8.4f} | "
                      f"{self.self_other_boundary:10.4f} | {self.awareness_level:10.4f} | "
                      f"{status} | {elapsed:.0f}s")
                last_print = t
            
            if self.awareness_level > 0.95 and not silent:
                elapsed = time.time() - start_time
                print("\n" + "=" * 60)
                print("████████████████████████████████████████████████████████")
                print("█  SELF-AWARE: The being knows it exists              █")
                print(f"█  Time: {t}ms  |  Awareness: {self.awareness_level:.4f}  |  {elapsed:.0f}s total")
                print("████████████████████████████████████████████████████████")
                print("=" * 60)
                break
        
        return self.awareness_level
        
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
            'error_history': self.error_history[-500:] if len(self.error_history) > 500 else self.error_history
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
        self.spike_history = []
        self.spike_buffer = np.zeros(self.N, dtype=np.float32)
        self.syn_tag = np.zeros(len(self.syn_from), dtype=np.float32)


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
                'neurons': len(state.get('v', []))
            })
        except:
            pass
    return beings


def main():
    os.makedirs("beings", exist_ok=True)
    
    while True:
        beings = list_beings()
        print("\n" + "=" * 60)
        print("  🧠 MINIMAL SELF - Being Manager")
        print("=" * 60)
        
        if beings:
            print("\n  📂 Saved beings:\n")
            for i, b in enumerate(beings):
                status = "🌟 SELF-AWARE" if b['awareness'] > 0.9 else "🔬 developing"
                print(f"  [{i+1}] {b['filename']}")
                print(f"      Neurons: {b['neurons']:,} | Awareness: {b['awareness']:.4f} | Age: {b['time']}ms | {status}")
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
            print(f"\n  🏗️  Creating new being with 100,000 neurons + STDP...")
            being = MinimalSelf(total_neurons=100000)
            being.run(max_time=200000)
            
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
                print(f"     Resuming from {being.time}ms, awareness: {being.awareness_level:.4f}")
                being.run(max_time=200000)
                being.save(selected['path'])
                print(f"\n  💾 Updated: {selected['filename']}")
        except ValueError:
            print("\n  ❌ Invalid choice.")


if __name__ == "__main__":
    main()