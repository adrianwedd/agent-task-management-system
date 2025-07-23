"""
Task Management System for Agentic Frameworks

This module provides automated task lifecycle management, dependency tracking,
and task analytics for the agent-based task system.
"""

from .task_manager import TaskManager
from .task_validator import TaskValidator
from .task_analytics import TaskAnalytics
from .task_templates import TaskTemplates

__all__ = ['TaskManager', 'TaskValidator', 'TaskAnalytics', 'TaskTemplates']