# snake.py
#
# Author: AlitheiaDeus & Gemini
# Date: 2025-09-03
#
# A classic Snake game implementation for the Game & Program Suite.
# Version 1.3: Added visual border, grid lines, and quit instructions.

import tkinter as tk
import random

# --- Constants ---
GRID_SIZE = 25
SNAKE_SPEED = 100  # A faster, more responsive speed
BG_COLOR = "#2E2E2E"
CANVAS_BG = "#1C1C1C"
SNAKE_COLOR = "#4CAF50" # Green
FOOD_COLOR = "#F44336"  # Red
HEAD_COLOR = "#81C784"  # Lighter Green
TEXT_COLOR = "#FFFFFF"
GRID_COLOR = "#333333"  # Faint color for grid lines
BORDER_COLOR = "#555555" # Color for the canvas border

class SnakeGame(tk.Frame):
    """
    A classic Snake game where the player controls a growing snake to eat food
    while avoiding collisions with the walls and its own body.
    """
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg=BG_COLOR)
        self.show_main_menu_callback = show_main_menu_callback
        self.master = master
        
        self.running = False
        self.game_started = False
        self.direction = "Right"
        self.new_direction = "Right"
        
        self.DIRECTIONS_SEQUENCE = ["Up", "Right", "Down", "Left"]
        
        self._setup_widgets()

    def _setup_widgets(self):
        """Creates and places the UI elements for the game."""
        # --- NEW: Frame to hold score and instructions ---
        top_frame = tk.Frame(self, bg=BG_COLOR)
        top_frame.pack(pady=5)

        self.score_var = tk.StringVar(value="Score: 0")
        score_label = tk.Label(
            top_frame, 
            textvariable=self.score_var, 
            font=("Helvetica", 18, "bold"),
            bg=BG_COLOR, 
            fg=TEXT_COLOR
        )
        score_label.pack()
        
        # --- NEW: Instructions Label ---
        instructions_label = tk.Label(
            top_frame, 
            text="Use Arrow Keys or WASD to move. Press ESC to Quit.",
            font=("Helvetica", 10),
            bg=BG_COLOR,
            fg="#AAAAAA" # Dimmer text color
        )
        instructions_label.pack()

        self.canvas = tk.Canvas(
            self, 
            bg=CANVAS_BG, 
            # --- MODIFIED: Added border properties ---
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        self.canvas.pack(padx=20, pady=(0, 20), expand=True, fill="both")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.game_over_frame = tk.Frame(self.canvas, bg=CANVAS_BG)
        
    def _on_canvas_resize(self, event):
        """Adjusts game dimensions and starts the game on first run."""
        self.width_in_grid = event.width // GRID_SIZE
        self.height_in_grid = event.height // GRID_SIZE
        self.game_over_frame.place(relx=0.5, rely=0.5, anchor="center")

        if not self.game_started and self.width_in_grid > 0:
            self.game_started = True
            self.start_game()

    def _bind_keys(self):
        """Binds all control schemes to the top-level window."""
        toplevel = self.master.winfo_toplevel()
        
        toplevel.bind("<Escape>", lambda event: self.show_main_menu_callback())
        toplevel.bind("<Left>", lambda event: self._change_direction("Left"))
        toplevel.bind("<Right>", lambda event: self._change_direction("Right"))
        toplevel.bind("<Up>", lambda event: self._change_direction("Up"))
        toplevel.bind("<Down>", lambda event: self._change_direction("Down"))
        toplevel.bind("<a>", lambda event: self._change_direction("Left"))
        toplevel.bind("<d>", lambda event: self._change_direction("Right"))
        toplevel.bind("<w>", lambda event: self._change_direction("Up"))
        toplevel.bind("<s>", lambda event: self._change_direction("Down"))
        toplevel.bind("<j>", lambda event: self._turn_relative("left"))
        toplevel.bind("<k>", lambda event: self._turn_relative("right"))

    def _unbind_keys(self):
        """Unbinds all keys to prevent conflicts with other modules."""
        toplevel = self.master.winfo_toplevel()
        keys_to_unbind = [
            "<Escape>", "<Left>", "<Right>", "<Up>", "<Down>",
            "<a>", "<d>", "<w>", "<s>", "<j>", "<k>"
        ]
        for key in keys_to_unbind:
            toplevel.unbind(key)

    def _change_direction(self, new_dir):
        """Updates the snake's direction (absolute), preventing 180-degree turns."""
        if self.running:
            if new_dir == "Left" and self.direction != "Right": self.new_direction = new_dir
            elif new_dir == "Right" and self.direction != "Left": self.new_direction = new_dir
            elif new_dir == "Up" and self.direction != "Down": self.new_direction = new_dir
            elif new_dir == "Down" and self.direction != "Up": self.new_direction = new_dir

    def _turn_relative(self, turn):
        """Updates the snake's direction (relative to current heading)."""
        if self.running:
            try:
                current_index = self.DIRECTIONS_SEQUENCE.index(self.direction)
                if turn == "left": new_index = (current_index - 1 + 4) % 4
                else: new_index = (current_index + 1) % 4
                self.new_direction = self.DIRECTIONS_SEQUENCE[new_index]
            except ValueError: pass

    def start_game(self):
        """Initializes or resets the game state."""
        self.running = True
        self.game_over = False
        self.score = 0
        self.score_var.set("Score: 0")
        self.direction = "Right"
        self.new_direction = "Right"
        
        self.canvas.delete("all")
        self.game_over_frame.place_forget()
        for widget in self.game_over_frame.winfo_children(): widget.destroy()

        self._bind_keys()

        start_x = (self.width_in_grid // 2) * GRID_SIZE
        start_y = (self.height_in_grid // 2) * GRID_SIZE
        self.snake = [(start_x, start_y)]
        self.food_pos = None
        self._place_food()
        
        self.game_loop()

    def game_loop(self):
        """The main update loop for the game."""
        if not self.running: return

        self.direction = self.new_direction
        head_x, head_y = self.snake[0]

        if self.direction == "Right": head_x += GRID_SIZE
        elif self.direction == "Left": head_x -= GRID_SIZE
        elif self.direction == "Up": head_y -= GRID_SIZE
        elif self.direction == "Down": head_y += GRID_SIZE

        new_head = (head_x, head_y)
        self.snake.insert(0, new_head)

        if self._check_collisions():
            self._end_game()
            return
            
        if new_head == self.food_pos:
            self.score += 10
            self.score_var.set(f"Score: {self.score}")

            max_length = self.width_in_grid * self.height_in_grid
            if len(self.snake) >= max_length:
                self._win_game()
                return

            self._place_food()
        else:
            self.snake.pop()

        self._draw_elements()
        self.after(SNAKE_SPEED, self.game_loop)

    def _check_collisions(self):
        """Checks for wall or self-collisions."""
        head_x, head_y = self.snake[0]
        canvas_width = self.width_in_grid * GRID_SIZE
        canvas_height = self.height_in_grid * GRID_SIZE

        if not (0 <= head_x < canvas_width and 0 <= head_y < canvas_height): return True
        if len(self.snake) > 1 and self.snake[0] in self.snake[1:]: return True
        return False

    def _place_food(self):
        """Places food in a random location not occupied by the snake."""
        while True:
            x = random.randint(0, self.width_in_grid - 1) * GRID_SIZE
            y = random.randint(0, self.height_in_grid - 1) * GRID_SIZE
            self.food_pos = (x, y)
            if self.food_pos not in self.snake: break
    
    def _draw_elements(self):
        """Clears the canvas and redraws all game elements."""
        self.canvas.delete("all")
        canvas_width = self.width_in_grid * GRID_SIZE
        canvas_height = self.height_in_grid * GRID_SIZE

        # --- NEW: Draw grid lines ---
        for i in range(0, canvas_width, GRID_SIZE):
            self.canvas.create_line(i, 0, i, canvas_height, fill=GRID_COLOR)
        for i in range(0, canvas_height, GRID_SIZE):
            self.canvas.create_line(0, i, canvas_width, i, fill=GRID_COLOR)
        
        # Draw food
        fx, fy = self.food_pos
        self.canvas.create_rectangle(fx, fy, fx + GRID_SIZE, fy + GRID_SIZE, fill=FOOD_COLOR, outline="")

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = HEAD_COLOR if i == 0 else SNAKE_COLOR
            self.canvas.create_rectangle(x, y, x + GRID_SIZE, y + GRID_SIZE, fill=color, outline="")

    def _end_game(self):
        """Stops the game and displays the game over screen."""
        self.running = False
        self.game_over = True
        self._unbind_keys()
        
        self.canvas.delete("all")
        
        tk.Label(self.game_over_frame, text="Game Over", font=("Helvetica", 32, "bold"), bg=CANVAS_BG, fg=TEXT_COLOR).pack(pady=10)
        tk.Label(self.game_over_frame, text=f"Final Score: {self.score}", font=("Helvetica", 20), bg=CANVAS_BG, fg=TEXT_COLOR).pack(pady=(0, 20))
        button_frame = tk.Frame(self.game_over_frame, bg=CANVAS_BG)
        button_frame.pack(pady=10)
        button_style = {"bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A", "activeforeground": "white", "relief": "flat", "bd": 0, "font":("Helvetica", 14), "padx": 15, "pady": 8}
        tk.Button(button_frame, text="Play Again", command=self.start_game, **button_style).pack(side="left", padx=10)
        tk.Button(button_frame, text="Back to Menu", command=self.show_main_menu_callback, **button_style).pack(side="right", padx=10)
        self.game_over_frame.place(relx=0.5, rely=0.5, anchor="center")

    def _win_game(self):
        """Stops the game and displays the win screen."""
        self.running = False
        self.game_over = True
        self._unbind_keys()
        self.canvas.delete("all")
        tk.Label(self.game_over_frame, text="You Win!", font=("Helvetica", 32, "bold"), bg=CANVAS_BG, fg="#FFD700").pack(pady=10)
        tk.Label(self.game_over_frame, text=f"Max Score: {self.score}", font=("Helvetica", 20), bg=CANVAS_BG, fg=TEXT_COLOR).pack(pady=(0, 20))
        button_frame = tk.Frame(self.game_over_frame, bg=CANVAS_BG)
        button_frame.pack(pady=10)
        button_style = {"bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A", "activeforeground": "white", "relief": "flat", "bd": 0, "font":("Helvetica", 14), "padx": 15, "pady": 8}
        tk.Button(button_frame, text="Play Again", command=self.start_game, **button_style).pack(side="left", padx=10)
        tk.Button(button_frame, text="Back to Menu", command=self.show_main_menu_callback, **button_style).pack(side="right", padx=10)
        self.game_over_frame.place(relx=0.5, rely=0.5, anchor="center")

    def stop_game_loop(self):
        """
        Required method by the main controller to cleanly exit the game loop
        when the user navigates away.
        """
        self.running = False
        self._unbind_keys()