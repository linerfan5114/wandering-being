# world.py
import numpy as np
import tkinter as tk

class World:
    def __init__(self, size=20):
        self.size = size
        self.light_map = np.zeros((size, size), dtype=np.float32)
        for x in range(size):
            for y in range(size):
                dist = np.sqrt((x-size/2)**2 + (y-size/2)**2)
                self.light_map[x,y] = max(0.0, min(1.0, 1.0 - dist/(size*0.7)))

class Body:
    def __init__(self, world, x=None, y=None):
        self.world = world
        self.x = x if x is not None else world.size//2
        self.y = y if y is not None else world.size//2
        self.vx, self.vy = 0.0, 0.0

    def get_visual_field(self):
        field = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                wx, wy = int(self.x+dx), int(self.y+dy)
                if 0<=wx<self.world.size and 0<=wy<self.world.size:
                    field.append(self.world.light_map[wx,wy])
                else:
                    field.append(0.0)
        return np.array(field, dtype=np.float32)

    def move(self, dx, dy):
        nx, ny = self.x + dx*0.3, self.y + dy*0.3
        if 0 <= nx < self.world.size-1 and 0 <= ny < self.world.size-1:
            self.x, self.y = nx, ny

class Display:
    def __init__(self, world, body):
        self.world = world
        self.body = body
        self.root = tk.Tk()
        self.root.title("Wandering Being")
        self.cs = 30
        self.canvas = tk.Canvas(self.root, width=world.size*self.cs+60, height=world.size*self.cs+60, bg='black')
        self.canvas.pack(pady=10)
        self.info = tk.Label(self.root, text="", font=("Courier",11), bg='black', fg='white')
        self.info.pack()
        self.aware = tk.Label(self.root, text="", font=("Courier",11), bg='black', fg='#ffaa00')
        self.aware.pack()
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.running = False
        self.root.destroy()

    def update(self, awareness, boundary, error):
        if not self.running: return
        self.canvas.delete("all")
        for x in range(self.world.size):
            for y in range(self.world.size):
                l = self.world.light_map[x,y]
                g = int(l*180+20)
                c = f'#{g:02x}{g:02x}{g:02x}'
                self.canvas.create_rectangle(x*self.cs+30, y*self.cs+30, (x+1)*self.cs+30, (y+1)*self.cs+30, fill=c, outline='#222')
        bx, by = self.body.x*self.cs+30, self.body.y*self.cs+30
        self.canvas.create_oval(bx+5, by+5, bx+self.cs-5, by+self.cs-5, fill='#ff4444', outline='white', width=2)
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                vx, vy = int(self.body.x+dx), int(self.body.y+dy)
                if 0<=vx<self.world.size and 0<=vy<self.world.size:
                    self.canvas.create_rectangle(vx*self.cs+32, vy*self.cs+32, (vx+1)*self.cs+28, (vy+1)*self.cs+28, outline='#fff', width=1, dash=(2,2))
        self.info.config(text=f"موقعيت: ({self.body.x:.1f}, {self.body.y:.1f}) | خطا: {error:.4f}")
        self.aware.config(text=f"آگاهي: {awareness:.4f} | مرز خود/جهان: {boundary:.4f}")
        self.root.update()

    def mainloop(self):
        self.root.mainloop()