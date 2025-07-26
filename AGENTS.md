# AGENTS.md

This file provides guidance to AI agents working with the **Agent Task Management System** repository.

## Project Overview
- **Purpose**: Provides a CLI-driven, file-based task management system for agent workflows. Tasks are stored as Markdown files with YAML frontmatter and organized in emoji directories (backlog, todo, in-progress, done, blocked).
- **Key Features**: automated task lifecycle management, dependency tracking, validation, analytics, templates, and migration utilities. Designed to integrate with larger Python projects via the `src/task_management` package.
- **Technologies**: Python 3, Click CLI, PyYAML for parsing, JSON logging utilities.

## Development Commands
- **Install dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
- **Run CLI help**:
  ```bash
  python -m src.task_management.cli --help
  ```
- **List tasks**:
  ```bash
  python -m src.task_management.cli list
  ```
- **Validate task integrity** (primary testing mechanism):
  ```bash
  python -m src.task_management.cli validate
  ```
- **Recommended workflow**: run validation before committing changes to ensure
  data integrity.

- **Run analytics**:
  ```bash
  python -m src.task_management.cli analytics
  ```
- There are no automated test suites in this repo, but `pytest` is listed as a dependency for future development.

## Architecture
- **src/task_management/** – Core package
  - `task_manager.py` – task lifecycle and storage
  - `task_validator.py` – validation rules
  - `task_analytics.py` – analytics engine
  - `task_templates.py` – workflow templates
  - `advanced_transitions.py` – advanced state change logic
  - `cli.py` – command-line interface
  - `migrate_tasks.py` – data migration helpers
- **tasks/** – task files organized by status using emoji folder names
  - `📦 backlog/`
  - `🚫 blocked/`
  - `📋 todo/`
  - `🔄 in-progress/`
  - `✅ done/`
- **docs/** – detailed documentation including system architecture and GitHub integration specification
- **utils/** – logging utilities

## Dependencies
Key packages listed in `requirements.txt`:
- `pyyaml` – YAML parsing
- `click` – CLI framework
- `pytest` – testing framework (no tests included yet)
- `python-json-logger` – structured logging support

## Development Notes
- Code follows standard Python conventions; modules export `TaskManager`, `TaskValidator`, `TaskAnalytics`, and `TaskTemplates` via `src/task_management/__init__.py`.
- Logging expects integration with a host project's logging setup (`utils/logger.py`).
- Tasks are plain Markdown files with YAML metadata – easy to edit and track in Git.
- Validation and auto-transition commands keep task states consistent; see `docs/task-management-system.md` for schema details.

## Current Status
- Implementation marked **complete** as of July 23, 2025.
- Repository contains 98+ task files managed across 28+ agents.
- Known areas for improvement include agent name normalization and workload balancing.
