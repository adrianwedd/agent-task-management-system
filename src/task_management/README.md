# Agent Task Management System

A comprehensive task management system designed for the any project's AI agent ecosystem. Provides automated task lifecycle management, dependency tracking, validation, analytics, and templates.

## Features

### ✅ Core Task Management
- **Automated Status Transitions**: Tasks automatically transition between states based on dependencies
- **Dependency Tracking**: Full dependency chain validation and automatic dependency resolution
- **Agent Assignment**: Tasks automatically routed to appropriate agents based on capabilities
- **Priority Management**: Four-tier priority system with automatic escalation
- **Due Date Tracking**: Automatic overdue detection and alerting

### 📊 Analytics & Reporting
- **Performance Metrics**: Agent performance tracking and completion rate analysis
- **Velocity Trends**: Historical velocity analysis and future projections
- **Bottleneck Detection**: Automatic identification of workflow bottlenecks
- **Dependency Analysis**: Critical path analysis and dependency risk assessment
- **Predictive Insights**: ML-powered predictions for completion times and resource needs

### ✅ Validation & Quality Assurance
- **Comprehensive Validation**: Multi-level validation for task integrity and consistency
- **Business Rule Enforcement**: Automatic enforcement of project-specific business rules
- **System-wide Consistency**: Cross-task validation for dependency integrity
- **Agent Workload Balancing**: Automatic detection of overloaded agents

### 📝 Templates & Automation
- **Task Templates**: Pre-defined templates for common agent workflows
- **Automated Task Creation**: Template-based task generation with variable substitution
- **Workflow Patterns**: Standardized workflows for research, development, compliance, and testing
- **Checklist Management**: Built-in checklists for consistent task execution

### 🔧 Integration & Tools
- **CLI Interface**: Comprehensive command-line interface for all operations
- **File-based Storage**: Human-readable YAML/Markdown task files
- **Export/Import**: JSON export for integration with external systems
- **Real-time Monitoring**: Live system monitoring and alerting

## Quick Start

### Installation

```bash
# Navigate to the project root
cd /path/to/repo # Replace with your project's root directory

# Install dependencies
pip install -r requirements.txt

# Initialize the task management system
python -m src.task_management.cli init

# Create a new task
python -m src.task_management.cli create \
  --id "implement-feature-x" \
  --title "Implement Feature X" \
  --description "Implement the new feature X with tests" \
  --agent "AGENT_NAME" \
  --priority "high"


# The task management system is part of the main project
# No additional installation required
```

### Basic Usage

```bash
# Create a new task
python -m src.task_management.cli create \
  --id "implement-feature-x" \
  --title "Implement Feature X" \
  --description "Implement the new feature X with tests" \
  --agent "AGENT_NAME" \
  --priority "high"

# List all tasks
python -m src.task_management.cli list

# Update task status
python -m src.task_management.cli status implement-feature-x in_progress

# Show task details
python -m src.task_management.cli show implement-feature-x

# View analytics
python -m src.task_management.cli analytics --type overview
```

### Using Templates

```bash
# List available templates
python -m src.task_management.cli templates

# Create task from template
python -m src.task_management.cli create \
  --template "feature-implementation" \
  --id "new-dashboard" \
  --title "Implement Analytics Dashboard" \
  --agent "AGENT_NAME" \
  --template-vars "feature_name=analytics-dashboard" "technologies=React,D3.js"
```

## System Architecture

### Directory Structure

```
src/task_management/
├── __init__.py                 # Package initialization
├── task_manager.py            # Core task management logic
├── task_validator.py          # Task validation system
├── task_analytics.py          # Analytics and reporting
├── task_templates.py          # Template management
├── cli.py                     # Command-line interface
└── README.md                  # This file

tasks/
├── backlog/                   # Pending and blocked tasks
├── todo/                      # Ready and in-progress tasks
├── done/                      # Completed tasks
└── README.md                  # Task system documentation
```

### Task Lifecycle

```
┌─────────┐    ┌─────────┐    ┌──────┐    ┌─────────────┐    ┌──────────┐
│ PENDING │───▶│ BLOCKED │───▶│ TODO │───▶│ IN_PROGRESS │───▶│ COMPLETE │
└─────────┘    └─────────┘    └──────┘    └─────────────┘    └──────────┘
     │              │            │               │                │
     └──────────────┼────────────┼───────────────┼────────────────┘
                    │            │               │
                    ▼            ▼               ▼
                ┌───────────────────────────────────┐
                │           CANCELLED               │
                └───────────────────────────────────┘
```

