class NestedGrouping:
    def __init__(self, task_manager):
        self.task_manager = task_manager

    def group_tasks_by_status(self):
        grouped_tasks = {}
        for status in self.task_manager.TaskStatus:
            grouped_tasks[status.value] = self.task_manager.get_tasks_by_status(status)
        return grouped_tasks

    def display_grouped_tasks(self):
        grouped = self.group_tasks_by_status()
        for status, tasks in grouped.items():
            print(f"\n--- {status.upper()} ---")
            if tasks:
                for task in tasks:
                    print(f"  - {task.title} ({task.id})")
            else:
                print("  No tasks.")

