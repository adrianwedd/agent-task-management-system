import os
import yaml
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

from .task_manager import TaskManager, TaskStatus

class ChangelogGenerator:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    def generate_changelog(self) -> str:
        changelog_entries = defaultdict(lambda: defaultdict(list))
        
        completed_tasks = self.task_manager.get_tasks_by_status(TaskStatus.COMPLETE)
        
        for task in completed_tasks:
            if task.updated_at:
                date_str = task.updated_at.strftime("%Y-%m-%d")
                # Categorize by tags or a default category
                category = "Uncategorized"
                if "feature" in task.tags:
                    category = "Features"
                elif "bug-fix" in task.tags or "fixes" in task.tags:
                    category = "Bug Fixes"
                elif "improvement" in task.tags:
                    category = "Improvements"
                
                changelog_entries[date_str][category].append(f"- {task.title} ({task.id})")

        changelog_content = "# Changelog\n\n"
        for date_str in sorted(changelog_entries.keys(), reverse=True):
            changelog_content += f"## {date_str}\n\n"
            for category in ["Features", "Improvements", "Bug Fixes", "Uncategorized"]:
                if changelog_entries[date_str][category]:
                    changelog_content += f"### {category}\n\n"
                    for entry in changelog_entries[date_str][category]:
                        changelog_content += f"{entry}\n"
                    changelog_content += "\n"
        return changelog_content

