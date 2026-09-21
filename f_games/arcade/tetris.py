# tetris.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-09-03
#
# A classic Tetris-style falling block game for the Game & Program Suite.
# Version 1.1: Fixed spawn collision bug, added keybind legend, and implemented game over screen.

import tkinter as tk
import random

# --- Constants ---
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
BG_COLOR = "#2E2E2E"
CANVAS_BG = "#1C1C1C"
GRID_COLOR = "#333333"
BORDER_COLOR = "#555555"
TEXT_COLOR = "#FFFFFF"

# Shape definitions for the 7 tetrominos
TETROMINOS = {
    'I': {'color': '#00FFFF', 'shapes': [[(0, -2), (0, -1), (0, 0), (0, 1)], [(-2, 0), (-1, 0), (0, 0), (1, 0)]]*2},
    'O': {'color': '#FFFF00', 'shapes': [[(0, 0), (0, 1), (1, 0), (1, 1)]]*4},
    'T': {'color': '#800080', 'shapes': [[(-1, 0), (0, 0), (1, 0), (0, -1)], [(0, -1), (0, 0), (0, 1), (-1, 0)], [(-1, 0), (0, 0), (1, 0), (0, 1)], [(0, -1), (0, 0), (0, 1), (1, 0)]]},
    'L': {'color': '#FFA500', 'shapes': [[(-1, 0), (0, 0), (1, 0), (1, -1)], [(0, 1), (0, 0), (0, -1), (-1, -1)], [(-1, 1), (-1, 0), (0, 0), (1, 0)], [(1, 1), (0, 1), (0, 0), (0, -1)]]},
    'J': {'color': '#0000FF', 'shapes': [[(-1, -1), (-1, 0), (0, 0), (1, 0)], [(-1, 1), (0, 1), (0, 0), (0, -1)], [(-1, 0), (0, 0), (1, 0), (1, 1)], [(1, -1), (0, -1), (0, 0), (0, 1)]]},
    'S': {'color': '#00FF00', 'shapes': [[(0, 0), (1, 0), (0, -1), (-1, -1)], [(-1, 0), (0, 0), (0, 1), (1, 1)]]*2},
    'Z': {'color': '#FF0000', 'shapes': [[(-1, 0), (0, 0), (0, 1), (1, 1)], [(1, -1), (1, 0), (0, 0), (0, 1)]]*2}
}
LINE_SCORES = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}

