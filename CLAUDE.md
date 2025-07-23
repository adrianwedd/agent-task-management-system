# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Agent Task Management System - a comprehensive, file-based task management solution designed for AI agent ecosystems. The system provides automated task lifecycle management, dependency tracking, validation, analytics, and templates for managing workflows across multiple AI agents.

## Development Commands

### Core Commands
```bash
# Run the CLI (main interface for all operations)
python -m src.task_management.cli --help

# Install dependencies
pip install -r requirements.txt

# List all tasks
python -m src.task_management.cli list

# Create a new task
python -m src.task_management.cli create --id "task-id" --title "Task Title" --description "Description" --agent "AGENT_NAME" --priority "high"

# Update task status
python -m src.task_management.cli status TASK_ID STATUS

# Show analytics
python -m src.task_management.cli analytics --type overview

# Validate task system integrity
python -m src.task_management.cli validate

# Auto-transition ready tasks
python -m src.task_management.cli auto-transition
```

### Template Operations
```bash
# List available templates
python -m src.task_management.cli templates

# Create task from template
python -m src.task_management.cli create --template "template-name" --id "task-id" --title "Title" --template-vars "key=value"
```

### Testing
```bash
# Run validation (primary testing mechanism)
python -m src.task_management.cli validate

# Test specific task
python -m src.task_management.cli validate --task-id TASK_ID
```

## Architecture

### Core Components
- **TaskManager** (`task_manager.py`): Core task lifecycle management, CRUD operations, automated status transitions
- **TaskValidator** (`task_validator.py`): Multi-level validation system for task integrity and business rules
- **TaskAnalytics** (`task_analytics.py`): Performance metrics, bottleneck detection, predictive analytics
- **TaskTemplates** (`task_templates.py`): Template system with 8 predefined workflows for different agent types
- **CLI** (`cli.py`): Complete command-line interface for all operations

### File Structure
```
src/task_management/          # Core system modules
tasks/                        # Task storage (file-based)
├── backlog/                  # Pending and blocked tasks
├── todo/                     # Ready and in-progress tasks  
├── done/                     # Completed tasks
└── in_progress/              # Currently active tasks
docs/                         # System documentation
```

### Task Schema
Tasks are stored as Markdown files with YAML frontmatter containing:
- `id`: Unique identifier
- `title`: Human-readable title
- `description`: Detailed task description
- `agent`: Assigned agent name
- `status`: Current status (pending/blocked/todo/in_progress/complete/cancelled)
- `priority`: Priority level (low/medium/high/critical)
- `dependencies`: Array of prerequisite task IDs
- `created_at`/`updated_at`: Timestamps
- `due_date`: Optional deadline
- `tags`: Classification tags

### Agent Integration
The system manages tasks for 28+ specialized agents including:
- **CODEFORGE**: Code development and implementation
- **TESTCRAFTERPRO**: Testing and quality assurance  
- **SECSENTINEL**: Security assessment
- **COMPLIANCE_SENTINEL**: Regulatory compliance
- **CONSENSUS_ENGINE**: Decision arbitration
- **ARCHAIOS_PRIME**: Meta-coordination

### Dependencies
- `pyyaml`: YAML processing for task frontmatter
- `click`: CLI framework
- `pytest`: Testing framework (referenced but no test files present)

## Development Notes

### Task Status Lifecycle
```
PENDING → BLOCKED → TODO → IN_PROGRESS → COMPLETE
    ↓        ↓        ↓         ↓           ↓
    └────────┴────────┴─────────┴───────────┴─→ CANCELLED
```

### Key Design Patterns
- **File-based storage**: Human-readable, version control friendly
- **Atomic operations**: Safe concurrent access
- **Dependency-driven transitions**: Tasks auto-advance when dependencies complete
- **Agent workload balancing**: Monitors and alerts on agent overload
- **Template-driven creation**: Standardized workflows for consistency

### Import Structure
The main module exports: `TaskManager`, `TaskValidator`, `TaskAnalytics`, `TaskTemplates`

### Logger Dependency
The code imports `from utils.logger import logger` but no utils module exists in the codebase. This suggests the system expects to be integrated into a larger project with existing logging infrastructure.

### Migration Support
The system includes `migrate_tasks.py` for data migration, indicating it can upgrade from previous task formats.

## Current Status
- **Implementation Status**: ✅ COMPLETE (as of July 23, 2025)
- **Task Count**: 98+ tasks successfully managed
- **Agent Coverage**: 28+ specialized agents
- **Lines of Code**: 4,261+ lines across all modules

## Integration Notes
- Designed to be embedded in larger projects as `src/task_management/`
- Expects parent project to provide logging utilities
- No database required - pure file-based storage
- Git-friendly task format for version control
- CLI provides complete functionality without additional interfaces required