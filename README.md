# Alitheia's Game & Program Suite

A collection of various Python games, puzzles, and utilities, unified into a single application using the Tkinter standard library. This suite serves as a central hub for launching modules, all presented with a consistent, dark-themed user interface.

The project uses a modular architecture with a dynamic loader, allowing for easy expansion. The main controller automatically discovers and loads modules from specially named directories.

---
## Key Features
---
* **Dynamic Module Loading**: Simply drop a correctly formatted Python file into a feature directory, and it appears in the menu on the next launch.
* **Automatic Category Discovery**: The main menu is built by scanning for folders with an `f_` prefix (e.g., `f_games`).
* **Sub-Category Organization**: Organize modules within sub-folders for a cleaner, grouped menu.
* **WIP Handling**: Files prefixed with `WIP_` are automatically recognized, displayed differently, and disabled in the UI.
* **Centralized Asset Management**: A top-level `assets/` folder provides a single, organized location for all shared resources like images, sounds, and data files.
* **Consistent UI**: A dark-themed, paged, and scrollable interface provides a unified user experience.

---
## Directory Structure
---

The project is organized into **feature categories**. A feature category is any directory in the root folder whose name is prefixed with `f_`. On first run, the application will automatically create `f_games`, `f_puzzles`, and `f_utilities` if they don't exist.

To better organize modules, you can create **subdirectories** within these main categories. The name of the subdirectory will be used as a sub-heading in the application menu.

```
GameSuite_Project/
├── main.py                     # Main application controller
├── launcher.bat                # Windows launcher script
├── README.md                   # This file
│
├── assets/                     # For all external assets
│   └── typing_master_words.txt
│
└── f_games/                    # A feature category for games
    ├── __init__.py
    ├── a_general_game.py       # Will appear under the "General" sub-heading
    │
    └── arcade/                 # This becomes a sub-category named "Arcade"
        ├── __init__.py
        ├── dot_dodger.py
        └── WIP_new_racer.py    # A disabled "Work in Progress" module
```

---
## Module Development Guide
---

The dynamic loader in `main.py` requires a specific structure to automatically discover and load new modules.

### 1. File Placement

Place your new module file (`.py`) inside the appropriate feature directory (e.g., `f_games`).
* To group it under a specific sub-heading, place it inside a subdirectory (e.g., `f_games/strategy/`).
* If no specific group is needed, place it directly in the root of the feature folder.

### 2. File Naming

* **Standard Files**: All Python module files must be named using **snake_case** (lowercase with underscores).
    * **CORRECT:** `my_cool_game.py`
    * **INCORRECT:** `MyCoolGame.py`

* **Work-in-Progress Files**: To mark a file as incomplete, prefix its name with `WIP_`. It will be loaded but disabled in the UI.
    * **EXAMPLE:** `WIP_unfinished_puzzle.py`

### 3. Class Naming

The main class inside each module file must be named using **PascalCase** and is derived directly from the filename. The loader automatically converts the `snake_case` filename to `PascalCase`.

* File: `dot_dodger.py` -> Base Class Name: `DotDodger`
* File: `queens_solver.py` -> Base Class Name: `QueensSolver`

While not strictly required, the convention is to append a suffix (`Game`, `App`, `Utility`) to the base name for clarity. The loader will find the class with or without the suffix.

**Examples:**
* File: `dot_dodger.py` -> Class: **`DotDodgerGame`**
* File: `queens_solver.py` -> Class: **`QueensSolverApp`**

### 4. Class Requirements

For a module to be loaded correctly, its main class **must** adhere to the following rules:

* It **must** be a subclass of `tkinter.Frame`.
* The `__init__` method **must** accept `master` and `show_main_menu_callback` as its first two arguments after `self`. The `show_main_menu_callback` is a function provided by the main app that, when called, will take the user back to the category page they came from.
    ```python
    import tkinter as tk

    class MyCoolGame(tk.Frame):
        def __init__(self, master, show_main_menu_callback):
            super().__init__(master)
            # Your code here
            # ...
            # Example of using the callback in a "Back" button
            back_button = tk.Button(self, text="Back to Games", command=show_main_menu_callback)
            back_button.pack()
    ```
* If the module has a persistent loop (like an animation using `after()`), it **must** have a `stop_game_loop()` method. This method is called automatically by the main application when the user navigates away, preventing orphaned loops from running in the background.

### 5. Handling External Assets

All external assets (images, sounds, data files, etc.) should be placed in the top-level `assets/` directory. To access these assets from within a module in a reliable way, you should programmatically find the project's root directory.

Here is the recommended approach to load an asset from within any module:
```python
# In your module file
from pathlib import Path

# Inside your class __init__ or another method:
try:
    current_path = Path(__file__).resolve()
    project_root = None
    # Search upwards for the directory containing main.py
    for parent in current_path.parents:
        if (parent / "main.py").exists():
            project_root = parent
            break
    
    if not project_root:
        raise FileNotFoundError("Project root not found.")

    asset_file = project_root / "assets" / "your_asset_file.txt"
    with open(asset_file, "r") as f:
        # ... load your asset
        pass

except FileNotFoundError:
    print("Asset not found, using fallback.")
    # ... handle the missing asset
```

---
## Running the Application
---

You can run the suite in two ways:

1.  **Directly via Python (All Platforms):**
    Execute the main file from the project's root directory.
    ```bash
    python main.py
    ```

2.  **Using the Launcher (Windows):**
    Double-click the `launcher.bat` file. This script will automatically try to find the best Python environment to run the application, prioritizing a local virtual environment, then a system-wide Python installation.