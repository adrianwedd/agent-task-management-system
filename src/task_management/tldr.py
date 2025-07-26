class TldrGenerator:
    def __init__(self, task_manager):
        self.task_manager = task_manager

    def generate_tldr(self):
        # Simplified TL;DR: just list top 3 TODO tasks
        todo_tasks = self.task_manager.get_tasks_by_status(self.task_manager.TaskStatus.TODO)
        if not todo_tasks:
            return "No tasks in TODO status."

        tldr = "TL;DR - Next Tasks:\n"
        for i, task in enumerate(todo_tasks[:3]):
            tldr += f"{i+1}. {task.title} ({task.id})\n"
        return tldr
