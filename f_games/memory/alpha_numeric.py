# f_games/memory/alpha_numeric_memory.py

import tkinter as tk
from tkinter import font
import random
import string

# --- Constants and Styling ---
BG_COLOR = "#2E2E2E"
TEXT_COLOR = "#FFFFFF"
BUTTON_BG = "#4A4A4A"
BUTTON_ACTIVE_BG = "#6A6A6A"
SUCCESS_COLOR = "#4CAF50"
FAILURE_COLOR = "#F44336"

class AlphaNumericGame(tk.Frame):
    """
    A game where the player must memorize and recall a sequence of alphanumeric characters.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        self._after_ids = []
        self._skippable_task = {}

        self.level = 1
        self.current_sequence = ""
        self.game_state = "idle"  # idle, showing, waiting, interlevel

        # --- Fonts and Styles ---
        self.button_style = {
            "bg": BUTTON_BG, "fg": TEXT_COLOR, "activebackground": BUTTON_ACTIVE_BG,
            "activeforeground": TEXT_COLOR, "relief": "flat", "pady": 10
        }
        self.info_font = font.Font(family="Helvetica", size=18)
        self.sequence_font = font.Font(family="Courier", size=80, weight="bold")
        self.entry_font = font.Font(family="Helvetica", size=24)

        # --- UI Layout ---
        self.header = tk.Frame(self, bg=BG_COLOR)
        self.header.pack(pady=(20, 10), fill='x')
        tk.Button(self.header, text="← Back", command=self.show_main_menu_callback, **self.button_style).pack(side='left', padx=20)
        self.level_label = tk.Label(self.header, text="Level: 1", font=self.info_font, bg=BG_COLOR, fg=TEXT_COLOR)
        self.level_label.pack(side='right', padx=20)

        self.display_label = tk.Label(self, text="", font=self.sequence_font, bg=BG_COLOR, fg=TEXT_COLOR, height=2)
        self.display_label.pack(pady=40, expand=True)

        self.info_label = tk.Label(self, text="Right-click or Enter to start", font=self.info_font, bg=BG_COLOR, fg=TEXT_COLOR)
        self.info_label.pack(pady=20)

        self.input_frame = tk.Frame(self, bg=BG_COLOR)
        self.input_frame.pack(pady=20)

        self.entry_var = tk.StringVar()
        self.user_entry = tk.Entry(self.input_frame, textvariable=self.entry_var, font=self.entry_font, width=20, justify='center', state='disabled')
        self.user_entry.pack(pady=10)
        self.user_entry.bind("<Return>", self.check_answer)

        self.start_button = tk.Button(self.input_frame, text="Start", command=self.start_game, font=self.info_font, **self.button_style)
        self.start_button.pack(pady=10)

        self.bind_controls()

    def bind_controls(self):
        """Binds controls for consistent interaction."""
        widgets_to_bind = [self, self.header, self.display_label, self.info_label, self.input_frame]
        for widget in widgets_to_bind:
            widget.bind("<Button-3>", self.on_right_click)
        self.bind("<Return>", self.on_enter_press)
        self.focus_set()

    def on_right_click(self, event=None):
        if self.game_state == "idle": self.start_game()
        elif self.game_state == "interlevel": self.skip_task()

    def on_enter_press(self, event=None):
        if self.game_state == "idle" and self.start_button.winfo_ismapped(): self.start_game()
        elif self.game_state == "interlevel": self.skip_task()

    def start_game(self):
        self.level = 1
        self.start_button.pack_forget()
        self.level_label.config(text=f"Level: {self.level}")
        self.info_label.config(text="Get Ready...")
        self.game_state = "interlevel"
        self.focus_set()
        self.schedule_skippable(1200, self.next_level)

    def next_level(self):
        self.game_state = "showing"
        self.entry_var.set("")
        self.user_entry.config(state='disabled')
        self.info_label.config(text="Memorize...", fg=TEXT_COLOR)
        self.current_sequence = ''.join(random.choices(string.ascii_uppercase + string.digits, k=self.level))
        self.schedule_skippable(1000, self.show_sequence_char, 0)

    def show_sequence_char(self, index):
        if index < len(self.current_sequence):
            self.display_label.config(text=self.current_sequence[index])
            self.schedule(700, self.clear_display, index)
        else:
            self.prompt_for_input()

    def clear_display(self, index):
        self.display_label.config(text="")
        self.schedule(300, self.show_sequence_char, index + 1)

    def prompt_for_input(self):
        self.game_state = "waiting"
        self.info_label.config(text="Your turn! (Press Enter to submit)")
        self.user_entry.config(state='normal')
        self.user_entry.focus_set()

    def check_answer(self, event=None):
        if self.game_state != "waiting": return
        if self.entry_var.get().upper() == self.current_sequence:
            self.level += 1
            self.level_label.config(text=f"Level: {self.level}")
            self.info_label.config(text="Correct! Press Enter to continue...", fg=SUCCESS_COLOR)
            self.game_state = "interlevel"
            self.focus_set()
            self.schedule_skippable(2000, self.next_level)
        else:
            self.game_over()

    def game_over(self):
        self.game_state = "idle"
        self.info_label.config(text=f"Game Over! Sequence was: {self.current_sequence}", fg=FAILURE_COLOR)
        self.display_label.config(text=f"Score: {self.level - 1}")
        self.user_entry.config(state='disabled')
        self.start_button.config(text="Play Again")
        self.start_button.pack(pady=10)

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
