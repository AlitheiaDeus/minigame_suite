# conways_game_of_life.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-09-03
#
# A simulation of Conway's Game of Life, a zero-player cellular automaton.

import tkinter as tk
from tkinter import font

# --- Constants ---
GRID_WIDTH, GRID_HEIGHT = 80, 60
CELL_SIZE = 10
LIVE_COLOR = "#FFFFFF"
DEAD_COLOR = "#1C1C1C"
GRID_COLOR = "#333333"
BG_COLOR = "#2E2E2E"

# --- Classic Patterns ---
PATTERNS = {
    "Glider": {(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)},
    "Blinker": {(0, 0), (0, 1), (0, 2)},
    "Toad": {(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2)},
    "Pulsar": {
        (2,4),(2,5),(2,6),(2,10),(2,11),(2,12),
        (4,2),(4,7),(4,9),(4,14), (5,2),(5,7),(5,9),(5,14),
        (6,2),(6,7),(6,9),(6,14), (7,4),(7,5),(7,6),(7,10),(7,11),(7,12),
        (9,4),(9,5),(9,6),(9,10),(9,11),(9,12),
        (10,2),(10,7),(10,9),(10,14), (11,2),(11,7),(11,9),(11,14),
        (12,2),(12,7),(12,9),(12,14), (14,4),(14,5),(14,6),(14,10),(14,11),(14,12)
    }
}

class ConwaysGameOfLifeApp(tk.Frame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        
        self._setup_ui()
        self.reset_simulation()
        self._bind_events()

    def _setup_ui(self):
        canvas_width = GRID_WIDTH * CELL_SIZE
        canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, bg=DEAD_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        control_frame = tk.Frame(self, bg=BG_COLOR)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_style = {"bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A", "activeforeground": "white", "relief": "flat", "bd": 0, "font":("Helvetica", 12), "pady": 5}

        self.run_button = tk.Button(control_frame, text="▶ Play", command=self.toggle_run, **btn_style)
        self.run_button.pack(side="left", padx=5)
        tk.Button(control_frame, text="Step", command=self.do_step, **btn_style).pack(side="left", padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_simulation, **btn_style).pack(side="left", padx=5)
        
        # Pattern selector
        tk.Label(control_frame, text="Patterns:", bg=BG_COLOR, fg="white", font=("Helvetica", 12)).pack(side="left", padx=(20, 5))
        self.pattern_var = tk.StringVar(self)
        self.pattern_var.set(list(PATTERNS.keys())[0]) # Default value
        pattern_menu = tk.OptionMenu(control_frame, self.pattern_var, *PATTERNS.keys())
        pattern_menu.config(bg="#4A4A4A", fg="white", activebackground="#6A6A6A", relief="flat", highlightthickness=0)
        pattern_menu["menu"].config(bg="#4A4A4A", fg="white")
        pattern_menu.pack(side="left", padx=5)
        tk.Button(control_frame, text="Place", command=self.enable_placing, **btn_style).pack(side="left", padx=5)

        self.gen_var = tk.StringVar(value="Generation: 0")
        tk.Label(control_frame, textvariable=self.gen_var, bg=BG_COLOR, fg="white", font=("Helvetica", 12)).pack(side="right", padx=10)

        self.speed_scale = tk.Scale(control_frame, from_=1, to=200, orient="horizontal", bg=BG_COLOR, fg="white", troughcolor="#4A4A4A", highlightthickness=0)
        self.speed_scale.set(150)
        self.speed_scale.pack(side="right", padx=10)
        tk.Label(control_frame, text="Speed:", bg=BG_COLOR, fg="white", font=("Helvetica", 12)).pack(side="right")
        tk.Label(self, text="Click or Drag to draw cells. Press ESC to Quit.", font=("Helvetica", 10), bg=BG_COLOR, fg="#AAAAAA").pack()

    def _bind_events(self):
        self.master.winfo_toplevel().bind("<Escape>", lambda e: self.show_main_menu_callback())
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_click)

    def _unbind_events(self):
        self.master.winfo_toplevel().unbind("<Escape>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")

    def reset_simulation(self):
        self.running = False
        self.run_button.config(text="▶ Play")
        if hasattr(self, 'run_job'): self.after_cancel(self.run_job)
        
        self.live_cells = set()
        self.generations = 0
        self.placing_pattern = False
        self.gen_var.set("Generation: 0")
        self._redraw_canvas()

    def toggle_run(self):
        self.running = not self.running
        self.placing_pattern = False
        if self.running:
            self.run_button.config(text="❚❚ Pause")
            self._run_loop()
        else:
            self.run_button.config(text="▶ Play")

    def do_step(self):
        if not self.running:
            self.placing_pattern = False
            self._step()
            self._redraw_canvas()

    def _run_loop(self):
        if not self.running: return
        self._step()
        self._redraw_canvas()
        speed_ms = 201 - self.speed_scale.get()
        self.run_job = self.after(speed_ms, self._run_loop)

    def _step(self):
        next_gen_cells = set()
        # Consider all live cells and their neighbors as candidates for the next generation
        cells_to_check = self.live_cells.union(*[self._get_neighbors(r, c) for r, c in self.live_cells])
        
        for r, c in cells_to_check:
            live_neighbors = sum(1 for neighbor in self._get_neighbors(r, c) if neighbor in self.live_cells)
            is_alive = (r, c) in self.live_cells
            
            if is_alive and live_neighbors in [2, 3]:
                next_gen_cells.add((r, c))
            elif not is_alive and live_neighbors == 3:
                next_gen_cells.add((r, c))
        
        self.live_cells = next_gen_cells
        self.generations += 1
        self.gen_var.set(f"Generation: {self.generations}")

    def _get_neighbors(self, r, c):
        """Gets all 8 neighbors of a cell, with grid wrapping (toroid)."""
        for r_off in range(-1, 2):
            for c_off in range(-1, 2):
                if r_off == 0 and c_off == 0: continue
                # Modulo operator handles the wrapping
                yield ((r + r_off) % GRID_HEIGHT, (c + c_off) % GRID_WIDTH)

    def _on_canvas_click(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if not (0 <= c < GRID_WIDTH and 0 <= r < GRID_HEIGHT): return

        if self.placing_pattern:
            pattern_name = self.pattern_var.get()
            pattern = PATTERNS[pattern_name]
            for r_off, c_off in pattern:
                cell = ((r + r_off) % GRID_HEIGHT, (c + c_off) % GRID_WIDTH)
                self.live_cells.add(cell)
            self.placing_pattern = False
        else:
            cell = (r, c)
            if cell in self.live_cells:
                self.live_cells.remove(cell)
            else:
                self.live_cells.add(cell)
        
        self._redraw_canvas()
    
    def enable_placing(self):
        self.placing_pattern = True
        self.running = False
        self.run_button.config(text="▶ Play")

    def _redraw_canvas(self):
        self.canvas.delete("all")
        # Draw grid lines for better visibility when paused
        if not self.running:
            for i in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
                self.canvas.create_line(i, 0, i, GRID_HEIGHT * CELL_SIZE, fill=GRID_COLOR)
            for i in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
                self.canvas.create_line(0, i, GRID_WIDTH * CELL_SIZE, i, fill=GRID_COLOR)

        for r, c in self.live_cells:
            x, y = c * CELL_SIZE, r * CELL_SIZE
            self.canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=LIVE_COLOR, outline=LIVE_COLOR)

    def stop_game_loop(self):
        self.running = False
        if hasattr(self, 'run_job'):
            self.after_cancel(self.run_job)
        self._unbind_events()