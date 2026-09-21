# games/arcade/dot_racer.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-09-01
#
# A momentum-based game with two modes:
# 1. Race Mode: Reach a target before the AI does.
# 2. Survival Mode: Collect targets to reset the timer while hunted by AI.

import tkinter as tk
import random
import math

# --- Game Constants ---
PLAYER_SIZE = 10
PLAYER_ACCEL = 0.4
PLAYER_FRICTION = 0.96
TARGET_SIZE = 15
OBSTACLE_COUNT = 10
OBSTACLE_SIZE_MIN = 20
OBSTACLE_SIZE_MAX = 50

# --- Race Mode Constants ---
RACE_AI_SIZE = 10
RACE_AI_ACCEL = 0.35
RACE_AI_FRICTION = 0.96
RACE_DURATION = 4 # seconds
RACE_RESTITUTION = 1.1

# --- NEW: Survival Mode Constants ---
SURVIVAL_AI_COUNT = 3
SURVIVAL_AI_SIZE = 12
SURVIVAL_AI_ACCEL = 0.42
SURVIVAL_AI_FRICTION = 0.97
SURVIVAL_DURATION = 8 # seconds
SURVIVAL_RESTITUTION = 1.3


class DotRacerGame(tk.Frame):
    """
    A dual-mode, momentum-based dot game.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu = show_main_menu_callback
        self.after_id = None

        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas_width = 800
        self.canvas_height = 600

        # --- Game State ---
        self.player_pos = {'x': 0, 'y': 0}
        self.player_vel = {'x': 0, 'y': 0}
        self.target_pos = {'x': 0, 'y': 0}

        # --- MODIFIED: Handle multiple AIs ---
        self.ais = []

        self.score = 0
        self.highest_score = 0
        self.player_targets_hit = 0
        self.time_left = 0
        self.game_over = False
        
        # --- NEW: Game mode state ---
        self.game_mode = None
        self.mode_frame = None

        self.player_id = self.target_id = None
        self.obstacle_ids = []
        self.score_text_id = self.timer_text_id = self.game_over_text_id = None

        self.keys_pressed = { "w": False, "a": False, "s": False, "d": False }

        self.setup_ui()
        # --- MODIFIED: Show mode selection instead of starting immediately ---
        self.show_mode_selection()

    def setup_ui(self):
        """Initializes the main UI elements of the game ONE TIME."""
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="#28283C", highlightthickness=0)
        self.canvas.grid(row=0, column=0, pady=20, padx=20)

        self.score_text_id = self.canvas.create_text(20, 20, anchor="nw", font=("Helvetica", 16, "bold"), fill="white")
        self.timer_text_id = self.canvas.create_text(self.canvas_width - 20, 20, anchor="ne", font=("Helvetica", 16, "bold"), fill="white")
        
        # --- NEW: Hide UI elements until game starts ---
        self.canvas.itemconfig(self.score_text_id, state='hidden')
        self.canvas.itemconfig(self.timer_text_id, state='hidden')

        back_button = tk.Button(self, text="← Menu", command=self.go_to_main_menu, bg="#4A4A4A", fg="white", font=("Helvetica", 12), relief="flat", padx=10, pady=5)
        self.canvas.create_window(20, self.canvas_height - 20, anchor="sw", window=back_button)

        restart_button = tk.Button(self, text="Restart", command=self.show_mode_selection, bg="#4A4A4A", fg="white", font=("Helvetica", 12), relief="flat", padx=10, pady=5)
        self.canvas.create_window(self.canvas_width - 20, self.canvas_height - 20, anchor="se", window=restart_button)

    # --- NEW: Mode Selection Screen ---
    def show_mode_selection(self):
        """Clears the canvas and displays buttons for the player to choose a game mode."""
        self.stop_game_loop()
        self.clear_game_objects()
        self.unbind_all_events() # Make sure no game keys are active
        
        if self.mode_frame: self.mode_frame.destroy()
        
        self.canvas.itemconfig(self.score_text_id, state='hidden')
        self.canvas.itemconfig(self.timer_text_id, state='hidden')
        
        self.mode_frame = tk.Frame(self, bg="#28283C")
        
        title = tk.Label(self.mode_frame, text="Select a Game Mode", font=("Helvetica", 24, "bold"), bg="#28283C", fg="white")
        title.pack(pady=(0, 20))

        race_btn = tk.Button(self.mode_frame, text="Race Mode", font=("Helvetica", 16), command=lambda: self.start_game(mode='race'), bg="#4A4A4A", fg="white", relief="flat", padx=20, pady=10, width=15)
        race_btn.pack(pady=10)
        
        survival_btn = tk.Button(self.mode_frame, text="Survival Mode", font=("Helvetica", 16), command=lambda: self.start_game(mode='survival'), bg="#4A4A4A", fg="white", relief="flat", padx=20, pady=10, width=15)
        survival_btn.pack(pady=10)

        self.canvas.create_window(self.canvas_width/2, self.canvas_height/2, window=self.mode_frame, anchor="center")

    def bind_events(self):
        """Binds keyboard events to the top-level window to ensure focus."""
        toplevel = self.winfo_toplevel()
        toplevel.bind("<KeyPress>", self.on_key_press)
        toplevel.bind("<KeyRelease>", self.on_key_release)
        toplevel.bind("<r>", lambda e: self.show_mode_selection())
        toplevel.bind("<R>", lambda e: self.show_mode_selection())

    def unbind_all_events(self):
        """Unbinds all game-related keyboard events."""
        toplevel = self.winfo_toplevel()
        toplevel.unbind("<KeyPress>")
        toplevel.unbind("<KeyRelease>")
        toplevel.unbind("<r>")
        toplevel.unbind("<R>")

    def unbind_movement_events(self):
        """Unbinds only the WASD movement keys."""
        toplevel = self.winfo_toplevel()
        toplevel.unbind("<KeyPress>")
        toplevel.unbind("<KeyRelease>")

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in self.keys_pressed: self.keys_pressed[key] = True

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys_pressed: self.keys_pressed[key] = False

    def clear_game_objects(self):
        """Deletes only the dynamic game objects from the canvas."""
        # --- MODIFIED: Clear multiple AIs ---
        ids_to_delete = [self.player_id, self.target_id, self.game_over_text_id] + self.obstacle_ids
        for ai in self.ais:
            ids_to_delete.append(ai.get('id'))
            
        for item_id in ids_to_delete:
            if item_id: self.canvas.delete(item_id)
            
        self.obstacle_ids.clear()
        self.ais.clear()
        self.player_id = self.target_id = self.game_over_text_id = None

    # --- MODIFIED: `start_game` now accepts a mode ---
    def start_game(self, mode):
        """Resets the game state and starts the main game loop for the chosen mode."""
        self.stop_game_loop()
        self.clear_game_objects()
        
        # --- NEW: Cleanup mode selection UI ---
        if self.mode_frame: self.mode_frame.destroy(); self.mode_frame = None
        self.canvas.itemconfig(self.score_text_id, state='normal')
        self.canvas.itemconfig(self.timer_text_id, state='normal')

        self.game_mode = mode
        self.keys_pressed = { "w": False, "a": False, "s": False, "d": False }
        self.game_over = False
        self.player_targets_hit = 0

        # --- NEW: Mode-specific setup ---
        if self.game_mode == 'race':
            self.score = 2
            self.highest_score = self.score
            self.time_left = RACE_DURATION
            self.spawn_ais(count=1)
        elif self.game_mode == 'survival':
            self.score = 0
            self.highest_score = self.score
            self.time_left = SURVIVAL_DURATION
            self.spawn_ais(count=SURVIVAL_AI_COUNT)

        self.update_score_display()
        self.update_timer_display()

        self.spawn_obstacles()

        self.player_pos = {'x': self.canvas_width / 2, 'y': self.canvas_height / 2}
        self.player_vel = {'x': 0, 'y': 0}
        self.player_id = self.canvas.create_oval(0, 0, PLAYER_SIZE * 2, PLAYER_SIZE * 2, fill="#FAD264", outline="")
        
        self.spawn_target()
        self.bind_events()
        self.game_loop()

    # --- NEW: Function to spawn AIs based on mode ---
    def spawn_ais(self, count):
        for _ in range(count):
            if self.game_mode == 'race':
                pos = {'x': self.canvas_width * 3 / 4, 'y': self.canvas_height / 2}
                size = RACE_AI_SIZE
                color = "magenta"
            else: # survival
                # Spawn away from the center
                side = random.choice(['top', 'bottom', 'left', 'right'])
                if side == 'top': pos = {'x': random.uniform(0, self.canvas_width), 'y': size}
                elif side == 'bottom': pos = {'x': random.uniform(0, self.canvas_width), 'y': self.canvas_height - size}
                elif side == 'left': pos = {'x': size, 'y': random.uniform(0, self.canvas_height)}
                else: pos = {'x': self.canvas_width - size, 'y': random.uniform(0, self.canvas_height)}
                size = SURVIVAL_AI_SIZE
                color = "#C70039"
            
            ai_id = self.canvas.create_oval(0, 0, size * 2, size * 2, fill=color, outline="")
            self.ais.append({
                'pos': pos, 'vel': {'x': 0, 'y': 0}, 'id': ai_id, 'size': size
            })

    def reset_obstacles(self):
        """Deletes old obstacles and spawns new ones."""
        for obs_id in self.obstacle_ids: self.canvas.delete(obs_id)
        self.obstacle_ids.clear()
        self.spawn_obstacles()

    def spawn_obstacles(self):
        """Creates a new set of obstacles on the canvas."""
        for _ in range(OBSTACLE_COUNT):
            size = random.uniform(OBSTACLE_SIZE_MIN, OBSTACLE_SIZE_MAX)
            while True:
                x = random.uniform(size, self.canvas_width - size)
                y = random.uniform(size, self.canvas_height - size)
                # Avoid spawn points
                player_dist_sq = (x - self.canvas_width/2)**2 + (y - self.canvas_height/2)**2
                ai_dist_sq = (x - self.canvas_width*3/4)**2 + (y - self.canvas_height/2)**2
                if player_dist_sq > 100**2 and (self.game_mode != 'race' or ai_dist_sq > 100**2):
                    break
            obs_id = self.canvas.create_oval(x-size/2, y-size/2, x+size/2, y+size/2, fill="#3C3C3C", outline="")
            self.obstacle_ids.append(obs_id)

    def spawn_target(self):
        while True:
            self.target_pos['x'] = random.uniform(TARGET_SIZE, self.canvas_width - TARGET_SIZE)
            self.target_pos['y'] = random.uniform(TARGET_SIZE, self.canvas_height - TARGET_SIZE)
            # Avoid corners with UI
            if (self.target_pos['x'] < 120 and self.target_pos['y'] > self.canvas_height - 70) or \
               (self.target_pos['x'] > self.canvas_width - 120 and self.target_pos['y'] > self.canvas_height - 70):
                continue
            if not any(self.check_collision_by_coords(self.target_pos, TARGET_SIZE, obs_id) for obs_id in self.obstacle_ids):
                break

        if self.target_id and self.canvas.find_withtag(self.target_id):
            self.canvas.coords(self.target_id, self.target_pos['x']-TARGET_SIZE, self.target_pos['y']-TARGET_SIZE, self.target_pos['x']+TARGET_SIZE, self.target_pos['y']+TARGET_SIZE)
        else:
            self.target_id = self.canvas.create_oval(self.target_pos['x']-TARGET_SIZE, self.target_pos['y']-TARGET_SIZE, self.target_pos['x']+TARGET_SIZE, self.target_pos['y']+TARGET_SIZE, fill="#3399FF", outline="")

    def update_player(self):
        if self.keys_pressed['w']: self.player_vel['y'] -= PLAYER_ACCEL
        if self.keys_pressed['s']: self.player_vel['y'] += PLAYER_ACCEL
        if self.keys_pressed['a']: self.player_vel['x'] -= PLAYER_ACCEL
        if self.keys_pressed['d']: self.player_vel['x'] += PLAYER_ACCEL

        self.player_vel['x'] *= PLAYER_FRICTION
        self.player_vel['y'] *= PLAYER_FRICTION
        self.player_pos['x'] += self.player_vel['x']
        self.player_pos['y'] += self.player_vel['y']

        if self.player_pos['x'] < PLAYER_SIZE or self.player_pos['x'] > self.canvas_width - PLAYER_SIZE:
            self.player_vel['x'] *= -0.8
            self.player_pos['x'] = max(PLAYER_SIZE, min(self.player_pos['x'], self.canvas_width - PLAYER_SIZE))
        if self.player_pos['y'] < PLAYER_SIZE or self.player_pos['y'] > self.canvas_height - PLAYER_SIZE:
            self.player_vel['y'] *= -0.8
            self.player_pos['y'] = max(PLAYER_SIZE, min(self.player_pos['y'], self.canvas_height - PLAYER_SIZE))

        self.canvas.moveto(self.player_id, self.player_pos['x'] - PLAYER_SIZE, self.player_pos['y'] - PLAYER_SIZE)

    # --- MODIFIED: `update_ai` now handles one AI from the list and uses mode logic ---
    def update_ai(self, ai):
        """Updates a single AI's position based on the current game mode."""
        if self.game_mode == 'survival':
            target_pos = self.player_pos
            accel = SURVIVAL_AI_ACCEL
            friction = SURVIVAL_AI_FRICTION
        else: # race
            target_pos = self.target_pos
            accel = RACE_AI_ACCEL
            friction = RACE_AI_FRICTION

        dx = target_pos['x'] - ai['pos']['x']
        dy = target_pos['y'] - ai['pos']['y']
        dist = math.hypot(dx, dy)

        if dist > 1:
            ai['vel']['x'] += (dx / dist) * accel
            ai['vel']['y'] += (dy / dist) * accel

        ai['vel']['x'] *= friction
        ai['vel']['y'] *= friction
        ai['pos']['x'] += ai['vel']['x']
        ai['pos']['y'] += ai['vel']['y']

        if ai['pos']['x'] < ai['size'] or ai['pos']['x'] > self.canvas_width - ai['size']:
            ai['vel']['x'] *= -0.8
            ai['pos']['x'] = max(ai['size'], min(ai['pos']['x'], self.canvas_width - ai['size']))
        if ai['pos']['y'] < ai['size'] or ai['pos']['y'] > self.canvas_height - ai['size']:
            ai['vel']['y'] *= -0.8
            ai['pos']['y'] = max(ai['size'], min(ai['pos']['y'], self.canvas_height - ai['size']))

        self.canvas.moveto(ai['id'], ai['pos']['x'] - ai['size'], ai['pos']['y'] - ai['size'])

    def handle_entity_bounce(self, entity_pos, entity_vel, entity_size, obs_id):
        coords = self.canvas.coords(obs_id)
        obs_radius = (coords[2] - coords[0]) / 2
        obs_center = {'x': coords[0] + obs_radius, 'y': coords[1] + obs_radius}
        restitution = SURVIVAL_RESTITUTION if self.game_mode == 'survival' else RACE_RESTITUTION
        
        nx, ny = entity_pos['x'] - obs_center['x'], entity_pos['y'] - obs_center['y']
        dist = math.hypot(nx, ny)
        if dist == 0: return
        nx /= dist; ny /= dist
        dot_product = entity_vel['x'] * nx + entity_vel['y'] * ny
        entity_vel['x'] -= (1 + restitution) * dot_product * nx
        entity_vel['y'] -= (1 + restitution) * dot_product * ny
        overlap = entity_size + obs_radius - dist + 1
        entity_pos['x'] += nx * overlap
        entity_pos['y'] += ny * overlap

    def check_collisions(self):
        # Target collisions
        if self.check_collision_by_coords(self.player_pos, PLAYER_SIZE, self.target_id):
            self.player_targets_hit += 1
            if self.game_mode == 'race':
                self.score += 1
                if self.score > self.highest_score: self.highest_score = self.score
                self.time_left = RACE_DURATION
                self.reset_obstacles(); self.spawn_target()
            else: # survival
                self.score += 1 # In survival, score is just targets hit
                self.time_left = SURVIVAL_DURATION # Reset timer
                self.spawn_target()
            self.update_score_display()
            return

        # --- MODIFIED: Loop through all AIs ---
        for ai in self.ais:
            # AI vs Target (Race mode only)
            if self.game_mode == 'race' and self.check_collision_by_coords(ai['pos'], ai['size'], self.target_id):
                self.score -= 1
                self.update_score_display()
                if self.score < 0: self.end_game("You Lose!"); return
                self.time_left = RACE_DURATION
                self.reset_obstacles(); self.spawn_target(); return

            # Player vs AI collision
            if self.check_collision_by_coords(self.player_pos, PLAYER_SIZE, ai['id']):
                restitution = SURVIVAL_RESTITUTION if self.game_mode == 'survival' else RACE_RESTITUTION
                dx, dy = self.player_pos['x'] - ai['pos']['x'], self.player_pos['y'] - ai['pos']['y']
                dist = math.hypot(dx, dy)
                if dist == 0: continue
                nx, ny = dx / dist, dy / dist

                p = (self.player_vel['x'] - ai['vel']['x']) * nx + (self.player_vel['y'] - ai['vel']['y']) * ny
                self.player_vel['x'] -= restitution * p * nx; self.player_vel['y'] -= restitution * p * ny
                ai['vel']['x'] += restitution * p * nx; ai['vel']['y'] += restitution * p * ny

                overlap = PLAYER_SIZE + ai['size'] - dist + 1
                self.player_pos['x'] += nx * overlap / 2; self.player_pos['y'] += ny * overlap / 2
                ai['pos']['x'] -= nx * overlap / 2; ai['pos']['y'] -= ny * overlap / 2

        # Obstacle collisions
        for obs_id in self.obstacle_ids:
            if self.check_collision_by_coords(self.player_pos, PLAYER_SIZE, obs_id):
                self.handle_entity_bounce(self.player_pos, self.player_vel, PLAYER_SIZE, obs_id)
            for ai in self.ais:
                if self.check_collision_by_coords(ai['pos'], ai['size'], obs_id):
                    self.handle_entity_bounce(ai['pos'], ai['vel'], ai['size'], obs_id)

    def check_collision_by_coords(self, pos, radius, item_id):
        if not item_id or not self.canvas.find_withtag(item_id): return False
        try:
            coords = self.canvas.coords(item_id)
            if not coords: return False
            item_radius = (coords[2] - coords[0]) / 2
            item_center = {'x': coords[0] + item_radius, 'y': coords[1] + item_radius}
            dist_sq = (pos['x'] - item_center['x'])**2 + (pos['y'] - item_center['y'])**2
            return dist_sq < (radius + item_radius)**2
        except tk.TclError: return False

    def update_score_display(self):
        if self.game_mode == 'survival':
            self.canvas.itemconfig(self.score_text_id, text=f"Targets: {self.score}")
        else:
            self.canvas.itemconfig(self.score_text_id, text=f"Score: {self.score}")

    def update_timer_display(self): self.canvas.itemconfig(self.timer_text_id, text=f"Time: {self.time_left:.2f}")

    def end_game(self, message):
        self.game_over = True
        self.unbind_movement_events()
        
        if self.game_mode == 'race':
             final_message = (
                f"{message}\n\n"
                f"Targets Hit: {self.player_targets_hit}\n"
                f"Highest Score: {self.highest_score}\n\n"
                f"(Press 'R' to select a mode)"
            )
        else: # survival
            final_message = (
                f"{message}\n\n"
                f"You collected {self.player_targets_hit} targets!\n\n"
                f"(Press 'R' to select a mode)"
            )
        
        self.game_over_text_id = self.canvas.create_text(self.canvas_width/2, self.canvas_height/2, text=final_message, font=("Helvetica", 28, "bold"), fill="white", justify="center", anchor="center")

    def game_loop(self):
        if self.game_over: return
        self.update_player()
        for ai in self.ais: self.update_ai(ai) # --- MODIFIED: Update all AIs
        self.check_collisions()
        
        self.time_left -= 16 / 1000
        if self.time_left <= 0:
            self.time_left = 0
            # --- NEW: Mode-specific end condition ---
            if self.game_mode == 'race' and self.score >= 0:
                self.end_game("You Win!") # Player survived timer in Race mode
            else:
                 self.end_game("Time's up!")
        
        self.update_timer_display()
        self.after_id = self.after(16, self.game_loop)

    def stop_game_loop(self):
        if self.after_id: self.after_cancel(self.after_id); self.after_id = None

    def go_to_main_menu(self):
        self.stop_game_loop(); self.unbind_all_events(); self.show_main_menu()
