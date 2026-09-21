# games/maze_runner.py

import tkinter as tk
import random

class MazeRunnerGame(tk.Frame):
    """A game where the player navigates a procedurally generated maze."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.CELL_SIZE = 20
        self.MAZE_WIDTH, self.MAZE_HEIGHT = 25, 25
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self, bg="#1E1E1E", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        bottom_frame = tk.Frame(self, bg="#2E2E2E")
        bottom_frame.grid(row=1, column=0, sticky="ew")
        
        self.status_label = tk.Label(bottom_frame, text="", font=("Arial", 14), bg="#2E2E2E", fg="white")
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Button(bottom_frame, text="New Maze", command=self.start_new_game, font=("Arial", 12), bg="#4CAF50", fg="white", relief="flat").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(bottom_frame, text="Back to Menu", command=self.show_main_menu_callback, font=("Arial", 12), bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10, pady=10)
        
        self.canvas.bind("<Key>", self.on_key_press)
        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.draw_maze()

    def start_new_game(self):
        self.maze = self._generate_maze(self.MAZE_WIDTH, self.MAZE_HEIGHT)
        self.player_pos = [0, 0]
        self.exit_pos = [self.MAZE_HEIGHT - 1, self.MAZE_WIDTH - 1]
        self.game_over = False
        self.status_label.config(text="Find the red exit!")
        self.draw_maze()
        self.canvas.focus_set()

    def _generate_maze(self, width, height):
        """Generates a maze using a recursive backtracking algorithm."""
        maze = [[{'N': True, 'S': True, 'E': True, 'W': True, 'visited': False} for _ in range(width)] for _ in range(height)]
        stack = [(0, 0)]
        maze[0][0]['visited'] = True
        
        while stack:
            r, c = stack[-1]
            neighbors = []
            if r > 0 and not maze[r-1][c]['visited']: neighbors.append(('N', r-1, c))
            if r < height-1 and not maze[r+1][c]['visited']: neighbors.append(('S', r+1, c))
            if c > 0 and not maze[r][c-1]['visited']: neighbors.append(('W', r, c-1))
            if c < width-1 and not maze[r][c+1]['visited']: neighbors.append(('E', r, c+1))
            
            if neighbors:
                direction, nr, nc = random.choice(neighbors)
                if direction == 'N': maze[r][c]['N'], maze[nr][nc]['S'] = False, False
                elif direction == 'S': maze[r][c]['S'], maze[nr][nc]['N'] = False, False
                elif direction == 'W': maze[r][c]['W'], maze[nr][nc]['E'] = False, False
                elif direction == 'E': maze[r][c]['E'], maze[nr][nc]['W'] = False, False
                maze[nr][nc]['visited'] = True
                stack.append((nr, nc))
            else:
                stack.pop()
        return maze

    def draw_maze(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        cell_w = canvas_width / self.MAZE_WIDTH
        cell_h = canvas_height / self.MAZE_HEIGHT
        self.CELL_SIZE = min(cell_w, cell_h)
        
        for r in range(self.MAZE_HEIGHT):
            for c in range(self.MAZE_WIDTH):
                x1, y1 = c * self.CELL_SIZE, r * self.CELL_SIZE
                x2, y2 = x1 + self.CELL_SIZE, y1 + self.CELL_SIZE
                if self.maze[r][c]['N']: self.canvas.create_line(x1, y1, x2, y1, fill="white")
                if self.maze[r][c]['S']: self.canvas.create_line(x1, y2, x2, y2, fill="white")
                if self.maze[r][c]['W']: self.canvas.create_line(x1, y1, x1, y2, fill="white")
                if self.maze[r][c]['E']: self.canvas.create_line(x2, y1, x2, y2, fill="white")
                
        # Draw exit
        ex, ey = self.exit_pos[1] * self.CELL_SIZE, self.exit_pos[0] * self.CELL_SIZE
        self.canvas.create_rectangle(ex+2, ey+2, ex+self.CELL_SIZE-2, ey+self.CELL_SIZE-2, fill="#E74C3C", outline="")
        
        # Draw player
        px, py = self.player_pos[1] * self.CELL_SIZE, self.player_pos[0] * self.CELL_SIZE
        self.canvas.create_oval(px+4, py+4, px+self.CELL_SIZE-4, py+self.CELL_SIZE-4, fill="#27AE60", outline="")

    def on_key_press(self, event):
        if self.game_over: return
        
        r, c = self.player_pos
        key = event.keysym.lower()
        
        if key in ['w', 'up'] and not self.maze[r][c]['N']: self.player_pos[0] -= 1
        elif key in ['s', 'down'] and not self.maze[r][c]['S']: self.player_pos[0] += 1
        elif key in ['a', 'left'] and not self.maze[r][c]['W']: self.player_pos[1] -= 1
        elif key in ['d', 'right'] and not self.maze[r][c]['E']: self.player_pos[1] += 1
        
        self.draw_maze()
        
        if self.player_pos == self.exit_pos:
            self.game_over = True
            self.status_label.config(text="You escaped!")
