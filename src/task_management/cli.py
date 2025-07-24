#!/usr/bin/env python3
"""
Command Line Interface for Agent Task Management System

Provides command-line access to task management functionality including
task creation, status updates, analytics, and validation.
"""

import argparse
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import click
from rich.console import Console
from rich.table import Table

from .task_manager import TaskManager, TaskStatus, TaskPriority
from .task_validator import TaskValidator
from .task_analytics import TaskAnalytics
from .task_templates import TaskTemplates
from .changelog_generator import ChangelogGenerator
from .task_deduplicator import TaskDeduplicator, MergeStrategy
from utils.logger import logger, setup_logging

# Initialize enhanced logging for CLI
setup_logging()


class TaskCLI:
    """Command line interface for task management"""
    
    def __init__(self, tasks_root: str = "tasks"):
        self.task_manager = TaskManager(tasks_root)
        self.validator = TaskValidator(task_manager=self.task_manager)
        self.analytics = TaskAnalytics(self.task_manager.tasks_cache)
        self.templates = TaskTemplates()
        self.changelog_generator = ChangelogGenerator(self.task_manager)
        self.deduplicator = TaskDeduplicator(self.task_manager)
    
    def create_task(self, args) -> None:
        """Create a new task"""
        if args.template:
            # Create from template
            template_kwargs = {}
            if args.template_vars:
                for var in args.template_vars:
                    if '=' in var:
                        key, value = var.split('=', 1)
                        template_kwargs[key] = value
            
            template_kwargs.update({
                'task_id': args.id,
                'title': args.title,
                'agent': args.agent,
                'priority': TaskPriority(args.priority) if args.priority else None
            })
            
            task = self.templates.create_task_from_template(args.template, **template_kwargs)
            if not task:
                if hasattr(logger, 'template_error'):
                    logger.template_error(f"Template '{args.template}' not found")
                else:
                    logger.error(f"❌ Template '{args.template}' not found")
                print(f"❌ Template '{args.template}' not found")
                return
        else:
            # Create manually
            task = self.task_manager.create_task(
                id=args.id,
                title=args.title,
                description=args.description,
                agent=args.agent,
                priority=TaskPriority(args.priority),
                estimated_hours=args.estimated_hours,
                due_date=datetime.fromisoformat(args.due_date) if args.due_date else None,
                tags=args.tags.split(',') if args.tags else [],
                dependencies=args.dependencies.split(',') if args.dependencies else []
            )
        
        if task:
            if hasattr(logger, 'task_created'):
                logger.task_created(f"Created task {task.id}: {task.title}")
            else:
                logger.info(f"✨ Created task {task.id}: {task.title}")
            print(f"✅ Created task: {task.id}")
            if args.validate:
                self._validate_task(task.id)
        else:
            if hasattr(logger, 'operation_failed'):
                logger.operation_failed("Failed to create task")
            else:
                logger.error("❌ Failed to create task")
            print("❌ Failed to create task")
    
    def update_status(self, args) -> None:
        """Update task status"""
        new_status = TaskStatus(args.status)
        success = self.task_manager.update_task_status(args.task_id, new_status, args.notes)
        
        if success:
            if hasattr(logger, 'task_updated'):
                logger.task_updated(f"Updated task {args.task_id} to {new_status.value}")
            else:
                logger.info(f"🔄 Updated task {args.task_id} to {new_status.value}")
            print(f"✅ Updated task {args.task_id} to {new_status.value}")
            
            # Show any auto-transitioned tasks
            auto_transitioned = self.task_manager.auto_transition_ready_tasks()
            if auto_transitioned:
                if hasattr(logger, 'auto_transition'):
                    logger.auto_transition(f"Auto-transitioned tasks: {', '.join(auto_transitioned)}")
                else:
                    logger.info(f"🔄 Auto-transitioned tasks: {', '.join(auto_transitioned)}")
                print(f"🔄 Auto-transitioned tasks: {', '.join(auto_transitioned)}")
        else:
            if hasattr(logger, 'operation_failed'):
                logger.operation_failed(f"Failed to update task {args.task_id}")
            else:
                logger.error(f"❌ Failed to update task {args.task_id}")
            print(f"❌ Failed to update task {args.task_id}")

    def add_note(self, args) -> None:
        """Add a note to a task."""
        success = self.task_manager.add_note_to_task(args.task_id, args.note)
        if success:
            if hasattr(logger, 'note_added'):
                logger.note_added(f"Added note to task {args.task_id}: {args.note[:50]}...")
            else:
                logger.info(f"📝 Added note to task {args.task_id}")
            print(f"✅ Added note to task {args.task_id}")
        else:
            if hasattr(logger, 'operation_failed'):
                logger.operation_failed(f"Failed to add note to task {args.task_id}")
            else:
                logger.error(f"❌ Failed to add note to task {args.task_id}")
            print(f"❌ Failed to add note to task {args.task_id}")

    def update_task(self, args) -> None:
        """Update task fields."""
        updates = {}
        if args.title: updates['title'] = args.title
        if args.description: updates['description'] = args.description
        if args.agent: updates['agent'] = args.agent
        if args.priority: updates['priority'] = TaskPriority(args.priority)
        if args.estimated_hours: updates['estimated_hours'] = args.estimated_hours
        if args.due_date: updates['due_date'] = datetime.fromisoformat(args.due_date)
        if args.tags: updates['tags'] = args.tags.split(',')
        if args.dependencies: updates['dependencies'] = args.dependencies.split(',')

        success = self.task_manager.update_task_fields(args.task_id, **updates)

        if success:
            logger.info(f"Updated task {args.task_id}")
            print(f"✅ Updated task {args.task_id}")
        else:
            logger.error(f"Failed to update task {args.task_id}")
            print(f"❌ Failed to update task {args.task_id}")
    
    def list_tasks(self, args) -> None:
        """List tasks with optional filters"""
        tasks = list(self.task_manager.tasks_cache.values())
        
        # Filter out completed tasks by default unless status is specified or --include-completed is used
        if not args.status and not getattr(args, 'include_completed', False):
            tasks = [t for t in tasks if t.status != TaskStatus.COMPLETE]
        
        # Apply filters
        if args.agent:
            tasks = [t for t in tasks if t.agent == args.agent]
        
        if args.status:
            status_filter = TaskStatus(args.status)
            tasks = [t for t in tasks if t.status == status_filter]
        
        if args.priority:
            priority_filter = TaskPriority(args.priority)
            tasks = [t for t in tasks if t.priority == priority_filter]
        
        if args.tag:
            tasks = [t for t in tasks if args.tag in t.tags]
        
        if args.overdue:
            overdue_tasks = self.task_manager.get_overdue_tasks()
            overdue_ids = {t.id for t in overdue_tasks}
            tasks = [t for t in tasks if t.id in overdue_ids]
        
        # Sort tasks
        if args.sort_by == 'priority':
            priority_order = {TaskPriority.CRITICAL: 0, TaskPriority.HIGH: 1, 
                            TaskPriority.MEDIUM: 2, TaskPriority.LOW: 3}
            tasks.sort(key=lambda t: priority_order.get(t.priority, 4))
        elif args.sort_by == 'created':
            tasks.sort(key=lambda t: t.created_at or datetime.min)
        elif args.sort_by == 'updated':
            tasks.sort(key=lambda t: t.updated_at or datetime.min)
        
        # Display tasks
        if args.blockers:
            blocking_tasks = self.task_manager.get_blocking_tasks()
            if blocking_tasks:
                print("🔗 Tasks Blocking Others:")
                for task in blocking_tasks:
                    print(f"  🔗 {task.id}: {task.title} ({task.agent})")
            else:
                print("No tasks are currently blocking others.")
            return

        if not tasks:
            if hasattr(logger, 'query_result'):
                logger.query_result("No tasks found matching criteria")
            else:
                logger.info("🔍 No tasks found matching criteria")
            print("No tasks found matching criteria")
            return
        
        if args.format == 'table':
            self._display_tasks_table(tasks)
        elif args.format == 'json':
            self._display_tasks_json(tasks)
        else:
            self._display_tasks_list(tasks)
        
        # Show action help if there are tasks with actions
        if tasks and args.format != 'json':
            self._show_action_help()
    
    def show_task(self, args) -> None:
        """Show detailed information about a task"""
        task = self.task_manager.get_task(args.task_id)
        if not task:
            if hasattr(logger, 'task_not_found'):
                logger.task_not_found(f"Task '{args.task_id}' not found")
            else:
                logger.warning(f"⚠️ Task '{args.task_id}' not found")
            print(f"❌ Task '{args.task_id}' not found")
            return
        
        print(f"📋 Task: {task.title}")
        print(f"ID: {task.id}")
        print(f"Agent: {task.agent}")
        print(f"Status: {task.status.value}")
        print(f"Priority: {task.priority.value}")
        
        if task.estimated_hours:
            print(f"Estimated Hours: {task.estimated_hours}")
        
        if task.due_date:
            print(f"Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
        
        if task.tags:
            print(f"Tags: {', '.join(task.tags)}")
        
        if task.dependencies:
            print(f"Dependencies: {', '.join(task.dependencies)}")
        
        print(f"\nDescription:\n{task.description}")
        
        if task.notes:
            print(f"\nNotes:\n{task.notes}")
        
        if task.created_at:
            print(f"\nCreated: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("\nCreated: N/A")
        if task.updated_at:
            print(f"Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("Updated: N/A")
        
        # Show validation if requested
        if args.validate:
            self._validate_task(args.task_id)
    
    def validate_tasks(self, args) -> None:
        """Validate tasks"""
        self.task_manager.load_all_tasks() # Reload tasks to ensure up-to-date cache
        if args.task_id:
            self._validate_task(args.task_id)
        else:
            self._validate_all_tasks()
    
    def _validate_task(self, task_id: str) -> None:
        """Validate a single task"""
        task = self.task_manager.get_task(task_id)
        if not task:
            if hasattr(logger, 'task_not_found'):
                logger.task_not_found(f"Task '{task_id}' not found")
            else:
                logger.warning(f"⚠️ Task '{task_id}' not found")
            print(f"❌ Task '{task_id}' not found")
            return
        
        errors = self.validator.validate_task(task)
        if not errors:
            if hasattr(logger, 'validation_passed'):
                logger.validation_passed(f"Task {task_id} validation passed")
            else:
                logger.info(f"✅ Task {task_id} validation passed")
            print(f"✅ Task {task_id} validation passed")
        else:
            if hasattr(logger, 'validation_issues'):
                logger.validation_issues(f"Task {task_id} has {len(errors)} validation issues")
            else:
                logger.warning(f"⚠️ Task {task_id} has {len(errors)} validation issues")
            print(f"⚠️ Task {task_id} validation issues:")
            for error in errors:
                icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[error.severity]
                print(f"  {icon} {error.field}: {error.message}")
    
    def _validate_all_tasks(self) -> None:
        """Validate all tasks in the system"""
        errors = self.validator.validate_task_system(self.task_manager.tasks_cache)
        report = self.validator.generate_validation_report(errors)
        print(report)
    
    def auto_fix_tasks(self, args) -> None:
        """Automatically fix common task issues"""
        if hasattr(logger, 'auto_fix_start'):
            logger.auto_fix_start("Starting auto-fix process for task issues")
        else:
            logger.info("🔧 Starting auto-fix process for task issues")
        print("🔧 Auto-fixing task issues...")
        
        fixes_applied = 0
        
        # Fix agent assignments
        agent_fixes = self.validator.auto_fix_agent_issues(self.task_manager.tasks_cache)
        if agent_fixes:
            print(f"\n✅ Fixed {len(agent_fixes)} agent assignment issues:")
            for task_id, change in agent_fixes.items():
                print(f"  • {task_id}: {change}")
                # Save the updated task
                task = self.task_manager.get_task(task_id)
                if task:
                    self.task_manager.save_task(task)
                    fixes_applied += 1
        
        # Fix dependency status issues
        dependency_fixes = self._auto_fix_dependency_status()
        if dependency_fixes:
            print(f"\n✅ Fixed {len(dependency_fixes)} dependency status issues:")
            for task_id, change in dependency_fixes.items():
                print(f"  • {task_id}: {change}")
                fixes_applied += len(dependency_fixes)
        
        if fixes_applied == 0:
            if hasattr(logger, 'auto_fix_complete'):
                logger.auto_fix_complete("No auto-fixable issues found")
            else:
                logger.info("✨ No auto-fixable issues found")
            print("✨ No auto-fixable issues found!")
        else:
            if hasattr(logger, 'auto_fix_complete'):
                logger.auto_fix_complete(f"Applied {fixes_applied} fixes successfully")
            else:
                logger.info(f"🎉 Applied {fixes_applied} fixes successfully")
            print(f"\n🎉 Applied {fixes_applied} fixes successfully!")
            
            # Run validation again to show remaining issues
            if not args.no_revalidate:
                print("\n" + "="*50)
                if hasattr(logger, 'validation_rerun'):
                    logger.validation_rerun("Re-validating after auto-fixes")
                else:
                    logger.info("🔍 Re-validating after auto-fixes")
                print("🔍 Re-validating after fixes...")
                self._validate_all_tasks()
    
    def _auto_fix_dependency_status(self) -> Dict[str, str]:
        """Fix tasks that have status TODO but unresolved dependencies"""
        fixes = {}
        
        for task in self.task_manager.tasks_cache.values():
            if task.status == TaskStatus.TODO and task.dependencies:
                # Check if dependencies are satisfied
                deps_satisfied = all(
                    (dep_task := self.task_manager.get_task(dep_id)) is not None and 
                    dep_task.status == TaskStatus.COMPLETE
                    for dep_id in task.dependencies
                )
                
                if not deps_satisfied:
                    old_status = task.status.value
                    task.status = TaskStatus.BLOCKED
                    self.task_manager.save_task(task)
                    fixes[task.id] = f"{old_status} -> blocked"
                    logger.info(f"Auto-fixed task {task.id} status: {old_status} -> blocked (dependencies not satisfied)")
        
        return fixes

    def update_blockers(self, args) -> None:
        """Update the status of tasks that are blocking others."""
        updated_tasks = self.task_manager.update_blocking_task_statuses()
        if updated_tasks:
            logger.info(f"Updated {len(updated_tasks)} tasks to BLOCKED_BY status.")
            print(f"Updated {len(updated_tasks)} tasks to BLOCKED_BY status:")
            for task_id in updated_tasks:
                print(f"  - {task_id}")
        else:
            logger.info("No tasks found to update to BLOCKED_BY status.")
            print("No tasks found to update to BLOCKED_BY status.")

    def generate_changelog(self, args) -> None:
        """Generate project changelog."""
        changelog_content = self.changelog_generator.generate_changelog()
        with open(args.output, 'w') as f:
            f.write(changelog_content)
        logger.info(f"Changelog generated to {args.output}")
        print(f"✅ Changelog generated to {args.output}")

    def promote_dependencies(self, args) -> None:
        """Promote priority of tasks that are blocking others."""
        promoted_tasks = self.task_manager.promote_dependency_priority()
        if promoted_tasks:
            logger.info(f"Promoted {len(promoted_tasks)} tasks: {', '.join(promoted_tasks)}")
            print(f"✅ Promoted {len(promoted_tasks)} tasks:")
            for task_id in promoted_tasks:
                print(f"  • {task_id}")
        else:
            logger.info("No tasks found to promote.")
            print("No tasks found to promote.")

    def assign_due_dates(self, args) -> None:
        """Assigns due dates to critical priority tasks missing them."""
        updated_tasks = self.task_manager.assign_due_dates_to_critical_tasks()
        if updated_tasks:
            logger.info(f"Assigned due dates to {len(updated_tasks)} critical tasks.")
            print(f"✅ Assigned due dates to {len(updated_tasks)} critical tasks:")
            for task_id in updated_tasks:
                print(f"  • {task_id}")
        else:
            logger.info("No critical tasks found missing due dates.")
            print("No critical tasks found missing due dates.")
    
    def find_duplicates(self, args) -> None:
        """Find potential duplicate tasks"""
        duplicates = self.deduplicator.find_duplicates(include_completed=args.include_completed)
        
        if not duplicates:
            logger.info("No duplicate tasks found.")
            print("✅ No duplicate tasks found!")
            return
        
        console = Console()
        
        # Show summary
        stats = self.deduplicator.get_duplicate_stats()
        print(f"🔍 Found {stats['total_duplicates']} potential duplicates")
        print(f"   Auto-mergeable: {stats['auto_mergeable']}")
        print(f"   High confidence: {stats['high_confidence']}")
        print(f"   Medium confidence: {stats['medium_confidence']}")
        print(f"   Low confidence: {stats['low_confidence']}")
        
        if args.format == 'table':
            self._display_duplicates_table(duplicates)
        elif args.format == 'detailed':
            self._display_duplicates_detailed(duplicates)
        else:
            self._display_duplicates_list(duplicates)
    
    def auto_merge_duplicates(self, args) -> None:
        """Automatically merge duplicate tasks"""
        print("🔍 Scanning for auto-mergeable duplicates...")
        
        merged_tasks = self.deduplicator.auto_merge_duplicates()
        
        if merged_tasks:
            print(f"✅ Successfully auto-merged {len(merged_tasks)} duplicate pairs:")
            for merge in merged_tasks:
                print(f"  • {merge}")
            
            # Reload tasks after merging
            self.task_manager.load_all_tasks()
            print(f"\n📊 Task count after merge: {len(self.task_manager.tasks_cache)}")
        else:
            print("ℹ️ No auto-mergeable duplicates found")
    
    def merge_tasks_manual(self, args) -> None:
        """Manually merge two tasks"""
        try:
            preview = self.deduplicator.manual_merge_preview(args.task1, args.task2)
            
            console = Console()
            print("🔍 Merge Preview:")
            print(f"Task 1: {preview['task1']['title']} ({args.task1})")
            print(f"Task 2: {preview['task2']['title']} ({args.task2})")
            
            if preview['conflicts']:
                print("\n⚠️ Conflicts found:")
                for conflict in preview['conflicts']:
                    print(f"  {conflict['field']}: '{conflict['task1_value']}' vs '{conflict['task2_value']}'")
            
            if not args.auto_resolve:
                # Interactive merge - simplified for now
                response = input("\nProceed with suggested merge? [y/N]: ")
                if response.lower() != 'y':
                    print("❌ Merge cancelled")
                    return
            
            # Create merge strategy
            strategy = MergeStrategy(
                keep_task_id=args.task1,  # Keep first task by default
                remove_task_id=args.task2,
                field_sources={},  # Use defaults from auto-merge logic
                merge_notes=True,
                merge_dependencies=True,
                merge_tags=True
            )
            
            success = self.deduplicator.execute_manual_merge(strategy)
            
            if success:
                print(f"✅ Successfully merged {args.task2} into {args.task1}")
                # Reload tasks
                self.task_manager.load_all_tasks()
            else:
                print("❌ Failed to merge tasks")
                
        except Exception as e:
            logger.error(f"Error in manual merge: {e}")
            print(f"❌ Error: {e}")
    
    def _display_duplicates_list(self, duplicates) -> None:
        """Display duplicates in simple list format"""
        console = Console()
        
        for i, dup in enumerate(duplicates, 1):
            confidence_color = {
                'high': 'red',
                'medium': 'yellow', 
                'low': 'blue'
            }.get(dup.confidence, 'white')
            
            auto_merge_icon = "🔄" if dup.auto_mergeable else "👥"
            
            console.print(f"{i}. {auto_merge_icon} [{confidence_color}]{dup.confidence.upper()}[/{confidence_color}] "
                         f"({dup.similarity_score:.2f}) {dup.task1.id} ↔ {dup.task2.id}")
            console.print(f"   '{dup.task1.title}' ↔ '{dup.task2.title}'")
            console.print(f"   Criteria: {', '.join(dup.match_criteria)}")
            console.print()
    
    def _display_duplicates_table(self, duplicates) -> None:
        """Display duplicates in table format"""
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Score", justify="center", width=6)
        table.add_column("Confidence", justify="center")
        table.add_column("Auto-Merge", justify="center")
        table.add_column("Task 1", min_width=15)
        table.add_column("Task 2", min_width=15)
        table.add_column("Criteria")
        
        for dup in duplicates:
            confidence_color = {
                'high': 'red',
                'medium': 'yellow',
                'low': 'blue'
            }.get(dup.confidence, 'white')
            
            table.add_row(
                f"{dup.similarity_score:.2f}",
                f"[{confidence_color}]{dup.confidence}[/{confidence_color}]",
                "🔄" if dup.auto_mergeable else "👥",
                f"{dup.task1.id}\n{dup.task1.title[:30]}...",
                f"{dup.task2.id}\n{dup.task2.title[:30]}...",
                ", ".join(dup.match_criteria)
            )
        
        console.print(table)
    
    def _display_duplicates_detailed(self, duplicates) -> None:
        """Display duplicates with detailed information"""
        console = Console()
        
        for i, dup in enumerate(duplicates, 1):
            console.print(f"\n[bold]Duplicate Pair {i}[/bold]")
            console.print(f"Similarity: {dup.similarity_score:.2f} | Confidence: {dup.confidence} | Auto-merge: {'Yes' if dup.auto_mergeable else 'No'}")
            console.print(f"Criteria: {', '.join(dup.match_criteria)}")
            
            console.print(f"\n[bold blue]Task 1:[/bold blue] {dup.task1.id}")
            console.print(f"Title: {dup.task1.title}")
            console.print(f"Agent: {dup.task1.agent} | Status: {dup.task1.status.value} | Priority: {dup.task1.priority.value}")
            if dup.task1.tags:
                console.print(f"Tags: {', '.join(dup.task1.tags)}")
            
            console.print(f"\n[bold green]Task 2:[/bold green] {dup.task2.id}")
            console.print(f"Title: {dup.task2.title}")
            console.print(f"Agent: {dup.task2.agent} | Status: {dup.task2.status.value} | Priority: {dup.task2.priority.value}")
            if dup.task2.tags:
                console.print(f"Tags: {', '.join(dup.task2.tags)}")
            
            console.print("-" * 80)
    
    def show_analytics(self, args) -> None:
        """Show task analytics"""
        self.analytics.update_tasks(self.task_manager.tasks_cache)
        
        if args.type == 'overview':
            self._show_overview_analytics()
        elif args.type == 'agents':
            self._show_agent_analytics()
        elif args.type == 'velocity':
            self._show_velocity_analytics()
        elif args.type == 'bottlenecks':
            self._show_bottleneck_analytics()
        elif args.type == 'dependencies':
            self._show_dependency_analytics()
        else:
            self._show_all_analytics()
    
    def _show_overview_analytics(self) -> None:
        """Show overview analytics"""
        stats = self.task_manager.get_task_statistics()
        completion_rate = self.analytics.get_completion_rate(30)
        
        print("📊 Task System Overview")
        print("=" * 40)
        print(f"Total Tasks: {stats['total_tasks']}")
        print(f"30-day Completion Rate: {completion_rate['completion_rate']:.1%}")
        print(f"Overdue Tasks: {stats['overdue_count']}")
        print(f"Dependency Violations: {stats['dependency_violations']}")
        
        if stats['avg_completion_time']:
            print(f"Average Completion Time: {stats['avg_completion_time']:.1f} hours")
        
        print(f"\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        
        print(f"\nBy Priority:")
        for priority, count in stats['by_priority'].items():
            print(f"  {priority}: {count}")
    
    def _show_agent_analytics(self) -> None:
        """Show agent performance analytics"""
        agent_perf = self.analytics.get_agent_performance()
        
        print("👥 Agent Performance")
        print("=" * 40)
        
        for agent, perf in agent_perf.items():
            print(f"\n🤖 {agent}")
            print(f"  Total Tasks: {perf['total_tasks']}")
            print(f"  Completion Rate: {perf['completion_rate']:.1%}")
            print(f"  Active Tasks: {perf['in_progress_tasks']}")
            print(f"  Overdue Tasks: {perf['overdue_tasks']}")
            
            if perf['avg_completion_time'] > 0:
                print(f"  Avg Completion: {perf['avg_completion_time']:.1f} hours")
    
    def _show_velocity_analytics(self) -> None:
        """Show velocity trend analytics"""
        velocity = self.analytics.get_velocity_trends(8)
        
        print("🚀 Velocity Trends (8 weeks)")
        print("=" * 40)
        
        if velocity.get('insufficient_data'):
            print("Insufficient data for velocity analysis")
            return
        
        print(f"Current Trajectory: {velocity['current_trajectory']}")
        print(f"Average Weekly Completion: {velocity['avg_weekly_completion']:.1f}")
        print(f"Velocity Trend: {velocity['velocity_trend']:.1%}")
        
        print(f"\nWeekly Data:")
        for week in velocity['weekly_data'][-4:]:  # Last 4 weeks
            week_start = datetime.fromisoformat(week['week_start']).strftime('%m/%d')
            print(f"  {week_start}: {week['completed_tasks']} completed, {week['created_tasks']} created")
    
    def _show_bottleneck_analytics(self) -> None:
        """Show bottleneck analysis"""
        bottlenecks = self.analytics.get_bottleneck_analysis()
        
        print("🚫 Bottleneck Analysis")
        print("=" * 40)
        
        if bottlenecks['identified_bottlenecks']:
            print("Identified Issues:")
            for bottleneck in bottlenecks['identified_bottlenecks']:
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[bottleneck['severity']]
                print(f"  {severity_icon} {bottleneck['description']}")
        else:
            print("✅ No significant bottlenecks detected")
        
        print(f"\nBlocked Tasks: {bottlenecks['blocked_tasks_count']}")
        print(f"Overdue Tasks: {bottlenecks['overdue_tasks']['count']}")
        
        cycle_stats = bottlenecks['cycle_time_stats']
        if cycle_stats['tasks_analyzed'] > 0:
            print(f"Avg Cycle Time: {cycle_stats['avg_hours']:.1f} hours")
            print(f"Max Cycle Time: {cycle_stats['max_hours']:.1f} hours")
    
    def _show_dependency_analytics(self) -> None:
        """Show dependency analysis"""
        deps = self.analytics.get_dependency_analysis()
        
        print("🔗 Dependency Analysis")
        print("=" * 40)
        
        print(f"Total Dependencies: {deps['total_dependencies']}")
        print(f"Avg Dependencies per Task: {deps['avg_dependencies_per_task']:.1f}")
        print(f"Max Dependency Depth: {deps['dependency_depth']['max_depth']}")
        print(f"Blocked by Dependencies: {deps['blocked_by_dependencies']}")
        
        if deps['critical_path_tasks']:
            print(f"\nCritical Path Tasks:")
            for task_id in deps['critical_path_tasks'][:5]:
                print(f"  • {task_id}")
        
        if deps['dependency_risks']:
            print(f"\nDependency Risks:")
            for risk in deps['dependency_risks']:
                print(f"  🔴 {risk['task_id']}: {risk['impact']}")
    
    def _show_all_analytics(self) -> None:
        """Show all analytics"""
        self._show_overview_analytics()
        print()
        self._show_agent_analytics()
        print()
        self._show_velocity_analytics()
        print()
        self._show_bottleneck_analytics()
    
    def list_templates(self, args) -> None:
        """List available task templates"""
        templates = self.templates.list_templates(
            agent=args.agent,
            tags=args.tags.split(',') if args.tags else []
        )
        
        if not templates:
            if hasattr(logger, 'query_result'):
                logger.query_result("No templates found matching criteria")
            else:
                logger.info("🔍 No templates found matching criteria")
            print("No templates found matching criteria")
            return
        
        print("📝 Available Task Templates")
        print("=" * 40)
        
        for template in templates:
            print(f"\n🔸 {template.id}")
            print(f"  Name: {template.name}")
            print(f"  Agent: {template.agent}")
            print(f"  Priority: {template.priority.value}")
            print(f"  Estimated Hours: {template.estimated_hours or 'N/A'}")
            print(f"  Tags: {', '.join(template.tags)}")
    
    def export_data(self, args) -> None:
        """Export task data or analytics"""
        if args.type == 'tasks':
            # Export task data
            tasks_data = {}
            for task_id, task in self.task_manager.tasks_cache.items():
                tasks_data[task_id] = task.to_dict()
            
            with open(args.output, 'w') as f:
                json.dump(tasks_data, f, indent=2, default=str)
            
            if hasattr(logger, 'export_complete'):
                logger.export_complete(f"Exported {len(tasks_data)} tasks to {args.output}")
            else:
                logger.info(f"📤 Exported {len(tasks_data)} tasks to {args.output}")
            print(f"✅ Exported {len(tasks_data)} tasks to {args.output}")
        
        elif args.type == 'analytics':
            # Export analytics
            success = self.analytics.export_analytics(args.output)
            if success:
                if hasattr(logger, 'export_complete'):
                    logger.export_complete(f"Exported analytics to {args.output}")
                else:
                    logger.info(f"📤 Exported analytics to {args.output}")
                print(f"✅ Exported analytics to {args.output}")
            else:
                if hasattr(logger, 'operation_failed'):
                    logger.operation_failed("Failed to export analytics")
                else:
                    logger.error(f"❌ Failed to export analytics")
                print(f"❌ Failed to export analytics")
    
    def auto_transition(self, args) -> None:
        """Auto-transition ready tasks"""
        transitioned = self.task_manager.auto_transition_ready_tasks()
        
        if transitioned:
            if hasattr(logger, 'auto_transition'):
                logger.auto_transition(f"Auto-transitioned {len(transitioned)} tasks: {', '.join(transitioned)}")
            else:
                logger.info(f"🔄 Auto-transitioned {len(transitioned)} tasks")
            print(f"🔄 Auto-transitioned {len(transitioned)} tasks:")
            for task_id in transitioned:
                print(f"  • {task_id}")
        else:
            if hasattr(logger, 'query_result'):
                logger.query_result("No tasks ready for auto-transition")
            else:
                logger.info("🔍 No tasks ready for auto-transition")
            print("No tasks ready for auto-transition")
    
    def _display_tasks_table(self, tasks) -> None:
        """Display tasks in table format using rich with clickable action links."""
        if not tasks:
            return

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=12)
        table.add_column("Title", min_width=20)
        table.add_column("Agent", justify="right")
        table.add_column("Status", justify="right")
        table.add_column("Priority", justify="right")
        table.add_column("Actions", justify="center", min_width=30)

        for task in tasks:
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.BLOCKED: "🚫", 
                TaskStatus.BLOCKED_BY: "🔗",
                TaskStatus.TODO: "📋",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETE: "✅",
                TaskStatus.CANCELLED: "❌"
            }.get(task.status, "❓")
            
            priority_color = {
                TaskPriority.CRITICAL: "red",
                TaskPriority.HIGH: "yellow", 
                TaskPriority.MEDIUM: "blue",
                TaskPriority.LOW: "white"
            }.get(task.priority, "white")

            # Generate compact action links for table format
            action_links = self._generate_compact_action_links(task)

            table.add_row(
                task.id,
                task.title,
                task.agent,
                f"{status_icon} {task.status.value}",
                f"[{priority_color}]{task.priority.value}[/{priority_color}]",
                action_links
            )
        
        console.print(table)
    
    def _display_tasks_list(self, tasks) -> None:
        """Display tasks in list format with clickable action links"""
        console = Console()
        for task in tasks:
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.BLOCKED: "🚫", 
                TaskStatus.BLOCKED_BY: "🔗",
                TaskStatus.TODO: "📋",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETE: "✅",
                TaskStatus.CANCELLED: "❌"
            }.get(task.status, "❓")
            
            priority_icon = {
                TaskPriority.CRITICAL: "🔴",
                TaskPriority.HIGH: "🟡", 
                TaskPriority.MEDIUM: "🔵",
                TaskPriority.LOW: "⚪"
            }.get(task.priority, "❓")
            
            # Generate clickable action links based on current status
            action_links = self._generate_action_links(task)
            
            console.print(f"{status_icon} {priority_icon} {task.id}: {task.title} ([bold]{task.agent}[/bold]) {action_links}")
    
    def _generate_action_links(self, task) -> str:
        """Generate action links for a task based on its status"""
        links = []
        
        # Status-specific actions with copy-paste friendly commands
        if task.status == TaskStatus.TODO:
            links.append("▶️ [blue]Start[/blue]")
            links.append("✅ [green]Complete[/green]")
        elif task.status == TaskStatus.IN_PROGRESS:
            links.append("✅ [green]Complete[/green]")
            links.append("🚫 [red]Block[/red]")
        elif task.status == TaskStatus.BLOCKED:
            links.append("📋 [yellow]Unblock[/yellow]")
        elif task.status == TaskStatus.COMPLETE:
            links.append("🔄 [cyan]Reopen[/cyan]")
        elif task.status == TaskStatus.PENDING:
            links.append("📋 [yellow]Ready[/yellow]")
        
        # Universal actions
        links.append("👁️ [dim]View[/dim]")
        links.append("💬 [dim]Note[/dim]")
        
        return " | ".join(links) if links else ""
    
    def _generate_compact_action_links(self, task) -> str:
        """Generate compact action links for table format"""
        links = []
        
        # Status-specific primary actions (more compact, emoji only)
        if task.status == TaskStatus.TODO:
            links.append("[blue]▶️[/blue]")
            links.append("[green]✅[/green]")
        elif task.status == TaskStatus.IN_PROGRESS:
            links.append("[green]✅[/green]")
            links.append("[red]🚫[/red]")
        elif task.status == TaskStatus.BLOCKED:
            links.append("[yellow]📋[/yellow]")
        elif task.status == TaskStatus.COMPLETE:
            links.append("[cyan]🔄[/cyan]")
        elif task.status == TaskStatus.PENDING:
            links.append("[yellow]📋[/yellow]")
        
        # Universal actions
        links.append("[dim]👁️[/dim]")
        links.append("[dim]💬[/dim]")
        
        return " ".join(links) if links else ""
    
    def _show_action_help(self) -> None:
        """Show help for action buttons in task list"""
        console = Console()
        console.print("\n[bold]Action Links Guide:[/bold]")
        console.print("▶️  Start task (todo → in_progress)")
        console.print("✅  Complete task (→ complete)")
        console.print("🚫  Block task (→ blocked)")
        console.print("📋  Make ready/unblock (→ todo)")
        console.print("🔄  Reopen task (complete → in_progress)")
        console.print("👁️  View task details")
        console.print("💬  Add quick note")
        console.print("\n[dim]Copy commands from 'python -m src.task_management.cli [action] [task-id] [status]'[/dim]")
    
    def _display_tasks_json(self, tasks) -> None:
        """Display tasks in JSON format"""
        tasks_data = [task.to_dict() for task in tasks]
        print(json.dumps(tasks_data, indent=2, default=str))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Agent Task Management CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create task command
    create_parser = subparsers.add_parser('create', help='Create a new task')
    create_parser.add_argument('--id', required=True, help='Task ID')
    create_parser.add_argument('--title', required=True, help='Task title')
    create_parser.add_argument('--description', help='Task description')
    create_parser.add_argument('--agent', required=True, help='Assigned agent')
    create_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'critical'], default='medium')
    create_parser.add_argument('--estimated-hours', type=float, help='Estimated hours')
    create_parser.add_argument('--due-date', help='Due date (ISO format)')
    create_parser.add_argument('--tags', help='Comma-separated tags')
    create_parser.add_argument('--dependencies', help='Comma-separated dependency IDs')
    create_parser.add_argument('--template', help='Template ID to use')
    create_parser.add_argument('--template-vars', nargs='*', help='Template variables (key=value)')
    create_parser.add_argument('--validate', action='store_true', help='Validate after creation')
    
    # Update status command
    status_parser = subparsers.add_parser('status', help='Update task status')
    status_parser.add_argument('task_id', help='Task ID')
    status_parser.add_argument('status', choices=['pending', 'blocked', 'todo', 'in_progress', 'complete', 'cancelled'])
    status_parser.add_argument('--notes', help='Status change notes')

    # Add note command
    add_note_parser = subparsers.add_parser('add-note', help='Add a note to a task')
    add_note_parser.add_argument('task_id', help='Task ID')
    add_note_parser.add_argument('note', help='The note to add')

    # Update task command
    update_parser = subparsers.add_parser('update', help='Update task fields')
    update_parser.add_argument('task_id', help='Task ID')
    update_parser.add_argument('--title', help='New title')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--agent', help='New agent')
    update_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'critical'], help='New priority')
    update_parser.add_argument('--estimated-hours', type=float, help='New estimated hours')
    update_parser.add_argument('--due-date', help='New due date (ISO format)')
    update_parser.add_argument('--tags', help='New comma-separated tags')
    update_parser.add_argument('--dependencies', help='New comma-separated dependency IDs')

    # List tasks command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--agent', help='Filter by agent')
    list_parser.add_argument('--status', choices=['pending', 'blocked', 'todo', 'in_progress', 'complete', 'cancelled'])
    list_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'critical'])
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--overdue', action='store_true', help='Show only overdue tasks')
    list_parser.add_argument('--include-completed', action='store_true', help='Include completed tasks in output')
    list_parser.add_argument('--sort-by', choices=['priority', 'created', 'updated'], default='priority')
    list_parser.add_argument('--format', choices=['list', 'table', 'json'], default='list')
    list_parser.add_argument('--blockers', action='store_true', help='Show tasks that are blocking other tasks')
    
    # Show task command
    show_parser = subparsers.add_parser('show', help='Show task details')
    show_parser.add_argument('task_id', help='Task ID')
    show_parser.add_argument('--validate', action='store_true', help='Include validation results')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate tasks')
    validate_parser.add_argument('--task-id', help='Validate specific task')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show analytics')
    analytics_parser.add_argument('--type', choices=['overview', 'agents', 'velocity', 'bottlenecks', 'dependencies'], default='overview')
    
    # Templates command
    templates_parser = subparsers.add_parser('templates', help='List task templates')
    templates_parser.add_argument('--agent', help='Filter by agent')
    templates_parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('type', choices=['tasks', 'analytics'])
    export_parser.add_argument('output', help='Output file path')
    
    # Auto-transition command
    subparsers.add_parser('auto-transition', help='Auto-transition ready tasks')
    
    # Auto-fix command
    auto_fix_parser = subparsers.add_parser('auto-fix', help='Automatically fix common task issues')
    auto_fix_parser.add_argument('--no-revalidate', action='store_true', 
                                help='Skip re-validation after fixes')

    # Update blockers command
    update_blockers_parser = subparsers.add_parser('update-blockers', help='Update status of tasks that are blocking others')

    # Generate changelog command
    changelog_parser = subparsers.add_parser('generate-changelog', help='Generate project changelog')
    changelog_parser.add_argument('--output', default='CHANGELOG.md', help='Output file path for changelog')

    # Promote dependencies command
    promote_deps_parser = subparsers.add_parser('promote-dependencies', help='Promote priority of tasks that are blocking others')

    # Assign due dates command
    assign_due_dates_parser = subparsers.add_parser('assign-due-dates', help='Assigns due dates to critical tasks missing them')
    
    # Deduplication commands
    find_dups_parser = subparsers.add_parser('find-duplicates', help='Find potential duplicate tasks')
    find_dups_parser.add_argument('--include-completed', action='store_true', help='Include completed tasks in search')
    find_dups_parser.add_argument('--format', choices=['list', 'table', 'detailed'], default='list', help='Output format')
    
    auto_merge_parser = subparsers.add_parser('auto-merge', help='Automatically merge duplicate tasks')
    
    merge_manual_parser = subparsers.add_parser('merge-tasks', help='Manually merge two tasks')
    merge_manual_parser.add_argument('task1', help='First task ID (will be kept)')
    merge_manual_parser.add_argument('task2', help='Second task ID (will be merged into first)')
    merge_manual_parser.add_argument('--auto-resolve', action='store_true', help='Auto-resolve conflicts without prompting')
    
    args = parser.parse_args()
    
    if not args.command:
        if hasattr(logger, 'user_help'):
            logger.user_help("CLI help requested")
        else:
            logger.info("❓ CLI help requested")
        parser.print_help()
        return
    
    # Initialize CLI with logging
    if hasattr(logger, 'system_init'):
        logger.system_init("TaskCLI starting up")
    else:
        logger.info("🚀 TaskCLI starting up")
    
    cli = TaskCLI()
    
    # Route commands with logging
    if hasattr(logger, 'command_start'):
        logger.command_start(f"Executing command: {args.command}")
    else:
        logger.info(f"▶️ Executing command: {args.command}")
    
    try:
        if args.command == 'create':
            cli.create_task(args)
        elif args.command == 'status':
            cli.update_status(args)
        elif args.command == 'add-note':
            cli.add_note(args)
        elif args.command == 'list':
            cli.list_tasks(args)
        elif args.command == 'show':
            cli.show_task(args)
        elif args.command == 'validate':
            cli.validate_tasks(args)
        elif args.command == 'analytics':
            cli.show_analytics(args)
        elif args.command == 'templates':
            cli.list_templates(args)
        elif args.command == 'export':
            cli.export_data(args)
        elif args.command == 'auto-transition':
            cli.auto_transition(args)
        elif args.command == 'auto-fix':
            cli.auto_fix_tasks(args)
        elif args.command == 'update-blockers':
            cli.update_blockers(args)
        elif args.command == 'generate-changelog':
            cli.generate_changelog(args)
        elif args.command == 'promote-dependencies':
            cli.promote_dependencies(args)
        elif args.command == 'assign-due-dates':
            cli.assign_due_dates(args)
        elif args.command == 'find-duplicates':
            cli.find_duplicates(args)
        elif args.command == 'auto-merge':
            cli.auto_merge_duplicates(args)
        elif args.command == 'merge-tasks':
            cli.merge_tasks_manual(args)
        
        if hasattr(logger, 'command_complete'):
            logger.command_complete(f"Command {args.command} completed successfully")
        else:
            logger.info(f"✅ Command {args.command} completed successfully")
            
    except Exception as e:
        if hasattr(logger, 'command_failed'):
            logger.command_failed(f"Command {args.command} failed: {str(e)}")
        else:
            logger.error(f"❌ Command {args.command} failed: {str(e)}")
        print(f"❌ Command failed: {str(e)}")
        sys.exit(1)
    finally:
        print("\n--- Reminder ---")
        print("Remember to update your tasks (status, notes, etc.) before committing changes.")
        print("This ensures your progress is accurately reflected.")