### Agent Integration

The system integrates with your main agent ecosystem:

- **ARCHAIOS_PRIME**: Meta-coordination and strategic oversight
- **CONSENSUS_ENGINE**: Decision arbitration and conflict resolution  
- **CODEFORGE**: Code development and implementation tasks
- **TESTCRAFTERPRO**: Testing and quality assurance
- **COMPLIANCE_SENTINEL**: Regulatory compliance monitoring
- **SECSENTINEL**: Security assessment and monitoring

## Task Schema

Each task follows a standardized YAML schema:

```yaml
---
id: unique-task-identifier
title: Human-readable task title
description: |
  Detailed task description with objectives and requirements
agent: ASSIGNED_AGENT
status: todo
priority: high
created_at: 2025-07-23T10:30:00
updated_at: 2025-07-23T12:45:00
due_date: 2025-07-30T17:00:00
estimated_hours: 8.0
actual_hours: 6.5
dependencies:
  - prerequisite-task-1
  - prerequisite-task-2
tags:
  - development
  - feature
notes: |
  Additional notes and status updates
---

## Extended Description

Additional markdown content can be included here for complex tasks.

### Checklist
- [ ] Requirement analysis
- [ ] Implementation
- [ ] Testing
- [ ] Documentation
```

## CLI Reference

### Task Management Commands

```bash
# Create new task
python -m src.task_management.cli create \
  --id TASK_ID \
  --title "Task Title" \
  --description "Description" \
  --agent AGENT_NAME \
  --priority {low|medium|high|critical} \
  [--estimated-hours HOURS] \
  [--due-date ISO_DATE] \
  [--tags tag1,tag2] \
  [--dependencies dep1,dep2]

# Update task status
python -m src.task_management.cli status TASK_ID {pending|blocked|todo|in_progress|complete|cancelled} \
  [--notes "Status change notes"]

# List tasks
python -m src.task_management.cli list \
  [--agent AGENT_NAME] \
  [--status STATUS] \
  [--priority PRIORITY] \
  [--tag TAG] \
  [--overdue] \
  [--sort-by {priority|created|updated}] \
  [--format {list|table|json}]

# Show task details
python -m src.task_management.cli show TASK_ID [--validate]

# Validate tasks
python -m src.task_management.cli validate [--task-id TASK_ID]

# Auto-transition ready tasks
python -m src.task_management.cli auto-transition
```

### Analytics Commands

```bash
# Show analytics
python -m src.task_management.cli analytics \
  [--type {overview|agents|velocity|bottlenecks|dependencies}]

# Export data
python -m src.task_management.cli export {tasks|analytics} OUTPUT_FILE
```

### Template Commands

```bash
# List templates
python -m src.task_management.cli templates \
  [--agent AGENT_NAME] \
  [--tags tag1,tag2]

# Create from template
python -m src.task_management.cli create \
  --template TEMPLATE_ID \
  --id TASK_ID \
  --title "Task Title" \
  --template-vars "key1=value1" "key2=value2"
```

## API Reference

### TaskManager Class

```python
from src.task_management import TaskManager

# Initialize
manager = TaskManager("tasks")

# Create task
task = manager.create_task(
    id="new-task",
    title="New Task", 
    description="Task description",
    agent="CODEFORGE",
    priority=TaskPriority.HIGH
)

# Update status
manager.update_task_status("new-task", TaskStatus.IN_PROGRESS)

# Get tasks
tasks = manager.get_tasks_by_agent("CODEFORGE")
overdue = manager.get_overdue_tasks()

# Statistics
stats = manager.get_task_statistics()
```

### TaskValidator Class

```python
from src.task_management import TaskValidator

validator = TaskValidator()

# Validate single task
errors = validator.validate_task(task)

# Validate entire system
system_errors = validator.validate_task_system(tasks_dict)

# Generate report
report = validator.generate_validation_report(errors)
```

### TaskAnalytics Class

```python
from src.task_management import TaskAnalytics

analytics = TaskAnalytics(tasks_dict)

# Get performance metrics
agent_perf = analytics.get_agent_performance()
velocity = analytics.get_velocity_trends(weeks=12)
bottlenecks = analytics.get_bottleneck_analysis()

# Export analytics
analytics.export_analytics("analytics.json")
```

### TaskTemplates Class

```python
from src.task_management import TaskTemplates

templates = TaskTemplates()

# List templates
available = templates.list_templates(agent="CODEFORGE")

# Create from template
task = templates.create_task_from_template(
    "feature-implementation",
    task_id="new-feature",
    feature_name="user-dashboard",
    technologies="React, Node.js"
)
```

