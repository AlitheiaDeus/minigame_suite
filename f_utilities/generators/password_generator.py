# f_utilities/password_generator.py

import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

class PasswordGeneratorUtility(tk.Frame):
    """A utility for generating secure, customizable passwords."""
    
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")

        # --- Define fonts and styles for a consistent look ---
        label_font = ("Helvetica", 12)
        entry_font = ("Helvetica", 12)
        button_font = ("Helvetica", 12, "bold")
        result_font = ("Courier", 16, "bold") # Monospaced for password
        
        # --- Create a central frame to hold all content ---
        main_frame = tk.Frame(self, bg="#2E2E2E", pady=20)
        main_frame.pack(expand=True)

        # --- Title Label ---
        tk.Label(
            main_frame, text="Password Generator", font=("Helvetica", 20, "bold"),
            bg="#2E2E2E", fg="white"
        ).pack(pady=(0, 30))

        # --- Options Frame (for length, checkboxes, etc.) ---
        options_frame = tk.Frame(main_frame, bg="#3A3A3A", padx=20, pady=20)
        options_frame.pack(pady=10)

        # --- Length Option ---
        tk.Label(
            options_frame, text="Password Length:", font=label_font,
            bg="#3A3A3A", fg="white"
        ).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.length_var = tk.IntVar(value=16)
        ttk.Spinbox(
            options_frame, from_=8, to_=128, textvariable=self.length_var,
            width=5, font=entry_font
        ).grid(row=0, column=1, sticky="w", padx=5)

        # --- Character Type Checkboxes ---
        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_numbers = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=True)

        # Custom style for Checkbuttons to look good on a dark background
        s = ttk.Style()
        s.configure('TCheckbutton', background="#3A3A3A", foreground="white", font=label_font)
        s.map('TCheckbutton', background=[('active', "#3A3A3A")], indicatorcolor=[('selected', '#007ACC')])

        ttk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=self.include_upper, style='TCheckbutton').grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=self.include_lower, style='TCheckbutton').grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(options_frame, text="Numbers (0-9)", variable=self.include_numbers, style='TCheckbutton').grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(options_frame, text="Symbols (!@#$)", variable=self.include_symbols, style='TCheckbutton').grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        
        # --- Result Display Entry ---
        self.result_var = tk.StringVar(value="Your password here...")
        result_entry = tk.Entry(
            main_frame, textvariable=self.result_var, font=result_font,
            bg="#4A4A4A", fg="#39FF14", relief="flat", justify="center", bd=5, width=40,
            readonlybackground="#4A4A4A" # Keep color when readonly
        )
        result_entry.config(state="readonly")
        result_entry.pack(pady=20, padx=20)

        # --- Action Buttons (Generate, Copy) ---
        action_frame = tk.Frame(main_frame, bg="#2E2E2E")
        action_frame.pack(pady=10)
        
        tk.Button(
            action_frame, text="Generate Password", command=self.generate_password, font=button_font,
            bg="#007ACC", fg="white", relief="flat", padx=15, pady=10
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            action_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, font=button_font,
            bg="#5A5A5A", fg="white", relief="flat", padx=15, pady=10
        ).grid(row=0, column=1, padx=10)

        # --- Back Button (uses the provided callback) ---
        tk.Button(
            self, text="← Back to Utilities", font=("Helvetica", 10),
            command=show_main_menu_callback, bg="#5A5A5A", fg="white",
            relief="flat", padx=10, pady=5
        ).pack(side="bottom", anchor="sw", padx=20, pady=20)

    def generate_password(self):
        """Generates a new password based on the selected options."""
        char_pool = ''
        if self.include_upper.get(): char_pool += string.ascii_uppercase
        if self.include_lower.get(): char_pool += string.ascii_lowercase
        if self.include_numbers.get(): char_pool += string.digits
        if self.include_symbols.get(): char_pool += string.punctuation

        if not char_pool:
            messagebox.showwarning("Warning", "You must select at least one character type!")
            return

        try:
            length = self.length_var.get()
            if length <= 0:
                messagebox.showwarning("Warning", "Password length must be greater than zero.")
                return
            password = ''.join(random.choice(char_pool) for _ in range(length))
            self.result_var.set(password)
        except tk.TclError:
             messagebox.showwarning("Warning", "Please enter a valid number for password length.")

    def copy_to_clipboard(self):
        """Copies the generated password to the system clipboard."""
        password = self.result_var.get()
        if password and password != "Your password here...":
            self.clipboard_clear()
            self.clipboard_append(password)
            messagebox.showinfo("Success", "Password copied to clipboard!")