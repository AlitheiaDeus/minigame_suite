# f_games/memory/pattern_grid.py

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
GRID_USER_SELECT_COLOR = "#2ECC71"

class PatternGridGame(tk.Frame):
    """
    A game where the player must recall a pattern of highlighted squares on a grid.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        self._after_ids = []
        self._skippable_task = {}
        
        self.level = 1
        self.grid_size = 3
        self.num_squares = 2
        self.pattern = set()
        self.user_selection = set()
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

        self.control_frame = tk.Frame(self, bg=BG_COLOR)
        self.control_frame.pack(pady=20)
        self.start_button = tk.Button(self.control_frame, text="Start", command=self.start_game, font=self.info_font, **self.button_style)
        self.start_button.pack(side='left', padx=10)
        self.submit_button = tk.Button(self.control_frame, text="Submit", command=self.check_pattern, font=self.info_font, state='disabled', **self.button_style)
        self.submit_button.pack(side='left', padx=10)
        
        self.bind_right_click()
        self.create_grid()

    def bind_right_click(self):
        widgets = [self, self.header, self.info_label, self.grid_frame, self.control_frame]
        for widget in widgets:
            widget.bind("<Button-3>", self.on_right_click)

    def on_right_click(self, event=None):
        if self.game_state == 'idle': self.start_game()
        elif self.game_state == 'waiting': self.check_pattern()
        elif self.game_state in ['showing', 'interlevel']: self.skip_task()
        
    def create_grid(self):
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.grid_buttons.clear()
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                btn = tk.Button(self.grid_frame, bg=GRID_DEFAULT_COLOR, activebackground=GRID_HIGHLIGHT_COLOR,
                    width=6, height=3, relief='raised', bd=2, command=lambda row=r, col=c: self.on_grid_click(row, col))
                btn.grid(row=r, column=c, padx=3, pady=3)
                btn.bind("<Button-3>", self.on_right_click)
                self.grid_buttons[(r, c)] = btn
        self.disable_grid()

    def update_grid_difficulty(self):
        if self.level >= 15: self.grid_size = 6
        elif self.level >= 8: self.grid_size = 5
        elif self.level >= 4: self.grid_size = 4
        self.num_squares = min(self.level + 1, self.grid_size * self.grid_size - 1)

    def start_game(self):
        self.level = 1
        self.start_button.pack_forget()
        self.submit_button.pack_forget()
        self.level_label.config(text=f"Level: {self.level}")
        self.info_label.config(text="Get Ready...")
        self.update_grid_difficulty()
        self.create_grid()
        self.game_state = "interlevel"
        self.schedule_skippable(1200, self.next_level)

    def next_level(self):
        self.update_grid_difficulty()
        self.create_grid()
        self.disable_grid()
        self.submit_button.config(state='disabled')
        self.level_label.config(text=f"Level: {self.level}")
        self.info_label.config(text="Memorize... (Right-click to skip)", fg=TEXT_COLOR)
        
        self.pattern.clear()
        self.user_selection.clear()
        while len(self.pattern) < self.num_squares:
            self.pattern.add((random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)))

        self.game_state = "showing"
        self.show_pattern()
        duration = max(800, 2500 - (self.level * 100))
        self.schedule_skippable(duration, self.hide_pattern)

    def show_pattern(self):
        for r, c in self.pattern: self.grid_buttons[(r, c)].config(bg=GRID_HIGHLIGHT_COLOR)

    def hide_pattern(self):
        for r, c in self.pattern: self.grid_buttons[(r, c)].config(bg=GRID_DEFAULT_COLOR)
        self.prompt_for_input()

    def prompt_for_input(self):
        self.game_state = "waiting"
        self.info_label.config(text="Your turn! (Right-click to submit)")
        self.enable_grid()
        self.submit_button.config(state='normal')

    def on_grid_click(self, r, c):
        if self.game_state != "waiting": return
        coord = (r, c)
        if coord in self.user_selection:
            self.user_selection.remove(coord)
            self.grid_buttons[coord].config(bg=GRID_DEFAULT_COLOR)
        else:
            self.user_selection.add(coord)
            self.grid_buttons[coord].config(bg=GRID_USER_SELECT_COLOR)

    def check_pattern(self):
        if self.game_state != "waiting": return
        self.disable_grid()
        if self.user_selection == self.pattern:
            self.level += 1
            self.info_label.config(text="Correct! Right-click to continue...", fg=SUCCESS_COLOR)
            self.game_state = "interlevel"
            self.schedule_skippable(1500, self.next_level)
        else:
            self.game_over()
    
    def game_over(self):
        self.game_state = "idle"
        for r_c, button in self.grid_buttons.items():
            if r_c in self.pattern and r_c in self.user_selection: button.config(bg=SUCCESS_COLOR)
            elif r_c in self.pattern and r_c not in self.user_selection: button.config(bg=GRID_HIGHLIGHT_COLOR)
            elif r_c not in self.pattern and r_c in self.user_selection: button.config(bg=FAILURE_COLOR)

        self.info_label.config(text=f"Game Over! Score: {self.level - 1}", fg=FAILURE_COLOR)
        self.start_button.config(text="Play Again"); self.submit_button.config(text="Submit")
        self.start_button.pack(side='left', padx=10); self.submit_button.pack(side='left', padx=10)
        self.submit_button.config(state='disabled')
        
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
