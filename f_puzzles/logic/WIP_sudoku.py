# puzzles/sudoku.py

import tkinter as tk
from tkinter import font, messagebox
import random

# Import solver logic for puzzle generation
from f_puzzles.solver.sudoku_solver import SudokuSolverApp

class SudokuGame(tk.Frame):
    """
    A playable, customizable Sudoku game.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback

        self.cells = []
        self.board = []
        self._solution_board = []
        
        # Default to a standard 9x9 grid
        self.grid_dim = 9
        self.box_w = 3
        self.box_h = 3
        
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # --- Top control frame ---
        control_frame = tk.Frame(self, bg="#2E2E2E")
        control_frame.grid(row=0, column=0, pady=10)
        
        # In a full game, you might add difficulty settings here
        tk.Label(control_frame, text="Sudoku", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").pack()

        # Board Frame will hold the Entry widgets
        self.board_frame = tk.Frame(self, bg="#555555")
        self.board_frame.grid(row=1, column=0, padx=20, pady=10)
        
        # --- Bottom button frame ---
        button_frame = tk.Frame(self, bg="#2E2E2E")
        button_frame.grid(row=2, column=0, pady=20)
        
        tk.Button(button_frame, text="New Game", command=self.start_new_game, font=("Arial", 12), bg="#3399FF", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Check", command=self.check_solution, font=("Arial", 12), bg="#4CAF50", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Back to Menu", command=self.show_main_menu_callback, font=("Arial", 12), bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(self, text="", font=("Arial", 12, "italic"), bg="#2E2E2E", fg="white")
        self.status_label.grid(row=3, column=0)

    def _build_grid_ui(self):
        # Clear previous grid if it exists
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.cells = [[None for _ in range(self.grid_dim)] for _ in range(self.grid_dim)]
        
        validate_cmd = self.register(self._validate_input)
        font_size = max(8, 30 - self.grid_dim)

        for r in range(self.grid_dim):
            for c in range(self.grid_dim):
                padx = (2, 0) if c % self.box_w == 0 else (1, 0)
                pady = (2, 0) if r % self.box_h == 0 else (1, 0)
                
                entry = tk.Entry(self.board_frame, font=("Helvetica", font_size, "bold"), justify="center",
                                 bg="#3C3C3C", fg="white", insertbackground="white", relief="flat", width=2,
                                 validate="key", validatecommand=(validate_cmd, '%P'))
                entry.grid(row=r, column=c, padx=padx, pady=pady, sticky="nsew")
                self.cells[r][c] = entry
    
    def _validate_input(self, value):
        """Ensures input is a valid symbol for the current grid size."""
        if value == "": return True
        return value in [str(i) for i in range(1, self.grid_dim + 1)]

    def start_new_game(self):
        self.status_label.config(text="Generating new puzzle...", fg="yellow")
        self.update_idletasks()

        self._build_grid_ui()
        self._generate_puzzle()
        self._populate_board()
        
        self.status_label.config(text="New puzzle loaded. Good luck!", fg="white")

    def _generate_puzzle(self):
        # 1. Create a solver instance to use its logic
        temp_solver = SudokuSolverApp(self, lambda: None)
        temp_solver.grid_dim = self.grid_dim
        temp_solver.box_w = self.box_w
        temp_solver.box_h = self.box_h
        
        # 2. Generate a full, valid board
        board = [[0 for _ in range(self.grid_dim)] for _ in range(self.grid_dim)]
        
        # A simplified generator: fill the board with a valid solution
        def solve(bo):
            find = temp_solver._find_empty(bo)
            if not find:
                return True
            else:
                r, c = find
            nums = list(range(1, self.grid_dim + 1))
            random.shuffle(nums)
            for num in nums:
                if temp_solver._is_safe(bo, num, (r, c)):
                    bo[r][c] = num
                    if solve(bo):
                        return True
                    bo[r][c] = 0
            return False
        
        solve(board)
        self._solution_board = [row[:] for row in board]
        
        # 3. "Poke holes" to create the puzzle
        self.board = [row[:] for row in self._solution_board]
        cells = [(r, c) for r in range(self.grid_dim) for c in range(self.grid_dim)]
        random.shuffle(cells)
        
        # Remove approx 55-60% of cells for a medium puzzle
        attempts = int(self.grid_dim * self.grid_dim * 0.65)
        
        while attempts > 0:
            r, c = cells.pop()
            
            if self.board[r][c] != 0:
                self.board[r][c] = 0
                attempts -=1
        
        # A more robust generator would now check for a unique solution.
        # For simplicity, we assume this heuristic method works well enough.

    def _populate_board(self):
        for r in range(self.grid_dim):
            for c in range(self.grid_dim):
                self.cells[r][c].delete(0, tk.END)
                if self.board[r][c] != 0:
                    self.cells[r][c].insert(0, str(self.board[r][c]))
                    self.cells[r][c].config(state='readonly', fg="#66b3ff")
                else:
                    self.cells[r][c].config(state='normal', fg="white")

    def check_solution(self):
        try:
            current_board = [[int(self.cells[r][c].get()) if self.cells[r][c].get() else 0 for c in range(self.grid_dim)] for r in range(self.grid_dim)]
        except ValueError:
            messagebox.showerror("Invalid Input", "Please make sure all cells contain valid numbers.")
            return

        if current_board == self._solution_board:
             messagebox.showinfo("You Won!", "Congratulations! You've solved the Sudoku.")
             self.start_new_game()
        else:
            # Check for empty cells
            if any(0 in row for row in current_board):
                 messagebox.showwarning("Not Finished", "The puzzle is not complete yet.")
            else:
                 messagebox.showerror("Incorrect", "That's not the correct solution. Keep trying!")