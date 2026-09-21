# utilities/swarm_sim.py

import tkinter as tk
import random
import time
import math

class SwarmSimApp(tk.Frame):
    """
    Manages a particle swarm simulation within a Tkinter window.
    The original logic from VisualSeries_Swarm.py has been refactored to
    remove external dependencies like NumPy and win32api.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#1a1a26")
        self.show_main_menu_callback = show_main_menu_callback
        self._after_id = None

        # --- Configuration ---
        self.NUM_PARTICLES = 100
        self.GRAVITY_STRENGTH = 5e6
        self.FRICTION = 0.92
        self.POINT_SIZE = 8
        self.BG_COLOR = "#1a1a26"
        self.BOUNDARY_MARGIN = 20
        self.BOUNCE_FACTOR = -0.7
        self.TARGET_RADIUS = 50
        self.TARGET_CAPTURE_COUNT = 3
        
        self.canvas = tk.Canvas(self, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.target_position = [0, 0]
        self.target_id = None
        
        self.particle_positions = []
        self.particle_velocities = []
        self.particle_ids = []
        self.particle_colors = []

        self.last_time = time.perf_counter()
        
        back_button = tk.Button(self, text="Back to Menu", command=self.go_to_menu, bg="#4A4A4A", fg="white", relief="flat")
        self.canvas.create_window(80, 25, window=back_button, anchor="center")

        self.after(100, self.initialize_simulation)

    def initialize_simulation(self):
        """Creates particles and target once the window dimensions are known."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        self.target_position = [width / 2, height / 2]
        self.spawn_target()

        for _ in range(self.NUM_PARTICLES):
            self.particle_positions.append([
                random.uniform(0, width),
                random.uniform(0, height)
            ])
            self.particle_velocities.append([0.0, 0.0])
            self.particle_colors.append(f'#{random.randint(100, 256):02x}{random.randint(100, 256):02x}{random.randint(200, 256):02x}')
            self.particle_ids.append(
                self.canvas.create_oval(0, 0, self.POINT_SIZE, self.POINT_SIZE, fill=self.particle_colors[-1], outline="")
            )

        self.update_loop()

    def go_to_menu(self):
        """Wrapper to stop the loop before calling the menu callback."""
        self.stop_game_loop()
        self.show_main_menu_callback()

    def stop_game_loop(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def spawn_target(self):
        """Creates or moves the target to a new random location."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        self.target_position[0] = random.uniform(self.BOUNDARY_MARGIN + self.TARGET_RADIUS, width - self.BOUNDARY_MARGIN - self.TARGET_RADIUS)
        self.target_position[1] = random.uniform(self.BOUNDARY_MARGIN + self.TARGET_RADIUS, height - self.BOUNDARY_MARGIN - self.TARGET_RADIUS)

        x0, y0 = self.target_position[0] - self.TARGET_RADIUS, self.target_position[1] - self.TARGET_RADIUS
        x1, y1 = self.target_position[0] + self.TARGET_RADIUS, self.target_position[1] + self.TARGET_RADIUS

        if self.target_id is None:
            self.target_id = self.canvas.create_oval(x0, y0, x1, y1, outline="yellow", width=3)
            self.canvas.lower(self.target_id)
        else:
            self.canvas.coords(self.target_id, x0, y0, x1, y1)
        
    def update_loop(self):
        """The main simulation loop, rewritten with standard Python math."""
        current_time = time.perf_counter()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for i in range(self.NUM_PARTICLES):
            pos = self.particle_positions[i]
            vel = self.particle_velocities[i]
            
            dir_x = self.target_position[0] - pos[0]
            dir_y = self.target_position[1] - pos[1]
            
            dist_sq = dir_x**2 + dir_y**2 + 1e-9
            
            force_magnitude = self.GRAVITY_STRENGTH / dist_sq
            dist = math.sqrt(dist_sq)
            
            accel_x = (dir_x / dist) * force_magnitude
            accel_y = (dir_y / dist) * force_magnitude
            
            vel[0] += accel_x * dt
            vel[1] += accel_y * dt
            
            vel[0] *= self.FRICTION
            vel[1] *= self.FRICTION
            
            # --- FIX: Update position based on delta time (dt) ---
            pos[0] += vel[0] * dt
            pos[1] += vel[1] * dt

        for i in range(self.NUM_PARTICLES):
            pos = self.particle_positions[i]
            vel = self.particle_velocities[i]
            if pos[0] < self.BOUNDARY_MARGIN:
                pos[0] = self.BOUNDARY_MARGIN
                vel[0] *= self.BOUNCE_FACTOR
            elif pos[0] > width - self.BOUNDARY_MARGIN:
                pos[0] = width - self.BOUNDARY_MARGIN
                vel[0] *= self.BOUNCE_FACTOR
            
            if pos[1] < self.BOUNDARY_MARGIN:
                pos[1] = self.BOUNDARY_MARGIN
                vel[1] *= self.BOUNCE_FACTOR
            elif pos[1] > height - self.BOUNDARY_MARGIN:
                pos[1] = height - self.BOUNDARY_MARGIN
                vel[1] *= self.BOUNCE_FACTOR

        particles_inside = 0
        for pos in self.particle_positions:
            dist_to_target = math.hypot(pos[0] - self.target_position[0], pos[1] - self.target_position[1])
            if dist_to_target < self.TARGET_RADIUS:
                particles_inside += 1
        
        if particles_inside >= self.TARGET_CAPTURE_COUNT:
            self.spawn_target()

        for i in range(self.NUM_PARTICLES):
            x, y = self.particle_positions[i]
            radius = self.POINT_SIZE / 2
            self.canvas.coords(self.particle_ids[i], x - radius, y - radius, x + radius, y + radius)

        self._after_id = self.after(16, self.update_loop)