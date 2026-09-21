# puzzles/dungeon_crawler.py

import tkinter as tk
import random

class DungeonCrawlerGame(tk.Frame):
    """A very simple roguelike game. (Work In Progress)"""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.TILE_SIZE = 24
        self.MAP_WIDTH, self.MAP_HEIGHT = 30, 20
        
        # Initialize properties before they are used
        self.game_map = []
        self.player_pos = []
        self.monsters = []
        
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(expand=True)
        self.canvas = tk.Canvas(main_frame, width=self.MAP_WIDTH*self.TILE_SIZE, height=self.MAP_HEIGHT*self.TILE_SIZE, bg="#111", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        self.log_text = tk.Text(main_frame, height=4, width=60, bg="#1E1E1E", fg="white", relief="flat", font=("Courier", 10))
        self.log_text.pack(pady=5)
        
        button_frame = tk.Frame(main_frame, bg="#2E2E2E")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="New Game", command=self.start_new_game, font=("Arial", 12), bg="#4CAF50", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Back to Menu", command=self.show_main_menu_callback, font=("Arial", 12), bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        
        self.bind_all("<Key>", self.on_key_press) # Bind keys to the frame to capture them reliably

    def start_new_game(self):
        self._generate_map()
        
        # --- FIX: Initialize lists before populating them ---
        self.player_pos = []
        self.monsters = []
        
        self.player_pos = self._place_entity_on_floor()
        for _ in range(3):
            monster_pos = self._place_entity_on_floor()
            if monster_pos: # Ensure a valid position was found
                self.monsters.append(monster_pos)
        
        self.log("Welcome to the Dungeon!")
        self.draw_map()
        self.canvas.focus_set()

    def _generate_map(self):
        """Generates a simple map with non-overlapping rooms."""
        self.game_map = [['#' for _ in range(self.MAP_WIDTH)] for _ in range(self.MAP_HEIGHT)]
        rooms = []
        for _ in range(random.randint(5, 8)):
            w, h = random.randint(3, 6), random.randint(3, 6)
            x, y = random.randint(1, self.MAP_WIDTH-w-2), random.randint(1, self.MAP_HEIGHT-h-2)
            
            new_room = {'x1': x, 'y1': y, 'x2': x+w, 'y2': y+h}
            
            if any((new_room['x1'] <= r['x2'] and new_room['x2'] >= r['x1'] and \
                    new_room['y1'] <= r['y2'] and new_room['y2'] >= r['y1']) for r in rooms):
                continue

            for i in range(new_room['y1'], new_room['y2']):
                for j in range(new_room['x1'], new_room['x2']):
                    self.game_map[i][j] = '.'
            
            rooms.append(new_room)

    def _place_entity_on_floor(self):
        """Finds a valid floor tile that isn't already occupied."""
        attempts = 0
        while attempts < 100: # Add a limit to prevent infinite loops
            x, y = random.randint(0, self.MAP_WIDTH-1), random.randint(0, self.MAP_HEIGHT-1)
            if self.game_map[y][x] == '.':
                pos = [x, y]
                # Check against player and existing monsters
                if pos != self.player_pos and pos not in self.monsters:
                    return pos
            attempts += 1
        return None # Return None if no spot is found

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def draw_map(self):
        self.canvas.delete("all")
        for r in range(self.MAP_HEIGHT):
            for c in range(self.MAP_WIDTH):
                x1, y1 = c * self.TILE_SIZE, r * self.TILE_SIZE
                color = "#555" if self.game_map[r][c] == '#' else "#333"
                self.canvas.create_rectangle(x1, y1, x1+self.TILE_SIZE, y1+self.TILE_SIZE, fill=color, outline="")
        
        for mx, my in self.monsters:
            self.canvas.create_text(mx*self.TILE_SIZE + self.TILE_SIZE/2, my*self.TILE_SIZE + self.TILE_SIZE/2, text="M", fill="red", font=("Courier", 16, "bold"))
        
        if self.player_pos:
            px, py = self.player_pos
            self.canvas.create_text(px*self.TILE_SIZE + self.TILE_SIZE/2, py*self.TILE_SIZE + self.TILE_SIZE/2, text="@", fill="cyan", font=("Courier", 16, "bold"))

    def on_key_press(self, event):
        if not self.player_pos: return # Don't move if player doesn't exist

        x, y = self.player_pos
        key = event.keysym.lower()
        nx, ny = x, y
        
        if key in ['w', 'up']: ny -= 1
        elif key in ['s', 'down']: ny += 1
        elif key in ['a', 'left']: nx -= 1
        elif key in ['d', 'right']: nx += 1
        else:
            return

        if 0 <= nx < self.MAP_WIDTH and 0 <= ny < self.MAP_HEIGHT and self.game_map[ny][nx] == '.':
            self.player_pos = [nx, ny]
            if self.player_pos in self.monsters:
                self.log("You attack and defeat a monster!")
                self.monsters.remove(self.player_pos)
            self.draw_map()
            
    def stop_game_loop(self):
        """Required method for cleanup."""
        self.unbind_all("<Key>")