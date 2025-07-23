import pytest
from src.task_management.task_manager import TaskManager, TaskStatus, TaskPriority

@pytest.fixture
def task_manager():
    # Use a temporary directory for tasks to avoid polluting the actual tasks directory
    # This is a simplified fixture, in a real scenario, you'd use tempfile.TemporaryDirectory
    # and clean up properly.
    if not os.path.exists("temp_tasks"): # Simplified temp dir
        os.makedirs("temp_tasks")
    tm = TaskManager(tasks_root="temp_tasks")
    yield tm
    # Cleanup (simplified)
    import shutil
    if os.path.exists("temp_tasks"): # Simplified cleanup
        shutil.rmtree("temp_tasks")

def test_create_task(task_manager):
    task = task_manager.create_task(
        id="test-task-1",
        title="Test Task 1",
        description="A test task.",
        agent="TEST_AGENT",
        priority=TaskPriority.HIGH,
        estimated_hours=1.0,
        tags=["test", "example"]
    )
    assert task is not None
    assert task.id == "test-task-1"
    assert task.status == TaskStatus.TODO

def test_update_task_status(task_manager):
    task = task_manager.create_task(
        id="test-task-2",
        title="Test Task 2",
        description="Another test task.",
        agent="TEST_AGENT",
        priority=TaskPriority.MEDIUM
    )
    success = task_manager.update_task_status("test-task-2", TaskStatus.IN_PROGRESS)
    assert success
    updated_task = task_manager.get_task("test-task-2")
    assert updated_task.status == TaskStatus.IN_PROGRESS
