This activity has been created as part of the 42 curriculum by mabu-are, aabtah.
# Pac-Man (A-Maze-ing Integration - Minecraft Style)

A Python implementation of the classic Pac-Man arcade game built with a modular,
object-oriented architecture, featuring procedural maze generation via an external
"A-Maze-ing" package, a persistent highscore system, and a unique Minecraft-inspired
visual theme and block style.

## Description

This project transforms the maze generator concept into a fully playable Pac-Man game
with a custom visual identity. Key features include:

```
Minecraft-Themed Visuals: A blocky, textured aesthetic rendering walls, corridors,
and the iconic "42" pattern using a Minecraft-inspired style instead of traditional
retro arcade assets.

External Maze Generator Integration: Automatically loads and adapts to an external
A-Maze-ing package (PERFECT=False) to build complex, loop-filled corridors without
dead-ends.

Multi-Level Progression: 10 progressive levels with timed challenges, starting from
a fixed seed (42) and moving to randomized layouts.

Dynamic Entities & Scoring: Complete gameplay loop including Pac-Man movement with
direction buffering, autonomous monsters with personality-driven chase/flee behaviors,
pacgums, super-pacgums (power pellets) in the corners, and an editable ghost
scoring mechanism.

Robust Configuration & Cheat Mode: JSON-with-comments configuration parser with
fault-tolerant safe defaults, plus an integrated cheat mode designed to streamline
peer reviews.

Persistent Highscores: Automatically loads and saves the top 10 player scores into
a persistent JSON storage file.
```

## Instructions

### Prerequisites

```
Python 3.10 or later
make utility
Virtual environment (venv recommended)
The assigned external A-Maze-ing package installed in your environment
```

### Installation

```bash
# Clone the repository
git clone <repository_url>
cd Pacman

# Install dependencies and the package
make install
```

### Running the Program

The game must be launched from the command line by passing a JSON configuration
file as its sole argument:

```bash
# Run with default configuration using make
make run

# Or run directly with a custom configuration file
python3 pac-man.py config.json
```

### Available Make Commands

| Command        | Description                                         |
| -------------- | --------------------------------------------------- |
| `make install` | Create venv and install all dependencies            |
| `make run`     | Execute the main Pac-Man script                     |
| `make debug`   | Run the main script with Python's built-in debugger |
| `make lint`    | Run flake8 and mypy static code analysis            |
| `make clean`   | Remove temporary files, caches and build artifacts  |
| `make help`    | Show all available targets                          |

## Configuration

The game uses a JSON configuration file supporting comments starting with `#`.

| Key                         | Description                                  | Default         |
| --------------------------- | -------------------------------------------- | --------------- |
| `highscore_filename`        | Path to persistent highscore storage         | highscores.json |
| `lives`                     | Initial lives for Pac-Man                    | 3               |
| `points_per_pacgum`         | Score points per regular pacgum              | 10              |
| `points_per_super_pacgum`   | Score points per super-pacgum                | 50              |
| `points_per_ghost`          | Score points per eaten ghost (per combo)     | 200             |
| `seed`                      | Initial random seed for level 1              | 42              |
| `level_max_time`            | Time limit per level in seconds              | 90              |

### Faulty Configuration Handling

If any configuration value is invalid or missing, the program clamps the parameter
to safe defaults, outputs a clear log message without crashing, and continues
execution smoothly without a traceback.

## Gameplay

### Core Loop

Navigate the procedurally generated maze, eat every pacgum to clear the level,
and avoid the monsters. Eating a super-pacgum (corner pellets) reverses the roles:
monsters enter frightened mode and become edible for a limited time, with each
consecutive kill multiplying the `points_per_ghost` score.

### Monster Personalities

The four monsters share a single movement engine (BFS pathfinding over the maze
grid) and differ only in how they choose their target cell — the classic
arcade design:

```
BabyZombie  (Chaser):  Targets Pac-Man's current cell directly. Relentless.
Skeleton    (Ambusher): Targets 4-5 cells ahead of Pac-Man's direction,
                        cutting him off at intersections.
Enderman    (Pincer):   Targets the midpoint between the chaser and Pac-Man,
                        closing the trap from the other side.
Witch       (Coward):   Wanders randomly, but switches to chase only when
                        far from Pac-Man and retreats when he gets close.
```

