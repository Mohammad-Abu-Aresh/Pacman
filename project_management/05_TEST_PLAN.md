
# Acceptance Test Plan

## 1. Purpose

This document defines acceptance test scenarios for the Pac-Man project.

The purpose is to verify that the game behaves according to its requirements and that its main systems work together correctly.

A test scenario is not considered passed merely because it is documented. Its actual result must be recorded after execution.

## 2. Test Status Definitions

| Status | Meaning |
|---|---|
| Not Run | The test has not yet been executed. |
| Passed | The test was executed and the expected result was observed. |
| Failed | The test was executed and the expected result was not observed. |
| Blocked | The test could not be executed because of an external dependency or another issue. |
| To Be Confirmed | The test scenario or expected behavior requires verification against the implementation. |

## 3. Acceptance Test Cases

All tests below begin with the status **Not Run** unless actual execution evidence is added.

| Test ID | Feature | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| T01 | Startup | Launch the game using the documented command. | The application starts without an unexpected crash. | Not recorded. | Not Run |
| T02 | Configuration | Start the game with the provided configuration file. | Supported settings are loaded. | Not recorded. | Not Run |
| T03 | Configuration | Remove a configuration value. | A safe default is used where supported. | Not recorded. | Not Run |
| T04 | Configuration | Provide an invalid configuration value. | The value is rejected or replaced safely without an unexpected crash. | Not recorded. | Not Run |
| T05 | Configuration | Include an unknown configuration key. | Unknown keys do not break execution. | Not recorded. | Not Run |
| T06 | Maze Integration | Generate a maze using the assigned package. | A maze is produced and adapted to the game. | Not recorded. | Not Run |
| T07 | Maze Integration | Verify the generator parameters. | The required `PERFECT=False` setting is used. | Not recorded. | Not Run |
| T08 | Player Movement | Move the player in available directions. | The player moves through valid paths. | Not recorded. | Not Run |
| T09 | Collision | Attempt to move through a wall. | The player cannot pass through blocked cells. | Not recorded. | Not Run |
| T10 | Monster AI | Run gameplay with all monster types. | Each monster follows its intended target-selection behavior. | Not recorded. | Not Run |
| T11 | Monster States | Collect a super-pacgum. | Monsters enter the frightened state for the configured duration. | Not recorded. | Not Run |
| T12 | Monster States | Eat a frightened monster. | The monster enters its dead/return behavior and respawns as designed. | Not recorded. | Not Run |
| T13 | Pacgums | Collect a regular pacgum. | The pacgum is removed and the score increases. | Not recorded. | Not Run |
| T14 | Super-pacgums | Collect a super-pacgum. | The power-up effect is activated. | Not recorded. | Not Run |
| T15 | Scoring | Eat a monster while it is frightened. | The score increases according to the scoring rules. | Not recorded. | Not Run |
| T16 | Lives | Lose a life after a monster collision. | The remaining lives are updated correctly. | Not recorded. | Not Run |
| T17 | Game Over | Lose all available lives. | The game-over flow is displayed. | Not recorded. | Not Run |
| T18 | Level Progression | Collect all required pacgums. | The game progresses according to its level rules. | Not recorded. | Not Run |
| T19 | Timer | Allow the level timer to expire. | The configured time-limit behavior is applied. | Not recorded. | Not Run |
| T20 | Highscores | Save a valid player name and score. | The score is stored persistently. | Not recorded. | Not Run |
| T21 | Highscores | Restart the application after saving a score. | Previously saved scores can be loaded. | Not recorded. | Not Run |
| T22 | Highscores | Provide malformed highscore JSON data. | The game handles the invalid data safely. | Not recorded. | Not Run |
| T23 | Highscores | Enter a name longer than the allowed length. | The input is rejected or handled according to the validation rules. | Not recorded. | Not Run |
| T24 | Main Menu | Open the main menu and navigate its options. | Available menu actions work as intended. | Not recorded. | Not Run |
| T25 | Pause | Pause and resume gameplay. | Gameplay state is preserved and resumed correctly. | Not recorded. | Not Run |
| T26 | Cheat Mode | Activate the review cheat mode. | The documented cheat functionality works as implemented. | Not recorded. | To Be Confirmed |
| T27 | Build | Execute the provided build script. | The packaging process completes successfully. | Not recorded. | Not Run |
| T28 | Packaging | Launch the packaged application. | The packaged game starts and its required resources are available. | Not recorded. | Not Run |

## 4. Existing Automated Tests

The repository contains a `tests/` directory.

The exact test coverage and execution results must be determined by inspecting the test files and running the project's configured test command.

Do not treat the existence of test files as proof that all acceptance scenarios pass.

## 5. Bug Recording

When a test fails, record:

- Test ID.
- Steps to reproduce.
- Expected behavior.
- Actual behavior.
- Relevant component.
- Root cause, if identified.
- Applied fix.
- Retest result.

No historical bug or fix is claimed in this document without supporting evidence.

## 6. Acceptance Criteria

The project is ready for acceptance when:

- The game launches using the documented procedure.
- Core gameplay works as intended.
- The assigned maze generator is integrated correctly.
- Configuration and highscore handling are reliable.
- Required screens and gameplay states work.
- The build and packaging process is verified.
- Failed tests are investigated and resolved or documented.

## 7. Test Execution Record

Execution date: Not recorded.

Test environment: To be documented.

Python version: Refer to `pyproject.toml`.

Test command: Refer to the configured test framework and project instructions.
