# langtons_ant.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-09-03
#
# A simulation of Langton's Ant, a cellular automaton with complex emergent behavior.
# Version 1.1: Added Escape key binding to quit.

import tkinter as tk
from tkinter import font

# --- Constants ---
CELL_SIZE = 10
WHITE_COLOR = "#1C1C1C" # Using canvas background as 'white'
BLACK_COLOR = "#FFFFFF"
ANT_COLOR = "#F44336" # Red
BG_COLOR = "#2E2E2E"

class LangtonsAntApp(tk.Frame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        
        self._setup_ui()
        self.reset_simulation()
        self._bind_keys() # --- MODIFIED: Bind keys on startup ---

    def _setup_ui(self):
        self.canvas = tk.Canvas(self, bg=WHITE_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        control_frame = tk.Frame(self, bg=BG_COLOR)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        control_frame.columnconfigure([0, 1, 2, 3, 4], weight=1)

        btn_style = {"bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A", 
                     "activeforeground": "white", "relief": "flat", "bd": 0, 
                     "font":("Helvetica", 12), "pady": 5}

        self.run_button = tk.Button(control_frame, text="▶ Play", command=self.toggle_run, **btn_style)
        self.run_button.grid(row=0, column=0, padx=5, sticky="ew")
        step_button = tk.Button(control_frame, text="Step", command=self.do_step, **btn_style)
        step_button.grid(row=0, column=1, padx=5, sticky="ew")
        reset_button = tk.Button(control_frame, text="Reset", command=self.reset_simulation, **btn_style)
        reset_button.grid(row=0, column=2, padx=5, sticky="ew")
        self.step_var = tk.StringVar(value="Step: 0")
        step_label = tk.Label(control_frame, textvariable=self.step_var, bg=BG_COLOR, fg="white", font=("Helvetica", 12))
        step_label.grid(row=0, column=3, padx=10)
        
        speed_frame = tk.Frame(control_frame, bg=BG_COLOR)
        speed_frame.grid(row=0, column=4, sticky="e")
        tk.Label(speed_frame, text="Speed:", bg=BG_COLOR, fg="white", font=("Helvetica", 12)).pack(side="left")
        self.speed_scale = tk.Scale(speed_frame, from_=1, to=200, orient="horizontal", bg=BG_COLOR, fg="white", troughcolor="#4A4A4A", highlightthickness=0)
        self.speed_scale.set(190)
        self.speed_scale.pack(side="left")

        # --- NEW: Add Quit Hint ---
        quit_label = tk.Label(control_frame, text="Press ESC to Quit", font=("Helvetica", 10), bg=BG_COLOR, fg="#AAAAAA")
        quit_label.grid(row=1, column=0, columnspan=5, pady=(5, 0))

    # --- NEW: Key binding methods ---
    def _bind_keys(self):
        """Binds keys for the simulation."""
        self.master.winfo_toplevel().bind("<Escape>", lambda e: self.show_main_menu_callback())

    def _unbind_keys(self):
        """Unbinds all simulation-specific keys."""
        self.master.winfo_toplevel().unbind("<Escape>")

    def reset_simulation(self):
        if hasattr(self, 'run_job'): self.after_cancel(self.run_job)
        self.running = False
        self.run_button.config(text="▶ Play")
        self.grid_cells = {}
        self.steps = 0
        self.step_var.set("Step: 0")

        canvas_width = self.winfo_width() if self.winfo_width() > 1 else 800
        canvas_height = self.winfo_height() if self.winfo_height() > 1 else 600
        center_r = canvas_height // (2 * CELL_SIZE)
        center_c = canvas_width // (2 * CELL_SIZE)

        self.ant = {'r': center_r, 'c': center_c, 'dir': 0}
        self.view_center_r, self.view_center_c = self.ant['r'], self.ant['c']
        self._redraw_canvas()

    def toggle_run(self):
        self.running = not self.running
        if self.running:
            self.run_button.config(text="❚❚ Pause")
            self._run_loop()
        else:
            self.run_button.config(text="▶ Play")

    def do_step(self):
        if not self.running:
            self._step()
            self._redraw_canvas()

    def _run_loop(self):
        if not self.running: return
        self._step()
        self._redraw_canvas()
        speed_ms = 201 - self.speed_scale.get()
        self.run_job = self.after(speed_ms, self._run_loop)

    def _step(self):
        r, c = self.ant['r'], self.ant['c']
        cell_color = self.grid_cells.get((r, c), 0)
        if cell_color == 0:
            self.ant['dir'] = (self.ant['dir'] + 1) % 4
            self.grid_cells[(r, c)] = 1
        else:
            self.ant['dir'] = (self.ant['dir'] - 1 + 4) % 4
            del self.grid_cells[(r, c)]
        
        direction = self.ant['dir']
        if direction == 0: self.ant['r'] -= 1
        elif direction == 1: self.ant['c'] += 1
        elif direction == 2: self.ant['r'] += 1
        elif direction == 3: self.ant['c'] -= 1

        self.view_center_r, self.view_center_c = self.ant['r'], self.ant['c']
        self.steps += 1
        self.step_var.set(f"Step: {self.steps}")

    def _redraw_canvas(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        for (r, c), color_val in self.grid_cells.items():
            x = (c - self.view_center_c) * CELL_SIZE + canvas_width / 2
            y = (r - self.view_center_r) * CELL_SIZE + canvas_height / 2
            if 0 <= x < canvas_width and 0 <= y < canvas_height:
                self.canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=BLACK_COLOR, outline=BLACK_COLOR)
        
        ant_x, ant_y = canvas_width / 2, canvas_height / 2
        self.canvas.create_rectangle(ant_x, ant_y, ant_x + CELL_SIZE, ant_y + CELL_SIZE, fill=ANT_COLOR, outline=ANT_COLOR)
        
    def stop_game_loop(self):
        self.running = False
        if hasattr(self, 'run_job'):
            self.after_cancel(self.run_job)
        self._unbind_keys() # --- MODIFIED: Unbind keys on exit ---