### Monster States

```
CHASE:    Normal hunt behavior, target depends on monster personality.
FRIGHTENED: Triggered by a super-pacgum. All monsters flee using the same
          engine with an inverted target (the farthest open cell). Edible.
DEAD:     After being eaten. The monster returns to its spawn point along a
          BFS path, then respawns in CHASE state.
```

Hardcore mode (configurable) empowers the monsters: the BabyZombie outruns the
player, the Skeleton shoots arrows down open corridors, the Enderman teleports
to random open cells, and the Witch slows the player with splash potions.

## Maze Generation Integration

The game relies entirely on the externally provided A-Maze-ing package to build
its levels:

```
Non-Perfect Mazes: The loader forces PERFECT=False to strip dead-ends and
introduce alternative corridors and loops required for arcade-style navigation.

Fixed & Dynamic Seeds: Level 1 generates deterministically using a fixed seed
(e.g., 42), whereas subsequent levels utilize randomized procedural generation.

The "42" Pattern: Embedded closed block structures representing "42" are
preserved in the center of the generated layout as structural obstacles.
```

## Highscore System

The persistent highscore mechanism records and tracks top player achievements:

```
Storage: Saved locally in a robust JSON file, safely managed against corruption
or missing inputs.

Validation: Restricts player names to a maximum of 10 alphanumeric characters
and spaces.

Leaderboard: Maintains and displays the top 10 highscores directly within the
main menu interface.
```

## Implementation & Architecture

### General Software Architecture

The application is structured into clean, modular layers adhering strictly to
object-oriented principles:

```
Core Engine & Game Loop (gameengine.py): Owns the window, the clock and the
finite state machine (Main Menu, Game, Pause, Game Over, Victory), delegating
all game rules to the systems below.

Game System (gameplay.py): Owns level lifecycle — maze loading, pacgum
placement, the level timer, scoring and lives. Contains no drawing code
beyond scene rendering.

Monster Controller (monster_controller.py): The brain of the hunt. Owns a
strategy registry (a dictionary mapping monster IDs to small target-selection
functions) and a single shared BFS pathfinder. Every tick it asks each
strategy for a target cell, resolves the next step, and drives the monster.
Monsters never query the controller — control flows one way.

Entity Layer (creature.py / monster.py): Monsters are deliberately "dumb":
position, speed, state and a move() that executes one validated step. No
pathfinding, no target logic. This keeps each personality to a few lines and
the engine shared.

Graphics & Screens (screens.py): UI layer — menus, buttons, HUD and the
Minecraft-style block rendering.
```

### Movement Model

All entities move in cells, not frames. Each entity accumulates
`speed * delta_time` and advances one grid cell when the accumulator crosses
1.0, which makes speed differences (player 100%, monsters 65%, hardcore 110%)
emerge naturally from a single constant.

## Project Management

A detailed overview of the project timeline, risk analysis, task breakdown, and
testing logs is located in the dedicated `project_management/` directory at the
root of the repository.

```
mabu-are: Config parsing architecture, JSON error handling, highscore
implementation, UI state management, and project documentation.

aabtah: Integration wrapper for the external A-Maze-ing package, entity
physics, monster movement AI, and the Minecraft-style graphical rendering engine.
```

## Resources & AI Usage

### References

```
Pac-Man Game History & Design - Toru Iwatani
Python 3.10 Documentation
PEP 257 - Docstring Conventions
External A-Maze-ing package documentation and interface specifications
```

### AI Usage Description

In accordance with 42 curriculum guidelines, AI tools were used selectively to
support development tasks:

```
Boilerplate architecture patterns: Structuring the JSON parser fallback logic
and initial UI loop designs.

Algorithm refinement: Optimizing monster distance-based chasing calculations,
grid collision checks, and the shared BFS pathfinding engine.

Documentation drafting: Outlining README file headers and template sections.
```

All AI-generated code and structural suggestions were systematically reviewed,
tested, debugged, and fully understood by both team members prior to integration.

## License

This project is licensed under the MIT License - see the LICENSE.md file for
details.
