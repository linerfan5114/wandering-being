import numpy as np

class Physics:
    def __init__(self, world_size=15):
        self.gravity = 0.02
        self.mass = 1.0
        self.friction = 0.85
        self.wind = np.zeros(3, dtype=np.float32)
        self.wind_change_timer = 0
        self.wind_interval = 100
        self.world_size = world_size
        
    def update(self):
        self.wind_change_timer += 1
        if self.wind_change_timer >= self.wind_interval:
            self.wind = np.random.uniform(-0.1, 0.1, 3).astype(np.float32)
            self.wind_change_timer = 0
            
    def apply_forces(self, velocity, position, world_size):
        gravity_force = np.array([0.0, 0.0, -self.gravity * self.mass])
        
        friction_force = -velocity * (1.0 - self.friction)
        
        wind_force = self.wind * 0.5
        
        total_force = gravity_force + friction_force + wind_force
        new_velocity = velocity + total_force
        new_velocity = np.clip(new_velocity, -0.5, 0.5)
        
        new_position = position + new_velocity
        
        new_position = np.array([
            np.clip(new_position[0], 0.5, world_size - 1.5),
            np.clip(new_position[1], 0.5, world_size - 1.5),
            np.clip(new_position[2], 0.5, world_size - 1.5)
        ])
        
        if new_position[2] <= 0.5:
            new_velocity[2] = 0
            new_position[2] = 0.5
            
        return new_velocity, new_position
        
    def get_wind_vector(self):
        return self.wind.copy()