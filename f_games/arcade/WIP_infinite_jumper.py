# games/infinite_jumper.py

import tkinter as tk
import random

class InfiniteJumperGame(tk.Frame):
    """An endless side-scrolling platform jumper game."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.WIDTH, self.HEIGHT = 800, 600
        self.FPS = 60
        self.PLAYER_SPEED = 4
        self.GRAVITY = 0.8
        self.JUMP_HEIGHT = -15
        self._after_id = None
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(expand=True)
        self.canvas = tk.Canvas(main_frame, width=self.WIDTH, height=self.HEIGHT, bg="#28283C", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<space>", self.jump)
        self.canvas.bind("<KeyPress-r>", lambda e: self.start_new_game())

    def start_new_game(self):
        self.stop_game_loop()
        self.game_over = False
        self.score = 0
        self.player_vel_y = 0
        self.on_ground = False
        self.platforms = []
        
        self.canvas.delete("all")
        self.player = self.canvas.create_rectangle(100, self.HEIGHT/2, 140, self.HEIGHT/2 + 40, fill="#FAD264", outline="")
        initial_platform = self.canvas.create_rectangle(0, self.HEIGHT-50, self.WIDTH, self.HEIGHT, fill="#8C96AA", outline="")
        self.platforms.append(initial_platform)
        
        self.score_text = self.canvas.create_text(20, 20, text="Score: 0", anchor="nw", font=("Arial", 16), fill="white")
        
        # Place back button inside canvas
        back_button = tk.Button(self, text="Back to Menu", command=self.stop_game_loop_and_exit, font=("Arial", 12), bg="#4A4A4A", fg="white", relief="flat")
        self.canvas.create_window(self.WIDTH-80, 25, window=back_button, anchor="center")

        self.canvas.focus_set()
        self.game_loop()

    def jump(self, event):
        if self.on_ground:
            self.player_vel_y = self.JUMP_HEIGHT

    def stop_game_loop(self):
        """Stops the main game loop."""
        self.game_over = True
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def stop_game_loop_and_exit(self):
        self.stop_game_loop()
        self.show_main_menu_callback()

    def _generate_next_platform(self, last_p_coords):
        lx1, ly1, lx2, ly2 = last_p_coords
        max_jump_height = abs((self.JUMP_HEIGHT ** 2) / (2 * self.GRAVITY))
        
        y_offset = random.uniform(-max_jump_height * 0.7, max_jump_height * 0.3)
        new_y = max(150, min(self.HEIGHT - 150, ly1 + y_offset))
        
        x_gap = random.uniform(80, 250)
        new_x = lx2 + x_gap
        new_width = random.randint(80, 150)
        
        return (new_x, new_y, new_x + new_width, new_y + 20)

    def game_loop(self):
        if self.game_over:
            self.canvas.create_text(self.WIDTH/2, self.HEIGHT/2, text="Game Over! Press 'R' to restart", font=("Helvetica", 24, "bold"), fill="white")
            return

        # Update player position
        self.player_vel_y += self.GRAVITY
        self.canvas.move(self.player, 0, self.player_vel_y)
        
        try:
            px1, py1, px2, py2 = self.canvas.coords(self.player)
        except (ValueError, tk.TclError): # Handle case where player is deleted
            return

        # Check for collisions with platforms
        self.on_ground = False
        for p in self.platforms:
            self.canvas.move(p, -self.PLAYER_SPEED, 0)
            try:
                x1, y1, x2, y2 = self.canvas.coords(p)
                if px2 > x1 and px1 < x2 and py2 > y1 and py1 < y1 + 10 and self.player_vel_y > 0:
                    self.canvas.coords(self.player, px1, y1-40, px2, y1)
                    self.player_vel_y = 0
                    self.on_ground = True
            except (ValueError, tk.TclError):
                continue

        # Generate new platforms and remove old ones
        if self.platforms:
            try:
                last_p_coords = self.canvas.coords(self.platforms[-1])
                if last_p_coords[2] < self.WIDTH + 100:
                    nx1, ny1, nx2, ny2 = self._generate_next_platform(last_p_coords)
                    new_p = self.canvas.create_rectangle(nx1, ny1, nx2, ny2, fill="#8C96AA", outline="")
                    self.platforms.append(new_p)
                
                if self.canvas.coords(self.platforms[0])[2] < 0:
                    self.canvas.delete(self.platforms.pop(0))
            except (ValueError, tk.TclError, IndexError):
                pass

        # Update score and check for game over condition
        self.score += 1
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        if py1 > self.HEIGHT:
            self.game_over = True

        self._after_id = self.after(1000 // self.FPS, self.game_loop)