@click.group()
def cli():
    """Agent Task Management CLI"""
    pass

@cli.command()
@click.option('--id', 'task_id', required=True, help='Task ID')
@click.option('--title', required=True, help='Task title')
@click.option('--description', help='Task description')
@click.option('--agent', required=True, help='Assigned agent')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'critical']), default='medium')
@click.option('--estimated-hours', type=float, help='Estimated hours')
@click.option('--due-date', help='Due date (ISO format)')
@click.option('--tags', help='Comma-separated tags')
@click.option('--dependencies', help='Comma-separated dependency IDs')
@click.option('--template', help='Template ID to use')
@click.option('--template-vars', multiple=True, help='Template variables (key=value)')
@click.option('--validate', is_flag=True, help='Validate after creation')
@click.option('--tasks-root', default='tasks', help='Tasks root directory')
def create(task_id, title, description, agent, priority, estimated_hours, due_date, tags, dependencies, template, template_vars, validate, tasks_root):
    """Create a new task"""
    # Convert to argparse-like namespace for compatibility
    class Args:
        def __init__(self):
            self.id = task_id
            self.title = title
            self.description = description
            self.agent = agent
            self.priority = priority
            self.estimated_hours = estimated_hours
            self.due_date = due_date
            self.tags = tags
            self.dependencies = dependencies
            self.template = template
            self.template_vars = list(template_vars) if template_vars else None
            self.validate = validate
    
    cli_instance = TaskCLI(tasks_root=tasks_root)
    cli_instance.create_task(Args())

@cli.command(name='list')
@click.option('--tasks-root', default='tasks', help='Tasks root directory')
def list_tasks_cmd(tasks_root):
    """List tasks"""
    class Args:
        def __init__(self):
            self.agent = None
            self.status = None
            self.priority = None
            self.tag = None
            self.overdue = False
            self.include_completed = False
            self.sort_by = 'priority'
            self.format = 'list'
            self.blockers = False
    
    cli_instance = TaskCLI(tasks_root=tasks_root)
    cli_instance.list_tasks(Args())

@cli.command()
@click.argument('task_id')
@click.argument('status', type=click.Choice(['pending', 'blocked', 'todo', 'in_progress', 'complete', 'cancelled']))
@click.option('--notes', help='Status change notes')
@click.option('--tasks-root', default='tasks', help='Tasks root directory')
def status(task_id, status, notes, tasks_root):
    """Update task status"""
    class Args:
        def __init__(self):
            self.task_id = task_id
            self.status = status
            self.notes = notes
    
    cli_instance = TaskCLI(tasks_root=tasks_root)
    cli_instance.update_status(Args())

if __name__ == '__main__':
    import sys
    # Use the original argparse-based main for command line usage
    if len(sys.argv) > 1:
        main()
    else:
        cli()