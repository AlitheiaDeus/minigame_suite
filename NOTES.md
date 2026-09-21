# Project To-Do and Ideas - 02 Sept 2025

A list of bugs, planned improvements, and new module ideas for the Game & Program Suite.

## 🐞 BUGS & IMMEDIATE FIXES

* **[ ] dot_racer:** The survival game mode is rendering a blank screen. Needs investigation.
* **[ ] infinite_jumper:** Review the platform generation logic. Some platforms may be appearing in impossible-to-reach locations.
* **[ ] Classic Radial:** The right-click-to-skip functionality does not work when the cursor is over the central canvas/grid area. It should be universal.

## 🎨 UI/UX TWEAKS

* **[ ] Classic Radial:** The contrast between the normal and "lit" states of the color segments is not strong enough for good peripheral vision gameplay. Need to select brighter, more distinct highlight colors.
* **[ ] Classic Radial:** Remove the artificial pause after the player successfully completes a sequence. The game should immediately proceed to showing the next sequence to improve flow.
* **[ ] chess_attack_solver:** Update the grid buttons to use the standard `relief='raised'` and `bd=2` style to match the aesthetic of the newer modules.

## ✨ NEW MODULES & FEATURES

* **[ ] Maze Solver Variants:**
    * **[ ] Version 1 (Wall-as-Edge):** Classic maze where thin walls exist *between* grid cells.
    * **[ ] Version 2 (Wall-as-Cell):** Maze where impassable walls occupy entire cells in the grid.
    * **[ ] Feature Additions:** Consider adding special rules to the maze solvers, such as portals that link two cells or edges that loop around to the opposite side (torus-like).

## 💡 GEMINI IDEAS

Here are a few ideas for new modules that would fit well within your existing categories:

* **f_games/arcade/Typing Master:** A game where words fall from the top of the screen and the player must type them correctly before they reach the bottom. Speed and difficulty can increase over time. This would make good use of the `assets/` folder for word lists.
* **f_puzzles/logic/Mastermind:** The classic code-breaking game. The player tries to guess a secret color code, and the game gives feedback on how many are the correct color and in the right position.
* **f_utilities/generators/Password Generator:** A simple but useful utility. It could have options for length, character types (uppercase, lowercase, numbers, symbols), and an easy "copy to clipboard" button.