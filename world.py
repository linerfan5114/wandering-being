# world.py
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

class World3D:
    def __init__(self, size=15):
        self.size = size
        self.light_map = np.zeros((size, size, size), dtype=np.float32)
        cx, cy, cz = size/2, size/2, size/2
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    dist = np.sqrt((x-cx)**2 + (y-cy)**2 + (z-cz)**2)
                    self.light_map[x,y,z] = max(0.0, min(1.0, 1.0 - dist/(size*0.7)))
        
        plt.ion()
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlim(0, size)
        self.ax.set_ylim(0, size)
        self.ax.set_zlim(0, size)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('Wandering Being - 3D World')
        
        self.scatter = None
        self.being_point = None
        
        self._draw_world()
        
        self.running = True
        self.fig.canvas.mpl_connect('close_event', self._on_close)
        
    def _on_close(self, event):
        self.running = False
        
    def _draw_world(self):
        xs, ys, zs = np.meshgrid(
            np.arange(self.size),
            np.arange(self.size),
            np.arange(self.size),
            indexing='ij'
        )
        xs = xs.flatten()
        ys = ys.flatten()
        zs = zs.flatten()
        colors = self.light_map.flatten()
        
        bright = colors * 0.3 + 0.7
        rgba = np.zeros((len(xs), 4))
        rgba[:, 0] = bright * 0.9
        rgba[:, 1] = bright * 0.7
        rgba[:, 2] = bright * 0.5
        rgba[:, 3] = 0.3
        
        self.scatter = self.ax.scatter(xs, ys, zs, c=rgba, s=20, marker='o')
        
    def render(self, body_x, body_y, body_z, awareness, boundary, error):
        if self.being_point:
            self.being_point.remove()
        
        self.being_point = self.ax.scatter([body_x], [body_y], [body_z], 
                                            c='red', s=200, marker='o', edgecolors='white', linewidth=2)
        
        self.ax.set_title(
            f'Awareness: {awareness:.4f} | Self/Other: {boundary:.4f} | Error: {error:.4f} | '
            f'Pos: ({body_x:.1f}, {body_y:.1f}, {body_z:.1f})'
        )
        
        plt.draw()
        plt.pause(0.01)