## Configuration

### Environment Variables

```bash
# Task system configuration
export AGENT_TASKS_ROOT="tasks"
export AGENT_TASK_VALIDATION_LEVEL="strict"
export AGENT_ANALYTICS_CACHE_TTL="3600"

# Agent configuration
export AGENT_AGENT_TIMEOUT="30"
export AGENT_MAX_AGENT_TASKS="10"
```

### Task System Settings

Create `tasks/config.yaml` for system-wide settings:

```yaml
# Task lifecycle settings
auto_transition_enabled: true
dependency_validation: strict
overdue_alert_threshold: 24  # hours

# Agent settings
max_tasks_per_agent: 10
agent_timeout_seconds: 30
workload_balancing: enabled

# Analytics settings
analytics_retention_days: 90
velocity_calculation_weeks: 12
bottleneck_threshold_percent: 10

# Validation settings
validation_level: strict  # strict, moderate, lenient
custom_validation_rules: []
```

## Integration Examples

### With GitHub Actions

```yaml
name: Task Management
on:
  push:
    paths: ['tasks/**']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Tasks
        run: python -m src.task_management.cli validate
      - name: Generate Analytics
        run: python -m src.task_management.cli export analytics analytics.json
```

### With Agent System

```python
# In agent code
from src.task_management import TaskManager

class CygneatAgent:
    def __init__(self):
        self.task_manager = TaskManager()
    
    def complete_task(self, task_id: str):
        # Mark task complete
        self.task_manager.update_task_status(
            task_id, 
            TaskStatus.COMPLETE,
            f"Completed by {self.agent_name}"
        )
        
        # Auto-transition dependent tasks
        self.task_manager.auto_transition_ready_tasks()
```

### With Dashboard

```javascript
// Fetch analytics for dashboard
fetch('/api/task-analytics')
  .then(response => response.json())
  .then(data => {
    updateDashboard(data);
  });
```

## Best Practices

### Task Creation
1. **Use Templates**: Leverage templates for consistent task structure
2. **Clear Descriptions**: Include objectives, deliverables, and acceptance criteria
3. **Proper Dependencies**: Map all prerequisite tasks
4. **Realistic Estimates**: Provide accurate time estimates
5. **Appropriate Priority**: Use priority levels consistently

### Task Management
1. **Regular Updates**: Update task status and notes frequently
2. **Dependency Management**: Keep dependencies current and validated
3. **Agent Workload**: Monitor agent workload distribution
4. **Deadline Management**: Set realistic due dates and monitor overdue tasks

### System Maintenance
1. **Regular Validation**: Run system validation weekly
2. **Analytics Review**: Review analytics monthly for insights
3. **Template Updates**: Keep templates current with evolving workflows
4. **Archive Completed**: Archive old completed tasks quarterly

## Troubleshooting

### Common Issues

**Task Not Transitioning**
- Check dependencies are completed
- Verify valid status transition
- Run validation to identify issues

**Agent Overloaded**
- Review agent workload analytics
- Redistribute tasks if needed
- Consider agent capability expansion

**Validation Errors**
- Review validation report details
- Fix data integrity issues
- Update task schema if needed

**Performance Issues**
- Check task cache size
- Optimize dependency graphs
- Review analytics cache settings

### Debug Commands

```bash
# Validate specific task
python -m src.task_management.cli validate --task-id TASK_ID

# Show bottleneck analysis
python -m src.task_management.cli analytics --type bottlenecks

# Export for debugging
python -m src.task_management.cli export tasks debug_tasks.json
```

## Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest src/task_management/tests/

# Run type checking
mypy src/task_management/

# Run linting
flake8 src/task_management/
```

### Adding New Features

1. **Templates**: Add new templates in `task_templates.py`
2. **Validation Rules**: Extend validation in `task_validator.py`
3. **Analytics**: Add new metrics in `task_analytics.py`
4. **CLI Commands**: Extend CLI in `cli.py`

### Testing

```bash
# Run all tests
pytest src/task_management/tests/

# Run specific test category
pytest src/task_management/tests/test_task_manager.py
pytest src/task_management/tests/test_analytics.py
pytest src/task_management/tests/test_validator.py
```

## License

This agent task management system is subject to the project's license terms.

## Support

For issues and questions:
1. Check this documentation
2. Review troubleshooting section  
3. Create issue in project repository
4. Contact project maintainers

---

**Last Updated**: 2025-07-23  
**Version**: 1.0.0  
**Maintainer**: adrian@adrianwedd.com