
# Project Overview

## 1. Project Objective

The objective of this project is to develop a complete and playable Pac-Man game in Python as part of the 42 curriculum.

The implementation combines object-oriented programming, modular architecture, procedural maze generation through an externally assigned package, game AI, graphical rendering, configuration management, and persistent highscore storage.

The game uses a Minecraft-inspired visual theme to provide a distinctive presentation while preserving the core Pac-Man gameplay loop.

## 2. Project Scope

The project includes the following areas:

- A playable Pac-Man game.
- A graphical user interface with menus and gameplay screens.
- Integration with the assigned A-Maze-ing maze generator.
- Player movement and collision handling.
- Monster movement and AI behaviors.
- Pacgum and super-pacgum mechanics.
- Scoring, lives, timers, and level progression.
- Configurable gameplay settings.
- Persistent highscore storage.
- Error handling for invalid configuration and storage data.
- Project packaging and documentation.

## 3. Main Deliverables

| Deliverable | Description |
|---|---|
| Game implementation | Python source code for the playable game. |
| Maze integration | Adapter for the assigned external A-Maze-ing package. |
| Configuration | JSON configuration file and its loading logic. |
| Highscore system | Persistent leaderboard storage. |
| Graphical interface | Menus, gameplay view, HUD, and game screens. |
| Tests | Test files and test scenarios for project functionality. |
| Packaging | Build and packaging configuration. |
| Documentation | README and project management documents. |

## 4. Technical Approach

The project follows a modular, object-oriented design.

Responsibilities are separated into different components so that gameplay rules, entities, AI, rendering, and supporting systems can be developed and maintained independently.

The assigned maze generator is integrated through an adapter rather than modified directly.

The game uses JSON for configuration and persistent highscore storage.

## 5. Main Technologies and Tools

| Technology / Tool | Purpose |
|---|---|
| Python | Main programming language. |
| External A-Maze-ing package | Procedural maze generation. |
| JSON | Configuration and highscore storage. |
| Make | Project installation, execution, and maintenance commands. |
| Git | Source control and collaboration. |
| Pytest or configured test framework | Testing, according to project configuration. |
| Packaging tools | Building the distributable game. |

The exact dependency versions are maintained in the project's dependency configuration.

## 6. Major Design Decisions

### Modular Architecture

The application separates the game engine, gameplay systems, entities, AI, and rendering. This makes responsibilities clearer and reduces unnecessary coupling.

### External Maze Generator

The assigned A-Maze-ing package is used as required by the activity. An integration layer adapts its interface to the game's needs.

### Shared Monster Movement System

Monster behaviors use a shared movement and pathfinding approach while selecting targets according to different personalities.

### JSON Configuration

JSON provides a simple way to customize gameplay parameters without changing the source code.

### JSON Highscores

A JSON file provides lightweight persistent storage without requiring a separate database service.

## 7. Project Constraints

The project must satisfy the requirements of the 42 subject, including:

- Using the assigned external maze generator.
- Keeping the external package unmodified.
- Providing a playable game.
- Supporting configuration through a file.
- Handling invalid configuration and storage data safely.
- Implementing persistent highscores.
- Providing a cheat mode for review purposes.
- Supplying packaging and documentation.
- Maintaining evidence of project management.

## 8. Definition of Completion

The project is considered ready for review when:

- The game can be installed and launched using the documented process.
- The required gameplay features are implemented.
- The external maze generator is integrated correctly.
- Configuration and highscore handling are robust.
- The project can be packaged using the provided build configuration.
- Relevant tests have been executed and their results recorded.
- The README explains how to install, run, and understand the project.
- Project management documentation is available in this directory.

The completion of individual requirements should be verified against the source code and test evidence.
