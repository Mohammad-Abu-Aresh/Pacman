This activity has been created as part of the 42 curriculum by mabu-are, aabtah.
Pac-Man (A-Maze-ing Integration - Minecraft Style)

A Python implementation of the classic Pac-Man arcade game built with a modular, object-oriented architecture, featuring procedural maze generation via an external "A-Maze-ing" package, a persistent highscore system, and a unique Minecraft-inspired visual theme and block style.
Description

This project transforms the maze generator concept into a fully playable Pac-Man game with a custom visual identity. Key features include:

    Minecraft-Themed Visuals: A blocky, textured aesthetic rendering walls, corridors, and the iconic "42" pattern using a Minecraft-inspired style instead of traditional retro arcade assets.

    External Maze Generator Integration: Automatically loads and adapts to an external A-Maze-ing package (PERFECT=False) to build complex, loop-filled corridors without dead-ends.

    Multi-Level Progression: Features at least 10 progressive levels with timed challenges, starting from a fixed seed (42) and moving to randomized layouts.

    Dynamic Entities & Scoring: Complete gameplay loop including Pac-Man movement, autonomous ghosts with chase/flee behaviors, pacgums, super-pacgums (power pellets) in the corners, and an editable ghost scoring mechanism.

    Robust Configuration & Cheat Mode: JSON-with-comments configuration parser with fault-tolerant safe defaults, plus an integrated cheat mode designed to streamline peer reviews.

    Persistent Highscores: Automatically loads and saves the top 10 player scores into a persistent JSON storage file.

Instructions
Prerequisites

    Python 3.10 or later

    make utility

    Virtual environment (venv recommended)

    The assigned external A-Maze-ing package installed in your environment

Installation
Bash

# Clone the repository
git clone <repository_url>
cd pac-man-project

# Install dependencies and the package
make install

Running the Program

The game must be launched from the command line by passing a JSON configuration file as its sole argument:
Bash

# Run with default configuration using make
make run

# Or run directly with a custom configuration file
python3 pac-man.py config.json

Available Make Commands
Command	Description
make install	Install activity dependencies and modules
make run	Execute the main Pac-Man script
make debug	Run the main script with Python's built-in debugger (pdb)
make clean	Remove temporary files, caches (__pycache__, .mypy_cache)
make lint	Run flake8 and mypy static code analysis
make lint-strict	Run strict linting checks
Configuration

The game uses a JSON configuration file supporting comments starting with #.
Configuration Keys
Key	Description	Default Example
highscore_filename	Path to persistent highscore storage	highscore.json
lives	Initial lives for Pac-Man	3
pacgum	Score points per regular pacgum	10
points_per_super_pacgum	Score points per super-pacgum	50
points_per_ghost	Score points per eaten ghost	200
seed	Initial random seed for level 1	42
level_max_time	Time limit per level in seconds	90
Faulty Configuration Handling

If any configuration value is invalid or missing, the program clamps the parameter to safe defaults, outputs a clear log message without crashing, and continues execution smoothly without a traceback.
Maze Generation Integration

The game relies entirely on the externally provided A-Maze-ing package to build its levels:

    Non-Perfect Mazes: The loader forces the parameter PERFECT=False to strip dead-ends and introduce alternative corridors and loops required for arcade-style navigation.

    Fixed & Dynamic Seeds: Level 1 generates deterministically using a fixed seed (e.g., 42), whereas subsequent levels utilize randomized procedural generation.

    The "42" Pattern: Embedded closed block structures representing "42" are preserved in the center of the generated layout as structural obstacles.

Highscore System

The persistent highscore mechanism records and tracks top player achievements:

    Storage: Saved locally in a robust JSON file (highscore.json), safely managed against corruption or missing inputs.

    Validation: Restricts player names to a maximum of 10 alphanumeric characters and spaces.

    Leaderboard: Maintains and displays the top 10 highscores directly within the main menu interface.

Implementation & Architecture
General Software Architecture

The application is structured into clean, modular layers adhering strictly to object-oriented principles:

    Core Engine & Game Loop (main.py / game.py): Handles the core finite state machine transitioning smoothly between the Main Menu, Game View, Pause Menu, Game Over, and Victory screens.

    Graphics & Rendering Engine: Utilizes a lightweight graphical library equivalent to MLX, custom-tailored to render a Minecraft block-style interface (pixelated textures, block grid layouts, and cubic wall rendering).

    Entity Management (player.py, ghost.py): Manages autonomous ghost artificial intelligence (Blinky, Pinky, Inky, Clyde variants) with specialized chase/flee logic, collision detection, and respawn loops.

    Loader & Config Parser (config_loader.py): Reads, cleans comment lines, and validates JSON configurations using fault-tolerant parsing rules.

Project Management

A detailed overview of the project timeline, risk analysis, task breakdown, and testing logs is located in the dedicated project_management/ directory at the root of the repository.

    mabu-are: Config parsing architecture, JSON error handling, highscore implementation, UI state management, and project documentation.

    aabtah: Integration wrapper for the external A-Maze-ing package, entity physics, ghost movement AI, and the Minecraft-style graphical rendering engine.

Resources & AI Usage
References

    Pac-Man Game History & Design - Toru Iwatani

      

    Python 3.10 Documentation

    PEP 257 - Docstring Conventions

    External A-Maze-ing package documentation and interface specifications

AI Usage Description

In accordance with 42 curriculum guidelines, AI tools were used selectively to support development tasks:

    Boilerplate architecture patterns: Structuring the JSON parser fallback logic and initial UI loop designs.

    Algorithm refinement: Optimizing ghost distance-based chasing calculations and grid collision checks.

    Documentation drafting: Outlining README file headers and template sections.

All AI-generated code and structural suggestions were systematically reviewed, tested, debugged, and fully understood by both team members prior to integration.
License

This project is licensed under the MIT License - see the LICENSE.md file for details.