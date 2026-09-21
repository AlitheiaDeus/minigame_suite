# utilities/nosleep.py

import tkinter as tk
import threading
import time
import sys
import os

# OS-specific imports for preventing sleep
if sys.platform == 'win32':
    import ctypes
elif sys.platform in ['darwin', 'linux']:
    import subprocess

class NoSleepApp(tk.Frame):
    """A utility to prevent the computer from going to sleep."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        self.is_active = False
        self.worker_thread = None
        self._setup_ui()

    def stop_game_loop(self):
        """Deactivates the utility when the frame is closed."""
        if self.is_active:
            self.toggle_nosleep()

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg="#2E2E2E"); main_frame.pack(expand=True)
        tk.Label(main_frame, text="NoSleep Utility", font=("Helvetica", 24, "bold"), bg="#2E2E2E", fg="white").pack(pady=20)
        
        info_text = "This utility prevents the system from entering sleep/standby mode.\n"
        if sys.platform == 'darwin':
            info_text += "Uses the 'caffeinate' command."
        elif sys.platform == 'win32':
            info_text += "Uses the 'SetThreadExecutionState' system call."
        elif sys.platform.startswith('linux'):
            info_text += "Uses the 'xdg-screensaver reset' command."
        else:
            info_text += "Platform not supported."

        tk.Label(main_frame, text=info_text, font=("Arial", 11), bg="#2E2E2E", fg="#CCCCCC").pack(pady=10)

        self.status_label = tk.Label(main_frame, text="Status: Inactive", font=("Arial", 16), bg="#2E2E2E", fg="white")
        self.status_label.pack(pady=10)
        self.toggle_button = tk.Button(main_frame, text="Activate", font=("Arial", 16, "bold"), command=self.toggle_nosleep, bg="#4CAF50", fg="white", relief="flat", width=12)
        self.toggle_button.pack(pady=20)
        tk.Button(main_frame, text="Back to Menu", font=("Arial", 14), command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").pack(pady=40)

        if sys.platform not in ['win32', 'darwin'] and not sys.platform.startswith('linux'):
            self.toggle_button.config(state=tk.DISABLED)

    def toggle_nosleep(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.status_label.config(text="Status: Active", fg="orange")
            self.toggle_button.config(text="Deactivate", bg="#FF5555")
            self.worker_thread = threading.Thread(target=self._prevent_sleep_worker, daemon=True)
            self.worker_thread.start()
        else:
            # The thread will see is_active is False and exit its loop
            self.status_label.config(text="Status: Inactive", fg="white")
            self.toggle_button.config(text="Activate", bg="#4CAF50")

    def _prevent_sleep_worker(self):
        """The actual work done in a separate thread to not block the UI."""
        if sys.platform == 'win32':
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            ES_DISPLAY_REQUIRED = 0x00000002
            # Prevent sleep
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            while self.is_active:
                time.sleep(1)
            # Allow sleep again
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        
        elif sys.platform == 'darwin':
            proc = subprocess.Popen(['caffeinate', '-d'])
            while self.is_active:
                time.sleep(1)
            proc.terminate()

        elif sys.platform.startswith('linux'):
            # Check if xdg-screensaver exists
            if subprocess.call(['which', 'xdg-screensaver']) == 0:
                while self.is_active:
                    subprocess.run(['xdg-screensaver', 'reset'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(50)
            else:
                print("Warning: 'xdg-screensaver' command not found. NoSleep may not work.")
                # Update UI from thread safely
                self.after(0, lambda: self.status_label.config(text="Error: xdg-screensaver not found", fg="red"))
