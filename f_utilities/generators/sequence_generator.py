# utilities/sequence_generator.py

import tkinter as tk

class SequenceGeneratorApp(tk.Frame):
    """A utility to generate and display mathematical sequences like Pi or Fibonacci."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.is_running = False
        self._after_id = None
        self._setup_ui()

    def stop_game_loop(self):
        """Stops the generator."""
        self.stop_generator()

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg="#2E2E2E"); main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1); main_frame.rowconfigure(2, weight=1)
        tk.Label(main_frame, text="Sequence Generator", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").grid(row=0, column=0, pady=20)
        
        controls_frame = tk.Frame(main_frame, bg="#2E2E2E"); controls_frame.grid(row=1, column=0, pady=10)
        self.mode_var = tk.StringVar(value="Pi")
        tk.Radiobutton(controls_frame, text="Pi Digits", variable=self.mode_var, value="Pi", bg="#2E2E2E", fg="white", selectcolor="#4A4A4A", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(controls_frame, text="Fibonacci", variable=self.mode_var, value="Fib", bg="#2E2E2E", fg="white", selectcolor="#4A4A4A", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.start_button = tk.Button(controls_frame, text="Start", command=self.start_generator, bg="#4CAF50", fg="white", relief="flat")
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = tk.Button(controls_frame, text="Stop", command=self.stop_generator, bg="#FF5555", fg="white", relief="flat", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.output_text = tk.Text(main_frame, bg="#1E1E1E", fg="white", font=("Courier", 14), wrap=tk.CHAR)
        self.output_text.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        tk.Button(main_frame, text="Back to Menu", command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").grid(row=3, column=0, pady=20)

    def start_generator(self):
        if self.is_running: return
        self.is_running = True
        self.output_text.delete("1.0", tk.END)
        self.start_button.config(state=tk.DISABLED); self.stop_button.config(state=tk.NORMAL)
        
        if self.mode_var.get() == "Pi":
            self.pi_gen = self._pi_digits_generator()
            self.output_text.insert(tk.END, f"{next(self.pi_gen)}.")
            self._pi_loop()
        elif self.mode_var.get() == "Fib":
            self.fib_a, self.fib_b = 0, 1
            self._fib_loop()

    def stop_generator(self):
        self.is_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.start_button.config(state=tk.NORMAL); self.stop_button.config(state=tk.DISABLED)

    def _pi_loop(self):
        if not self.is_running: return
        digits = "".join(str(next(self.pi_gen)) for _ in range(50))
        self.output_text.insert(tk.END, digits)
        self.output_text.see(tk.END)
        self._after_id = self.after(50, self._pi_loop)

    def _fib_loop(self):
        if not self.is_running: return
        self.output_text.insert(tk.END, str(self.fib_a) + "\n")
        self.output_text.see(tk.END)
        self.fib_a, self.fib_b = self.fib_b, self.fib_a + self.fib_b
        self._after_id = self.after(100, self._fib_loop)

    def _pi_digits_generator(self):
        """A generator for the digits of Pi using the spigot algorithm."""
        q, r, t, k, n, l = 1, 0, 1, 1, 3, 3
        while True:
            if 4 * q + r - t < n * t:
                yield n
                nr = 10 * (r - n * t)
                n = ((10 * (3 * q + r)) // t) - 10 * n
                q *= 10
                r = nr
            else:
                nr = (2 * q + r) * l
                nn = (q * (7 * k + 2) + r * l) // (t * l)
                q *= k
                t *= l
                l += 2
                k += 1
                n = nn
                r = nr
