---
id: implement-generic-task-update-cli
title: Implement Generic Task Update Command in CLI
description: 'Develop a new CLI command that allows users to update any field of an
  existing task

  by specifying the task ID and the field-value pairs. This will provide comprehensive

  control over task attributes directly from the command line.

  '
agent: CODEFORGE
status: todo
priority: high
created_at: '2025-07-23T04:14:55.830325+00:00'
updated_at: '2025-07-23T04:14:55.830325+00:00'
due_date: null
dependencies: []
tags:
- cli
- ux
- flexibility
- data-management
notes: 'The command should be able to update fields like title, description, agent,
  priority,

  estimated_hours, due_date, tags, and dependencies. It should handle different data
  types

  and provide clear feedback on successful updates or errors.

  '
estimated_hours: 3.0
actual_hours: null
assignee: null
---







## Task Description

Create a new `update` command for the CLI that enables users to modify any attribute of a task. This command should be flexible enough to accept multiple field updates in a single call.

## Acceptance Criteria

- [ ] A new `update` subcommand is added to `src/task_management/cli.py`.
- [ ] The `update` command accepts a `task_id` as a required argument.
- [ ] The `update` command accepts optional arguments for each updatable task field (e.g., `--title`, `--description`, `--agent`, `--priority`, `--due-date`, `--tags`, `--dependencies`).
- [ ] The command correctly parses and applies updates to the specified task fields.
- [ ] It handles various data types for fields (strings, numbers, dates, lists).
- [ ] Provides clear success/failure messages.
- [ ] Integrates with existing validation logic to prevent invalid updates.

## Implementation Steps

1.  **Define `update` subcommand**: Add a new parser for `update` in `main()` function of `cli.py`.
2.  **Add arguments for task fields**: For each field in the `Task` dataclass that can be updated, add a corresponding argument to the `update` subcommand.
3.  **Implement `update_task` method in `TaskCLI`**: Create a new method in `TaskCLI` that takes `task_id` and a dictionary of updates, then calls `self.task_manager.update_task` (or a similar method).
4.  **Implement `update_task` in `TaskManager`**: Add a method to `TaskManager` that loads the task, applies the updates, and saves the task. This method should handle partial updates and leverage existing validation.
5.  **Handle data type conversions**: Ensure that input from the CLI (which is string-based) is correctly converted to the appropriate Python types for the `Task` fields.
6.  **Test**: Write unit and integration tests for the new `update` command, covering various update scenarios and edge cases.

## Notes

-   Consider how to handle list fields like `tags` and `dependencies` (e.g., append, overwrite, remove specific items).
-   Leverage `argparse`'s features for argument parsing.
