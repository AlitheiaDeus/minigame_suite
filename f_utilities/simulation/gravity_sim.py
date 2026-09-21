# utilities/gravity_sim.py

import tkinter as tk
import math
import random
import time

# --- A simple Vector2 class for physics calculations ---
class Vector2:
    """A simple 2D vector class to handle position, velocity, and acceleration."""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    @property
    def magnitude(self):
        # Use hypot for safe square root calculation
        return math.hypot(self.x, self.y)

    def normalize(self):
        mag = self.magnitude
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

# --- The Particle class, adapted for Tkinter ---
class Particle:
    """Represents a single arrow particle in the simulation for Tkinter."""
    def __init__(self, x, y, canvas):
        self.canvas = canvas
        self.position = Vector2(x, y)
        
        initial_angle = random.uniform(0, 2 * math.pi)
        initial_speed = random.uniform(20.0, 125.0) # MIN_SPEED, MAX_SPEED / 2
        self.velocity = Vector2(math.cos(initial_angle) * initial_speed, math.sin(initial_angle) * initial_speed)

        self.acceleration_magnitude = 150.0 + random.uniform(-100.0, 100.0) # ACCELERATION_BASE, ACCELERATION_VARIANCE
        
        # Base shape of the particle (a simple triangle)
        self.base_shape = [
            Vector2(0, -10),   # Tip
            Vector2(-6, 8),    # Bottom-left
            Vector2(6, 8)     # Bottom-right
        ]
        
        self.shape_id = self.canvas.create_polygon(0,0, 0,0, 0,0, fill=self._random_color(), outline="")
        self.rotation = 0 # Stored in degrees

    def _random_color(self):
        """Generates a random bright color string for Tkinter."""
        return f'#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(200, 255):02x}'

    def update_shape_on_canvas(self):
        """Calculates rotated points and updates the polygon on the canvas."""
        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Transform base shape points to world coordinates
        rotated_points = []
        for point in self.base_shape:
            rotated_x = point.x * cos_a - point.y * sin_a
            rotated_y = point.x * sin_a + point.y * cos_a
            
            final_x = self.position.x + rotated_x
            final_y = self.position.y + rotated_y
            rotated_points.extend([final_x, final_y])
        
        self.canvas.coords(self.shape_id, *rotated_points)

class GravitySimApp(tk.Frame):
    """A particle attraction simulation where particles follow the mouse."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#1a1a26")
        self.show_main_menu_callback = show_main_menu_callback
        self._after_id = None
        
        # --- Configuration ---
        self.NUM_PARTICLES = 150
        self.MAX_SPEED = 250.0
        self.DAMPING_FACTOR = 0.99
        self.MAX_ROTATION_SPEED = 270.0  # degrees per second
        self.BOUNDARY_MARGIN = 20
        self.BOUNCE_FACTOR = -0.8
        self.BG_COLOR = "#1a1a26"

        self.canvas = tk.Canvas(self, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.mouse_pos = Vector2(self.winfo_width() / 2, self.winfo_height() / 2)
        self.mouse_in_window = False

        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<Enter>", self.on_mouse_enter)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        
        # Add a back button
        back_button = tk.Button(self, text="Back to Menu", command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat")
        self.canvas.create_window(80, 25, window=back_button, anchor="center")

        self.particles = []
        self.last_time = time.perf_counter()
        
        # Defer particle creation until the canvas has a size
        self.after(100, self.initialize_simulation)

    def initialize_simulation(self):
        """Create particles once the window dimensions are known."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.particles = [Particle(
            random.randint(self.BOUNDARY_MARGIN, width - self.BOUNDARY_MARGIN),
            random.randint(self.BOUNDARY_MARGIN, height - self.BOUNDARY_MARGIN),
            self.canvas
        ) for _ in range(self.NUM_PARTICLES)]
        self.update_loop()

    def stop_game_loop(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def on_mouse_motion(self, event):
        self.mouse_pos.x = event.x
        self.mouse_pos.y = event.y

    def on_mouse_enter(self, event):
        self.mouse_in_window = True

    def on_mouse_leave(self, event):
        self.mouse_in_window = False

    def update_loop(self):
        """The core logic and rendering loop."""
        current_time = time.perf_counter()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for p in self.particles:
            # 1. ORIENTATION
            if self.mouse_in_window:
                direction_to_mouse = self.mouse_pos - p.position
                target_angle = math.degrees(math.atan2(direction_to_mouse.y, direction_to_mouse.x)) - 90
            else:
                target_angle = math.degrees(math.atan2(p.velocity.y, p.velocity.x)) - 90 if p.velocity.magnitude > 1 else p.rotation

            angle_diff = (target_angle - p.rotation + 180) % 360 - 180
            turn_this_frame = max(-self.MAX_ROTATION_SPEED * dt, min(self.MAX_ROTATION_SPEED * dt, angle_diff))
            p.rotation += turn_this_frame

            # 2. ACCELERATION & DAMPING
            if self.mouse_in_window:
                current_angle_rad = math.radians(p.rotation + 90)
                accel_direction = Vector2(math.cos(current_angle_rad), math.sin(current_angle_rad))
                acceleration = accel_direction * p.acceleration_magnitude
                p.velocity = p.velocity + (acceleration * dt)
            else:
                p.velocity = p.velocity * self.DAMPING_FACTOR

            # 3. CAPPED VELOCITY
            if p.velocity.magnitude > self.MAX_SPEED:
                p.velocity = p.velocity.normalize() * self.MAX_SPEED
            
            # 4. POSITION UPDATE
            p.position = p.position + (p.velocity * dt)

            # 5. BOUNDARY COLLISION
            if p.position.x < self.BOUNDARY_MARGIN and p.velocity.x < 0:
                p.velocity.x *= self.BOUNCE_FACTOR
                p.position.x = self.BOUNDARY_MARGIN
            elif p.position.x > width - self.BOUNDARY_MARGIN and p.velocity.x > 0:
                p.velocity.x *= self.BOUNCE_FACTOR
                p.position.x = width - self.BOUNDARY_MARGIN

            if p.position.y < self.BOUNDARY_MARGIN and p.velocity.y < 0:
                p.velocity.y *= self.BOUNCE_FACTOR
                p.position.y = self.BOUNDARY_MARGIN
            elif p.position.y > height - self.BOUNDARY_MARGIN and p.velocity.y > 0:
                p.velocity.y *= self.BOUNCE_FACTOR
                p.position.y = height - self.BOUNDARY_MARGIN
            
            # 6. VISUAL UPDATE
            p.update_shape_on_canvas()

        self._after_id = self.after(16, self.update_loop)
