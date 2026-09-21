# f_utilities/pomodoro_timer.py

import tkinter as tk
from tkinter import font

class PomodoroTimerApp(tk.Frame):
    """A timer for the Pomodoro productivity technique."""
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master, bg="#2E2E2E")
        self.show_main_menu_callback = show_main_menu_callback
        
        # --- Constants ---
        self.WORK_TIME = 25 * 60
        self.SHORT_BREAK = 5 * 60
        self.LONG_BREAK = 15 * 60
        self.EXTENSION_TIME = 5 * 60

        # --- State Variables ---
        self.is_running = False
        self.time_left = self.WORK_TIME
        self.cycles = 0
        self.current_mode = "Work"
        self._after_id = None
        self._notification_window = None
        
        # --- Get a reference to the main application window ---
        self.root = self.winfo_toplevel()
        
        self._setup_ui()

    def stop_game_loop(self):
        """Stops the timer and closes notification when the frame is closed."""
        self.is_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        # --- NEW: Ensure notification is destroyed on exit ---
        if self._notification_window:
            self._notification_window.destroy()
            self._notification_window = None

    def _clear_frame(self):
        """Helper to destroy all widgets in the frame."""
        for widget in self.winfo_children():
            widget.destroy()

    def _setup_ui(self):
        """Sets up the main timer view."""
        self._clear_frame()

        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(expand=True)
        
        self.status_label = tk.Label(main_frame, text="Work", font=("Helvetica", 28, "bold"), bg="#2E2E2E", fg="white")
        self.status_label.pack(pady=(20, 10))
        
        self.timer_label = tk.Label(main_frame, text="25:00", font=("Courier", 80, "bold"), bg="#2E2E2E", fg="#4CAF50")
        self.timer_label.pack(pady=20)
        
        button_frame = tk.Frame(main_frame, bg="#2E2E2E")
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="Start", font=("Arial", 16), command=self.start_timer, bg="#4CAF50", fg="white", relief="flat", width=8)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.pause_button = tk.Button(button_frame, text="Pause", font=("Arial", 16), command=self.pause_timer, bg="#F5A623", fg="white", relief="flat", width=8, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = tk.Button(button_frame, text="Reset", font=("Arial", 16), command=self.reset_timer, bg="#FF5555", fg="white", relief="flat", width=8)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        tk.Button(main_frame, text="Back to Menu", font=("Arial", 14), command=self.show_main_menu_callback, bg="#4A4A4A", fg="white", relief="flat").pack(pady=30)
        
        self._update_display()

    def start_timer(self):
        if self.is_running: return
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(text="Pause", state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)
        self._update_timer()

    def pause_timer(self):
        if not self.is_running: # If it was paused, resume it
            self.is_running = True
            self.pause_button.config(text="Pause")
            self._update_timer()
        else: # If it was running, pause it
            self.is_running = False
            self.pause_button.config(text="Resume")
            if self._after_id:
                self.after_cancel(self._after_id)

    def reset_timer(self):
        self.stop_game_loop()
        self.cycles = 0
        self.current_mode = "Work"
        self.time_left = self.WORK_TIME
        self._setup_ui() # Rebuild the UI to reset state

    def _update_timer(self):
        if not self.is_running: return
        
        self._update_display()
        
        if self.time_left > 0:
            self.time_left -= 1
            self._after_id = self.after(1000, self._update_timer)
        else:
            self._next_session()

    def _update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

    # --- MODIFIED: The core logic for transitioning between states ---
    def _next_session(self):
        self.is_running = False
        
        if self.current_mode == "Work":
            # Work session ended: show quiet notification
            self._show_work_complete_notification()
        else: 
            # Break session ended: bring window forward with "loud" colors
            self.current_mode = "Work"
            self.time_left = self.WORK_TIME
            self.root.deiconify() # Un-minimize if necessary
            self.root.lift()      # Bring to front
            self._setup_ui()
            self.status_label.config(text="Break's Over! Ready for Work?", fg="#FF5555")
            self.timer_label.config(fg="#FF5555")
            
    # --- NEW: Creates the mini notification window ---
    def _show_work_complete_notification(self):
        if self._notification_window:
            self._notification_window.destroy()

        self._clear_frame() # Hide the main timer UI
        
        # Create a Toplevel window (a new, separate window)
        self._notification_window = tk.Toplevel(self.root)
        self._notification_window.overrideredirect(True) # No title bar or border
        self._notification_window.attributes("-topmost", True) # Keep on top of other windows
        self._notification_window.geometry("250x100")
        
        # Position it at the bottom-right of the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 270 # 250 width + 20px padding
        y = screen_height - 150 # 100 height + 50px padding
        self._notification_window.geometry(f'+{x}+{y}')
        
        # Style the notification
        notif_frame = tk.Frame(self._notification_window, bg="#202020", relief="solid", bd=1, highlightbackground="#007ACC", highlightthickness=2)
        notif_frame.pack(fill="both", expand=True)

        tk.Label(notif_frame, text="Work session complete!", font=("Helvetica", 12), bg="#202020", fg="white").pack(pady=(15, 5))
        tk.Label(notif_frame, text="Click here to continue...", font=("Helvetica", 10), bg="#202020", fg="#888888").pack()

        # Make it clickable
        notif_frame.bind("<Button-1>", self._handle_notification_click)
        for child in notif_frame.winfo_children():
            child.bind("<Button-1>", self._handle_notification_click)

    # --- NEW: Handles the click on the notification ---
    def _handle_notification_click(self, event=None):
        if self._notification_window:
            self._notification_window.destroy()
            self._notification_window = None
        self.root.deiconify()
        self.root.lift()
        self._show_decision_ui()

    # --- NEW: Shows the screen with "Start Break" and "Extend Work" ---
    def _show_decision_ui(self):
        self._clear_frame()
        self.cycles += 1
        
        # Determine which break is next
        if self.cycles % 4 == 0:
            break_text = "Start Long Break (15 min)"
            self.time_left = self.LONG_BREAK
            self.current_mode = "Long Break"
        else:
            break_text = "Start Short Break (5 min)"
            self.time_left = self.SHORT_BREAK
            self.current_mode = "Short Break"
            
        decision_frame = tk.Frame(self, bg="#2E2E2E")
        decision_frame.pack(expand=True)
        
        tk.Label(decision_frame, text="Time for a break?", font=("Helvetica", 28, "bold"), bg="#2E2E2E", fg="white").pack(pady=(40, 30))

        tk.Button(decision_frame, text=break_text, font=("Arial", 16),
                  command=self._start_break, bg="#3399FF", fg="white", relief="flat", width=25, pady=10).pack(pady=15)
                  
        tk.Button(decision_frame, text="Extend Work (+5 min)", font=("Arial", 16),
                  command=self._extend_work, bg="#4A4A4A", fg="white", relief="flat", width=25, pady=10).pack(pady=15)

    # --- NEW: Logic for starting the chosen break ---
    def _start_break(self):
        self._setup_ui()
        # Configure colors based on break type
        if self.current_mode == "Long Break":
            self.status_label.config(text="Long Break", fg="#3399FF")
            self.timer_label.config(fg="#3399FF")
        else:
            self.status_label.config(text="Short Break", fg="#FF9933")
            self.timer_label.config(fg="#FF9933")
        self.start_timer()

    # --- NEW: Logic for extending the work session ---
    def _extend_work(self):
        self.current_mode = "Work"
        self.time_left = self.EXTENSION_TIME
        self._setup_ui()
        self.status_label.config(text="Work (Extended)", fg="white")
        self.timer_label.config(fg="#4CAF50")
        self.start_timer()