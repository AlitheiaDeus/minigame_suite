# f_games/memory/classic_radial.py

import tkinter as tk
from tkinter import font
import random
import math

# --- Constants and Styling ---
BG_COLOR = "#2E2E2E"
TEXT_COLOR = "#FFFFFF"
BUTTON_BG = "#4A4A4A"
BUTTON_ACTIVE_BG = "#6A6A6A"
SUCCESS_COLOR = "#4CAF50"
FAILURE_COLOR = "#F44336"

COLORS = {
    "red": {"normal": "#D32F2F", "lit": "#FF5252"},
    "green": {"normal": "#388E3C", "lit": "#69F0AE"},
    "blue": {"normal": "#1976D2", "lit": "#448AFF"},
    "yellow": {"normal": "#FBC02D", "lit": "#FFFF8D"},
}
COLOR_ORDER = ["red", "green", "blue", "yellow"]

class ClassicRadialGame(tk.Frame):
    """
    A classic 'Simon-like' game with four colored radial buttons.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        self._after_ids = []
        self._skippable_task = {}

        self.level = 1
        self.sequence = []
        self.player_step = 0
        self.game_state = "idle"

        # --- Fonts and Styles ---
        self.button_style = {
            "bg": BUTTON_BG, "fg": TEXT_COLOR, "activebackground": BUTTON_ACTIVE_BG,
            "activeforeground": TEXT_COLOR, "relief": "flat", "pady": 10
        }
        self.info_font = font.Font(family="Helvetica", size=18)
        self.segments = {}

        # --- UI Layout ---
        self.header = tk.Frame(self, bg=BG_COLOR)
        self.header.pack(pady=(20,10), fill='x')
        tk.Button(self.header, text="← Back", command=self.show_main_menu_callback, **self.button_style).pack(side='left', padx=20)
        self.level_label = tk.Label(self.header, text="Level: 1", font=self.info_font, bg=BG_COLOR, fg=TEXT_COLOR)
        self.level_label.pack(side='right', padx=20)

        self.info_label = tk.Label(self, text="Right-click to start", font=self.info_font, bg=BG_COLOR, fg=TEXT_COLOR)
        self.info_label.pack(pady=10)

        self.canvas = tk.Canvas(self, width=400, height=400, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=20, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.start_button = tk.Button(self, text="Start", command=self.start_game, font=self.info_font, **self.button_style)
        self.start_button.pack(pady=20)
        
        self.bind("<Button-3>", self.on_right_click)
        self.info_label.bind("<Button-3>", self.on_right_click)
        self.header.bind("<Button-3>", self.on_right_click)
        
        self.draw_board()

    def on_right_click(self, event=None):
        if self.game_state == 'idle': self.start_game()
        elif self.game_state in ['showing', 'interlevel']: self.skip_task()

    def draw_board(self):
        self.canvas.delete("all")
        size = 400
        pad = 10
        
        coords = (pad, pad, size - pad, size - pad)
        self.segments[COLOR_ORDER[0]] = self.canvas.create_arc(coords, start=0, extent=90, fill=COLORS["red"]["normal"], outline=BG_COLOR, width=5)
        self.segments[COLOR_ORDER[1]] = self.canvas.create_arc(coords, start=90, extent=90, fill=COLORS["green"]["normal"], outline=BG_COLOR, width=5)
        self.segments[COLOR_ORDER[2]] = self.canvas.create_arc(coords, start=180, extent=90, fill=COLORS["blue"]["normal"], outline=BG_COLOR, width=5)
        self.segments[COLOR_ORDER[3]] = self.canvas.create_arc(coords, start=270, extent=90, fill=COLORS["yellow"]["normal"], outline=BG_COLOR, width=5)

    def start_game(self):
        self.level = 1
        self.sequence = []
        self.start_button.pack_forget()
        self.level_label.config(text=f"Level: {self.level}")
        self.info_label.config(text="Get Ready...")
        self.game_state = "interlevel"
        self.schedule_skippable(1200, self.next_level)

    def next_level(self):
        self.level_label.config(text=f"Level: {self.level}")
        self.info_label.config(text="Memorize the sequence...", fg=TEXT_COLOR)
        self.player_step = 0
        self.sequence.append(random.choice(COLOR_ORDER))
        self.game_state = "showing"
        self.schedule_skippable(1000, self.show_sequence_step, 0)

    def show_sequence_step(self, index):
        if index < len(self.sequence):
            color = self.sequence[index]
            self.canvas.itemconfig(self.segments[color], fill=COLORS[color]["lit"])
            self.schedule(400, self.hide_sequence_step, index)
        else:
            self.prompt_for_input()

    def hide_sequence_step(self, index):
        color = self.sequence[index]
        self.canvas.itemconfig(self.segments[color], fill=COLORS[color]["normal"])
        self.schedule(150, self.show_sequence_step, index + 1)

    def prompt_for_input(self):
        self.game_state = "waiting"
        self.info_label.config(text="Your turn!")

    def on_canvas_click(self, event):
        if self.game_state != "waiting": return
        
        cx, cy = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        dx, dy = event.x - cx, event.y - cy
        
        # Ignore clicks near the center
        if math.hypot(dx, dy) < 50: return

        angle = math.degrees(math.atan2(-dy, dx))
        angle = (angle + 360) % 360
        
        if 0 <= angle < 90: clicked_color = "red"
        elif 90 <= angle < 180: clicked_color = "green"
        elif 180 <= angle < 270: clicked_color = "blue"
        else: clicked_color = "yellow"

        expected_color = self.sequence[self.player_step]
        
        # Flash the clicked color
        self.canvas.itemconfig(self.segments[clicked_color], fill=COLORS[clicked_color]["lit"])
        self.schedule(200, lambda c=clicked_color: self.canvas.itemconfig(self.segments[c], fill=COLORS[c]["normal"]))

        if clicked_color == expected_color:
            self.player_step += 1
            if self.player_step == len(self.sequence):
                self.level += 1
                self.info_label.config(text="Correct! Right-click to continue...", fg=SUCCESS_COLOR)
                self.game_state = "interlevel"
                self.schedule_skippable(1500, self.next_level)
        else:
            self.info_label.config(text=f"Game Over! Score: {self.level - 1}", fg=FAILURE_COLOR)
            self.game_state = "idle"
            self.start_button.config(text="Play Again")
            self.start_button.pack(pady=20)
    
    # --- Scheduling Methods ---
    def _clear_skippable_task(self):
        if self._skippable_task.get('id'): self.after_cancel(self._skippable_task['id'])
        self._skippable_task = {}

    def schedule(self, delay, callback, *args):
        after_id = self.after(delay, callback, *args)
        self._after_ids.append(after_id)

    def schedule_skippable(self, delay, callback, *args):
        self._clear_skippable_task()
        def task_wrapper():
            self._skippable_task = {}
            callback(*args)
        task_id = self.after(delay, task_wrapper)
        self._skippable_task = {'id': task_id, 'callback': task_wrapper}

    def skip_task(self):
        if self._skippable_task.get('id'):
            self.after_cancel(self._skippable_task['id'])
            if self._skippable_task.get('callback'): self._skippable_task['callback']()

    def stop_game_loop(self):
        self._clear_skippable_task()
        for after_id in self._after_ids: self.after_cancel(after_id)
        self._after_ids.clear()
