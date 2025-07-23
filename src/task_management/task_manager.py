"""
Core Task Management System

Handles task lifecycle management, automated status transitions,
and dependency tracking for the agentic framework.
"""

import os
import yaml
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from utils.logger import logger, audit_logger, performance_logger, log_performance


class TaskStatus(Enum):
    PENDING = "pending"
    BLOCKED = "blocked"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """Represents a task in the system"""
    id: str
    title: str
    description: str
    agent: str
    status: TaskStatus
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    dependencies: List[str] = None
    notes: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    assignee: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for YAML serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        # Convert datetimes to ISO strings
        for field in ['created_at', 'updated_at', 'due_date']:
            if data[field]:
                data[field] = data[field].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        # Convert string enums back
        if 'status' in data:
            data['status'] = TaskStatus(data['status'])
        if 'priority' in data:
            data['priority'] = TaskPriority(data['priority'])
        
        # Convert ISO strings back to datetimes
        for field in ['created_at', 'updated_at', 'due_date']:
            if isinstance(data.get(field), str):
                dt_obj = datetime.fromisoformat(data[field])
                if dt_obj.tzinfo is None:
                    data[field] = dt_obj.replace(tzinfo=timezone.utc)
                else:
                    data[field] = dt_obj
        
        task = cls(**data)
        now = datetime.now(timezone.utc)

        # Ensure created_at is not in the future
        if task.created_at and task.created_at > now:
            task.created_at = now
        
        # Ensure updated_at is not in the future
        if task.updated_at and task.updated_at > now:
            task.updated_at = now
        
        # Ensure updated_at is not before created_at
        if task.created_at and task.updated_at and task.updated_at < task.created_at:
            task.updated_at = task.created_at
            
        return task


