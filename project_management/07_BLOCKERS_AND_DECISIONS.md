
# Blockers and Technical Decisions

## 1. Purpose

This document records important technical decisions, challenges, blockers, and lessons learned during the development of the Pac-Man project.

The available project documentation describes several architectural decisions. Historical incident records and detailed blocker logs were not available when this document was prepared.

## 2. Technical Challenges

The following areas represent important technical challenges associated with the project.

### External Maze Generator Integration

The game depends on an externally assigned A-Maze-ing package.

The integration must adapt to the package's interface without modifying the external implementation.

This separation is important because the package may be reinstalled during peer review.

### Grid-Based Movement

The game uses a grid-based environment.

Movement must account for valid cells, blocked paths, and the timing of entity movement.

Player and monster movement must remain consistent with the maze structure.

### Monster AI

The game contains multiple monster personalities that share movement infrastructure but select targets differently.

Keeping target-selection logic separate from movement logic makes the system easier to extend and maintain.

### Configuration Reliability

The game accepts external configuration values.

Invalid or missing values must be handled safely so that configuration mistakes do not unnecessarily terminate the application.

### Persistent Highscores

Highscore data must survive application restarts.

The system must account for missing files, invalid JSON, and invalid player input.

## 3. Architectural Decisions

### Decision 1: Modular Game Architecture

**Decision:** Separate the game into modules with distinct responsibilities.

**Reason:** A modular structure improves readability, maintainability, and the ability to work on individual systems.

**Expected benefit:** Changes to one system should have limited impact on unrelated components.

### Decision 2: External Maze Generator Adapter

**Decision:** Use an integration layer for the assigned A-Maze-ing package.

**Reason:** The subject requires using the external package without modifying it.

**Expected benefit:** The game can adapt to the package interface while keeping the external implementation independent.

### Decision 3: Shared Monster Movement Infrastructure

**Decision:** Use shared movement and pathfinding infrastructure for the monsters while keeping their target-selection strategies separate.

**Reason:** Monsters share the same maze and movement constraints but need different behaviors.

**Expected benefit:** Less duplicated movement logic and easier maintenance.

### Decision 4: JSON Configuration

**Decision:** Use a JSON configuration file for gameplay settings.

**Reason:** JSON is simple to read and edit, and Python provides built-in support for JSON parsing.

**Expected benefit:** Gameplay parameters can be adjusted without changing the source code.

### Decision 5: JSON Highscore Storage

**Decision:** Use local JSON storage for highscores.

**Reason:** The game requires lightweight persistent storage and does not need a database server.

**Expected benefit:** Scores can be saved and loaded using a simple, portable format.

## 4. Bugs and Resolutions

No verified historical bug-resolution log was available in the existing documentation.

When a bug is identified, add a record using this format:

| Field | Description |
|---|---|
| Issue | Short description of the bug. |
| Component | Affected subsystem or file. |
| Reproduction | Steps required to reproduce the problem. |
| Root Cause | Identified reason for the failure. |
| Resolution | Change applied to resolve it. |
| Verification | Test or procedure used to confirm the fix. |

Only add completed bug records after confirming the issue and its resolution.

## 5. Blockers

No formal historical blocker or conflict records were available in the existing documentation.

Potential areas that may block development or review include:

- External package compatibility.
- Dependency installation.
- Configuration or storage errors.
- Gameplay integration issues.
- Packaging failures.
- Missing test coverage.

These are potential blockers, not claims that such incidents occurred.

## 6. Decision-Making and Issue Handling

Technical decisions should be evaluated using the following criteria:

1. Compliance with the subject.
2. Correctness and reliability.
3. Compatibility with the existing implementation.
4. Simplicity and maintainability.
5. Ease of testing and explanation during peer review.

When an issue occurs, the team should identify its source, discuss possible solutions, implement a focused change, and verify the result.

## 7. Lessons Learned

The project highlights several important software engineering practices:

- Keep modules focused on clear responsibilities.
- Isolate external dependencies behind integration layers.
- Validate external configuration and stored data.
- Separate AI decision-making from entity movement.
- Test interactions between systems, not only individual components.
- Keep technical documentation consistent with the actual implementation.
- Record test results and decisions while development is in progress.
- Ensure every team member can explain the architecture and implementation.

## 8. Future Updates

This document should be updated whenever:

- A significant technical decision is made.
- A blocking issue is discovered or resolved.
- A major bug is fixed.
- A design is changed.
- An important lesson is learned during testing or peer review.
