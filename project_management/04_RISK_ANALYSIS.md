
# Risk Analysis

## 1. Purpose

This document identifies technical and project risks that could affect the development, reliability, packaging, or review of the Pac-Man project.

The risks below are potential risks relevant to the project's architecture. Their inclusion does not mean that every risk occurred.

## 2. Risk Assessment Method

Each risk is evaluated using:

- **Probability:** Likelihood of the risk occurring.
- **Impact:** Potential effect on the project if it occurs.
- **Mitigation:** Actions that can reduce the likelihood or consequences.

Ratings use Low, Medium, and High.

## 3. Risk Register

| ID | Risk | Probability | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R01 | External maze generator integration failure. | Medium | High | Keep the integration isolated in an adapter, validate the generator interface, and test generated mazes. | To Be Monitored |
| R02 | Dependency or Python environment incompatibility. | Medium | High | Use the declared project dependencies and test installation in a clean environment. | To Be Monitored |
| R03 | Missing or invalid configuration values. | Medium | Medium | Validate configuration values and use safe defaults. | Addressed by documented design; verify tests. |
| R04 | Corrupted or missing highscore file. | Medium | Medium | Handle file and JSON errors safely and initialize valid storage when necessary. | Addressed by documented design; verify tests. |
| R05 | Monster pathfinding or movement errors. | Medium | High | Test movement around walls, intersections, and changing monster states. | To Be Monitored |
| R06 | Performance issues during gameplay. | Low | Medium | Profile expensive operations and avoid unnecessary repeated calculations. | To Be Monitored |
| R07 | Packaging or build failure. | Medium | High | Test the build process and verify required resources and dependencies are included. | To Be Monitored |
| R08 | Insufficient testing before peer review. | Medium | High | Maintain an acceptance test plan and record test results. | To Be Monitored |
| R09 | Inconsistency between documentation and implementation. | Medium | Medium | Review documentation against the source code before submission. | Being Addressed |

## 4. Mitigation Strategy

### External Package Integration

The external maze generator is a critical dependency. Its interface and expected parameters must be verified. The integration layer should handle errors without crashing the game.

### Environment Compatibility

The project should be installed and tested using the Python version and dependencies declared by its configuration files.

### Configuration Reliability

Configuration values should be validated before being used by gameplay systems. Missing or invalid values should fall back to safe defaults where supported.

### Highscore Reliability

The highscore system should handle missing files, malformed JSON, invalid player names, and invalid scores without preventing the game from starting.

### Gameplay Reliability

Player movement, monster movement, collisions, pathfinding, and state transitions should be tested in different maze situations.

### Packaging Reliability

The build process should be tested independently from the development environment to identify missing dependencies or resources.

## 5. Risk Review

Risks should be reviewed when:

- A new dependency is introduced.
- A major subsystem is integrated.
- A significant bug is discovered.
- Packaging behavior changes.
- The project approaches peer review.

The current risk statuses should be updated when actual test or development evidence becomes available.
