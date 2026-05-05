# run.py
import time
import numpy as np
import matplotlib.pyplot as plt
from being import Being
from world import World3D
import os, glob

class Body:
    def __init__(self, world_size=15):
        self.x = world_size // 2
        self.y = world_size // 2
        self.z = world_size // 2
        self.world_size = world_size
    
    def get_visual_field(self, world_light):
        field = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    wx, wy, wz = int(self.x+dx), int(self.y+dy), int(self.z+dz)
                    if 0<=wx<self.world_size and 0<=wy<self.world_size and 0<=wz<self.world_size:
                        field.append(world_light[wx,wy,wz])
                    else:
                        field.append(0.0)
        return np.array(field, dtype=np.float32)
    
    def move(self, motor):
        dx = (motor[3] - motor[2]) * 0.5
        dy = (motor[1] - motor[0]) * 0.5
        dz = (motor[5] - motor[4]) * 0.5
        
        nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
        if 0 <= nx < self.world_size-1: self.x = nx
        if 0 <= ny < self.world_size-1: self.y = ny
        if 0 <= nz < self.world_size-1: self.z = nz


def main():
    os.makedirs("beings", exist_ok=True)
    beings = sorted(glob.glob("beings/*.npy"))
    
    print("="*60)
    print("  🧠 WANDERING BEING - 3D World (matplotlib)")
    print("="*60)
    
    if beings:
        print("\n  📂 Saved beings:")
        for i,b in enumerate(beings):
            print(f"  [{i+1}] {os.path.basename(b)}")
        print(f"  [N] Create new being")
        c = input("  Choose: ").strip().upper()
        if c == 'N':
            being = Being(total_neurons=100000)
            print("\n  🆕 New being created for 3D world.")
        else:
            try:
                idx = int(c)-1
                being = Being(total_neurons=100000)
                being.load(beings[idx])
                print(f"\n  🔄 Loaded. Awareness: {being.awareness:.4f}")
            except:
                print("  ❌ Invalid. Creating new.")
                being = Being(total_neurons=100000)
    else:
        print("\n  🆕 No saved beings. Creating new for 3D world.")
        being = Being(total_neurons=100000)
    
    world = World3D(size=15)
    body = Body(world_size=15)
    
    print("\n  🖱️  Close window to save and exit.")
    print("  🧠 Being will explore the 3D world freely.")
    
    step = 0
    while world.running:
        fov = body.get_visual_field(world.light_map)
        motor = being.step(fov)
        body.move(motor)
        
        if step % 5 == 0:
            world.render(body.x, body.y, body.z, being.awareness, being.self_boundary, being.prediction_error)
        step += 1
    
    plt.close('all')
    
    filename = f"beings/being_{int(time.time())}.npy"
    being.save(filename)
    print(f"\n  💾 Saved: {filename}")
    print(f"  🧠 Awareness: {being.awareness:.4f}")

if __name__ == "__main__":
    main()