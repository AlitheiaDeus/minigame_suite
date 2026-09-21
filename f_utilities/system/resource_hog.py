# utilities/resource_hog.py

import tkinter as tk
import multiprocessing
import math
import time
import sys

def _cpu_eater_worker_task():
    """ 
    A standalone function for multiprocessing to prevent pickling issues.
    This function performs complex, meaningless calculations in a loop to
    consume CPU resources.
    """
    try:
        while True:
            for i in range(1_000_000):
                _ = math.sqrt(abs(i * 3.14159 - 500000) + 1.0) * \
                        math.sin(i / (abs(i-1000) + 1.0)) * \
                        math.cos(i / (abs(i-2000) + 1.0)) / \
                        (abs(i - 750000) + 0.001)
            time.sleep(0.001) # Small sleep to prevent total system lockup
    except KeyboardInterrupt:
        pass # Allows the process to be terminated gracefully

class ResourceHogApp(tk.Frame):
    """A utility to intentionally consume CPU or RAM resources."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.cpu_workers = []
        self.ram_chunks = []
        self.is_running = False
        self._after_id = None
        self._setup_ui()

    def stop_game_loop(self):
        """Ensures all hogging activities are stopped on exit."""
        self.stop_hog()

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg="#2E2E2E"); main_frame.pack(expand=True)
        tk.Label(main_frame, text="Resource Hog", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").pack(pady=20)
        
        self.mode_var = tk.StringVar(value="CPU")
        options_frame = tk.Frame(main_frame, bg="#2E2E2E"); options_frame.pack(pady=10)
        tk.Radiobutton(options_frame, text="CPU Eater", variable=self.mode_var, value="CPU", command=self.update_ui_for_mode, bg="#2E2E2E", fg="white", selectcolor="#4A4A4A", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(options_frame, text="RAM Eater", variable=self.mode_var, value="RAM", command=self.update_ui_for_mode, bg="#2E2E2E", fg="white", selectcolor="#4A4A4A", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

        self.settings_frame = tk.Frame(main_frame, bg="#2E2E2E"); self.settings_frame.pack(pady=10)
        
        self.start_button = tk.Button(main_frame, text="Start", font=("Arial", 16, "bold"), command=self.start_hog, bg="#4CAF50", fg="white", relief="flat", width=10)
        self.start_button.pack(pady=10)
        self.stop_button = tk.Button(main_frame, text="Stop", font=("Arial", 16, "bold"), command=self.stop_hog, bg="#FF5555", fg="white", relief="flat", width=10, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(main_frame, text="Status: Idle", font=("Arial", 12), bg="#2E2E2E", fg="white")
        self.status_label.pack(pady=10)
        
        tk.Button(main_frame, text="Back to Menu", font=("Arial", 14), command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").pack(pady=30)
        self.update_ui_for_mode()

    def update_ui_for_mode(self):
        for widget in self.settings_frame.winfo_children(): widget.destroy()
        mode = self.mode_var.get()
        if mode == "CPU":
            tk.Label(self.settings_frame, text="Worker Processes:", font=("Arial", 12), bg="#2E2E2E", fg="white").pack(side=tk.LEFT, padx=5)
            self.cpu_workers_var = tk.StringVar(value=str(multiprocessing.cpu_count()))
            tk.Entry(self.settings_frame, textvariable=self.cpu_workers_var, width=5, font=("Arial", 12)).pack(side=tk.LEFT)
        elif mode == "RAM":
            tk.Label(self.settings_frame, text="MB per 2s:", font=("Arial", 12), bg="#2E2E2E", fg="white").pack(side=tk.LEFT, padx=5)
            self.ram_chunk_var = tk.StringVar(value="250")
            tk.Entry(self.settings_frame, textvariable=self.ram_chunk_var, width=5, font=("Arial", 12)).pack(side=tk.LEFT)

    def start_hog(self):
        if self.is_running: return
        self.is_running = True
        self.start_button.config(state=tk.DISABLED); self.stop_button.config(state=tk.NORMAL)
        if self.mode_var.get() == "CPU":
            try:
                num_workers = int(self.cpu_workers_var.get())
                self.status_label.config(text=f"Starting {num_workers} CPU workers...")
                for i in range(num_workers):
                    p = multiprocessing.Process(target=_cpu_eater_worker_task, daemon=True)
                    p.start(); self.cpu_workers.append(p)
                self.status_label.config(text=f"Running {len(self.cpu_workers)} CPU workers.", fg="orange")
            except ValueError:
                self.status_label.config(text="Invalid number of workers.", fg="red")
                self.stop_hog()
        elif self.mode_var.get() == "RAM":
            self.status_label.config(text="Starting RAM allocation...", fg="orange")
            self._ram_eater_loop()

    def stop_hog(self):
        self.is_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
            
        self.start_button.config(state=tk.NORMAL); self.stop_button.config(state=tk.DISABLED)
        
        for p in self.cpu_workers:
            if p.is_alive():
                p.terminate()
                p.join(0.1) # Wait briefly for termination
        self.cpu_workers.clear()
        
        self.ram_chunks.clear() # This releases the memory
        self.status_label.config(text="Status: Idle", fg="white")

    def _ram_eater_loop(self):
        if not self.is_running: return
        try:
            chunk_size_mb = int(self.ram_chunk_var.get())
            # Create a large byte array to allocate memory
            new_chunk = bytearray(chunk_size_mb * 1024 * 1024)
            self.ram_chunks.append(new_chunk)
            
            total_ram = sum(sys.getsizeof(c) for c in self.ram_chunks) / (1024*1024)
            self.status_label.config(text=f"Allocated RAM: {total_ram:.0f} MB")
            
            self._after_id = self.after(2000, self._ram_eater_loop)
        except (ValueError, MemoryError) as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            self.stop_hog()
