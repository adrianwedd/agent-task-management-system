# AGENT.md
This file provides guidance to agents when working with code in this repository.

## Project Overview
This project contains the command-line interface (CLI) and core logic for an Agent Task Management System. It's designed to be integrated into Python projects utilizing agents for task and workflow management. Tasks are stored as Markdown files with YAML frontmatter, supporting various states (backlog, todo, in_progress, done, cancelled), validation, and analytics.

**Key Technologies:**
- Python
- PyYAML (for YAML parsing)
- Click (for CLI)
- Pytest (for testing, though no dedicated test files are present in this repo, only a task to create them)

## Development Commands
- **Install dependencies:** `pip install -r requirements.txt`
- **Run CLI:** `python -m src.task_management.cli --help` (replace `src.task_management.cli` with the actual path to `cli.py` within your project)
- **List all tasks:** `python -m src.task_management.cli list`
- **View task analytics:** `python -m src.task_management.cli analytics`
- **Validate task integrity:** `python -m src.task_management.cli validate`
- **Create a new task:**
  ```bash
  python -m src.task_management.cli create \
    --id "implement-dashboard" \
    --title "Implement Analytics Dashboard" \
    --description "Create interactive dashboard for task metrics" \
    --agent "CODEFORGE" \
    --priority "high"
  ```
- **Update task status:** `python -m src.task_management.cli status implement-dashboard in_progress`
- **Create from template:**
  ```bash
  python -m src.task_management.cli create \
    --template "feature-implementation" \
    --id "new-feature" \
    --title "Implement New Feature" \
    --template-vars "feature_name=user-dashboard" "technologies=React,Node.js"
  ```
- **List available templates:** `python -m src.task_management.cli templates`

## Architecture
The core logic resides in `src/task_management/`.
- `task_manager.py`: Core task management logic, handles lifecycle, transitions, and dependency tracking.
- `task_validator.py`: Validation system for task integrity.
- `task_analytics.py`: Generates insights and reports from tasks.
- `task_templates.py`: Manages task templates for consistent creation.
- `cli.py`: Command-line interface for interacting with the system.
- `migrate_tasks.py`: Utilities for data migration.

**Task Storage Structure:**
Tasks are stored as Markdown files with YAML frontmatter in the `tasks/` directory, organized by status:
- `tasks/backlog/`
- `tasks/todo/`
- `tasks/done/`
- `tasks/in_progress/`
- `tasks/repeatable/`

## Dependencies
- `pyyaml`: For parsing YAML frontmatter in task files.
- `click`: For building the command-line interface.
- `pytest`: For testing (development dependency).

## Development Notes
- **Code Style:** Follows standard Python conventions.
- **Testing Strategy:** While `pytest` is a dependency, dedicated test files are not present in this repository. The `docs/task-management-system.md` mentions "Comprehensive with integration tests" and lists `test_integration.py`, `test_simple.py`, `test_standalone.py` as part of the architecture, but these files are not found in the provided directory listing. A task `create-comprehensive-test-suite.md` exists in `tasks/todo`.
- **Task Structure:** Tasks are Markdown files with YAML frontmatter. Refer to `docs/task-management-system.md` for the detailed schema.
- **Integration:** Designed to be integrated into other Python projects. Example integration with GitHub Actions and agent code is provided in `docs/task-management-system.md`.

## Task Management Rules
When creating or modifying tasks, adhere to the following rules:

-   **Dependencies and Status**: If a task has unresolved dependencies, its status should be `BLOCKED` or `PENDING`, not `TODO`.
-   **Critical Tasks Due Dates**: All tasks with `critical` priority must have a `due_date` specified.
-   **Agent Workload**: Be mindful of agent workload. If an agent (e.g., CODEFORGE) is overloaded, consider reassigning tasks to other available agents.
-   **Agent Assignment**: Ensure the assigned `agent` aligns with the task's `title` and `description`. For example, tasks involving 'implement', 'develop', 'code', or 'build' should ideally be assigned to `CODEFORGE`.
-   **Timestamp Consistency**: `created_at` and `updated_at` timestamps should accurately reflect the task's history and not be in the future.

## File Modification Strategy

- **Prioritize `read_file`:** Before any `replace` operation, *always* use `read_file` to get the exact, current content of the target file. This ensures the `old_string` provided to `replace` is an exact match.
- **Precision with `replace`:**
    - For single-line changes, ensure the `old_string` includes surrounding context (e.g., the entire line, or a few characters before and after the target text) to make it unique.
    - For multi-line changes, the `old_string` *must* include all lines, including whitespace and indentation, that are to be replaced. Provide at least 3 lines of context before and after the target text.
- **Handling Syntax Errors/Corruption:**
    - If a file becomes syntactically invalid or corrupted, the immediate action should be to **revert to a known good state** using `git restore <file_path>`.
    - **Do NOT attempt to fix syntax errors iteratively with `replace` on a corrupted file.**
    - Once reverted, re-evaluate the change. For substantial changes or when `replace` proves too difficult/risky, consider using `write_file` with the *entire* correct content of the file. This ensures a clean slate.
- **Post-Modification Verification:** After *any* file modification, immediately run relevant linters, formatters, and tests (if applicable) to catch errors early and confirm the change's correctness.

## Current Status
The system is described as "✅ COMPLETE" as of July 23, 2025, with 98+ tasks managed across 28+ agents.
- **Known Issues/Limitations:**
    - Some agent name normalization is needed (e.g., BuildFlow vs BUILDFLOW).
    - Dependency ID standardization is recommended.
    - Workload balancing for agents might be needed.
- **Areas for Improvement (Future Enhancements):**
    - Web Dashboard
    - Real-time Updates
    - Advanced Analytics (ML-based prediction)
    - External Integrations (Jira, GitHub Issues)

```