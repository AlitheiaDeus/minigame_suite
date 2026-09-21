# main.py
#
# Author: AlitheiaDeus
# Date: 2025-08-31
#
# The central hub for the Game & Program Suite. This file contains the main
# application controller which dynamically scans for feature directories (prefixed
# with 'f_') to discover and load all available modules, presenting them in a
# paged navigation system.

import tkinter as tk
from tkinter import font
import multiprocessing
import importlib
from pathlib import Path
import sys
import os

# --- ANSI Colors for Console Output ---
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def load_modules_from_directory(directory_name):
    """
    Scans a directory and its subdirectories for Python files, imports them,
    and returns a nested dictionary mapping subcategory -> display name -> module info.
    It reloads already imported modules to pick up changes.
    """

    importlib.invalidate_caches()

    modules = {}
    dir_path = Path(directory_name)

    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    if not dir_path.is_dir():
        print(f"Warning: Directory '{directory_name}' not found.")
        return modules

    print(f"\n--- Loading modules from '{directory_name}' ---")
    for file in sorted(dir_path.rglob("*.py")):
        if file.name == "__init__.py":
            continue

        is_wip = file.stem.startswith("WIP_")
        module_stem = file.stem[4:] if is_wip else file.stem
        
        relative_path = file.relative_to(dir_path)
        subcategory = relative_path.parent.name.replace("_", " ").title() if len(relative_path.parts) > 1 else "General"

        module_path_parts = [directory_name] + list(relative_path.parents[0].parts) + [file.stem]
        module_name = ".".join(module_path_parts)
        
        base_name = "".join(word.capitalize() for word in module_stem.split('_'))
        class_name_options = [base_name, f"{base_name}Game", f"{base_name}App", f"{base_name}Utility"]

        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            imported_class = None
            for c_name in class_name_options:
                if hasattr(module, c_name):
                    imported_class = getattr(module, c_name)
                    break
            
            if not imported_class:
                raise AttributeError(f"Could not find a suitable class in {file.name}")

            display_name = module_stem.replace("_", " ").title()
            if is_wip:
                display_name = f"🚧 {display_name}"
            
            if subcategory not in modules:
                modules[subcategory] = {}
                
            modules[subcategory][display_name] = { "class": imported_class, "is_wip": is_wip }
            
            category_str = f"[{subcategory}]"
            status_str, color = ("WIP", Colors.YELLOW) if is_wip else ("Loaded", Colors.GREEN)
            print(f"  {category_str:<14} {display_name:<30} {color}{status_str}{Colors.RESET}")
            
        except (ImportError, AttributeError) as e:
            failed_module_str = f"File: {file.name}"
            status_str = "Failed"
            print(f"  {failed_module_str:<45} {Colors.RED}{Colors.BOLD}{status_str}{Colors.RESET}")
            print(f"    └─ Reason: {e}")
            
    return modules

