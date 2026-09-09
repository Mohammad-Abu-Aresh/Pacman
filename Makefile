# ==============================================================================
# A-Maze-ing Makefile
# 42 Curriculum Project
# Made by: mabu-are, aabtah
# ==============================================================================

# Variables
PYTHON       := python3
VENV         := .venv
VENV_PYTHON  := $(VENV)/bin/python
VENV_PIP     := $(VENV)/bin/pip

# Main Script Configuration
SCRIPT       := a_maze_ing.py
CONFIG       := config.txt

# Default Target
.PHONY: all
all: install

# ------------------------------------------------------------------------------
# Installation & Setup
# ------------------------------------------------------------------------------

# Create venv if not exists, upgrade pip, install poetry and all requirements
.PHONY: install
install: venv
	@echo "Installing dependencies using poetry in virtual environment..."
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install poetry
	@$(VENV_PYTHON) -m poetry install
	@echo ""
	@echo "========================================"
	@echo "Dependencies installed successfully!"
	@echo "To activate the virtual environment, run:"
	@echo "  source $(VENV)/bin/activate"
	@echo "========================================"

# Create virtual environment only
.PHONY: venv
venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment at $(VENV)..."; \
		$(PYTHON) -m venv $(VENV); \
		echo "Virtual environment created successfully."; \
	else \
		echo "Virtual environment already exists at $(VENV)."; \
	fi

# ------------------------------------------------------------------------------
# Execution & Debugging
# ------------------------------------------------------------------------------

# Run the main script (uses venv if exists)
.PHONY: run
run:
	@if [ -d "$(VENV)" ]; then \
		$(VENV_PYTHON) $(SCRIPT) $(CONFIG); \
	else \
		$(PYTHON) $(SCRIPT) $(CONFIG); \
	fi

# Run in debug mode with pdb (uses venv if exists)
.PHONY: debug
debug:
	@if [ -d "$(VENV)" ]; then \
		$(VENV_PYTHON) -m pdb $(SCRIPT) $(CONFIG); \
	else \
		$(PYTHON) -m pdb $(SCRIPT) $(CONFIG); \
	fi

# ------------------------------------------------------------------------------
# Code Quality & Testing
# ------------------------------------------------------------------------------

# Run linting with flake8 and mypy
.PHONY: lint
lint:
	@if [ -d "$(VENV)" ]; then \
		$(VENV_PYTHON) -m flake8 . --exclude=$(VENV); \
		$(VENV_PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
			--ignore-missing-imports --disallow-untyped-defs \
			--check-untyped-defs --exclude=$(VENV); \
	else \
		flake8 . --exclude=$(VENV); \
		mypy . --warn-return-any --warn-unused-ignores \
			--ignore-missing-imports --disallow-untyped-defs \
			--check-untyped-defs --exclude=$(VENV); \
	fi

# Run strict linting
.PHONY: lint-strict
lint-strict:
	@if [ -d "$(VENV)" ]; then \
		$(VENV_PYTHON) -m flake8 . --exclude=$(VENV); \
		$(VENV_PYTHON) -m mypy . --strict --exclude=$(VENV); \
	else \
		flake8 . --exclude=$(VENV); \
		mypy . --strict --exclude=$(VENV); \
	fi

# ------------------------------------------------------------------------------
# Build & Cleanup
# ------------------------------------------------------------------------------

# Build the reusable package
.PHONY: build
build:
	@if [ -d "$(VENV)" ]; then \
		$(VENV_PIP) install build; \
	fi
	@echo "Building package..."
	@if [ -f pyproject.toml ] || [ -f setup.py ]; then \
		if [ -d "$(VENV)" ]; then \
			$(VENV_PYTHON) -m build; \
		else \
			$(PYTHON) -m build; \
		fi \
	else \
		echo "Warning: pyproject.toml or setup.py not found. Skipping build."; \
	fi

# Clean temporary files, caches, and venv
.PHONY: clean
clean:
	@echo "Cleaning project..."
	@rm -rf __pycache__ .mypy_cache .pytest_cache
	@rm -rf build/ dist/ *.egg-info .venv poetry.lock
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@echo "Cleanup complete."

# ------------------------------------------------------------------------------
# Help Target
# ------------------------------------------------------------------------------

.PHONY: help
help:
	@echo "A-Maze-ing Makefile - Made by mabu-are, aabtah"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Create venv + install poetry dependencies"
	@echo "  run          - Execute the main script (uses venv if exists)"
	@echo "  debug        - Run with Python debugger (uses venv if exists)"
	@echo "  lint         - Run flake8 and mypy checks"
	@echo "  lint-strict  - Run strict mypy linting"
	@echo "  build        - Build the package (requires pyproject.toml)"
	@echo "  clean        - Remove caches, temporary files, and .venv"
	@echo "  venv         - Create virtual environment only"
	@echo "  help         - Show this help message
