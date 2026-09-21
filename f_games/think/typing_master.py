# games/typing_master.py

import tkinter as tk
import random
import time
import os
from pathlib import Path

class TypingMasterGame(tk.Frame):
    """A game to test and improve typing speed and accuracy."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.sentences = []
        self._load_sentences_from_file()
        self._setup_ui()
        self.reset_game()

    def _load_sentences_from_file(self):
        """Loads sentences from an external file or uses defaults."""
        try:
            # Start from the current file's location
            current_path = Path(__file__).resolve()
            
            # Search upwards for the project root (a directory containing 'main.py')
            project_root = None
            for parent in current_path.parents:
                if (parent / "main.py").exists():
                    project_root = parent
                    break
            
            if not project_root:
                raise FileNotFoundError("Could not determine the project's root directory.")

            file_path = project_root / "assets" / "GS_TypingMaster.txt"
            
            with open(file_path, "r", encoding="utf-8") as f:
                self.sentences = [line.strip() for line in f.readlines() if line.strip()]
            
            if not self.sentences:
                print("Warning: 'GS_TypingMaster.txt' is empty. Using default sentences.")
                raise FileNotFoundError

        except (FileNotFoundError, TypeError):
            print("Warning: 'GS_TypingMaster.txt' not found or project root invalid. Using default sentences.")
            self.sentences = [
                "The old lighthouse stood sentinel against the churning sea.",
                "A software developer debugged a complex segment of code.",
                "The intricate workings of a mechanical clock were a marvel of micro-engineering."
            ]

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        tk.Label(self, text="Typing Master", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").grid(row=0, column=0, pady=10)
        
        self.prompt_widget = tk.Text(self, font=("Courier", 18), height=5, wrap=tk.WORD, bg="#3C3C3C", fg="white", relief="flat", highlightthickness=0)
        self.prompt_widget.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 5))
        self.prompt_widget.tag_config("correct", foreground="#4CAF50")
        self.prompt_widget.tag_config("current", background="#555555")
        self.prompt_widget.tag_config("error", foreground="white", background="#FF5555")
        
        self.input_var = tk.StringVar()
        self.input_var.trace_add("write", self._on_text_change)
        self.input_entry = tk.Entry(self, textvariable=self.input_var, font=("Courier", 18), bg="#1E1E1E", fg="white", relief="flat", insertbackground="white")
        self.input_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 20))
        
        self.stats_label = tk.Label(self, text="WPM: 0 | Accuracy: 100.0%", font=("Arial", 16), bg="#2E2E2E", fg="white")
        self.stats_label.grid(row=3, column=0, pady=10)
        
        button_frame = tk.Frame(self, bg="#2E2E2E")
        button_frame.grid(row=4, column=0, pady=10)
        tk.Button(button_frame, text="Reset", font=("Arial", 14), command=self.reset_game, bg="#FF6B6B", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Back to Menu", font=("Arial", 14), command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").pack(side=tk.LEFT, padx=10)

    def reset_game(self):
        self.text_to_type = random.choice(self.sentences)
        self.current_index = 0
        self.start_time = 0
        self.game_started = False
        self.game_finished = False
        
        self.prompt_widget.config(state=tk.NORMAL)
        self.prompt_widget.delete("1.0", tk.END)
        self.prompt_widget.insert("1.0", self.text_to_type)
        self.prompt_widget.config(state=tk.DISABLED)
        
        self.input_var.set("")
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus_set()
        
        self._update_display()
        self.stats_label.config(text="WPM: 0 | Accuracy: 100.0%", fg="white")

    def _on_text_change(self, *args):
        if self.game_finished: return
        
        typed_text = self.input_var.get()
        if not self.game_started and typed_text:
            self.game_started = True
            self.start_time = time.time()
            
        self._update_display()
        self.update_stats()
        
        if len(typed_text) >= len(self.text_to_type) and typed_text == self.text_to_type:
            self.game_finished = True
            self.input_entry.config(state=tk.DISABLED)
            self.stats_label.config(text=f"Finished! Final Stats: {self.stats_label.cget('text')}", fg="#4CAF50")

    def _update_display(self):
        typed_text = self.input_var.get()
        typed_len = len(typed_text)
        
        self.prompt_widget.config(state=tk.NORMAL)
        self.prompt_widget.tag_remove("correct", "1.0", tk.END)
        self.prompt_widget.tag_remove("error", "1.0", tk.END)
        self.prompt_widget.tag_remove("current", "1.0", tk.END)
        
        self.current_index = 0
        has_error = False
        for i in range(len(self.text_to_type)):
            if i < typed_len:
                if typed_text[i] == self.text_to_type[i] and not has_error:
                    self.prompt_widget.tag_add("correct", f"1.{i}", f"1.{i+1}")
                    self.current_index = i + 1
                else:
                    self.prompt_widget.tag_add("error", f"1.{i}", f"1.{i+1}")
                    has_error = True
            else:
                break
                
        if not self.game_finished and not has_error and typed_len < len(self.text_to_type):
            current_pos = f"1.{typed_len}"
            self.prompt_widget.tag_add("current", current_pos)
            self.prompt_widget.see(current_pos)
            
        self.prompt_widget.config(state=tk.DISABLED)

    def update_stats(self):
        if not self.game_started or self.start_time == 0: return
        
        elapsed_time = time.time() - self.start_time
        correct_chars = self.current_index
        
        # WPM calculation (standard is 5 chars per word)
        words_typed = correct_chars / 5.0
        minutes_elapsed = elapsed_time / 60.0
        wpm = int(words_typed / minutes_elapsed) if minutes_elapsed > 0 else 0
        
        # Accuracy calculation
        total_typed_chars = len(self.input_var.get())
        errors = 0
        for i in range(total_typed_chars):
            if i >= len(self.text_to_type) or self.input_var.get()[i] != self.text_to_type[i]:
                errors += 1
        
        accuracy = ((correct_chars - errors) / correct_chars) * 100 if correct_chars > 0 else 100.0
        
        self.stats_label.config(text=f"WPM: {wpm} | Accuracy: {max(0, accuracy):.1f}%")
