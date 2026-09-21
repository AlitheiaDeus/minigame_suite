# boids.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-09-03
#
# A classic Boids flocking simulation demonstrating emergent behavior.

import tkinter as tk
import math
import random

# --- Vector2 Class for physics calculations ---
class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y
    def __add__(self, other): return Vector2(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Vector2(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar): return Vector2(self.x * scalar, self.y * scalar)
    def __truediv__(self, scalar): return Vector2(self.x / scalar, self.y / scalar) if scalar != 0 else Vector2()
    def magnitude_sq(self): return self.x**2 + self.y**2
    def magnitude(self): return math.hypot(self.x, self.y)
    def normalize(self):
        mag = self.magnitude()
        return self / mag if mag != 0 else Vector2()
    def limit(self, max_val):
        if self.magnitude_sq() > max_val**2:
            return self.normalize() * max_val
        return self

# --- Boid Class ---
class Boid:
    def __init__(self, x, y, canvas):
        self.canvas = canvas
        self.position = Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2(math.cos(angle), math.sin(angle))
        self.acceleration = Vector2()
        self.max_speed = 3.0
        self.max_force = 0.1
        self.shape_id = self.canvas.create_polygon(0,0,0,0,0,0, fill=self._random_color())
        
    def _random_color(self):
        return f'#{random.randint(100,255):02x}{random.randint(100,255):02x}{random.randint(200,255):02x}'

    def update(self):
        self.velocity += self.acceleration
        self.velocity = self.velocity.limit(self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0 # Reset acceleration each frame

    def apply_force(self, force):
        self.acceleration += force

    def flock(self, boids, perception, weights):
        """Calculates and applies the three flocking rules."""
        alignment = Vector2()
        cohesion = Vector2()
        separation = Vector2()
        total = 0
        
        for other in boids:
            if other is self: continue
            dist_sq = (self.position - other.position).magnitude_sq()
            if dist_sq < perception**2:
                alignment += other.velocity
                cohesion += other.position
                # Separation force is inversely proportional to distance
                diff = self.position - other.position
                separation += diff / dist_sq if dist_sq > 0 else diff
                total += 1

        if total > 0:
            alignment /= total
            alignment = alignment.normalize() * self.max_speed
            alignment -= self.velocity
            alignment = alignment.limit(self.max_force)

            cohesion /= total
            cohesion -= self.position
            cohesion = cohesion.normalize() * self.max_speed
            cohesion -= self.velocity
            cohesion = cohesion.limit(self.max_force)

            separation /= total
            separation = separation.normalize() * self.max_speed
            separation -= self.velocity
            separation = separation.limit(self.max_force)
        
        # --- FIX: Use the correct dictionary keys from the sliders ---
        self.apply_force(alignment * weights['alignment'])
        self.apply_force(cohesion * weights['cohesion'])
        self.apply_force(separation * weights['separation'])

    def wrap_edges(self, width, height):
        if self.position.x > width: self.position.x = 0
        elif self.position.x < 0: self.position.x = width
        if self.position.y > height: self.position.y = 0
        elif self.position.y < 0: self.position.y = height

    def draw(self):
        angle = math.atan2(self.velocity.y, self.velocity.x)
        p1 = (self.position.x + math.cos(angle) * 10, self.position.y + math.sin(angle) * 10)
        p2 = (self.position.x + math.cos(angle - 2.5) * 5, self.position.y + math.sin(angle - 2.5) * 5)
        p3 = (self.position.x + math.cos(angle + 2.5) * 5, self.position.y + math.sin(angle + 2.5) * 5)
        self.canvas.coords(self.shape_id, *p1, *p2, *p3)

# --- Main Application ---
class BoidsApp(tk.Frame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#1a1a26")
        self.show_main_menu_callback = show_main_menu_callback
        self.running = False
        self._setup_ui()
        self._bind_events()
        self.reset_simulation()

    def _setup_ui(self):
        self.canvas = tk.Canvas(self, bg="#1a1a26", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        control_panel = tk.Frame(self, bg="#2E2E2E", padx=10, pady=10)
        control_panel.pack(side="right", fill="y")
        
        self.sliders = {}
        slider_params = [
            ("Alignment", 0, 2, 1.0), ("Cohesion", 0, 2, 1.0),
            ("Separation", 0, 2, 1.2), ("Perception", 10, 200, 75)
        ]
        
        for name, from_, to, default in slider_params:
            tk.Label(control_panel, text=name, bg="#2E2E2E", fg="white").pack()
            slider = tk.Scale(control_panel, from_=from_, to=to, resolution=0.1, orient="horizontal", bg="#2E2E2E", fg="white", troughcolor="#4A4A4A", highlightthickness=0)
            slider.set(default)
            slider.pack(pady=(0, 10))
            self.sliders[name.lower()] = slider
            
        btn_style = {"bg": "#4A4A4A", "fg": "white", "relief": "flat", "pady": 5}
        self.run_button = tk.Button(control_panel, text="▶ Play", command=self.toggle_run, **btn_style)
        self.run_button.pack(fill="x", pady=5)
        tk.Button(control_panel, text="Reset", command=self.reset_simulation, **btn_style).pack(fill="x", pady=5)
        tk.Label(control_panel, text="Press ESC to Quit", font=("Helvetica", 10), bg="#2E2E2E", fg="#AAAAAA").pack(side="bottom", pady=10)

    def _bind_events(self):
        self.master.winfo_toplevel().bind("<Escape>", lambda e: self.show_main_menu_callback())

    def _unbind_events(self):
        self.master.winfo_toplevel().unbind("<Escape>")

    def reset_simulation(self):
        self.running = False
        self.run_button.config(text="▶ Play")
        if hasattr(self, 'run_job'): self.after_cancel(self.run_job)
        self.canvas.delete("all")
        
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 50: width, height = 800, 600 # Default size before window is drawn
        
        self.flock = [Boid(random.uniform(0, width), random.uniform(0, height), self.canvas) for _ in range(100)]
        for boid in self.flock: boid.draw()

    def toggle_run(self):
        self.running = not self.running
        if self.running:
            self.run_button.config(text="❚❚ Pause")
            self._run_loop()
        else:
            self.run_button.config(text="▶ Play")

    def _run_loop(self):
        if not self.running: return
        
        weights = {key: slider.get() for key, slider in self.sliders.items() if key != 'perception'}
        perception_radius = self.sliders['perception'].get()
        
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        for boid in self.flock:
            boid.wrap_edges(width, height)
            boid.flock(self.flock, perception_radius, weights)
            boid.update()
            boid.draw()
            
        self.run_job = self.after(16, self._run_loop)

    def stop_game_loop(self):
        self.running = False
        if hasattr(self, 'run_job'): self.after_cancel(self.run_job)
        self._unbind_events()