class EpicManager:
    def __init__(self, task_manager):
        self.task_manager = task_manager

    def create_epic(self, epic_id, title, description):
        print(f"Creating epic {epic_id}: {title}")

    def add_task_to_epic(self, task_id, epic_id):
        print(f"Adding task {task_id} to epic {epic_id}")

    def get_epic_tasks(self, epic_id):
        return []
