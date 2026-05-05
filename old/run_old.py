# run.py
import time
import threading
import numpy as np
from being import Being
from world import World, Body, Display
import os, glob

def main():
    os.makedirs("beings", exist_ok=True)
    beings = sorted(glob.glob("beings/*.npy"))

    print("="*60)
    print("  🧠 WANDERING BEING - Self-Discovery")
    print("="*60)

    if beings:
        print("\n  📂 Saved beings:")
        for i,b in enumerate(beings):
            print(f"  [{i+1}] {os.path.basename(b)}")
        print(f"  [N] Create new being")
        c = input("  Choose: ").strip().upper()
        if c == 'N':
            being = Being(total_neurons=100000)
            print("\n  🆕 New being created.")
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

    world = World(size=20)
    body = Body(world)
    display = Display(world, body)

    def simulation():
        while display.running:
            fov = body.get_visual_field()
            motor = being.step(fov)

            dx = (motor[3]-motor[2])*0.5
            dy = (motor[1]-motor[0])*0.5
            body.move(dx, dy)

            display.update(being.awareness, being.self_boundary, being.prediction_error)
            time.sleep(0.05)

    t = threading.Thread(target=simulation, daemon=True)
    t.start()

    print("\n  🖱️  Close window to save and exit.")
    display.mainloop()

    filename = f"beings/being_{int(time.time())}.npy"
    being.save(filename)
    print(f"\n  💾 Saved: {filename}")
    print(f"  🧠 Awareness: {being.awareness:.4f}")

if __name__ == "__main__":
    main()