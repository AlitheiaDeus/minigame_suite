# puzzles/flip.py

import tkinter as tk
from tkinter import font
from tkinter import messagebox
import random

class FlipGame(tk.Frame):
    """
    A logic puzzle, also known as 'Lights Out', where the goal is
    to turn off all the tiles on a grid.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback

        # --- Style & Game Constants ---
        self.DIFFICULTY_LEVELS = {"Easy (4x4)": 4, "Normal (5x5)": 5, "Hard (6x6)": 6}
        self.COLOR_BG = "#2E2E2E"
        self.COLOR_GRID_BG = "#1E1E1E"
        self.COLOR_OFF = "#3C3C3C"
        self.COLOR_ON = "#3399FF" # A bright blue

        # --- Game State ---
        self.board = []
        self.moves = 0
        
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        """Creates and lays out the widgets for the game."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- Top control frame ---
        control_frame = tk.Frame(self, bg=self.COLOR_BG)
        control_frame.grid(row=0, column=0, pady=10, sticky="ew")
        
        self.difficulty_var = tk.StringVar(value="Normal (5x5)")
        for text in self.DIFFICULTY_LEVELS:
            tk.Radiobutton(
                control_frame, text=text, variable=self.difficulty_var, value=text,
                command=self.start_new_game, bg=self.COLOR_BG, fg="white",
                selectcolor="#4A4A4A", activebackground=self.COLOR_BG,
                activeforeground="white", font=("Arial", 11)
            ).pack(side=tk.LEFT, padx=10)

        self.moves_label = tk.Label(control_frame, text="Moves: 0", font=("Arial", 14, "bold"), bg=self.COLOR_BG, fg="white")
        self.moves_label.pack(side=tk.RIGHT, padx=20)

        # --- Canvas for the game board ---
        self.canvas = tk.Canvas(self, bg=self.COLOR_GRID_BG, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda e: self._draw_board())

        # --- Bottom button frame ---
        button_frame = tk.Frame(self, bg=self.COLOR_BG)
        button_frame.grid(row=2, column=0, pady=10, sticky="ew")
        
        button_group = tk.Frame(button_frame, bg=self.COLOR_BG)
        button_group.pack(side=tk.LEFT, padx=10)

        tk.Button(button_group, text="Reset Puzzle", command=lambda: self._draw_board(reset_moves=True), font=("Arial", 12), bg="#FF6B6B", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_group, text="Back to Menu", command=self.show_main_menu_callback, font=("Arial", 12), bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)

        # --- NEW: Legend ---
        legend_frame = tk.Frame(button_frame, bg=self.COLOR_BG)
        legend_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(legend_frame, text="■", fg=self.COLOR_ON, bg=self.COLOR_BG, font=("Arial", 16)).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="= On", font=("Arial", 12), bg=self.COLOR_BG, fg="white").pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(legend_frame, text="■", fg=self.COLOR_OFF, bg=self.COLOR_BG, font=("Arial", 16)).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="= Off", font=("Arial", 12), bg=self.COLOR_BG, fg="white").pack(side=tk.LEFT)

    def start_new_game(self):
        """Sets up a new board and generates a new puzzle."""
        self.board_size = self.DIFFICULTY_LEVELS[self.difficulty_var.get()]
        self._generate_puzzle()
        self._draw_board(reset_moves=True)

    def _generate_puzzle(self):
        """Generates a new solvable puzzle by working backward from a solved state."""
        # Start with a solved board (all 'False' or off)
        self.board = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        # Perform a number of random flips to create a puzzle
        # The number of flips can be adjusted to change initial difficulty
        num_flips = self.board_size * self.board_size
        for _ in range(num_flips):
            rand_row = random.randint(0, self.board_size - 1)
            rand_col = random.randint(0, self.board_size - 1)
            self._flip_tiles(rand_row, rand_col)
        
        # Keep a copy of the starting state for the reset button
        self.starting_board = [row[:] for row in self.board]

    def _draw_board(self, reset_moves=False):
        """Renders the current board state on the canvas."""
        self.canvas.delete("all")

        if reset_moves:
            self.moves = 0
            self.board = [row[:] for row in self.starting_board] # Restore initial puzzle state
        
        self.moves_label.config(text=f"Moves: {self.moves}")
        
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cell_size = min(canvas_w, canvas_h) / self.board_size
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                x1, y1 = c * cell_size, r * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                
                fill_color = self.COLOR_ON if self.board[r][c] else self.COLOR_OFF
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=self.COLOR_GRID_BG, width=2)
    
    def on_canvas_click(self, event):
        """Handles the player's click, flipping tiles and checking for a win."""
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cell_size = min(canvas_w, canvas_h) / self.board_size
        
        # Determine which cell was clicked
        col = int(event.x // cell_size)
        row = int(event.y // cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            self.moves += 1
            self._flip_tiles(row, col)
            self._draw_board()

            # Check for win condition
            if not any(any(row) for row in self.board):
                messagebox.showinfo("You Won!", f"Congratulations! You solved the puzzle in {self.moves} moves.")
                self.start_new_game()

    def _flip_tiles(self, r, c):
        """
        Toggles the state of the clicked tile and its orthogonal neighbors.
        Includes boundary checks to prevent errors.
        """
        positions_to_flip = [(r, c)] # The clicked tile
        
        # Check and add neighbors
        if r > 0: positions_to_flip.append((r - 1, c)) # North
        if r < self.board_size - 1: positions_to_flip.append((r + 1, c)) # South
        if c > 0: positions_to_flip.append((r, c - 1)) # West
        if c < self.board_size - 1: positions_to_flip.append((r, c + 1)) # East
        
        for row, col in positions_to_flip:
            self.board[row][col] = not self.board[row][col]