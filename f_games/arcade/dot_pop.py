# f_games/arcade/dot_pop.py

import tkinter as tk
from tkinter import messagebox
import random
import math

class DotPopGame(tk.Frame):
    """A simple game where the player clicks dots to score points."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.CANVAS_WIDTH, self.CANVAS_HEIGHT = 650, 400
        self.GAME_DURATION = 30
        self.score = 0
        self.time_left = self.GAME_DURATION
        self.game_is_running = False
        self.dots = []
        self.hovered_dot = None
        self._after_id = None
        self._setup_ui()

    def stop_game_loop(self):
        """Stops any running game loops or after() calls."""
        self.game_is_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(expand=True)
        tk.Label(main_frame, text="Click blue dots to score! Avoid the grey dots.", font=("Arial", 14), bg="#2E2E2E", fg="white").pack(pady=10)
        stats_frame = tk.Frame(main_frame, bg="#2E2E2E")
        stats_frame.pack(pady=5)
        self.score_label = tk.Label(stats_frame, text="Score: 0", font=("Arial", 16, "bold"), width=15, bg="#2E2E2E", fg="white")
        self.score_label.pack(side=tk.LEFT, padx=20)
        self.timer_label = tk.Label(stats_frame, text=f"Time: {self.time_left}", font=("Arial", 16, "bold"), width=15, bg="#2E2E2E", fg="white")
        self.timer_label.pack(side=tk.LEFT, padx=20)
        self.canvas = tk.Canvas(main_frame, bg="#3C3C3C", width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        button_frame = tk.Frame(main_frame, bg="#2E2E2E")
        button_frame.pack(pady=10)
        self.start_button = tk.Button(button_frame, text="Start Game", font=("Arial", 14, "bold"), command=self.start_game, bg="#4CAF50", fg="white", relief="flat")
        self.start_button.pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Back to Menu", font=("Arial", 14, "bold"), command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)

    def start_game(self):
        if self.game_is_running: return
        self.game_is_running = True
        self.score = 0
        self.time_left = self.GAME_DURATION
        self.score_label.config(text=f"Score: {self.score}")
        self.timer_label.config(text=f"Time: {self.time_left}")
        self.start_button.config(state=tk.DISABLED)
        self.spawn_dots()
        self.update_timer()

    def update_timer(self):
        if not self.game_is_running: return
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left}")
            self._after_id = self.after(1000, self.update_timer)
        else: self.end_game()

    def end_game(self):
        self.stop_game_loop()
        self.start_button.config(state=tk.NORMAL)
        self._clear_dots()
        messagebox.showinfo("Game Over", f"Time's up!\nYour final score is: {self.score}")

    def _clear_dots(self):
        for dot in self.dots: self.canvas.delete(dot['id'])
        self.dots.clear()
        self.hovered_dot = None

    def spawn_dots(self):
        self._clear_dots()
        self._create_one_dot(is_bad=False)
        if random.random() < 0.3 + (self.score * 0.02): self._create_one_dot(is_bad=True)

    def _create_one_dot(self, is_bad):
        radius = max(6, 20 - (self.score * 0.4))
        for _ in range(100): # Attempt to place dot 100 times
            x = random.randint(int(radius), self.CANVAS_WIDTH - int(radius))
            y = random.randint(int(radius), self.CANVAS_HEIGHT - int(radius))
            if not any(math.hypot(x - d['x'], y - d['y']) < radius + d['radius'] for d in self.dots):
                color = "#555555" if is_bad else "#3399FF"
                dot_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="black")
                self.dots.append({'id': dot_id, 'x': x, 'y': y, 'radius': radius, 'is_bad': is_bad, 'color': color})
                return
        print("Warning: Could not place a new dot without overlapping.")


    def on_mouse_motion(self, event):
        if not self.game_is_running: return
        new_hovered = None
        for dot in self.dots:
            if math.hypot(event.x - dot['x'], event.y - dot['y']) <= dot['radius']: new_hovered = dot; break
        if self.hovered_dot != new_hovered:
            if self.hovered_dot: self.canvas.itemconfig(self.hovered_dot['id'], fill=self.hovered_dot['color'])
            if new_hovered: self.canvas.itemconfig(new_hovered['id'], fill="#F5A623")
            self.hovered_dot = new_hovered

    def on_mouse_click(self, event):
        if not self.game_is_running or not self.hovered_dot: return
        self.score += -2 if self.hovered_dot['is_bad'] else 1
        self.score = max(0, self.score)
        self.score_label.config(text=f"Score: {self.score}")
        self.spawn_dots()
