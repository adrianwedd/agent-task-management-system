import pytest
from click.testing import CliRunner
from src.task_management.cli import main

@pytest.fixture
def runner():
    return CliRunner()

def test_create_task_cli(runner):
    result = runner.invoke(main, ['create', '--id', 'cli-test-task', '--title', 'CLI Test Task', '--agent', 'TESTER'])
    assert result.exit_code == 0
    assert "Created task: cli-test-task" in result.output

def test_list_tasks_cli(runner):
    result = runner.invoke(main, ['list'])
    assert result.exit_code == 0
    assert "cli-test-task" in result.output

def test_update_task_status_cli(runner):
    runner.invoke(main, ['create', '--id', 'cli-test-task-2', '--title', 'CLI Test Task 2', '--agent', 'TESTER'])
    result = runner.invoke(main, ['status', 'cli-test-task-2', 'in_progress'])
    assert result.exit_code == 0
    assert "Updated task cli-test-task-2 to in_progress" in result.output
