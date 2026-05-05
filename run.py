import time
import numpy as np
import matplotlib.pyplot as plt
from being import Being
from world import World3D
from physics import Physics
import os, glob

class Body:
    def __init__(self, world_size=15):
        self.x = float(world_size // 2)
        self.y = float(world_size // 2)
        self.z = float(world_size // 2)
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
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
    
    def apply_motor(self, motor):
        fwd = motor[3] - motor[2]
        side = motor[1] - motor[0]
        up = motor[5] - motor[4]
        self.vx += fwd * 0.1
        self.vy += side * 0.1
        self.vz += up * 0.1


def main():
    os.makedirs("beings", exist_ok=True)
    beings = sorted(glob.glob("beings/*.npy"))
    
    print("="*60)
    print("  🧠 WANDERING BEING - Physics World")
    print("="*60)
    print("  Gravity | Wind | Mass | Friction | Weight")
    print("="*60)
    
    if beings:
        print("\n  📂 Saved beings:")
        for i,b in enumerate(beings):
            print(f"  [{i+1}] {os.path.basename(b)}")
        print(f"  [N] Create new being")
        c = input("  Choose: ").strip().upper()
        if c == 'N':
            being = Being(total_neurons=100000)
            print("\n  🆕 New being with physics world.")
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
        print("\n  🆕 No saved beings. Creating new.")
        being = Being(total_neurons=100000)
    
    world = World3D(size=15)
    body = Body(world_size=15)
    physics = Physics(world_size=15)
    
    print("\n  🖱️  Close window to save and exit.")
    print("  🌬️  Wind changes every 100 steps")
    print("  ⬇️  Gravity pulls being down")
    print("  🧱  Being has weight and friction")
    
    step = 0
    awake_steps = 200
    sleep_steps = 50
    is_asleep = False
    
    while world.running:
        if step % (awake_steps + sleep_steps) < awake_steps:
            is_asleep = False
        else:
            is_asleep = True
        
        physics.update()
        
        if not is_asleep:
            fov = body.get_visual_field(world.light_map)
            motor = being.step(fov, is_asleep=False)
            body.apply_motor(motor)
            
            velocity = np.array([body.vx, body.vy, body.vz])
            position = np.array([body.x, body.y, body.z])
            new_velocity, new_position = physics.apply_forces(velocity, position, world.size)
            
            body.x, body.y, body.z = new_position
            body.vx, body.vy, body.vz = new_velocity
        else:
            being.step(np.zeros(27), is_asleep=True)
        
        if step % 5 == 0:
            velocity = np.array([body.vx, body.vy, body.vz])
            world.render(
                body.x, body.y, body.z,
                velocity,
                physics.get_wind_vector(),
                being.awareness,
                being.self_boundary,
                being.prediction_error,
                being.nonexistence_awareness,
                being.temporal_depth,
                being.was_here_before,
                being.could_not_be,
                being.wake_cycles,
                is_asleep
            )
        
        step += 1
    
    plt.close('all')
    
    filename = f"beings/being_{int(time.time())}.npy"
    being.save(filename)
    print(f"\n  💾 Saved: {filename}")
    print(f"  🧠 Awareness: {being.awareness:.4f}")

if __name__ == "__main__":
    main()