class TetrisGame(tk.Frame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        self.master = master
        self.running = False

        self._setup_ui()
        self._bind_keys()
        # Game is started by the first call to _on_canvas_ready

    def _setup_ui(self):
        canvas_width = BOARD_WIDTH * CELL_SIZE
        canvas_height = BOARD_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, bg=CANVAS_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.canvas.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ns")
        # --- NEW: Defer game start until canvas is drawn to prevent race conditions ---
        self.canvas.bind("<Configure>", self._on_canvas_ready)
        self.game_started = False

        side_panel = tk.Frame(self, bg=BG_COLOR, padx=10)
        side_panel.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="ns")

        font_style = ("Helvetica", 14); stat_style = {"bg": BG_COLOR, "fg": TEXT_COLOR, "font": font_style}
        tk.Label(side_panel, text="SCORE", **stat_style).pack(pady=(0, 5))
        self.score_var = tk.StringVar(value="0")
        tk.Label(side_panel, textvariable=self.score_var, font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg="white").pack(pady=(0, 20))
        tk.Label(side_panel, text="LEVEL", **stat_style).pack(pady=(0, 5))
        self.level_var = tk.StringVar(value="1")
        tk.Label(side_panel, textvariable=self.level_var, font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg="white").pack(pady=(0, 20))
        tk.Label(side_panel, text="LINES", **stat_style).pack(pady=(0, 5))
        self.lines_var = tk.StringVar(value="0")
        tk.Label(side_panel, textvariable=self.lines_var, font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg="white").pack(pady=(0, 20))
        tk.Label(side_panel, text="NEXT", **stat_style).pack(pady=(10, 5))
        self.next_piece_canvas = tk.Canvas(side_panel, width=4 * CELL_SIZE, height=4 * CELL_SIZE, bg=CANVAS_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.next_piece_canvas.pack()

        # --- NEW: Keybind Legend ---
        legend_frame = tk.Frame(side_panel, bg=BG_COLOR)
        legend_frame.pack(pady=20)
        tk.Label(legend_frame, text="Controls", font=("Helvetica", 14), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, columnspan=2, pady=5)
        controls = {"Move": "A / D / Arrows", "Rotate": "W / Up Arrow", "Soft Drop": "S / Down Arrow", "Hard Drop": "Spacebar", "Quit": "Escape"}
        for i, (action, key) in enumerate(controls.items()):
            tk.Label(legend_frame, text=action, font=("Helvetica", 10), bg=BG_COLOR, fg="#AAAAAA").grid(row=i+1, column=0, sticky="w", padx=5)
            tk.Label(legend_frame, text=key, font=("Helvetica", 10, "bold"), bg=BG_COLOR, fg="#DDDDDD").grid(row=i+1, column=1, sticky="w", padx=5)

    def _on_canvas_ready(self, event):
        if not self.game_started:
            self.game_started = True
            self.start_game()

    def _bind_keys(self):
        toplevel = self.master.winfo_toplevel()
        bindings = {
            "<Escape>": lambda e: self.show_main_menu_callback(), "<Left>": lambda e: self._move(-1),
            "<Right>": lambda e: self._move(1), "<Down>": lambda e: self._soft_drop(),
            "<Up>": lambda e: self._rotate(), "<space>": lambda e: self._hard_drop(),
            "<a>": lambda e: self._move(-1), "<d>": lambda e: self._move(1),
            "<s>": lambda e: self._soft_drop(), "<w>": lambda e: self._rotate()
        }
        for key, func in bindings.items():
            toplevel.bind(key, func)
        self.bound_keys = bindings.keys()

    def _unbind_keys(self):
        toplevel = self.master.winfo_toplevel()
        if hasattr(self, 'bound_keys'):
            for key in self.bound_keys: toplevel.unbind(key)

    def start_game(self):
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0; self.level = 1; self.lines_cleared = 0
        self.score_var.set("0"); self.level_var.set("1"); self.lines_var.set("0")
        
        # Clear any 'Game Over' widgets
        if hasattr(self, 'game_over_frame'): self.game_over_frame.destroy()

        self.piece_bag = []
        self._new_piece(); self._new_piece()
        
        self.running = True; self.game_over = False
        self._bind_keys()
        self.game_loop()

    def game_loop(self):
        if not self.running: return

        if not self._move_piece(1, 0):
            self._lock_piece()
            cleared = self._clear_lines()
            if cleared > 0: self._update_score(cleared)
            self._new_piece()
            if not self._is_valid_position(self.current_piece['shape'], self.current_pos):
                self._end_game(); return
        
        self._update_ui()
        speed = max(100, 1000 - (self.level - 1) * 70)
        self.after(speed, self.game_loop)

    def _new_piece(self):
        if not self.piece_bag:
            self.piece_bag = list(TETROMINOS.keys()); random.shuffle(self.piece_bag)
        
        piece_key = self.piece_bag.pop()
        piece_data = TETROMINOS[piece_key]
        self.current_piece = getattr(self, 'next_piece', None)
        self.next_piece = {'key': piece_key, 'shape': piece_data['shapes'][0], 'color': piece_data['color'], 'rotation': 0}
        
        if self.current_piece:
            # --- FIX: Spawn piece higher to avoid collision with its own negative offsets ---
            self.current_pos = [1, BOARD_WIDTH // 2]

    def _is_valid_position(self, shape, pos):
        row, col = pos
        for r_off, c_off in shape:
            r, c = row + r_off, col + c_off
            if not (0 <= c < BOARD_WIDTH and 0 <= r < BOARD_HEIGHT and self.board[r][c] is None):
                return False
        return True

    def _move_piece(self, r_delta, c_delta):
        new_pos = [self.current_pos[0] + r_delta, self.current_pos[1] + c_delta]
        if self._is_valid_position(self.current_piece['shape'], new_pos):
            self.current_pos = new_pos; return True
        return False

    def _lock_piece(self):
        row, col = self.current_pos
        for r_off, c_off in self.current_piece['shape']:
            r, c = row + r_off, col + c_off
            if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
                self.board[r][c] = self.current_piece['color']

    def _clear_lines(self):
        lines_to_clear = [r for r, row in enumerate(self.board) if all(row)]
        if not lines_to_clear: return 0
        for r_idx in sorted(lines_to_clear, reverse=True):
            del self.board[r_idx]; self.board.insert(0, [None for _ in range(BOARD_WIDTH)])
        return len(lines_to_clear)

    def _update_score(self, cleared_count):
        self.score += LINE_SCORES[cleared_count] * self.level
        self.lines_cleared += cleared_count
        self.level = (self.lines_cleared // 10) + 1
        self.score_var.set(str(self.score)); self.level_var.set(str(self.level)); self.lines_var.set(str(self.lines_cleared))

    def _update_ui(self):
        self.canvas.delete("all")
        for r in range(BOARD_HEIGHT): self.canvas.create_line(0, r * CELL_SIZE, BOARD_WIDTH * CELL_SIZE, r * CELL_SIZE, fill=GRID_COLOR)
        for c in range(BOARD_WIDTH): self.canvas.create_line(c * CELL_SIZE, 0, c * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE, fill=GRID_COLOR)
        for r, row in enumerate(self.board):
            for c, color in enumerate(row):
                if color: self._draw_cell(self.canvas, r, c, color)
        if self.current_piece and not self.game_over:
            row, col = self.current_pos
            for r_off, c_off in self.current_piece['shape']: self._draw_cell(self.canvas, row + r_off, col + c_off, self.current_piece['color'])
        self.next_piece_canvas.delete("all")
        if self.next_piece:
            for r_off, c_off in self.next_piece['shape']: self._draw_cell(self.next_piece_canvas, r_off + 2, c_off + 2, self.next_piece['color'])

    def _draw_cell(self, canvas, r, c, color):
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=CANVAS_BG, width=1)

    def _move(self, direction):
        if self.running and not self.game_over: self._move_piece(0, direction); self._update_ui()
    
    def _soft_drop(self):
        if self.running and not self.game_over: self._move_piece(1, 0); self.score += 1; self.score_var.set(str(self.score)); self._update_ui()

    def _hard_drop(self):
        if self.running and not self.game_over:
            rows_dropped = 0
            while self._move_piece(1, 0): rows_dropped += 1
            self.score += rows_dropped * 2; self.score_var.set(str(self.score))
            self.game_loop()

    def _rotate(self):
        if self.running and not self.game_over:
            rot = (self.current_piece['rotation'] + 1) % 4
            new_shape = TETROMINOS[self.current_piece['key']]['shapes'][rot]
            for c_offset in [0, -1, 1, -2, 2]:
                test_pos = [self.current_pos[0], self.current_pos[1] + c_offset]
                if self._is_valid_position(new_shape, test_pos):
                    self.current_piece['shape'] = new_shape; self.current_piece['rotation'] = rot
                    self.current_pos = test_pos; self._update_ui(); return

    def _end_game(self):
        self.running = False; self.game_over = True; self._unbind_keys()
        
        # --- NEW: Interactive Game Over Screen ---
        self.game_over_frame = tk.Frame(self.canvas, bg="black")
        tk.Label(self.game_over_frame, text="Game Over", font=("Helvetica", 32, "bold"), bg="black", fg="red").pack(pady=20)
        button_frame = tk.Frame(self.game_over_frame, bg="black")
        button_frame.pack(pady=20, padx=20, fill="x")
        button_style = {"bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A", "activeforeground": "white", "relief": "flat", "bd": 0, "font":("Helvetica", 14), "padx": 15, "pady": 8}
        tk.Button(button_frame, text="Play Again", command=self.start_game, **button_style).pack(side="left", expand=True, padx=5)
        tk.Button(button_frame, text="Back to Menu", command=self.show_main_menu_callback, **button_style).pack(side="right", expand=True, padx=5)
        self.game_over_frame.place(relx=0.5, rely=0.5, anchor="center")

    def stop_game_loop(self):
        self.running = False; self._unbind_keys()