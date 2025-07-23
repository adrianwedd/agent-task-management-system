import subprocess
import os

def run_cli_command(command):
    """Helper function to run CLI commands."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"\n--- Command: {command} ---")
    print(result.stdout)
    if result.stderr:
        print(f"--- Error ---\n{result.stderr}")
    return result

if __name__ == "__main__":
    print("Starting demo of Agent Task Management System CLI")

    # 1. Create a new task
    run_cli_command("python -m src.task_management.cli create --id demo-task-1 --title \"My First Demo Task\" --description \"This is a task created during the demo.\" --agent DEMO_AGENT --priority low")

    # 2. List all tasks
    run_cli_command("python -m src.task_management.cli list")

    # 3. Update task status
    run_cli_command("python -m src.task_management.cli status demo-task-1 in_progress")

    # 4. Add a note to the task
    run_cli_command("python -m src.task_management.cli add-note demo-task-1 \"Started working on this demo task.\"")

    # 5. Show task details
    run_cli_command("python -m src.task_management.cli show demo-task-1")

    # 6. Complete the task
    run_cli_command("python -m src.task_management.cli status demo-task-1 complete")

    print("\nDemo finished.")