class TaskManager:
    """Main task management system"""
    
    def __init__(self, tasks_root: str = "tasks"):
        self.tasks_root = Path(tasks_root)
        self.tasks_cache: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # Directory structure mapping with emoji and logical ordering
        self.status_dirs = {
            TaskStatus.PENDING: self.tasks_root / "📦 backlog",
            TaskStatus.BLOCKED: self.tasks_root / "🚫 blocked", 
            TaskStatus.TODO: self.tasks_root / "📋 todo",
            TaskStatus.IN_PROGRESS: self.tasks_root / "🔄 in-progress",
            TaskStatus.COMPLETE: self.tasks_root / "✅ done",
            TaskStatus.CANCELLED: self.tasks_root / "❌ cancelled"
        }
        
        # Ensure directories exist
        for directory in self.status_dirs.values():
            directory.mkdir(parents=True, exist_ok=True)
        
        # Log system initialization with emoji
        if hasattr(logger, 'system_init'):
            logger.system_init(f"TaskManager initialized with tasks_root: {tasks_root}")
        else:
            logger.info(f"🚀 TaskManager initialized with tasks_root: {tasks_root}")
            
        if audit_logger:
            audit_logger.log_system_event(
                "SYSTEM_INIT", 
                "TaskManager initialized",
                {"tasks_root": str(tasks_root), "directories": list(str(d) for d in self.status_dirs.values())}
            )
        
        self.load_all_tasks()
    
    def load_all_tasks(self) -> None:
        """Load all tasks from the filesystem"""
        start_time = time.time()
        
        self.tasks_cache.clear()
        self.dependency_graph.clear()
        
        task_count = 0
        error_count = 0
        
        for status_dir in self.status_dirs.values():
            if status_dir.exists():
                for task_file in status_dir.glob("*.md"):
                    try:
                        task = self.load_task_from_file(task_file)
                        if task:
                            self.tasks_cache[task.id] = task
                            self.dependency_graph[task.id] = task.dependencies.copy()
                            task_count += 1
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error loading task from {task_file}: {e}")
        
        # Log performance metrics with emoji
        duration = time.time() - start_time
        if hasattr(logger, 'performance_log'):
            logger.performance_log(f"Loaded {task_count} tasks in {duration:.3f}s ({error_count} errors)")
        else:
            logger.info(f"⚡ Loaded {task_count} tasks in {duration:.3f}s ({error_count} errors)")
        
        if performance_logger:
            performance_logger.log_operation_timing(
                "load_all_tasks", 
                duration,
                {"task_count": task_count, "error_count": error_count}
            )
    
    def load_task_from_file(self, file_path: Path) -> Optional[Task]:
        """Load a single task from a markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    yaml_content = parts[1]
                    task_data = yaml.safe_load(yaml_content)
                    
                    # Handle missing required fields
                    if 'id' not in task_data:
                        task_data['id'] = file_path.stem
                    if 'status' not in task_data:
                        # Infer status from directory
                        for status, directory in self.status_dirs.items():
                            if file_path.parent == directory:
                                task_data['status'] = status.value
                                break
                    
                    task = Task.from_dict(task_data)
                    return task
            else:
                # Handle old format files
                lines = content.strip().split('\n')
                task_data = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        task_data[key.strip()] = value.strip()
                
                if 'id' in task_data:
                    return Task.from_dict(task_data)
                    
        except Exception as e:
            logger.error(f"Error parsing task file {file_path}: {e}")
        
        return None
    
    def save_task(self, task: Task) -> bool:
        """Save a task to the appropriate directory"""
        try:
            if task.created_at is None:
                task.created_at = datetime.now()
            task.updated_at = datetime.now()
            
            # Determine target directory
            target_dir = self.status_dirs[task.status]
            target_file = target_dir / f"{task.id}.md"
            
            # Remove from old location if status changed
            old_task = self.tasks_cache.get(task.id)
            if old_task and old_task.status != task.status:
                old_dir = self.status_dirs[old_task.status]
                old_file = old_dir / f"{task.id}.md"
                if old_file.exists():
                    old_file.unlink()
            
            # Generate content
            content = self._generate_task_file_content(task)
            
            # Write file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update cache
            self.tasks_cache[task.id] = task
            self.dependency_graph[task.id] = task.dependencies.copy()
            
            logger.info(f"Saved task {task.id} with status {task.status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving task {task.id}: {e}")
            return False
    
    def _generate_task_file_content(self, task: Task) -> str:
        """Generate markdown file content for a task"""
        # YAML frontmatter
        yaml_data = task.to_dict()
        yaml_content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
        
        content = f"---\n{yaml_content}---\n\n"
        
        # Add description as markdown if it contains newlines
        if '\n' in task.description:
            content += f"## Description\n\n{task.description}\n\n"
        
        # Add notes if present
        if task.notes:
            content += f"## Notes\n\n{task.notes}\n\n"
        
        return content
    
    def create_task(self, **kwargs) -> Optional[Task]:
        """Create a new task with comprehensive logging"""
        start_time = time.time()
        
        try:
            # Set default status if not provided
            if 'status' not in kwargs:
                kwargs['status'] = TaskStatus.TODO
            
            task = Task(**kwargs)
            
            if self.save_task(task):
                self.tasks_cache[task.id] = task
                self.dependency_graph[task.id] = task.dependencies.copy()
                
                # Log successful creation with emoji
                duration = time.time() - start_time
                if hasattr(logger, 'task_created'):
                    logger.task_created(f"Created task {task.id}: {task.title}")
                else:
                    logger.info(f"✨ Created task {task.id}: {task.title}")
                
                # Audit log
                if audit_logger:
                    audit_logger.log_task_operation(
                        "CREATE",
                        task.id,
                        task.agent,
                        details={
                            "title": task.title,
                            "priority": task.priority.value,
                            "status": task.status.value,
                            "dependencies": task.dependencies,
                            "tags": task.tags
                        }
                    )
                
                # Performance log
                if performance_logger:
                    performance_logger.log_operation_timing(
                        "create_task",
                        duration,
                        {"task_id": task.id, "has_dependencies": len(task.dependencies) > 0}
                    )
                
                return task
                
        except Exception as e:
            logger.error(f"Error creating task: {e}", exc_info=True)
            
        return None
    
    def update_task_status(self, task_id: str, new_status: TaskStatus, notes: str = None) -> bool:
        """Update task status with comprehensive audit and performance logging"""
        start_time = time.time()
        
        try:
            task = self.tasks_cache.get(task_id)
            if not task:
                logger.error(f"Task {task_id} not found")
                return False
            
            # Validate status transition
            if not self._is_valid_status_transition(task.status, new_status):
                logger.warning(f"Invalid status transition for {task_id}: {task.status.value} -> {new_status.value}")
                return False
            
            # Check dependencies for certain status changes
            if new_status == TaskStatus.TODO and not self._dependencies_satisfied(task_id):
                logger.warning(f"Cannot move {task_id} to TODO: dependencies not satisfied")
                return False
            
            # Update task
            old_status = task.status
            task.status = new_status
            if notes:
                task.notes = f"{task.notes}\n\n[{datetime.now().isoformat()}] Status changed from {old_status.value} to {new_status.value}: {notes}" if task.notes else f"[{datetime.now().isoformat()}] {notes}"
            
            success = self.save_task(task)
            if success:
                # Log successful status change with emoji
                duration = time.time() - start_time
                if new_status == TaskStatus.COMPLETE:
                    if hasattr(logger, 'task_completed'):
                        logger.task_completed(f"Task {task_id} completed: {old_status.value} -> {new_status.value}")
                    else:
                        logger.info(f"✅ Task {task_id} completed: {old_status.value} -> {new_status.value}")
                else:
                    if hasattr(logger, 'task_updated'):
                        logger.task_updated(f"Updated task {task_id} status: {old_status.value} -> {new_status.value}")
                    else:
                        logger.info(f"🔄 Updated task {task_id} status: {old_status.value} -> {new_status.value}")
                
                # Audit log
                if audit_logger:
                    audit_logger.log_task_operation(
                        "STATUS_CHANGE",
                        task_id,
                        task.agent,
                        details={
                            "old_status": old_status.value,
                            "new_status": new_status.value,
                            "notes": notes,
                            "title": task.title,
                            "dependencies_satisfied": self._dependencies_satisfied(task_id)
                        }
                    )
                
                # Performance log
                if performance_logger:
                    performance_logger.log_operation_timing(
                        "update_task_status",
                        duration,
                        {
                            "task_id": task_id,
                            "status_change": f"{old_status.value}->{new_status.value}",
                            "has_notes": notes is not None
                        }
                    )
                
                # Auto-update dependent tasks
                self._update_dependent_tasks(task_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating task {task_id} status: {e}", exc_info=True)
            return False

    def add_note_to_task(self, task_id: str, note: str) -> bool:
        """Add a note to a task with audit logging"""
        start_time = time.time()
        
        try:
            task = self.tasks_cache.get(task_id)
            if not task:
                logger.error(f"Task {task_id} not found")
                return False

            new_note = f"[{datetime.now().isoformat()}] {note}"
            if task.notes:
                task.notes = f"{task.notes}\n\n{new_note}"
            else:
                task.notes = new_note

            success = self.save_task(task)
            if success:
                duration = time.time() - start_time
                logger.info(f"Added note to task {task_id}")
                
                # Audit log
                if audit_logger:
                    audit_logger.log_task_operation(
                        "ADD_NOTE",
                        task_id,
                        task.agent,
                        details={
                            "note": note,
                            "title": task.title
                        }
                    )
                
                # Performance log
                if performance_logger:
                    performance_logger.log_operation_timing(
                        "add_note_to_task",
                        duration,
                        {"task_id": task_id, "note_length": len(note)}
                    )
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding note to task {task_id}: {e}", exc_info=True)
            return False
    
    def _is_valid_status_transition(self, current: TaskStatus, new: TaskStatus) -> bool:
        """Validate if status transition is allowed"""
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.TODO, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            TaskStatus.BLOCKED: [TaskStatus.TODO, TaskStatus.PENDING, TaskStatus.CANCELLED],
            TaskStatus.TODO: [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.COMPLETE],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETE, TaskStatus.TODO, TaskStatus.BLOCKED],
            TaskStatus.COMPLETE: [TaskStatus.IN_PROGRESS],  # Allow reopening
            TaskStatus.CANCELLED: [TaskStatus.PENDING, TaskStatus.TODO]  # Allow reactivation
        }
        
        return new in valid_transitions.get(current, [])
    
    def _dependencies_satisfied(self, task_id: str) -> bool:
        """Check if all dependencies for a task are satisfied"""
        task = self.tasks_cache.get(task_id)
        if not task or not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            dep_task = self.tasks_cache.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETE:
                return False
        
        return True
    
    def _update_dependent_tasks(self, completed_task_id: str) -> None:
        """Update tasks that depend on the completed task"""
        completed_task = self.tasks_cache.get(completed_task_id)
        if not completed_task or completed_task.status != TaskStatus.COMPLETE:
            return
        
        # Find tasks that depend on this one
        for task_id, dependencies in self.dependency_graph.items():
            if completed_task_id in dependencies:
                dependent_task = self.tasks_cache.get(task_id)
                if dependent_task and dependent_task.status == TaskStatus.BLOCKED:
                    # Check if all dependencies are now satisfied
                    if self._dependencies_satisfied(task_id):
                        self.update_task_status(task_id, TaskStatus.TODO, 
                                              f"Automatically moved to TODO - dependency {completed_task_id} completed")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks_cache.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status"""
        return [task for task in self.tasks_cache.values() if task.status == status]
    
    def get_tasks_by_agent(self, agent: str) -> List[Task]:
        """Get all tasks assigned to a specific agent"""
        return [task for task in self.tasks_cache.values() if task.agent == agent]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all tasks that are overdue"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        overdue_tasks = []
        for task in self.tasks_cache.values():
            if task.due_date and task.status not in [TaskStatus.COMPLETE, TaskStatus.CANCELLED]:
                # Handle both timezone-aware and naive datetimes
                due_date = task.due_date
                if due_date.tzinfo is None:
                    due_date = due_date.replace(tzinfo=timezone.utc)
                if due_date < now:
                    overdue_tasks.append(task)
        
        return overdue_tasks
    
    def get_dependency_chain(self, task_id: str) -> List[str]:
        """Get the full dependency chain for a task"""
        visited = set()
        chain = []
        
        def _build_chain(tid: str):
            if tid in visited:
                return  # Avoid cycles
            visited.add(tid)
            
            task = self.tasks_cache.get(tid)
            if task:
                for dep_id in task.dependencies:
                    _build_chain(dep_id)
                    if dep_id not in chain:
                        chain.append(dep_id)
        
        _build_chain(task_id)
        return chain
    
    def validate_dependencies(self) -> List[str]:
        """Validate all task dependencies and return errors"""
        errors = []
        
        for task_id, dependencies in self.dependency_graph.items():
            for dep_id in dependencies:
                if dep_id not in self.tasks_cache:
                    errors.append(f"Task {task_id} depends on non-existent task {dep_id}")
        
        # Check for circular dependencies
        for task_id in self.tasks_cache:
            if self._has_circular_dependency(task_id):
                errors.append(f"Circular dependency detected for task {task_id}")
        
        return errors
    
    def _has_circular_dependency(self, task_id: str, visited: set = None) -> bool:
        """Check if a task has circular dependencies"""
        if visited is None:
            visited = set()
        
        if task_id in visited:
            return True
        
        visited.add(task_id)
        dependencies = self.dependency_graph.get(task_id, [])
        
        for dep_id in dependencies:
            if self._has_circular_dependency(dep_id, visited.copy()):
                return True
        
        return False
    
    def auto_transition_ready_tasks(self) -> List[str]:
        """Automatically transition tasks that are ready to move"""
        transitioned = []
        
        # Move BLOCKED tasks to TODO if dependencies are satisfied
        blocked_tasks = self.get_tasks_by_status(TaskStatus.BLOCKED)
        for task in blocked_tasks:
            if self._dependencies_satisfied(task.id):
                if self.update_task_status(task.id, TaskStatus.TODO, "Auto-transitioned: dependencies satisfied"):
                    transitioned.append(task.id)
        
        return transitioned
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get comprehensive task statistics"""
        stats = {
            'total_tasks': len(self.tasks_cache),
            'by_status': {},
            'by_priority': {},
            'by_agent': {},
            'overdue_count': len(self.get_overdue_tasks()),
            'avg_completion_time': None,
            'dependency_violations': len(self.validate_dependencies())
        }
        
        # Count by status
        for status in TaskStatus:
            stats['by_status'][status.value] = len(self.get_tasks_by_status(status))
        
        # Count by priority
        for priority in TaskPriority:
            count = len([t for t in self.tasks_cache.values() if t.priority == priority])
            stats['by_priority'][priority.value] = count
        
        # Count by agent
        agents = set(task.agent for task in self.tasks_cache.values())
        for agent in agents:
            stats['by_agent'][agent] = len(self.get_tasks_by_agent(agent))
        
        # Calculate average completion time for completed tasks
        completed_tasks = self.get_tasks_by_status(TaskStatus.COMPLETE)
        if completed_tasks:
            completion_times = []
            for task in completed_tasks:
                if task.created_at and task.updated_at:
                    completion_time = (task.updated_at - task.created_at).total_seconds() / 3600  # hours
                    completion_times.append(completion_time)
            
            if completion_times:
                stats['avg_completion_time'] = sum(completion_times) / len(completion_times)
        
        return stats