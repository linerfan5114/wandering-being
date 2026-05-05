import numpy as np
import matplotlib.pyplot as plt

class World3D:
    def __init__(self, size=15):
        self.size = size
        self.light_map = np.zeros((size, size, size), dtype=np.float32)
        cx, cy, cz = size/2, size/2, size/2
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    dist = np.sqrt((x-cx)**2 + (y-cy)**2 + (z-cz)**2)
                    self.light_map[x,y,z] = max(0.01, min(1.0, 1.0 - dist/(size*0.7)))
        
        self.vanished_region = None
        self.vanished_timer = 0
        
        plt.ion()
        self.fig = plt.figure(figsize=(14, 8))
        
        self.ax = self.fig.add_subplot(121, projection='3d')
        self.ax.set_xlim(0, size)
        self.ax.set_ylim(0, size)
        self.ax.set_zlim(0, size)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        self.ax_info = self.fig.add_subplot(122)
        self.ax_info.set_xlim(0, 10)
        self.ax_info.set_ylim(0, 10)
        self.ax_info.axis('off')
        
        self.scatter = None
        self.being_point = None
        self.wind_arrow = None
        self.gravity_line = None
        self.info_texts = []
        
        self._draw_world()
        
        self.running = True
        self.fig.canvas.mpl_connect('close_event', self._on_close)
        self.step_count = 0
        
    def _on_close(self, event):
        self.running = False
        
    def update_vanished_region(self):
        self.step_count += 1
        if self.step_count % 500 == 0 and self.vanished_region is None:
            cx, cy, cz = np.random.randint(2, self.size-2, 3)
            self.vanished_region = (cx, cy, cz, 3)
            self.vanished_timer = 200
        elif self.vanished_timer > 0:
            self.vanished_timer -= 1
            if self.vanished_timer <= 0:
                self.vanished_region = None
        
    def _draw_world(self):
        xs, ys, zs = np.meshgrid(np.arange(self.size), np.arange(self.size), np.arange(self.size), indexing='ij')
        xs, ys, zs = xs.flatten(), ys.flatten(), zs.flatten()
        colors = self.light_map.flatten()
        
        bright = colors * 0.3 + 0.7
        rgba = np.zeros((len(xs), 4))
        rgba[:, 0] = bright * 0.9
        rgba[:, 1] = bright * 0.7
        rgba[:, 2] = bright * 0.5
        rgba[:, 3] = 0.3
        
        if self.vanished_region:
            vx, vy, vz, vr = self.vanished_region
            for i, (x, y, z) in enumerate(zip(xs, ys, zs)):
                dist = np.sqrt((x-vx)**2 + (y-vy)**2 + (z-vz)**2)
                if dist < vr:
                    rgba[i, 3] = 0.05
        
        if self.scatter:
            self.scatter.remove()
        self.scatter = self.ax.scatter(xs, ys, zs, c=rgba, s=15, marker='o')
        
    def render(self, body_x, body_y, body_z, velocity, wind, awareness, boundary, error,
               nonexistence_aw, temporal_depth, was_here, could_not_be, wake_cycles, is_asleep=False):
        self.update_vanished_region()
        
        if self.step_count % 20 == 0:
            self._draw_world()
        
        if self.being_point:
            self.being_point.remove()
        if self.wind_arrow:
            self.wind_arrow.remove()
        if self.gravity_line:
            self.gravity_line.remove()
        
        being_color = '#4444ff' if is_asleep else '#ff3333'
        being_size = 80 if is_asleep else 180
        self.being_point = self.ax.scatter([body_x], [body_y], [body_z], 
                                            c=being_color, s=being_size, marker='o', 
                                            edgecolors='white', linewidth=2)
        
        if wind[0] != 0 or wind[1] != 0 or wind[2] != 0:
            wind_scale = 10
            self.wind_arrow = self.ax.quiver(body_x, body_y, body_z,
                                              wind[0]*wind_scale, wind[1]*wind_scale, wind[2]*wind_scale,
                                              color='cyan', linewidth=2, alpha=0.7)
        
        self.gravity_line = self.ax.plot([body_x, body_x], [body_y, body_y], 
                                          [body_z, 0], 'g--', linewidth=1, alpha=0.5)[0]
        
        status = "SLEEP" if is_asleep else "AWAKE"
        speed = np.sqrt(velocity[0]**2 + velocity[1]**2 + velocity[2]**2)
        self.ax.set_title(f'{status} | Pos: ({body_x:.1f},{body_y:.1f},{body_z:.1f}) | Speed: {speed:.3f}')
        
        for text in self.info_texts:
            text.remove()
        self.info_texts = []
        
        info_lines = [
            f"STATE: {status} | Cycles: {wake_cycles}",
            f"",
            f"PHYSICS:",
            f"  Gravity: ↓ 0.02",
            f"  Mass: 1.0",
            f"  Speed: {speed:.4f}",
            f"  Wind: ({wind[0]:.3f}, {wind[1]:.3f}, {wind[2]:.3f})",
            f"",
            f"CONSCIOUSNESS:",
            f"  Awareness: {awareness:.4f}",
            f"  Self/Other: {boundary:.4f}",
            f"  Error: {error:.4f}",
            f"",
            f"EXISTENCE:",
            f"  Non-Exist Aw: {nonexistence_aw:.4f}",
            f"  Temporal Depth: {temporal_depth:.4f}",
            f"  Was Here: {was_here:.4f}",
            f"  Could Not Be: {could_not_be:.4f}",
        ]
        
        for i, line in enumerate(info_lines):
            text = self.ax_info.text(0.5, 9.5 - i*0.42, line, fontsize=8, 
                                     fontfamily='monospace', verticalalignment='top')
            self.info_texts.append(text)
        
        if self.vanished_region:
            v_text = self.ax_info.text(0.5, 0.3, f"VANISHED REGION! {self.vanished_timer}", 
                                       fontsize=10, color='red', fontweight='bold',
                                       fontfamily='monospace', verticalalignment='top')
            self.info_texts.append(v_text)
        
        plt.draw()
        plt.pause(0.01)