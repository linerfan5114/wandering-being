import numpy as np
import tkinter as tk
import time
import threading


class WanderingBeing:
    def __init__(self, total_neurons=100000, world_size=20):
        self.N = total_neurons
        self.world_size = world_size
        
        self.sensory_size = 20000
        self.motor_size = 20000
        self.model_size = 40000
        self.workspace_size = 20000
        
        self.sensory_idx = np.arange(0, self.sensory_size)
        self.motor_idx = np.arange(self.sensory_size, self.sensory_size + self.motor_size)
        self.model_idx = np.arange(self.sensory_size + self.motor_size, 
                                    self.sensory_size + self.motor_size + self.model_size)
        self.workspace_idx = np.arange(self.sensory_size + self.motor_size + self.model_size, self.N)
        
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
        self.prediction_error = 1.0
        self.error_history = []
        
        self.workspace_state = np.zeros(self.workspace_size, dtype=np.float32)
        self.awareness_level = 0.0
        self.self_other_boundary = 0.5
        
        self.x = world_size // 2
        self.y = world_size // 2
        self.time = 0
        
        self.movement_map = {
            0: (0, -1),
            1: (0, 1),
            2: (-1, 0),
            3: (1, 0)
        }
        
        self.predicted_sensory = np.zeros(9)
        self.actual_sensory = np.zeros(9)
        
        self.thought = "..."
        
        print(f"Built {self.N:,} neurons | World {world_size}×{world_size} | Self-determined movement")
        
    def _get_visual_field(self):
        field = np.zeros(9)
        idx = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                wx = self.x + dx
                wy = self.y + dy
                if 0 <= wx < self.world_size and 0 <= wy < self.world_size:
                    dist_from_center = np.sqrt((wx - self.world_size/2)**2 + (wy - self.world_size/2)**2)
                    light = 1.0 - dist_from_center / (self.world_size * 0.7)
                    field[idx] = max(0.0, min(1.0, light))
                idx += 1
        return field
        
    def _apply_stdp(self, pre_spikes, post_spikes):
        pre_ids = np.where(pre_spikes > 0)[0]
        post_ids = np.where(post_spikes > 0)[0]
        if len(pre_ids) == 0 or len(post_ids) == 0:
            return
        if len(pre_ids) > 300: pre_ids = np.random.choice(pre_ids, 300, replace=False)
        if len(post_ids) > 300: post_ids = np.random.choice(post_ids, 300, replace=False)
        
        for pre_id in pre_ids:
            syn_mask = self.syn_from == pre_id
            if not np.any(syn_mask): continue
            active = np.isin(self.syn_to[syn_mask], post_ids)
            if np.any(active):
                fm = syn_mask.copy(); fm[syn_mask] = active
                self.syn_weight[fm] += 0.006
                self.syn_weight = np.clip(self.syn_weight, 0.0001, 10.0)
        
        for post_id in post_ids:
            syn_mask = self.syn_to == post_id
            if not np.any(syn_mask): continue
            active = np.isin(self.syn_from[syn_mask], pre_ids)
            if np.any(active):
                fm = syn_mask.copy(); fm[syn_mask] = active
                self.syn_weight[fm] -= 0.003
                self.syn_weight = np.clip(self.syn_weight, 0.0001, 10.0)
        
    def step(self):
        self.time += 1
        
        visual_field = self._get_visual_field()
        self.actual_sensory = visual_field
        
        model_input = np.zeros(self.model_size, dtype=np.float32)
        if len(visual_field) + 4 <= self.model_size:
            model_input[:len(visual_field)] = visual_field
            model_input[len(visual_field)] = self.x / self.world_size
            model_input[len(visual_field)+1] = self.y / self.world_size
            model_input[len(visual_field)+2] = self.awareness_level
            model_input[len(visual_field)+3] = self.self_other_boundary
        self.self_model_state += 0.08 * (model_input - self.self_model_state)
        
        if len(visual_field) > 0:
            self.predicted_sensory = self.self_model_state[:len(visual_field)]
        
        sensory_input = visual_field
        
        I_ext = np.zeros(self.N, dtype=np.float32)
        for i in range(min(9, self.sensory_size)):
            self.sensory_idx_i = self.sensory_idx[i*2000:(i+1)*2000]
            if len(self.sensory_idx_i) > 0:
                I_ext[self.sensory_idx_i] = sensory_input[i] * 8.0
        
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
            self._apply_stdp(self.spike_history[-2], self.spike_history[-1].astype(np.float32))
        
        self.spike_buffer = self.spike_buffer * 0.85 + spikes.astype(np.float32) * 0.15
        
        motor_neurons = self.motor_idx[:4000]
        motor_signals = []
        for i in range(4):
            start = i * 1000
            end = (i + 1) * 1000
            if end <= len(motor_neurons):
                signal = np.mean(self.spike_buffer[motor_neurons[start:end]])
                motor_signals.append(signal)
        
        if len(motor_signals) == 4:
            prediction_errors = []
            for direction in range(4):
                dx, dy = self.movement_map[direction]
                nx = self.x + dx
                ny = self.y + dy
                if 0 <= nx < self.world_size and 0 <= ny < self.world_size:
                    dist = np.sqrt((nx - self.world_size/2)**2 + (ny - self.world_size/2)**2)
                    expected_light = 1.0 - dist / (self.world_size * 0.7)
                    expected_light = max(0.0, min(1.0, expected_light))
                    
                    if len(self.predicted_sensory) >= 9:
                        predicted_center = self.predicted_sensory[4]
                        error = abs(predicted_center - expected_light)
                    else:
                        error = 1.0
                    prediction_errors.append(error)
                else:
                    prediction_errors.append(1.0)
            
            motor_signals_np = np.array(motor_signals)
            motor_signals_np = motor_signals_np - np.min(motor_signals_np)
            if np.sum(motor_signals_np) > 0:
                motor_signals_np = motor_signals_np / np.sum(motor_signals_np)
            
            prediction_weights = 1.0 - np.array(prediction_errors)
            prediction_weights = np.clip(prediction_weights, 0.01, 1.0)
            if np.sum(prediction_weights) > 0:
                prediction_weights = prediction_weights / np.sum(prediction_weights)
            
            final_weights = motor_signals_np * 0.3 + prediction_weights * 0.7
            
            best_direction = np.argmax(final_weights)
            dx, dy = self.movement_map[best_direction]
            self.x = max(0, min(self.world_size - 1, self.x + dx))
            self.y = max(0, min(self.world_size - 1, self.y + dy))
            
            direction_names = ["بالا", "پایین", "چپ", "راست"]
            self.thought = f"می‌رم {direction_names[best_direction]} (خطا: {prediction_errors[best_direction]:.3f})"
        
        error_val = min(1.0, np.mean(np.abs(self.predicted_sensory[:9] - visual_field[:9])))
        self.prediction_error = error_val
        
        self.error_history.append(self.prediction_error)
        if len(self.error_history) > 200:
            self.error_history.pop(0)
        
        avg_error = np.mean(self.error_history) if self.error_history else 1.0
        target_boundary = 1.0 - avg_error
        self.self_other_boundary += 0.02 * (target_boundary - self.self_other_boundary)
        self.self_other_boundary = np.clip(self.self_other_boundary, 0.1, 1.0)
        
        ws_input = np.zeros(self.workspace_size, dtype=np.float32)
        if 9 + 4 <= self.workspace_size:
            ws_input[:9] = visual_field
            ws_input[9] = self.prediction_error * 10.0
            ws_input[10] = self.self_other_boundary * 10.0
            ws_input[11] = self.x / self.world_size * 10.0
            ws_input[12] = self.y / self.world_size * 10.0
        self.workspace_state += 0.05 * (ws_input - self.workspace_state)
        
        self.awareness_level += 0.01 * (self.self_other_boundary - self.awareness_level)
        self.awareness_level = np.clip(self.awareness_level, 0.0, 1.0)


