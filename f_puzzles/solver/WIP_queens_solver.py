# puzzles/queens_solver.py

import tkinter as tk
from tkinter import font, messagebox
import random
from collections import deque
from itertools import combinations

# --- Conditional Import for Numpy ---
# This puzzle is greatly enhanced by numpy for array operations, but will
# fall back to standard lists if numpy is not available.
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False
    print("Warning: Numpy not found. N-Queens solver will use a slower list-based implementation.")


class QueensSolverApp(tk.Frame):
    """An interactive puzzle for solving the N-Queens problem with zones."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.show_start_menu()

    def stop_game_loop(self):
        """Stops the solver if it's running."""
        self.solver_running = False

    def _clear_container(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_start_menu(self):
        self._reset_game_state()
        self._clear_container()
        menu_frame = tk.Frame(self, bg="#2E2E2E")
        menu_frame.pack(expand=True)
        tk.Label(menu_frame, text="N-Queens Solver", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").pack(pady=(40, 20))
        input_frame = tk.Frame(menu_frame, bg="#2E2E2E")
        input_frame.pack(pady=20)
        tk.Label(input_frame, text="Enter board size (N):", font=("Helvetica", 14), bg="#2E2E2E", fg="white").pack(side="left", padx=(0, 10))
        self.n_entry = tk.Entry(input_frame, font=("Helvetica", 14), width=5, justify="center", bg="#3C3C3C", fg="white", insertbackground="white", relief="flat")
        self.n_entry.pack(side="left")
        self.n_entry.focus_set()
        self.n_entry.bind("<Return>", self.process_input_event)
        tk.Button(input_frame, text="Go", font=("Helvetica", 12), command=self.process_input, bg="#4A4A4A", fg="white", relief="flat").pack(side="left", padx=(10, 0))
        self.error_label = tk.Label(menu_frame, text="", font=("Helvetica", 10), bg="#2E2E2E", fg="#FF5555")
        self.error_label.pack(pady=5)
        tk.Button(menu_frame, text="Back to Menu", font=("Helvetica", 14), command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").pack(pady=40)

    def _reset_game_state(self):
        self.n = 0
        self.zones = []
        self.cell_to_zone_map = None
        self.current_zone_index = 0
        self.current_zone_cells = []
        self.solver_running = False
        self.solution_found = False
        self.board = None
        self.solver_generator = None
        # --- CHANGE: Add state for dragging ---
        self.is_dragging = False
        self.start_drag_cell = None

    def process_input_event(self, event):
        self.process_input()

    def process_input(self):
        try:
            n = int(self.n_entry.get())
            if n > 0:
                if not NUMPY_AVAILABLE and n > 8:
                    self.error_label.config(text="Without numpy, N > 8 is very slow. Proceed with caution.")
                else:
                    self.error_label.config(text="")
                self.start_game(n)
            else:
                self.error_label.config(text="Please enter a positive number.")
        except ValueError:
            self.error_label.config(text="Invalid input. Please enter an integer.")

    def start_game(self, n):
        self.n = n
        self.zones = [[] for _ in range(n)]
        if NUMPY_AVAILABLE:
            self.cell_to_zone_map = np.full((n, n), -1, dtype=int)
        else:
            self.cell_to_zone_map = [[-1 for _ in range(n)] for _ in range(n)]
        self.current_zone_index = 0
        self.current_zone_cells = []
        self.zone_colors = self._generate_colors(n)
        self.show_game_board()

    def _generate_colors(self, num_colors):
        bright_palette = ["#FF3333", "#3399FF", "#33CC33", "#FFFF33", "#FF66CC", "#66FFFF", "#FF9933", "#9966FF", "#00FF99", "#FF6666", "#33CCCC", "#CCFF33", "#CC33FF", "#FFCC33", "#3366FF"]
        if num_colors <= len(bright_palette):
            return bright_palette[:num_colors]
        else:
            return ["#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(num_colors)]

    def show_game_board(self):
        self._clear_container()
        cell_size = max(30, 600 // (self.n + 1))
        main_game_frame = tk.Frame(self, bg="#2E2E2E")
        main_game_frame.pack(expand=True, padx=10, pady=10)
        board_frame = tk.Frame(main_game_frame, bg="#1E1E1E")
        board_frame.grid(row=0, column=0, padx=(0, 20))
        self.board_cells = [[None for _ in range(self.n)] for _ in range(self.n)]
        for r in range(self.n):
            for c in range(self.n):
                canvas = tk.Canvas(board_frame, width=cell_size, height=cell_size, bg="#3C3C3C", highlightbackground="#555555", highlightthickness=1, bd=0)
                canvas.grid(row=r, column=c)
                # --- CHANGE: Add bindings for drag-and-drop ---
                canvas.bind("<Button-1>", lambda e, row=r, col=c: self.handle_mouse_down(row, col))
                canvas.bind("<B1-Motion>", lambda e, row=r, col=c: self.handle_mouse_drag(row, col))
                canvas.bind("<ButtonRelease-1>", lambda e: self.handle_mouse_up())
                canvas.bind("<Button-3>", lambda e: self.handle_right_click())
                self.board_cells[r][c] = canvas
        
        side_panel = tk.Frame(main_game_frame, bg="#2E2E2E")
        side_panel.grid(row=0, column=1, sticky="N")
        tk.Label(side_panel, text="Zones", font=("Helvetica", 14, "bold"), bg="#2E2E2E", fg="white").pack(pady=(0, 10))
        self.zone_indicators = []
        for i in range(self.n):
            indicator = tk.Frame(side_panel, width=40, height=20, bg=self.zone_colors[i], highlightbackground="white", highlightthickness=0, cursor="hand2")
            indicator.pack(pady=2)
            indicator.bind("<Button-1>", lambda e, index=i: self.set_current_zone(index))
            self.zone_indicators.append(indicator)
        self.update_zone_indicator()
        
        action_frame = tk.Frame(side_panel, bg="#2E2E2E")
        action_frame.pack(pady=20)
        self.solve_button = tk.Button(action_frame, text="Solve", command=self.solve_puzzle, bg="#4CAF50", fg="white", relief="flat", font=("Helvetica", 12, "bold"), state=tk.DISABLED)
        self.solve_button.pack(pady=5, fill='x')
        self.reset_button = tk.Button(action_frame, text="Reset Zones", command=self.reset_board, bg="#FF6B6B", fg="white", relief="flat", font=("Helvetica", 11))
        self.reset_button.pack(pady=5, fill='x')
        
        tk.Button(action_frame, text="New Size", command=self.show_start_menu, bg="#3399FF", fg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5, fill='x')
        tk.Button(action_frame, text="Back to Menu", command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat", font=("Helvetica", 11)).pack(pady=5, fill='x')

        self.new_game_button = tk.Button(action_frame, text="New Game", command=self.show_start_menu, bg="#3399FF", fg="white", relief="flat", font=("Helvetica", 11))

        self.status_label = tk.Label(side_panel, text="", font=("Helvetica", 10, "italic"), bg="#2E2E2E", fg="lightgreen")
        self.status_label.pack(pady=10)

    def reset_board(self):
        if self.solver_running: return
        self.start_game(self.n)

    def set_current_zone(self, zone_index):
        if self.solver_running: return
        if self.current_zone_cells:
            self.zones[self.current_zone_index] = list(self.current_zone_cells)
            for r, c in self.current_zone_cells: self.cell_to_zone_map[r][c] = self.current_zone_index
        
        cells_to_edit = self.zones[zone_index]
        if cells_to_edit:
            self.zones[zone_index] = []
            for r, c in cells_to_edit: self.cell_to_zone_map[r][c] = -1
        
        self.current_zone_cells = list(cells_to_edit)
        self.current_zone_index = zone_index
        self.update_zone_indicator()
        self.check_completion()

    # --- NEW: Handle mouse down to prepare for a click or drag ---
    def handle_mouse_down(self, row, col):
        if self.solver_running: return
        self.is_dragging = False
        self.start_drag_cell = (row, col)

    # --- NEW: Handle mouse drag to paint cells ---
    def handle_mouse_drag(self, row, col):
        if self.solver_running: return
        self.is_dragging = True
        self._paint_cell(row, col)

    # --- NEW: Handle mouse up to differentiate click from drag ---
    def handle_mouse_up(self):
        if self.solver_running: return
        if not self.is_dragging:
            # If it was a click, not a drag, perform the toggle
            self._toggle_cell(self.start_drag_cell[0], self.start_drag_cell[1])
        self.is_dragging = False

    # --- NEW: Logic for painting a cell during a drag ---
    def _paint_cell(self, row, col):
        if self.current_zone_index >= self.n: return
        cell_coords = (row, col)
        # Only paint if the cell is unassigned and not already in the current temp zone
        if self.cell_to_zone_map[row][col] == -1 and cell_coords not in self.current_zone_cells:
            self.current_zone_cells.append(cell_coords)
            self.board_cells[row][col].config(bg=self.zone_colors[self.current_zone_index])
            self.check_completion()

    # --- NEW: Renamed from handle_left_click, now handles single-click toggles ---
    def _toggle_cell(self, row, col):
        if self.current_zone_index >= self.n: return
        cell_coords = (row, col)
        if cell_coords in self.current_zone_cells:
            self.current_zone_cells.remove(cell_coords)
            self.board_cells[row][col].config(bg="#3C3C3C")
        elif self.cell_to_zone_map[row][col] == -1:
            self.current_zone_cells.append(cell_coords)
            self.board_cells[row][col].config(bg=self.zone_colors[self.current_zone_index])
        self.check_completion()

    def handle_right_click(self):
        if self.current_zone_index >= self.n or not self.current_zone_cells or self.solver_running: return
        
        self.zones[self.current_zone_index] = list(self.current_zone_cells)
        for r, c in self.current_zone_cells: self.cell_to_zone_map[r][c] = self.current_zone_index
        self.current_zone_cells.clear()
        
        start_search = (self.current_zone_index + 1) % self.n
        next_zone_found = False
        for i in range(self.n):
            idx = (start_search + i) % self.n
            if not self.zones[idx]:
                self.current_zone_index = idx
                next_zone_found = True
                break
        
        if not next_zone_found:
            self.current_zone_index = self.n
            
        self.update_zone_indicator()
        self.check_completion()

    def update_zone_indicator(self):
        for i, indicator in enumerate(self.zone_indicators):
            indicator.config(highlightthickness=2 if i == self.current_zone_index else 0)

    def check_completion(self):
        all_defined = all(self.zones) and not self.current_zone_cells
        self.solve_button.config(state=tk.NORMAL if all_defined else tk.DISABLED)
        self.status_label.config(text="All zones set!" if all_defined else "")
        if all_defined:
            self.current_zone_index = self.n
            self.update_zone_indicator()

    def _is_zone_contiguous(self, zone):
        if not zone or len(zone) == 1: return True
        q, visited, zone_set = deque([zone[0]]), {zone[0]}, set(zone)
        while q:
            r, c = q.popleft()
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (r + dr, c + dc)
                if neighbor in zone_set and neighbor not in visited:
                    visited.add(neighbor)
                    q.append(neighbor)
        return len(visited) == len(zone)

    def solve_puzzle(self):
        if sum(len(z) for z in self.zones) != self.n * self.n:
            messagebox.showerror("Error", f"Expected {self.n*self.n} zoned cells, but found {sum(len(z) for z in self.zones)}.")
            return
        for i, zone in enumerate(self.zones):
            if not self._is_zone_contiguous(zone):
                messagebox.showerror("Error", f"Zone {i+1} is not contiguous.")
                return

        self.solver_running = True
        self.solution_found = False
        self.solve_button.pack_forget()
        self.reset_button.pack_forget()
        
        if NUMPY_AVAILABLE:
            self.board = np.zeros((self.n, self.n), dtype=int)
        else:
            self.board = [[0 for _ in range(self.n)] for _ in range(self.n)]
            
        for r in range(self.n):
            for c in range(self.n):
                self.board_cells[r][c].delete("all")
        
        self.solver_generator = self._solver_step(0)
        self.after(10, self._run_solver_step)

    def _on_solver_finish(self):
        self.solver_running = False
        if self.solution_found:
            self.status_label.config(text="Solution Found!", fg="lightgreen")
        else:
            self.status_label.config(text="No solution found.", fg="#FF5555")
        self.reset_button.pack(pady=5)
        self.new_game_button.pack(pady=5)

    def _run_solver_step(self):
        try:
            for _ in range(self.n * 2):
                if not self.solver_running: break
                next(self.solver_generator)
            
            if self.solver_running:
                self.after(1, self._run_solver_step)
        except StopIteration:
            self._on_solver_finish()

    def _update_cell_display(self, r, c, is_queen):
        canvas = self.board_cells[r][c]
        canvas.delete("all")
        if is_queen:
            cell_size = canvas.winfo_width()
            center_x, center_y = cell_size / 2, cell_size / 2
            star_font = font.Font(family="Arial", size=int(cell_size * 0.6), weight="bold")
            canvas.create_text(center_x, center_y, text="★", fill="white", font=star_font)

    def _is_safe(self, row, col):
        # Check row and column
        for i in range(self.n):
            if self.board[row][i] == 1 or self.board[i][col] == 1:
                return False
        # Check diagonals
        for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
            if self.board[i][j] == 1: return False
        for i, j in zip(range(row, self.n, 1), range(col, -1, -1)):
            if self.board[i][j] == 1: return False
        # Check zone constraint
        zone_idx = self.cell_to_zone_map[row][col]
        for r_z, c_z in self.zones[zone_idx]:
            if self.board[r_z][c_z] == 1:
                return False
        return True

    def _solver_step(self, col):
        """A generator that solves the puzzle column by column using backtracking."""
        if col >= self.n:
            self.solution_found = True
            yield True
            return

        for i in range(self.n):
            if not self.solver_running: return
            
            yield
            if self._is_safe(i, col):
                self.board[i][col] = 1
                self._update_cell_display(i, col, True)
                
                yield
                sub_solver = self._solver_step(col + 1)
                for _ in sub_solver:
                    if self.solution_found:
                        yield True
                        return
                    yield
                
                # Backtrack
                self.board[i][col] = 0
                self._update_cell_display(i, col, False)
        yield False
