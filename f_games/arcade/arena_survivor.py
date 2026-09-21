# games/arcade/arena_survivor.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-08-29
#
# A top-down, infinite bullet-hell game where survival is key.
# The player's health is represented by a shrinking "Life Ring,"
# creating a tense, visually-driven experience.

import tkinter as tk
from tkinter import font
import random
import math

class ArenaSurvivorGame(tk.Frame):
    """
    An infinite arcade game where the player must dodge an ever-increasing
    barrage of projectiles. The player's health is a visible, shrinking ring
    around them, making the play area progressively more dangerous.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#1a1a1a")
        self.show_main_menu_callback = show_main_menu_callback
        self.game_loop_id = None

        # --- Game Configuration ---
        self.player_size = 15
        self.player_speed = 350  # Pixels per second
        self.projectile_size = 8
        self.base_projectile_speed = 180 # Pixels per second
        self.initial_base_projectile_speed = 180 # Store initial value for resets
        self.max_projectile_speed = 450 # Pixels per second
        self.initial_health = 10
        self.gravity_strength = 0.5 # A small acceleration factor for homing

        # --- Game State Variables ---
        self.player = None
        self.life_ring = None
        self.projectiles = []
        self.keys_pressed = set()
        self.is_game_over = True
        self.score = 0
        self.health = 0
        
        # Difficulty scaling timers
        self.spawn_rate_ms = 500
        self.difficulty_timer = 0
        self.time_elapsed = 0
        self.spawn_timer = 0

        # --- UI Setup ---
        self.setup_ui()
        
        # Bind events to the top-level window to ensure they are always captured.
        self.bind_events()
        
        # The canvas takes a moment to get its size.
        # We start the game after a short delay to ensure dimensions are correct.
        self.after(100, self.start_game)

    def setup_ui(self):
        """Initializes the canvas and UI elements like score and health displays."""
        # --- Fonts ---
        self.score_font = font.Font(family="Consolas", size=24, weight="bold")
        self.health_font = font.Font(family="Consolas", size=16)
        self.game_over_font = font.Font(family="Helvetica", size=48, weight="bold")
        self.final_score_font = font.Font(family="Helvetica", size=20)
        self.button_font = font.Font(family="Helvetica", size=14)

        # --- Game Canvas ---
        self.canvas = tk.Canvas(self, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Heads-Up Display (HUD) ---
        self.hud_frame = tk.Frame(self, bg="#1a1a1a")
        self.hud_frame.pack(fill="x", padx=10, pady=(0, 10))

        # --- Left-aligned HUD items ---
        left_hud = tk.Frame(self.hud_frame, bg="#1a1a1a")
        left_hud.pack(side="left")
        
        button_style = {
            "bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A",
            "activeforeground": "white", "relief": "flat", "pady": 5, "padx": 10,
            "font": self.button_font
        }
        menu_button = tk.Button(left_hud, text="← Menu (Esc)", command=self.go_to_main_menu, **button_style)
        menu_button.pack(side="left", padx=(0, 20))

        self.score_label = tk.Label(left_hud, text="Time: 0.0s", font=self.score_font, bg="#1a1a1a", fg="#00ff99")
        self.score_label.pack(side="left", padx=10)

        # --- Right-aligned HUD items ---
        self.health_label = tk.Label(self.hud_frame, text=f"Ring Integrity: {self.initial_health}", font=self.health_font, bg="#1a1a1a", fg="#ff5555")
        self.health_label.pack(side="right", padx=10)


    def start_game(self):
        """Resets the game state and starts the main game loop."""
        # --- FIX: Re-bind events on every restart to ensure controls work ---
        self.bind_events()

        self.is_game_over = False
        self.score = 0
        self.time_elapsed = 0
        self.health = self.initial_health
        self.spawn_rate_ms = 500
        self.difficulty_timer = 0
        # --- FIX: Reset projectile speed and spawn timer on restart ---
        self.base_projectile_speed = self.initial_base_projectile_speed
        self.spawn_timer = 0
        
        self.canvas.delete("all")
        self.projectiles.clear()
        self.keys_pressed.clear()

        # Center the player
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.player_pos = [canvas_width / 2, canvas_height / 2]

        # Create player and life ring objects
        self.player = self.canvas.create_oval(0, 0, self.player_size * 2, self.player_size * 2, fill="#00aaff", outline="")
        self.life_ring = self.canvas.create_oval(0, 0, 0, 0, outline="#ff5555", width=3)
        
        self.update_player_position()
        self.update_life_ring()
        self.update_hud()

        # Start the game loop
        self.game_loop()

    def game_loop(self):
        """The main game loop, running every ~16ms (60 FPS)."""
        if self.is_game_over:
            return

        # --- Timers and Score ---
        # Using a fixed delta time for consistent physics
        delta_time = 16 / 1000.0
        self.time_elapsed += delta_time
        self.score = self.time_elapsed
        self.difficulty_timer += delta_time

        # --- Game Logic ---
        self.move_player(delta_time)
        self.spawn_projectiles()
        self.move_projectiles(delta_time)
        self.check_collisions()
        self.update_difficulty()
        self.update_hud()

        # Schedule the next frame
        self.game_loop_id = self.after(16, self.game_loop)

    def stop_game_loop(self):
        """Safely stops the game loop and unbinds events when the frame is destroyed."""
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
        # --- FIX: Unbind from the top-level window to properly clean up ---
        toplevel = self.winfo_toplevel()
        toplevel.unbind("<KeyPress>")
        toplevel.unbind("<KeyRelease>")
        # --- FIX: Removed redundant <Escape> unbind, as it's handled by the general <KeyPress> event ---

    # --- Player & Events ---
    def bind_events(self):
        """Binds all necessary game events to the top-level window."""
        toplevel = self.winfo_toplevel()
        toplevel.bind("<KeyPress>", self.on_key_press)
        toplevel.bind("<KeyRelease>", self.on_key_release)

    def go_to_main_menu(self):
        """Stops the game and returns to the main menu."""
        self.stop_game_loop()
        self.show_main_menu_callback()

    def on_key_press(self, event):
        """Handles key press events for player movement and game actions."""
        key = event.keysym.lower()
        # --- FEATURE: Allow quitting mid-game with Escape key ---
        if key == 'escape':
            self.go_to_main_menu()
            return
        self.keys_pressed.add(key)

    def on_key_release(self, event):
        """Handles key release events."""
        self.keys_pressed.discard(event.keysym.lower())

    def move_player(self, delta_time):
        """Updates player position based on currently pressed keys."""
        velocity = [0, 0]
        if 'w' in self.keys_pressed or 'up' in self.keys_pressed:
            velocity[1] -= 1
        if 's' in self.keys_pressed or 'down' in self.keys_pressed:
            velocity[1] += 1
        if 'a' in self.keys_pressed or 'left' in self.keys_pressed:
            velocity[0] -= 1
        if 'd' in self.keys_pressed or 'right' in self.keys_pressed:
            velocity[0] += 1

        # Normalize diagonal movement to prevent faster speed
        magnitude = math.sqrt(velocity[0]**2 + velocity[1]**2)
        if magnitude > 0:
            velocity[0] /= magnitude
            velocity[1] /= magnitude

        # Update position based on speed and delta_time for frame-rate independence
        self.player_pos[0] += velocity[0] * self.player_speed * delta_time
        self.player_pos[1] += velocity[1] * self.player_speed * delta_time

        # Boundary checks
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.player_pos[0] = max(self.player_size, min(self.player_pos[0], canvas_width - self.player_size))
        self.player_pos[1] = max(self.player_size, min(self.player_pos[1], canvas_height - self.player_size))

        self.update_player_position()
        self.update_life_ring()
        
    def update_player_position(self):
        """Syncs the player's canvas object with its state variables."""
        if not self.player: return
        x, y = self.player_pos
        self.canvas.coords(self.player, x - self.player_size, y - self.player_size, x + self.player_size, y + self.player_size)

    # --- Health & Life Ring ---
    def update_life_ring(self):
        """Updates the size and position of the health ring based on current health."""
        if not self.life_ring: return
        
        if self.health <= 0:
            self.canvas.itemconfig(self.life_ring, state='hidden')
            return
        
        ring_radius = self.player_size + (self.health * 2.5) + 5
        x, y = self.player_pos
        self.canvas.coords(self.life_ring, x - ring_radius, y - ring_radius, x + ring_radius, y + ring_radius)

    def take_damage(self):
        """Reduces health and checks for game over."""
        self.health -= 1
        self.update_life_ring()
        if self.health <= 0:
            self.health = 0
            self.game_over()

    # --- Projectiles ---
    def spawn_projectiles(self):
        """Spawns new projectiles at a rate determined by spawn_rate_ms."""
        # --- FIX: Timer is now correctly reset in start_game() ---
        if self.time_elapsed - self.spawn_timer > self.spawn_rate_ms / 1000.0:
            self.spawn_timer = self.time_elapsed
            self.create_projectile()

    def create_projectile(self):
        """Creates a single projectile at a random screen edge, aimed at the player."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        
        if edge == 'top':
            x = random.uniform(0, canvas_width)
            y = -self.projectile_size
        elif edge == 'bottom':
            x = random.uniform(0, canvas_width)
            y = canvas_height + self.projectile_size
        elif edge == 'left':
            x = -self.projectile_size
            y = random.uniform(0, canvas_height)
        else: # right
            x = canvas_width + self.projectile_size
            y = random.uniform(0, canvas_height)
            
        player_x, player_y = self.player_pos
        angle_rad = math.atan2(player_y - y, player_x - x)
        angle_rad += random.uniform(-0.1, 0.1)

        current_speed = random.uniform(self.base_projectile_speed, self.base_projectile_speed * 1.2)
        vx = math.cos(angle_rad) * current_speed
        vy = math.sin(angle_rad) * current_speed

        obj = self.canvas.create_oval(
            x - self.projectile_size, y - self.projectile_size,
            x + self.projectile_size, y + self.projectile_size,
            fill="#ff4444", outline=""
        )
        self.projectiles.append({'id': obj, 'x': x, 'y': y, 'vx': vx, 'vy': vy})

    def move_projectiles(self, delta_time):
        """Moves all projectiles, applies gravity, and removes those off-screen."""
        projectiles_to_remove = []
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        player_x, player_y = self.player_pos

        for proj in self.projectiles:
            vec_to_player_x = player_x - proj['x']
            vec_to_player_y = player_y - proj['y']
            dist_to_player = math.sqrt(vec_to_player_x**2 + vec_to_player_y**2)
            
            if dist_to_player > 1:
                proj['vx'] += (vec_to_player_x / dist_to_player) * self.gravity_strength
                proj['vy'] += (vec_to_player_y / dist_to_player) * self.gravity_strength

            proj['x'] += proj['vx'] * delta_time
            proj['y'] += proj['vy'] * delta_time
            
            self.canvas.coords(proj['id'], 
                proj['x'] - self.projectile_size, proj['y'] - self.projectile_size,
                proj['x'] + self.projectile_size, proj['y'] + self.projectile_size
            )

            if (proj['x'] < -self.projectile_size * 2 or 
                proj['x'] > canvas_width + self.projectile_size * 2 or
                proj['y'] < -self.projectile_size * 2 or 
                proj['y'] > canvas_height + self.projectile_size * 2):
                projectiles_to_remove.append(proj)

        for proj in projectiles_to_remove:
            self.canvas.delete(proj['id'])
            self.projectiles.remove(proj)

    # --- Game Logic & State ---
    def check_collisions(self):
        """Checks for collisions between the player and projectiles."""
        projectiles_to_remove = []
        px, py = self.player_pos

        for proj in self.projectiles:
            dist_sq = (px - proj['x'])**2 + (py - proj['y'])**2
            if dist_sq < (self.player_size + self.projectile_size)**2:
                projectiles_to_remove.append(proj)
                self.take_damage()

        for proj in projectiles_to_remove:
            if proj in self.projectiles: 
                self.canvas.delete(proj['id'])
                self.projectiles.remove(proj)
    
    def update_difficulty(self):
        """Increases game difficulty over time."""
        if self.difficulty_timer > 5.0:
            self.difficulty_timer = 0
            
            if self.spawn_rate_ms > 100:
                self.spawn_rate_ms -= 20

            if self.base_projectile_speed < self.max_projectile_speed:
                self.base_projectile_speed += 10

    def update_hud(self):
        """Updates the score and health labels."""
        self.score_label.config(text=f"Time: {self.score:.1f}s")
        self.health_label.config(text=f"Ring Integrity: {self.health}")

    def game_over(self):
        """Stops the game and displays the game over screen."""
        self.is_game_over = True
        self.stop_game_loop() 
        
        overlay = self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill="black", stipple="gray50", outline="")

        self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2 - 50, text="GAME OVER", font=self.game_over_font, fill="#ff3333")
        self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2 + 30, text=f"You survived for {self.score:.2f} seconds", font=self.final_score_font, fill="white")

        button_frame = tk.Frame(self.canvas, bg="#111111", highlightthickness=0)
        
        button_style = {
            "bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A",
            "activeforeground": "white", "relief": "flat", "pady": 10, "padx": 20,
            "font": self.button_font
        }

        retry_btn = tk.Button(button_frame, text="Retry", command=self.start_game, **button_style)
        retry_btn.pack(side="left", padx=10)

        menu_btn = tk.Button(button_frame, text="Back to Menu", command=self.go_to_main_menu, **button_style)
        menu_btn.pack(side="left", padx=10)
        
        self.canvas.create_window(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2 + 120, window=button_frame)