# --- Main Application Controller ---
class GameSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("Alitheia's Game & Program Suite")
        self.root.configure(bg="#2E2E2E")
        self.root.minsize(800, 600)
        self.root.geometry("900x700")
        self.center_window(900, 700)

        # Style configuration
        self.title_font = font.Font(family="Helvetica", size=28, weight="bold")
        self.category_font = font.Font(family="Helvetica", size=22, weight="bold")
        self.subcategory_font = font.Font(family="Helvetica", size=11, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=14)
        self.big_button_font = font.Font(family="Helvetica", size=18)
        self.small_button_font = font.Font(family="Helvetica", size=10)
        
        self.button_style = {
            "bg": "#4A4A4A", "fg": "white", "activebackground": "#6A6A6A",
            "activeforeground": "white", "relief": "flat", "bd": 0,
            "pady": 10, "padx": 20
        }
        self.disabled_button_style = {
            "bg": "#3A3A3A", "fg": "#777777", "relief": "flat", "bd": 0,
            "pady": 10, "padx": 20
        }

        self.container = tk.Frame(root, bg="#2E2E2E")
        self.container.pack(fill="both", expand=True)

        self.current_frame = None
        self.show_main_menu()

    def center_window(self, width, height):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def clear_container(self):
        # Unbind mouse wheel events when leaving a scrollable page
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")

        if self.current_frame:
            if hasattr(self.current_frame, 'stop_game_loop') and callable(getattr(self.current_frame, 'stop_game_loop')):
                self.current_frame.stop_game_loop()
            self.current_frame.destroy()
            self.current_frame = None

    def discover_categories(self):
        """Scans for directories prefixed with 'f_' to dynamically find categories."""
        root_path = Path(__file__).parent
        categories = []
        print("\n--- Discovering feature categories ---")
        for path in sorted(root_path.iterdir()):
            if path.is_dir() and path.name.startswith("f_"):
                # Format the name: remove prefix, replace underscore, capitalize
                display_name = path.name[2:].replace("_", " ").title()
                categories.append({"display": display_name, "path": path.name})
                print(f"  Found: '{path.name}' -> Displaying as '{display_name}'")
        return categories

    def show_main_menu(self):
        self.clear_container()
        self.root.title("Alitheia's Game & Program Suite")
        self.center_window(900, 700)

        menu_frame = tk.Frame(self.container, bg="#2E2E2E")
        menu_frame.pack(fill="both", expand=True)
        self.current_frame = menu_frame

        tk.Label(menu_frame, text="Game & Program Suite", font=self.title_font, bg="#2E2E2E", fg="white").pack(pady=(60, 40))
        
        categories = self.discover_categories()
        
        buttons_frame = tk.Frame(menu_frame, bg="#2E2E2E")
        buttons_frame.pack(pady=20)

        if not categories:
            tk.Label(buttons_frame, text="No feature folders (f_*) found.",
                     font=self.button_font, bg="#2E2E2E", fg="#999999").pack(pady=20)
        else:
            for category_info in categories:
                button = tk.Button(buttons_frame, text=category_info["display"], font=self.big_button_font,
                                   command=lambda c=category_info: self.show_category_page(c['display'], c['path']),
                                   **self.button_style, width=15, height=2)
                button.pack(pady=15)
            
    def show_category_page(self, category_title, category_directory):
        self.clear_container()
        self.root.title(f"Suite - {category_title}")
        
        page_frame = tk.Frame(self.container, bg="#2E2E2E")
        page_frame.pack(fill="both", expand=True)
        self.current_frame = page_frame

        # --- Header ---
        header_frame = tk.Frame(page_frame, bg="#2E2E2E")
        header_frame.pack(fill="x", pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)

        tk.Label(header_frame, text=category_title, font=self.category_font, bg="#2E2E2E", fg="white").grid(row=0, column=1)
        
        back_button = tk.Button(header_frame, text="← Back to Menu", font=self.small_button_font,
                                command=self.show_main_menu, bg="#007ACC", fg="white", relief="flat", padx=10, pady=5)
        back_button.grid(row=0, column=0, sticky="w", padx=20)

        refresh_button = tk.Button(header_frame, text="Refresh ↻", font=self.small_button_font,
                                 command=lambda: self.show_category_page(category_title, category_directory),
                                 bg="#5A5A5A", fg="white", relief="flat", padx=10, pady=5)
        refresh_button.grid(row=0, column=2, sticky="e", padx=20)


        # --- Scrollable Area ---
        canvas, scrollable_frame = self._create_scrollable_area(page_frame)

        # --- Load and Display Modules ---
        modules = load_modules_from_directory(category_directory)

        content_frame = tk.Frame(scrollable_frame, bg="#2E2E2E")
        content_frame.pack(pady=10, padx=40, anchor='n', fill="x", expand=True)

        if not modules:
            tk.Label(content_frame, text=f"No modules found in '{category_directory}/'", 
                     font=self.button_font, bg="#2E2E2E", fg="#999999").pack(pady=50)
        else:
            for subcategory_name, items in sorted(modules.items()):
                if len(modules) > 1 or subcategory_name != "General":
                    tk.Label(content_frame, text=subcategory_name, font=self.subcategory_font, 
                             bg="#2E2E2E", fg="#999999").pack(pady=(15, 5), anchor='w')

                for name, item_info in sorted(items.items()):
                    item_class = item_info["class"]
                    is_wip = item_info["is_wip"]

                    style = self.button_style if not is_wip else self.disabled_button_style
                    state = tk.NORMAL if not is_wip else tk.DISABLED
                    
                    # Create the callback to return to this specific page
                    return_callback = lambda c_title=category_title, c_dir=category_directory: self.show_category_page(c_title, c_dir)

                    button = tk.Button(content_frame, text=name, font=self.button_font,
                                       command=lambda ic=item_class, t=name, cb=return_callback: self.launch_item(ic, t, cb),
                                       **style, width=30, state=state)
                    button.pack(pady=6, fill='x')

    def _create_scrollable_area(self, parent):
        """Helper to create a standard canvas with scrollbar."""
        scroll_container = tk.Frame(parent, bg="#2E2E2E")
        scroll_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(scroll_container, bg="#2E2E2E", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg="#2E2E2E")
        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_configure(event):
            canvas.itemconfig(frame_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_frame_configure)

        def on_mouse_wheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                if event.num == 5:
                    canvas.yview_scroll(1, "units")
                elif event.num == 4:
                    canvas.yview_scroll(-1, "units")
        
        # Bind events to the root window to ensure they are captured
        self.root.bind_all("<MouseWheel>", on_mouse_wheel)
        self.root.bind_all("<Button-4>", on_mouse_wheel)
        self.root.bind_all("<Button-5>", on_mouse_wheel)
        
        return canvas, scrollable_frame

    def launch_item(self, item_class, title, return_callback):
        self.clear_container()
        self.root.title(title)
        
        # Pass the specific callback to the launched item
        item = item_class(self.container, return_callback)
        item.pack(fill="both", expand=True)
        self.current_frame = item

# --- Application Entry Point ---
if __name__ == "__main__":
    if os.name == 'nt': os.system('') # Enables ANSI escape codes on Windows
    multiprocessing.freeze_support()
    
    # Ensure base directories exist for new users
    print("--- Initializing ---")
    print("Checking for base directories...")
    for d in ["f_games", "f_puzzles", "f_utilities"]:
        if not os.path.exists(d):
            print(f"Creating missing directory: '{d}'")
            os.makedirs(d, exist_ok=True)
            # Create __init__.py to ensure the folder is treated as a package
            Path(f"{d}/__init__.py").touch()

    root = tk.Tk()
    app = GameSuite(root)
    root.mainloop()