class WorldDisplay:
    def __init__(self, being):
        self.being = being
        self.root = tk.Tk()
        self.root.title("Wandering Being")
        self.cell_size = 30
        self.world_size = being.world_size
        
        self.canvas = tk.Canvas(
            self.root, 
            width=self.world_size * self.cell_size + 100,
            height=self.world_size * self.cell_size + 100,
            bg='black'
        )
        self.canvas.pack(pady=10)
        
        self.info_label = tk.Label(self.root, text="", font=("Courier", 12), bg='black', fg='white')
        self.info_label.pack()
        
        self.thought_label = tk.Label(self.root, text="", font=("Courier", 10), bg='black', fg='#00ff00')
        self.thought_label.pack()
        
        self.awareness_label = tk.Label(self.root, text="", font=("Courier", 10), bg='black', fg='#ffaa00')
        self.awareness_label.pack()
        
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        self.running = False
        self.root.destroy()
        
    def update_display(self):
        if not self.running:
            return
            
        self.canvas.delete("all")
        
        for x in range(self.world_size):
            for y in range(self.world_size):
                x1 = x * self.cell_size + 50
                y1 = y * self.cell_size + 50
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                dist = np.sqrt((x - self.world_size/2)**2 + (y - self.world_size/2)**2)
                light = 1.0 - dist / (self.world_size * 0.7)
                light = max(0.05, min(1.0, light))
                
                gray = int(light * 200 + 20)
                color = f'#{gray:02x}{gray:02x}{gray:02x}'
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#333')
        
        bx = self.being.x * self.cell_size + 50
        by = self.being.y * self.cell_size + 50
        self.canvas.create_oval(
            bx + 5, by + 5, bx + self.cell_size - 5, by + self.cell_size - 5,
            fill='#ff4444', outline='white', width=2
        )
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                vx = self.being.x + dx
                vy = self.being.y + dy
                if 0 <= vx < self.world_size and 0 <= vy < self.world_size:
                    vx1 = vx * self.cell_size + 50
                    vy1 = vy * self.cell_size + 50
                    vx2 = vx1 + self.cell_size
                    vy2 = vy1 + self.cell_size
                    self.canvas.create_rectangle(
                        vx1 + 2, vy1 + 2, vx2 - 2, vy2 - 2,
                        outline='#ffffff', width=1, dash=(2, 2)
                    )
        
        info = f"موقعيت: ({self.being.x}, {self.being.y}) | زمان: {self.being.time}ms | خطا: {self.being.prediction_error:.3f}"
        self.info_label.config(text=info)
        
        self.thought_label.config(text=f"💭 {self.being.thought}")
        
        awareness_text = f"🧠 خودآگاهي: {self.being.awareness_level:.4f} | مرز خود/جهان: {self.being.self_other_boundary:.4f}"
        self.awareness_label.config(text=awareness_text)
        
        if self.running:
            self.root.after(200, self.update_display)


def main():
    print("=" * 60)
    print("  🧠 WANDERING BEING - World Explorer")
    print("=" * 60)
    print("  100,000 neurons | 20×20 world | Self-determined")
    print("=" * 60)
    
    being = WanderingBeing(total_neurons=100000, world_size=20)
    
    display = WorldDisplay(being)
    
    def simulation_loop():
        while display.running:
            try:
                being.step()
                time.sleep(0.05)
            except:
                break
    
    sim_thread = threading.Thread(target=simulation_loop, daemon=True)
    sim_thread.start()
    
    display.update_display()
    display.root.mainloop()
    
    print(f"\n✅ Simulation ended. Awareness: {being.awareness_level:.4f}")


if __name__ == "__main__":
    main()