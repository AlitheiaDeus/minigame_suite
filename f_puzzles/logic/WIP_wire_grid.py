# puzzles/wire_grid.py

import tkinter as tk
from tkinter import font, messagebox
import random

class WireGridGame(tk.Frame):
    """
    A playable version of the 'Flow' or 'Numberlink' puzzle, renamed to Wire Grid.
    Connect the matching terminals to fill the grid.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback

        self.grid_size = 7
        self.colors = ["#FF3333", "#3399FF", "#33CC33", "#FFFF33", "#FF66CC", "#66FFFF", "#FFA500", "#9933FF", "#FF6600", "#009999", "#FF9999", "#663300"]
        
        self.path_data = {}
        self.checkpoints = {}
        self.drawing = False
        self.current_color = None
        
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        top_frame = tk.Frame(self, bg="#2E2E2E")
        top_frame.grid(row=0, column=0, pady=10)
        tk.Label(top_frame, text="Wire Grid", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").pack()
        
        self.canvas = tk.Canvas(self, bg="#1E1E1E", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.canvas.bind("<Configure>", lambda e: self._draw_board())
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        button_frame = tk.Frame(self, bg="#2E2E2E")
        button_frame.grid(row=2, column=0, pady=20)
        tk.Button(button_frame, text="New Game", command=self.start_new_game, font=("Arial", 12), bg="#3399FF", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Reset", command=self._reset_paths, font=("Arial", 12), bg="#FF6B6B", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Back to Menu", command=self.show_main_menu_callback, font=("Arial", 12), bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        
    def start_new_game(self):
        self._generate_puzzle()
        self._reset_paths()

    def _reset_paths(self):
        self.path_data = {color: [] for color in self.checkpoints}
        self._draw_board()
        
    def _generate_puzzle(self):
        """FIXED: Procedurally generates a new puzzle, guaranteeing all cells are used."""
        self.checkpoints.clear()
        unvisited_cells = set((r, c) for r in range(self.grid_size) for c in range(self.grid_size))
        
        generated_paths = {}
        color_idx = 0
        
        while unvisited_cells:
            if color_idx >= len(self.colors):
                print("Error: Not enough colors to fill the grid.")
                # As a fallback, clear and try again.
                self.start_new_game()
                return

            color = self.colors[color_idx]
            
            # Start a new path from a random unvisited cell
            start_pos = random.choice(list(unvisited_cells))
            path = [start_pos]
            unvisited_cells.remove(start_pos)
            
            # "Carve" a path through the grid
            while True:
                r, c = path[-1]
                moves = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
                random.shuffle(moves)
                
                moved = False
                for nr, nc in moves:
                    if (nr, nc) in unvisited_cells:
                        path.append((nr, nc))
                        unvisited_cells.remove((nr, nc))
                        moved = True
                        break
                if not moved:
                    break # Path is stuck
            
            # Quality Check: If a path is just a dot, don't use it.
            # Put its cell back and try the color again.
            if len(path) > 1:
                generated_paths[color] = path
                color_idx += 1
            else:
                unvisited_cells.add(path[0]) # Put the single cell back
        
        # Extract the endpoints from the fully generated paths
        for color, path in generated_paths.items():
            self.checkpoints[color] = [path[0], path[-1]]

    def _get_cell_from_event(self, event):
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if min(canvas_w, canvas_h) < self.grid_size: return None, None
        cell_size = min(canvas_w, canvas_h) / self.grid_size
        col, row = int(event.x // cell_size), int(event.y // cell_size)
        return (row, col) if 0 <= row < self.grid_size and 0 <= col < self.grid_size else (None, None)
        
    def on_mouse_down(self, event):
        r, c = self._get_cell_from_event(event)
        if r is None: return

        for color, (start_pos, end_pos) in self.checkpoints.items():
            if (r, c) == start_pos or (r, c) == end_pos:
                self.drawing = True
                self.current_color = color
                self.path_data[color] = [(r, c)]
                self._draw_board()
                break

    def on_mouse_drag(self, event):
        if not self.drawing: return
        r, c = self._get_cell_from_event(event)
        if r is None: return
        
        current_path = self.path_data[self.current_color]
        last_pos = current_path[-1]
        
        is_adjacent = (r, c) != last_pos and abs(r - last_pos[0]) + abs(c - last_pos[1]) == 1
        if not is_adjacent: return

        is_occupied = any((r, c) in path for color, path in self.path_data.items() if color != self.current_color)
        is_checkpoint = any((r, c) in points for color, points in self.checkpoints.items() if color != self.current_color)

        if not is_occupied and not is_checkpoint:
            if (r, c) in current_path: # Backtracking
                idx = current_path.index((r, c))
                self.path_data[self.current_color] = current_path[:idx+1]
            else: # Moving forward
                current_path.append((r, c))
            self._draw_board()
            
            endpoints = self.checkpoints[self.current_color]
            if (r, c) in endpoints and len(current_path) > 1 and current_path[0] != (r, c):
                self.on_mouse_up(event)

    def on_mouse_up(self, event):
        if self.drawing:
            self.drawing = False
            self.current_color = None
            self.check_win()

    def check_win(self):
        filled_cells = {cell for path in self.path_data.values() for cell in path}
        all_connected = all(
            (p[0] in self.path_data[c] and p[1] in self.path_data[c])
            for c, p in self.checkpoints.items()
        )
        if all_connected and len(filled_cells) == self.grid_size ** 2:
            self._draw_board()
            messagebox.showinfo("You Won!", "Congratulations! All circuits are connected.")
            self.start_new_game()

    def _draw_board(self):
        self.canvas.delete("all")
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if min(canvas_w, canvas_h) < self.grid_size: return
        cell_size = min(canvas_w, canvas_h) / self.grid_size
        
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * cell_size, 0, i * cell_size, self.grid_size * cell_size, fill="#3C3C3C")
            self.canvas.create_line(0, i * cell_size, self.grid_size * cell_size, i * cell_size, fill="#3C3C3C")

        for color, path in self.path_data.items():
            if len(path) > 1:
                coords = [c * cell_size + cell_size/2 for pos in path for c in reversed(pos)]
                self.canvas.create_line(coords, fill="#101010", width=cell_size*0.7, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                self.canvas.create_line(coords, fill=color, width=cell_size*0.5, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        for color, (start, end) in self.checkpoints.items():
            for r, c in [start, end]:
                x1, y1 = c * cell_size, r * cell_size
                padding = cell_size * 0.1
                self.canvas.create_oval(x1 + padding, y1 + padding, x1 + cell_size - padding, y1 + cell_size - padding, 
                                        fill=color, outline="#101010", width=4)

    def stop_game_loop(self):
        """Required by the main suite for API compliance."""
        pass