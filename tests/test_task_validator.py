import pytest
from src.task_management.task_validator import TaskValidator
from src.task_management.task_manager import Task, TaskStatus, TaskPriority
from datetime import datetime, timedelta, timezone

@pytest.fixture
def mock_task_manager():
    class MockTaskManager:
        def __init__(self):
            self.tasks_cache = {}
        
        def get_task(self, task_id):
            # Simplified mock: return a dummy task if needed for validation logic
            if task_id == "blocked-task":
                return Task(id="blocked-task", title="Blocked Task", description="", agent="NONE", status=TaskStatus.TODO, priority=TaskPriority.MEDIUM, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
            return None

    return MockTaskManager()

@pytest.fixture
def validator(mock_task_manager):
    return TaskValidator(mock_task_manager)

def test_validate_task_valid(validator):
    task = Task(
        id="test-valid-task",
        title="Valid Task",
        description="This is a valid task.",
        agent="CODEFORGE",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        due_date=(datetime.now(timezone.utc) + timedelta(days=7)),
        dependencies=[],
        notes="",
        estimated_hours=1.0,
        actual_hours=0.0,
        assignee="test_user",
        tags=["test"]
    )
    warnings, errors = validator.validate_task(task)
    assert not warnings
    assert not errors

def test_validate_task_missing_critical_due_date(validator):
    task = Task(
        id="test-critical-no-due-date",
        title="Critical Task No Due Date",
        description="A critical task without a due date.",
        agent="CODEFORGE",
        status=TaskStatus.TODO,
        priority=TaskPriority.CRITICAL,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        due_date=None,
        dependencies=[],
        notes="",
        estimated_hours=1.0,
        actual_hours=0.0,
        assignee="test_user",
        tags=["test"]
    )
    warnings, errors = validator.validate_task(task)
    assert not warnings
    assert any("critical priority must have a due_date" in error for error in errors)

def test_validate_task_future_timestamps(validator):
    future_time = (datetime.now(timezone.utc) + timedelta(days=1))
    task = Task(
        id="test-future-timestamps",
        title="Future Timestamps",
        description="Task with future created_at and updated_at.",
        agent="CODEFORGE",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_at=future_time,
        updated_at=future_time,
        due_date=None,
        dependencies=[],
        notes="",
        estimated_hours=1.0,
        actual_hours=0.0,
        assignee="test_user",
        tags=["test"]
    )
    warnings, errors = validator.validate_task(task)
    assert any("created_at cannot be in the future" in warning for warning in warnings)
    assert any("updated_at cannot be in the future" in warning.message for warning in warnings)
    assert not errors

def test_validate_task_invalid_status_transition(validator):
    task = Task(
        id="test-invalid-transition",
        title="Invalid Transition",
        description="Task with invalid status transition.",
        agent="CODEFORGE",
        status=TaskStatus.COMPLETE,
        priority=TaskPriority.MEDIUM,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        due_date=None,
        dependencies=["blocked-task"],
        notes="",
        estimated_hours=1.0,
        actual_hours=0.0,
        assignee="test_user",
        tags=["test"]
    )
    warnings, errors = validator.validate_task(task)
    assert any("unresolved dependencies" in error.message for error in errors)
    assert not warnings

def test_validate_task_agent_assignment(validator):
    task = Task(
        id="test-agent-assignment",
        title="Implement Feature",
        description="Implement a new feature.",
        agent="DOCUMENTER",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        due_date=None,
        dependencies=[],
        notes="",
        estimated_hours=1.0,
        actual_hours=0.0,
        assignee="test_user",
        tags=["test"]
    )
    warnings, errors = validator.validate_task(task)
    assert any("Unknown agent 'DOCUMENTER'. Suggested migration: 'DEVELOPER' (auto-fixable)" in warning.message for warning in warnings)
    assert not errors
