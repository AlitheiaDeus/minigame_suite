# utilities/dice_roller.py

import tkinter as tk
from tkinter import font
import random

class DiceRollerApp(tk.Frame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        
        self.show_main_menu_callback = show_main_menu_callback
        
        # --- State Variables for Cumulative Rolls ---
        self.all_rolls = []
        self.current_total = 0
        
        # --- Font and Style Definitions ---
        self.header_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=18)
        self.total_font = font.Font(family="Helvetica", size=28, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=14)
        self.small_font = font.Font(family="Helvetica", size=11)
        
        self.button_style = {
            "bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A",
            "activeforeground": "white", "relief": "flat", "bd": 0,
            "pady": 10, "padx": 15
        }

        self._create_widgets()
        self.reset_rolls()

    def _create_widgets(self):
        """Creates and places the UI elements for the dice roller. (No changes here)"""
        
        # --- Header ---
        tk.Label(
            self, text="Dice Roller", 
            font=self.header_font, bg="#2E2E2E", fg="white"
        ).pack(pady=(20, 10))

        # --- Number of Dice Input ---
        control_frame = tk.Frame(self, bg="#2E2E2E")
        control_frame.pack(pady=10)
        
        tk.Label(
            control_frame, text="Number of Dice:", 
            font=self.label_font, bg="#2E2E2E", fg="white"
        ).pack(side="left", padx=(0, 10))
        
        self.dice_count_var = tk.StringVar(value="1")
        self.dice_count_spinbox = tk.Spinbox(
            control_frame, from_=1, to=100, width=5, 
            textvariable=self.dice_count_var, font=self.label_font,
            bg="#3C3C3C", fg="white", relief="flat", buttonbackground="#4A4A4A"
        )
        self.dice_count_spinbox.pack(side="left")

        # --- Result Display ---
        self.total_label = tk.Label(
            self, text="", font=self.total_font,
            bg="#2E2E2E", fg="#4CAF50"
        )
        self.total_label.pack(pady=20)
        
        self.rolls_label = tk.Label(
            self, text="", font=self.small_font,
            bg="#2E2E2E", fg="#CCCCCC", wraplength=400
        )
        self.rolls_label.pack(pady=(0, 20))

        # --- Dice Roll Buttons ---
        dice_frame = tk.Frame(self, bg="#2E2E2E")
        dice_frame.pack(pady=10)
        
        dice_types = [4, 6, 8, 12, 20, 10, 100]
        for sides in dice_types:
            tk.Button(
                dice_frame, text=f"Roll D{sides}", font=self.button_font,
                command=lambda s=sides: self.roll_dice(s), **self.button_style
            ).pack(side="left", padx=5)
        
        # --- Action Buttons ---
        action_frame = tk.Frame(self, bg="#2E2E2E")
        action_frame.pack(pady=20)
        
        tk.Button(
            action_frame, text="Reset", font=self.button_font,
            command=self.reset_rolls, **self.button_style
        ).pack(side="left", padx=10)

        tk.Button(
            self, text="Back to Menu", font=self.button_font,
            command=self.show_main_menu_callback, **self.button_style
        ).pack(side="bottom", pady=20)
        
    def roll_dice(self, sides):
        """Generates new rolls and adds them to the cumulative total."""
        try:
            num_dice = int(self.dice_count_var.get())
        except ValueError:
            num_dice = 1
            
        # Generate only the new rolls
        new_rolls = [random.randint(1, sides) for _ in range(num_dice)]
        
        # Add the new rolls and sum to the persistent state
        self.all_rolls.extend(new_rolls)
        self.current_total += sum(new_rolls)
        
        # Update the display with the new cumulative totals
        self.total_label.config(text=f"Total: {self.current_total}")
        self.rolls_label.config(text=f"Rolls: {str(self.all_rolls)}")

    def reset_rolls(self):
        """Resets the state variables and result display."""
        self.all_rolls.clear()
        self.current_total = 0
        self.total_label.config(text="Total: 0")
        self.rolls_label.config(text="Rolls: []")

    def stop_game_loop(self):
        """Required by the main suite for API compliance."""
        pass