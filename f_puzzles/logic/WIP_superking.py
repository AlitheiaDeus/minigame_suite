# puzzles/superking.py

import tkinter as tk
from tkinter import font, messagebox

class SuperkingGame(tk.Frame):
    """
    An interactive board for the N-Superking placement puzzle.
    The goal is to place N superkings on an N x N board so that none attack each other.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback

        self.n = 8 # Default size
        self.board = []
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- Top control frame ---
        control_frame = tk.Frame(self, bg="#2E2E2E")
        control_frame.grid(row=0, column=0, pady=10, sticky="ew")
        control_frame.columnconfigure(1, weight=1)

        options_frame = tk.Frame(control_frame, bg="#2E2E2E")
        options_frame.grid(row=0, column=0, padx=20)
        
        tk.Label(options_frame, text="Board Size (N):", font=("Arial", 12), bg="#2E2E2E", fg="white").pack(side=tk.LEFT)
        self.n_var = tk.IntVar(value=8)
        self.n_spinbox = tk.Spinbox(options_frame, from_=4, to=12, textvariable=self.n_var, width=5, font=("Arial", 12), justify="center",
                                     bg="#3C3C3C", fg="white", buttonbackground="#4A4A4A", relief="flat")
        self.n_spinbox.pack(side=tk.LEFT, padx=5)

        self.kings_label = tk.Label(control_frame, text="Kings Placed: 0 / 8", font=("Arial", 14, "bold"), bg="#2E2E2E", fg="white")
        self.kings_label.grid(row=0, column=2, padx=20)

        # --- Canvas for the game board ---
        self.canvas = tk.Canvas(self, bg="#1E1E1E", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda e: self._draw_board())

        # --- Bottom button frame ---
        button_frame = tk.Frame(self, bg="#2E2E2E")
        button_frame.grid(row=2, column=0, pady=10, sticky="ew")
        button_group = tk.Frame(button_frame, bg="#2E2E2E")
        button_group.pack()

        tk.Button(button_group, text="New Game", command=self.start_new_game, font=("Arial", 12), bg="#3399FF", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_group, text="Back to Menu", command=self.show_main_menu_callback, font=("Arial", 12), bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)

    def start_new_game(self):
        """Sets up a new, empty board."""
        try:
            self.n = self.n_var.get()
            if not 4 <= self.n <= 12:
                messagebox.showerror("Invalid Size", "Please choose a size between 4 and 12.")
                self.n_var.set(8)
                self.n = 8
        except tk.TclError:
            self.n_var.set(8)
            self.n = 8
            
        self.board = [[0 for _ in range(self.n)] for _ in range(self.n)]
        self._draw_board()
        self._update_king_count()

    def _draw_board(self):
        """Renders the current board state on the canvas."""
        self.canvas.delete("all")
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cell_size = min(canvas_w, canvas_h) / self.n
        
        star_font = font.Font(family="Arial", size=int(cell_size * 0.6), weight="bold")
        
        for r in range(self.n):
            for c in range(self.n):
                x1, y1 = c * cell_size, r * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                
                fill_color = "#3C3C3C" if (r + c) % 2 == 0 else "#323232"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="")
                
                if self.board[r][c] == 1: # It's a king
                    is_safe = self._is_safe(r, c, check_self=False)
                    king_color = "white" if is_safe else "#FF5555"
                    self.canvas.create_text(x1 + cell_size/2, y1 + cell_size/2, text="★", font=star_font, fill=king_color)

    def on_canvas_click(self, event):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cell_size = min(canvas_w, canvas_h) / self.n
        
        col = int(event.x // cell_size)
        row = int(event.y // cell_size)
        
        if 0 <= row < self.n and 0 <= col < self.n:
            self.board[row][col] = 1 - self.board[row][col] # Toggle
            self._draw_board()
            self._update_king_count()
            self.check_win()

    def _update_king_count(self):
        count = sum(row.count(1) for row in self.board)
        self.kings_label.config(text=f"Kings Placed: {count} / {self.n}")

    def _is_safe(self, row, col, check_self=True):
        # Temporarily remove the king at (row, col) to check its safety against others
        if check_self: self.board[row][col] = 0
        
        # Check Rook attacks
        for i in range(self.n):
            if self.board[row][i] == 1 or self.board[i][col] == 1:
                if check_self: self.board[row][col] = 1
                return False
        # Check King attacks
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.n and 0 <= nc < self.n and self.board[nr][nc] == 1:
                    if check_self: self.board[row][col] = 1
                    return False
        
        if check_self: self.board[row][col] = 1
        return True

    def check_win(self):
        king_count = sum(row.count(1) for row in self.board)
        if king_count != self.n:
            return

        all_kings_safe = True
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 1 and not self._is_safe(r, c):
                    all_kings_safe = False
                    break
            if not all_kings_safe:
                break
        
        if all_kings_safe:
            messagebox.showinfo("You Won!", f"Congratulations! You correctly placed {self.n} superkings.")
            self.start_new_game()