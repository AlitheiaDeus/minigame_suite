# f_games/memory/sequential_grid.py

import tkinter as tk
from tkinter import font
import random

# --- Constants and Styling ---
BG_COLOR = "#2E2E2E"
TEXT_COLOR = "#FFFFFF"
BUTTON_BG = "#4A4A4A"
BUTTON_ACTIVE_BG = "#6A6A6A"
SUCCESS_COLOR = "#4CAF50"
FAILURE_COLOR = "#F44336"
GRID_DEFAULT_COLOR = "#404040"
GRID_HIGHLIGHT_COLOR = "#3498DB"

class SequentialGridGame(tk.Frame):
    """
    A game where the player must repeat a sequence of highlighted squares on a fixed grid.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        self._after_ids = []
        self._skippable_task = {}
        
        self.level = 1
        self.grid_size = 5
        self.sequence = []
        self.player_step = 0
        self.game_state = "idle"

        # --- Fonts and Styles ---
        self.button_style = {
            "bg": BUTTON_BG, "fg": TEXT_COLOR, "activebackground": BUTTON_ACTIVE_BG,
            "activeforeground": TEXT_COLOR, "relief": "flat", "pady": 10
        }
        self.info_font = font.Font(family="Helvetica", size=18)
        self.grid_buttons = {}

        # --- UI Layout ---
        self.header = tk.Frame(self, bg=BG_COLOR)
        self.header.pack(pady=(20,10), fill='x')
        tk.Button(self.header, text="← Back", command=self.show_main_menu_callback, **self.button_style).pack(side='left', padx=20)
        self.level_label = tk.Label(self.header, text="Level: 1", font=self.info_font, bg=BG_COLOR, fg=TEXT_COLOR)
        self.level_label.pack(side='right', padx=20)

        self.info_label = tk.Label(self, text="Right-click to start", font=self.info_font, bg=BG_COLOR, fg=TEXT_COLOR)
        self.info_label.pack(pady=10)

        self.grid_frame = tk.Frame(self, bg=BG_COLOR)
        self.grid_frame.pack(pady=20, expand=True)

        self.start_button = tk.Button(self, text="Start", command=self.start_game, font=self.info_font, **self.button_style)
        self.start_button.pack(pady=20)
        
        self.bind_right_click()
        self.create_grid()

    def bind_right_click(self):
        widgets = [self, self.header, self.info_label, self.grid_frame]
        for widget in widgets:
            widget.bind("<Button-3>", self.on_right_click)

    def on_right_click(self, event=None):
        if self.game_state == 'idle': self.start_game()
        elif self.game_state in ['showing', 'interlevel']: self.skip_task()
        
    def create_grid(self):
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.grid_buttons.clear()
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                btn = tk.Button(self.grid_frame, bg=GRID_DEFAULT_COLOR, activebackground=GRID_HIGHLIGHT_COLOR,
                    width=4, height=2, relief='raised', bd=2, command=lambda row=r, col=c: self.on_grid_click(row, col))
                btn.grid(row=r, column=c, padx=3, pady=3)
                btn.bind("<Button-3>", self.on_right_click)
                self.grid_buttons[(r, c)] = btn
        self.disable_grid()

    def start_game(self):
        self.level = 1
        self.start_button.pack_forget()
        self.level_label.config(text=f"Level: {self.level}")
        self.info_label.config(text="Get Ready...")
        self.game_state = "interlevel"
        self.schedule_skippable(1200, self.next_level)

    def next_level(self):
        self.level_label.config(text=f"Level: {self.level}")
        self.info_label.config(text="Memorize the sequence...", fg=TEXT_COLOR)
        self.disable_grid()
        self.player_step = 0
        
        all_coords = list(self.grid_buttons.keys())
        self.sequence.append(random.choice(all_coords))

        self.game_state = "showing"
        self.schedule_skippable(1000, self.show_sequence_step, 0)

    def show_sequence_step(self, index):
        if index < len(self.sequence):
            r, c = self.sequence[index]
            self.grid_buttons[(r, c)].config(bg=GRID_HIGHLIGHT_COLOR)
            self.schedule(400, self.hide_sequence_step, index)
        else:
            self.prompt_for_input()

    def hide_sequence_step(self, index):
        r, c = self.sequence[index]
        self.grid_buttons[(r, c)].config(bg=GRID_DEFAULT_COLOR)
        self.schedule(150, self.show_sequence_step, index + 1)

    def prompt_for_input(self):
        self.game_state = "waiting"
        self.info_label.config(text="Your turn! Repeat the sequence.")
        self.enable_grid()

    def on_grid_click(self, r, c):
        if self.game_state != "waiting": return
        
        clicked, expected = (r, c), self.sequence[self.player_step]
        button = self.grid_buttons[clicked]

        if clicked == expected:
            self.player_step += 1
            button.config(bg=SUCCESS_COLOR)
            self.schedule(200, lambda b=button: b.config(bg=GRID_DEFAULT_COLOR))
            if self.player_step == len(self.sequence):
                self.level += 1
                self.info_label.config(text="Correct! Right-click to continue...", fg=SUCCESS_COLOR)
                self.game_state = "interlevel"
                self.disable_grid()
                self.schedule_skippable(1500, self.next_level)
        else:
            button.config(bg=FAILURE_COLOR)
            self.game_over()
    
    def game_over(self):
        self.game_state = "idle"
        self.disable_grid()
        self.sequence.clear()
        self.info_label.config(text=f"Game Over! Score: {self.level - 1}", fg=FAILURE_COLOR)
        self.start_button.config(text="Play Again")
        self.start_button.pack(pady=20)
        
    def enable_grid(self):
        for button in self.grid_buttons.values(): button.config(state='normal')

    def disable_grid(self):
        for button in self.grid_buttons.values(): button.config(state='disabled')
    
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
