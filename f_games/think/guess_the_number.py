# games/guess_the_number.py

import tkinter as tk
import random

class GuessTheNumberGame(tk.Frame):
    """A classic number guessing game with difficulty levels."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.DIFFICULTY = {"Easy (1-50)": (1, 50, 10), "Medium (1-100)": (1, 100, 7), "Hard (1-500)": (1, 500, 9)}
        self._setup_ui()
        self.start_new_game()

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(expand=True)
        tk.Label(main_frame, text="Guess the Number!", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").pack(pady=20)
        self.difficulty_var = tk.StringVar(value="Medium (1-100)")
        options_frame = tk.Frame(main_frame, bg="#2E2E2E")
        options_frame.pack(pady=10)
        tk.Label(options_frame, text="Difficulty:", font=("Arial", 14), bg="#2E2E2E", fg="white").pack(side=tk.LEFT, padx=10)
        for text in self.DIFFICULTY:
            tk.Radiobutton(options_frame, text=text, variable=self.difficulty_var, value=text, command=self.start_new_game, bg="#2E2E2E", fg="white", selectcolor="#4A4A4A", activebackground="#2E2E2E", activeforeground="white", font=("Arial", 12)).pack(side=tk.LEFT)
        self.info_label = tk.Label(main_frame, text="", font=("Arial", 14), bg="#2E2E2E", fg="#CCCCCC")
        self.info_label.pack(pady=10)
        entry_frame = tk.Frame(main_frame, bg="#2E2E2E")
        entry_frame.pack(pady=10)
        self.guess_entry = tk.Entry(entry_frame, font=("Arial", 16), width=10, justify="center", bg="#3C3C3C", fg="white", relief="flat")
        self.guess_entry.pack(side=tk.LEFT, padx=10)
        self.guess_entry.bind("<Return>", lambda e: self.make_guess())
        self.guess_button = tk.Button(entry_frame, text="Guess", command=self.make_guess, font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", relief="flat")
        self.guess_button.pack(side=tk.LEFT)
        self.feedback_label = tk.Label(main_frame, text="Make your first guess.", font=("Arial", 16, "italic"), bg="#2E2E2E", fg="white")
        self.feedback_label.pack(pady=20)
        tk.Button(main_frame, text="Back to Menu", font=("Arial", 14), command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").pack(pady=30)

    def start_new_game(self):
        level = self.difficulty_var.get()
        self.min_range, self.max_range, self.guess_limit = self.DIFFICULTY[level]
        self.secret_number = random.randint(self.min_range, self.max_range)
        self.guesses_taken = 0
        self.info_label.config(text=f"I'm thinking of a number between {self.min_range} and {self.max_range}. You have {self.guess_limit} guesses.")
        self.feedback_label.config(text="New game started. Good luck!", fg="white")
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.config(state=tk.NORMAL)
        self.guess_button.config(state=tk.NORMAL, text="Guess", command=self.make_guess)
        self.guess_entry.focus_set()

    def make_guess(self):
        try:
            guess = int(self.guess_entry.get())
            self.guesses_taken += 1
            remaining = self.guess_limit - self.guesses_taken
            if guess < self.secret_number: self.feedback_label.config(text=f"Too low! You have {remaining} guesses left.", fg="#3399FF")
            elif guess > self.secret_number: self.feedback_label.config(text=f"Too high! You have {remaining} guesses left.", fg="#FF9933")
            else: self.feedback_label.config(text=f"Congratulations! You found it in {self.guesses_taken} guesses.", fg="#4CAF50"); self.end_game(); return
            if self.guesses_taken >= self.guess_limit: self.feedback_label.config(text=f"Game Over! The number was {self.secret_number}.", fg="#FF5555"); self.end_game()
        except ValueError: self.feedback_label.config(text="Invalid input. Please enter a number.", fg="#FF5555")
        finally: self.guess_entry.delete(0, tk.END)

    def end_game(self):
        self.guess_entry.config(state=tk.DISABLED)
        self.guess_button.config(state=tk.DISABLED, text="Play Again", command=self.start_new_game)
        self.guess_button.config(state=tk.NORMAL)
