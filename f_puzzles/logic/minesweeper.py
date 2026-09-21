# minesweeper.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-09-03
#
# A classic Minesweeper puzzle with a guaranteed safe first click.
# Version 1.1: Fixed UI color and stability issues.

import tkinter as tk
from tkinter import font
import random

# --- Constants ---
ROWS, COLS, MINES = 16, 16, 40
BG_COLOR = "#2E2E2E"
BUTTON_COLOR = "#4A4A4A"
REVEALED_COLOR = "#3A3A3A"
TEXT_COLOR = "white"
FLAG_CHAR = "🚩"
MINE_CHAR = "💣"

NUMBER_COLORS = {
    1: "#007ACC", 2: "#4CAF50", 3: "#F44336", 4: "#800080",
    5: "#A52A2A", 6: "#008B8B", 7: "#000000", 8: "#808080"
}

class MinesweeperApp(tk.Frame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        
        self.bold_font = font.Font(family="Helvetica", size=12, weight="bold")
        self._setup_ui()
        self.start_game()

    def _setup_ui(self):
        # Top bar for stats and reset button
        top_bar = tk.Frame(self, bg=BG_COLOR)
        top_bar.pack(pady=10)

        self.mines_var = tk.StringVar(value=str(MINES))
        tk.Label(top_bar, textvariable=self.mines_var, font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg=TEXT_COLOR, width=5).pack(side="left", padx=20)
        
        self.reset_button = tk.Button(top_bar, text="🙂", font=("Helvetica", 18), bg=BUTTON_COLOR, fg=TEXT_COLOR, relief="raised", bd=2, command=self.start_game)
        self.reset_button.pack(side="left", padx=40)
        
        self.timer_var = tk.StringVar(value="0")
        tk.Label(top_bar, textvariable=self.timer_var, font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg=TEXT_COLOR, width=5).pack(side="right", padx=20)

        # Game grid
        self.grid_frame = tk.Frame(self, bg=BG_COLOR)
        self.grid_frame.pack(padx=20, pady=(0, 20))
        
        tk.Label(self, text="Press ESC to Quit", font=("Helvetica", 10),
                 bg=BG_COLOR, fg="#AAAAAA").pack(pady=(0, 10))

    def start_game(self):
        # Clear any old buttons before creating new ones
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        self.first_click = True
        self.game_over = False
        self.flags = 0
        self.revealed_cells = 0
        self.timer = 0
        self.timer_running = False

        self.mines_var.set(str(MINES - self.flags))
        self.timer_var.set("0")
        self.reset_button.config(text="🙂")
        
        if hasattr(self, 'timer_job'): self.after_cancel(self.timer_job)

        self._bind_keys()

        self.cells = [[{'is_mine': False, 'state': 'hidden', 'count': 0} for _ in range(COLS)] for _ in range(ROWS)]
        self.buttons = [[None for _ in range(COLS)] for _ in range(ROWS)]

        for r in range(ROWS):
            for c in range(COLS):
                # --- FIX: Use flat relief and a border to prevent grid shifting ---
                btn = tk.Button(self.grid_frame, width=2, height=1, bg=BUTTON_COLOR,
                relief="flat", bd=1, activebackground=REVEALED_COLOR,
                font=self.bold_font)
                btn.grid(row=r, column=c)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self._on_left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self._on_right_click(r, c))
                self.buttons[r][c] = btn

    def _generate_board(self, safe_r, safe_c):
        possible_mine_locs = [(r, c) for r in range(ROWS) for c in range(COLS)]
        safe_area = set()
        for r_off in range(-1, 2):
            for c_off in range(-1, 2):
                if 0 <= safe_r + r_off < ROWS and 0 <= safe_c + c_off < COLS:
                    safe_area.add((safe_r + r_off, safe_c + c_off))
        
        possible_mine_locs = [loc for loc in possible_mine_locs if loc not in safe_area]
        mine_locs = random.sample(possible_mine_locs, MINES)
        
        for r, c in mine_locs: self.cells[r][c]['is_mine'] = True

        for r in range(ROWS):
            for c in range(COLS):
                if not self.cells[r][c]['is_mine']:
                    count = 0
                    for r_off in range(-1, 2):
                        for c_off in range(-1, 2):
                            nr, nc = r + r_off, c + c_off
                            if 0 <= nr < ROWS and 0 <= nc < COLS and self.cells[nr][nc]['is_mine']:
                                count += 1
                    self.cells[r][c]['count'] = count

    def _bind_keys(self):
        """Binds keys for the game."""
        self.master.winfo_toplevel().bind("<Escape>", lambda e: self.show_main_menu_callback())

    def _unbind_keys(self):
        """Unbinds all game-specific keys."""
        self.master.winfo_toplevel().unbind("<Escape>")
    def _on_left_click(self, r, c):
        if self.game_over: return

        if self.first_click:
            self.first_click = False
            self._generate_board(r, c)
            self.timer_running = True
            self._update_timer()

        cell_data = self.cells[r][c]
        if cell_data['state'] in ['revealed', 'flagged']: return

        if cell_data['is_mine']:
            self._game_over(win=False); return
        
        self._reveal_cell(r, c)
        self._check_win()

    def _on_right_click(self, r, c):
        if self.game_over: return
        
        cell_data = self.cells[r][c]
        if cell_data['state'] == 'revealed': return

        if cell_data['state'] == 'hidden':
            cell_data['state'] = 'flagged'
            self.flags += 1
            # --- FIX: Set disabledforeground to make the flag visible ---
            self.buttons[r][c].config(text=FLAG_CHAR, state="disabled", disabledforeground="red")
        elif cell_data['state'] == 'flagged':
            cell_data['state'] = 'hidden'
            self.flags -= 1
            self.buttons[r][c].config(text="", state="normal")
        
        self.mines_var.set(str(MINES - self.flags))
        self._check_win()

    def _reveal_cell(self, r, c):
        cell_data = self.cells[r][c]
        if cell_data['state'] == 'revealed': return
        
        if cell_data['state'] == 'flagged':
            self.flags -= 1
            self.mines_var.set(str(MINES - self.flags))

        cell_data['state'] = 'revealed'
        self.revealed_cells += 1
        btn = self.buttons[r][c]
        btn.config(bg=REVEALED_COLOR, state="disabled")

        if cell_data['count'] > 0:
            # --- FIX: Use disabledforeground to show number colors ---
            btn.config(text=str(cell_data['count']), font=self.bold_font,
                       disabledforeground=NUMBER_COLORS[cell_data['count']])
        else:
            for r_off in range(-1, 2):
                for c_off in range(-1, 2):
                    nr, nc = r + r_off, c + c_off
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        self._reveal_cell(nr, nc)

    def _check_win(self):
        if self.revealed_cells == (ROWS * COLS) - MINES:
            self._game_over(win=True)

    def _game_over(self, win):
        self.game_over = True
        self.timer_running = False
        
        if win:
            self.reset_button.config(text="😎")
        else:
            self.reset_button.config(text="😵")
            for r in range(ROWS):
                for c in range(COLS):
                    if self.cells[r][c]['is_mine']:
                        # --- FIX: Use flat relief for consistency ---
                        self.buttons[r][c].config(text=MINE_CHAR, bg="red", relief="flat")

    def _update_timer(self):
        if self.timer_running:
            self.timer += 1
            self.timer_var.set(str(self.timer))
            self.timer_job = self.after(1000, self._update_timer)

    def stop_game_loop(self):
        self.timer_running = False
        if hasattr(self, 'timer_job'):
            self.after_cancel(self.timer_job)