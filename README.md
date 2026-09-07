*This activity has been created as part of the 42 curriculum by mabu-are, aabtah.*

# A-Maze-ing

A Python maze generator that creates both perfect mazes (single path) and playable Pac-Man-style boards with multiple routes. The program reads a configuration file, generates a maze according to the specified parameters, and outputs both a hexadecimal-encoded file and a visual representation.

## Description

This project implements a maze generator in Python 3.10+ with the following features:
- **Two generation modes**: Perfect mazes (single unique path) or playable boards (loops, no dead-ends, Pac-Man style)
- **"42" pattern**: A visible "42" drawn by fully closed cells embedded in the maze
- **Reproducible generation**: Seed-based randomness for consistent results
- **Visual representation**: Terminal ASCII rendering with interactive controls
- **Reusable module**: The core `MazeGenerator` class is packaged as a standalone installable module (`mazegen-*`)

The maze generator uses a modified recursive backtracker algorithm for perfect mazes and an enhanced version with selective wall removal for playable boards.

## Instructions

### Prerequisites
- Python 3.10 or later
- `make` utility
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone git@github.com:Qlb-Alaasad/my_maze.git
cd my_maze

# Install dependencies
make install
```

### Running the Program

```bash
# Run with default configuration
make run

# Or run directly with a custom config file
python3 a_maze_ing.py config.txt
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make install` | Install activity dependencies |
| `make run` | Execute the main script |
| `make debug` | Run with Python debugger (pdb) |
| `make clean` | Remove temporary files and caches |
| `make lint` | Run flake8 and mypy static analysis |
| `make lint-strict` | Run strict linting checks |

### Configuration File

The configuration file uses `KEY=VALUE` pairs (one per line). Lines starting with `#` are comments.

**Mandatory keys:**

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width (number of cells) | `WIDTH=20` |
| `HEIGHT` | Maze height (number of cells) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Is the maze perfect? | `PERFECT=True` |

**Optional keys:**

| Key | Description | Example |
|-----|-------------|---------|
| `SEED` | Random seed for reproducibility | `SEED=42` |
| `ALGORITHM` | Generation algorithm | `ALGORITHM=recursive_backtracker` |
| `DISPLAY_MODE` | Visual display mode | `DISPLAY_MODE=terminal` |

### Output File Format

The output file contains:
1. Hexadecimal digits representing each cell's walls (one per cell, row by row)
2. An empty line separator
3. Entry coordinates
4. Exit coordinates
5. Shortest valid path using N, E, S, W directions

**Wall encoding (4 bits):**
- Bit 0 (LSB): North
- Bit 1: East
- Bit 2: South
- Bit 3: West
- `1` = wall closed, `0` = wall open

### Interactive Controls (Terminal)

When running the visual display:
- `1` or `r` — Re-generate a new maze
- `2` or `p` — Show/Hide the shortest path
- `3` or `c` — Change wall colors
- `4` or `q` — Quit

## Technical Choices

### Algorithm
We chose the **Recursive Backtracker** (modified depth-first search) as our primary algorithm because:
- It produces long, winding corridors with fewer dead-ends compared to other algorithms
- It's straightforward to implement and extend for both perfect and non-perfect modes
- It naturally supports the "42" pattern embedding by reserving cells during generation
- For playable boards, we add selective wall removal to create loops while maintaining connectivity

### Reusable Module

The core maze generation logic is encapsulated in the `MazeGenerator` class, available as a standalone installable package.

**Installation:**
```bash
pip install mazegen-*.whl
# or
pip install mazegen-*.tar.gz
```

**Usage:**
```python
from mazegen import MazeGenerator

# Instantiate with parameters
generator = MazeGenerator(width=20, height=15, seed=42)

# Generate a perfect maze
maze = generator.generate_perfect(entry=(0, 0), exit=(19, 14))

# Or generate a playable board
maze = generator.generate_playable(entry=(0, 0), exit=(19, 14))

# Access the maze structure
walls = maze.get_walls(x, y)  # Returns dict: {'N': bool, 'E': bool, 'S': bool, 'W': bool}
path = maze.find_shortest_path()  # Returns list of directions

# Save to file
maze.save_to_file("output.txt", entry=(0, 0), exit=(19, 14))
```

The module is located at the root of the repository as `mazegen-*.tar.gz` or `mazegen-*.whl`, with build files included.

## Team and Project Management

### Roles
- **mabu-are**: Project architecture, configuration parsing and validation (Pydantic `MazeConfig`, `dict_validate`), file I/O (`file_processor`), "42" pattern generation (`make_42_pattern`, `draw_block`), maze solving (`solve_maze`, `get_neighbors`), main program flow (`main`), and terminal interactive controls.
- **aabtah**: Core maze generation algorithm (`Cell` class, `create_maze`, recursive backtracker with seed support), imperfect maze mode (`Imperfect` — selective wall removal for loops and playable boards), terminal ASCII visual rendering (`drawing_a_maze` with color support and path highlighting), and output file formatting (`output_file` with hexadecimal encoding).

### Planning
1. **Week 1**: Research maze algorithms, design architecture, implement core generator (aabtah)
2. **Week 2**: Implement configuration parsing, validation, "42" pattern, and solving logic (mabu-are)
3. **Week 3**: Integration, terminal rendering, output formatting, testing with maze_analyzer.py, bug fixes, packaging, documentation (both)

### What Worked Well
- Modular design allowed parallel development — aabtah worked on the generator core while mabu-are built the I/O, validation, and solving layers
- Early testing with `maze_analyzer.py` caught coherence issues quickly
- Using `make` for automation streamlined the workflow
- The class-based architecture made the module naturally reusable for future projects

### What Could Be Improved
- More extensive unit testing coverage (only basic edge cases were tested)
- Better handling of edge cases in very small mazes (e.g., 5x5 or smaller)
- Performance optimization for very large mazes (>100x100)
- Adding support for multiple generation algorithms (Prim's, Kruskal's) as configurable options

### Tools Used
- **Git & GitHub**: Version control and collaboration
- **VS Code**: Primary IDE for both team members
- **pytest**: Unit testing framework
- **flake8 & mypy**: Code quality and type checking
- **make**: Build automation
- **venv**: Virtual environment isolation
- **GitHub Issues**: Task tracking and bug reporting

## AI Usage

AI tools were used for the following tasks:
- **Code structure suggestions**: Initial class design and module organization
- **Algorithm research**: Comparing maze generation algorithms and their properties
- **Documentation drafting**: README structure and docstring templates
- **Debugging assistance**: Identifying type hint issues and mypy errors

All AI-generated content was reviewed, tested, and fully understood before integration. No AI-generated code was used without manual verification and adaptation to our specific requirements.

## Resources

- [Maze Generation Algorithms - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker Algorithm - Jamis Buck](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
- [Python 3.10 Documentation](https://docs.python.org/3.10/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [flake8 Documentation](https://flake8.pycqa.org/en/latest/)
- [mypy Documentation](https://mypy.readthedocs.io/en/stable/)
- `maze_analyzer.py` - Provided analysis script for validation

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

The maze generator module (`mazegen-*`) is explicitly licensed for reuse and distribution in later projects as stated in the LICENSE.md file.
