import pytest
import tempfile
import shutil
from click.testing import CliRunner
from src.task_management.cli import cli, TaskCLI

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def temp_tasks_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_create_task_cli(runner, temp_tasks_dir):
    result = runner.invoke(cli, ['create', '--id', 'cli-test-task', '--title', 'CLI Test Task', '--agent', 'TESTER', '--tasks-root', temp_tasks_dir])
    if result.exit_code != 0:
        print(f"Create command failed: {result.output}")
        if result.exception:
            import traceback
            print(f"Exception: {result.exception}")
            print(f"Traceback: {''.join(traceback.format_exception(type(result.exception), result.exception, result.exception.__traceback__))}")
    assert result.exit_code == 0
    assert "Created task: cli-test-task" in result.output

def test_list_tasks_cli(runner, temp_tasks_dir):
    # First create a task to ensure there's something to list
    runner.invoke(cli, ['create', '--id', 'test-list-task', '--title', 'Test List Task', '--agent', 'TESTER', '--tasks-root', temp_tasks_dir])
    
    result = runner.invoke(cli, ['list', '--tasks-root', temp_tasks_dir])
    if result.exit_code != 0:
        print(f"List command failed with exit code {result.exit_code}")
        print(f"Output: {result.output}")
        if result.exception:
            print(f"Exception: {result.exception}")
            import traceback
            print(f"Traceback: {''.join(traceback.format_exception(type(result.exception), result.exception, result.exception.__traceback__))}")
    assert result.exit_code == 0

def test_update_task_status_cli(runner, temp_tasks_dir):
    runner.invoke(cli, ['create', '--id', 'cli-test-task-2', '--title', 'CLI Test Task 2', '--agent', 'TESTER', '--tasks-root', temp_tasks_dir])
    result = runner.invoke(cli, ['status', 'cli-test-task-2', 'in_progress', '--tasks-root', temp_tasks_dir])
    if result.exit_code != 0:
        print(f"Status command failed: {result.output}")
        if result.exception:
            import traceback
            print(f"Exception: {result.exception}")
            print(f"Traceback: {''.join(traceback.format_exception(type(result.exception), result.exception, result.exception.__traceback__))}")
    assert result.exit_code == 0
    assert "Updated task cli-test-task-2 to in_progress" in result.output
