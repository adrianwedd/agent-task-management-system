"""
Advanced Task Status Transitions

Provides intelligent dependency-based state changes, automated progression triggers,
and status validation with rollback capabilities for the task management system.
"""

import logging
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from .task_manager import Task, TaskStatus, TaskPriority, TaskManager
from utils.logger import logger


class TransitionTrigger(Enum):
    """Types of transition triggers"""
    MANUAL = "manual"
    DEPENDENCY_COMPLETE = "dependency_complete"
    TIME_BASED = "time_based"
    CONDITION_MET = "condition_met"
    AGENT_AVAILABLE = "agent_available"
    RESOURCE_AVAILABLE = "resource_available"


@dataclass
class TransitionRule:
    """Defines a transition rule"""
    from_status: TaskStatus
    to_status: TaskStatus
    trigger: TransitionTrigger
    conditions: List[str]  # Condition expressions
    auto_execute: bool = False
    delay_minutes: int = 0
    requires_approval: bool = False
    rollback_enabled: bool = True
    

@dataclass 
class TransitionEvent:
    """Records a transition event"""
    task_id: str
    from_status: TaskStatus
    to_status: TaskStatus
    trigger: TransitionTrigger
    timestamp: datetime
    user: Optional[str] = None
    automated: bool = False
    rollback_id: Optional[str] = None
    

class AdvancedTransitionEngine:
    """Advanced task status transition engine with intelligent automation"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.transition_rules = self._initialize_transition_rules()
        self.transition_history: List[TransitionEvent] = []
        self.pending_transitions: Dict[str, List[Tuple[TransitionRule, datetime]]] = {}
        
    def _initialize_transition_rules(self) -> List[TransitionRule]:
        """Initialize default transition rules"""
        return [
            # Automatic dependency-based transitions
            TransitionRule(
                from_status=TaskStatus.BLOCKED,
                to_status=TaskStatus.TODO,
                trigger=TransitionTrigger.DEPENDENCY_COMPLETE,
                conditions=["all_dependencies_complete"],
                auto_execute=True,
                rollback_enabled=True
            ),
            
            TransitionRule(
                from_status=TaskStatus.PENDING,
                to_status=TaskStatus.TODO,
                trigger=TransitionTrigger.DEPENDENCY_COMPLETE,
                conditions=["all_dependencies_complete", "agent_available"],
                auto_execute=True,
                rollback_enabled=True
            ),
            
            # Time-based transitions
            TransitionRule(
                from_status=TaskStatus.TODO,
                to_status=TaskStatus.IN_PROGRESS,
                trigger=TransitionTrigger.TIME_BASED,
                conditions=["high_priority", "agent_available"],
                auto_execute=True,
                delay_minutes=60,  # Auto-start high priority tasks after 1 hour
                rollback_enabled=True
            ),
            
            # Agent availability transitions
            TransitionRule(
                from_status=TaskStatus.TODO,
                to_status=TaskStatus.IN_PROGRESS,
                trigger=TransitionTrigger.AGENT_AVAILABLE,
                conditions=["agent_has_capacity", "no_blocking_tasks"],
                auto_execute=True,
                rollback_enabled=True
            ),
            
            # Completion validation
            TransitionRule(
                from_status=TaskStatus.IN_PROGRESS,
                to_status=TaskStatus.COMPLETE,
                trigger=TransitionTrigger.CONDITION_MET,
                conditions=["validation_passed", "tests_green", "documentation_updated"],
                auto_execute=False,
                requires_approval=True,
                rollback_enabled=True
            ),
            
            # Emergency escalation
            TransitionRule(
                from_status=TaskStatus.BLOCKED,
                to_status=TaskStatus.CANCELLED,
                trigger=TransitionTrigger.TIME_BASED,
                conditions=["blocked_over_threshold", "no_resolution_path"],
                auto_execute=False,
                delay_minutes=10080,  # 7 days
                requires_approval=True,
                rollback_enabled=True
            )
        ]
    
    def evaluate_transitions(self, task_id: Optional[str] = None) -> List[TransitionEvent]:
        """Evaluate and execute eligible transitions"""
        transitions_executed = []
        
        tasks_to_check = [self.task_manager.get_task(task_id)] if task_id else list(self.task_manager.tasks_cache.values())
        tasks_to_check = [t for t in tasks_to_check if t is not None]
        
        for task in tasks_to_check:
            eligible_rules = self._get_eligible_rules(task)
            
            for rule in eligible_rules:
                if self._evaluate_conditions(task, rule):
                    if rule.auto_execute and not rule.requires_approval:
                        event = self._execute_transition(task, rule)
                        if event:
                            transitions_executed.append(event)
                    else:
                        # Queue for manual approval or delayed execution
                        self._queue_transition(task.id, rule)
        
        return transitions_executed
    
    def _get_eligible_rules(self, task: Task) -> List[TransitionRule]:
        """Get transition rules eligible for the task's current status"""
        return [rule for rule in self.transition_rules if rule.from_status == task.status]
    
    def _evaluate_conditions(self, task: Task, rule: TransitionRule) -> bool:
        """Evaluate if all conditions for a transition rule are met"""
        for condition in rule.conditions:
            if not self._check_condition(task, condition):
                return False
        return True
    
    def _check_condition(self, task: Task, condition: str) -> bool:
        """Check a specific condition"""
        if condition == "all_dependencies_complete":
            return self._all_dependencies_complete(task)
        
        elif condition == "agent_available":
            return self._agent_available(task.agent)
        
        elif condition == "high_priority":
            return task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]
        
        elif condition == "agent_has_capacity":
            return self._agent_has_capacity(task.agent)
        
        elif condition == "no_blocking_tasks":
            return self._no_blocking_tasks(task.agent)
        
        elif condition == "validation_passed":
            return self._validation_passed(task)
        
        elif condition == "tests_green":
            return self._tests_green(task)
        
        elif condition == "documentation_updated":
            return self._documentation_updated(task)
        
        elif condition == "blocked_over_threshold":
            return self._blocked_over_threshold(task)
        
        elif condition == "no_resolution_path":
            return self._no_resolution_path(task)
        
        return False
    
    def _all_dependencies_complete(self, task: Task) -> bool:
        """Check if all dependencies are complete"""
        for dep_id in task.dependencies:
            dep_task = self.task_manager.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETE:
                return False
        return True
    
    def _agent_available(self, agent: str) -> bool:
        """Check if agent is available (simplified heuristic)"""
        agent_tasks = self.task_manager.get_tasks_by_agent(agent)
        in_progress_count = len([t for t in agent_tasks if t.status == TaskStatus.IN_PROGRESS])
        return in_progress_count < 3  # Max 3 concurrent tasks per agent
    
    def _agent_has_capacity(self, agent: str) -> bool:
        """Check if agent has capacity for new work"""
        agent_tasks = self.task_manager.get_tasks_by_agent(agent)
        active_count = len([t for t in agent_tasks if t.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]])
        return active_count < 5  # Max 5 active tasks per agent
    
    def _no_blocking_tasks(self, agent: str) -> bool:
        """Check if agent has no blocking higher priority tasks"""
        agent_tasks = self.task_manager.get_tasks_by_agent(agent)
        critical_todo = [t for t in agent_tasks if t.status == TaskStatus.TODO and t.priority == TaskPriority.CRITICAL]
        return len(critical_todo) == 0
    
    def _validation_passed(self, task: Task) -> bool:
        """Check if task validation has passed (placeholder)"""
        # Would integrate with actual validation system
        return "validation_complete" in (task.notes or "")
    
    def _tests_green(self, task: Task) -> bool:
        """Check if tests are passing (placeholder)"""
        # Would integrate with CI/CD system
        return "tests_passed" in (task.notes or "")
    
    def _documentation_updated(self, task: Task) -> bool:
        """Check if documentation is updated (placeholder)"""
        # Would check documentation system
        return "docs_updated" in (task.notes or "")
    
    def _blocked_over_threshold(self, task: Task) -> bool:
        """Check if task has been blocked beyond threshold"""
        if task.status != TaskStatus.BLOCKED:
            return False
        
        # Check how long it's been blocked
        blocked_duration = datetime.now() - task.updated_at
        return blocked_duration > timedelta(days=7)
    
    def _no_resolution_path(self, task: Task) -> bool:
        """Check if there's no clear path to resolve blocking issues"""
        # Simplified heuristic - would be more sophisticated in practice
        blocking_deps = []
        for dep_id in task.dependencies:
            dep_task = self.task_manager.get_task(dep_id)
            if dep_task and dep_task.status == TaskStatus.BLOCKED:
                blocking_deps.append(dep_task)
        
        return len(blocking_deps) > 0
    
    def _execute_transition(self, task: Task, rule: TransitionRule) -> Optional[TransitionEvent]:
        """Execute a transition"""
        try:
            old_status = task.status
            
            # Create rollback point if enabled
            rollback_id = None
            if rule.rollback_enabled:
                rollback_id = self._create_rollback_point(task)
            
            # Execute the transition
            success = self.task_manager.update_task_status(
                task.id, 
                rule.to_status,
                f"Auto-transition via {rule.trigger.value}: {', '.join(rule.conditions)}"
            )
            
            if success:
                event = TransitionEvent(
                    task_id=task.id,
                    from_status=old_status,
                    to_status=rule.to_status,
                    trigger=rule.trigger,
                    timestamp=datetime.now(),
                    automated=True,
                    rollback_id=rollback_id
                )
                
                self.transition_history.append(event)
                logger.info(f"Auto-transitioned task {task.id}: {old_status.value} -> {rule.to_status.value}")
                
                # Trigger cascade evaluation for dependent tasks
                self._trigger_cascade_evaluation(task.id)
                
                return event
            
        except Exception as e:
            logger.error(f"Error executing transition for task {task.id}: {e}")
        
        return None
    
    def _queue_transition(self, task_id: str, rule: TransitionRule) -> None:
        """Queue a transition for later execution or approval"""
        if task_id not in self.pending_transitions:
            self.pending_transitions[task_id] = []
        
        execute_time = datetime.now() + timedelta(minutes=rule.delay_minutes)
        self.pending_transitions[task_id].append((rule, execute_time))
        
        logger.info(f"Queued transition for task {task_id}: {rule.from_status.value} -> {rule.to_status.value}")
    
    def _create_rollback_point(self, task: Task) -> str:
        """Create a rollback point for the task"""
        rollback_id = f"rollback_{task.id}_{datetime.now().isoformat()}"
        # In a real implementation, this would save the complete task state
        logger.debug(f"Created rollback point {rollback_id} for task {task.id}")
        return rollback_id
    
    def rollback_transition(self, event: TransitionEvent) -> bool:
        """Rollback a transition using its event record"""
        if not event.rollback_id:
            logger.warning(f"Cannot rollback transition {event.task_id}: no rollback point")
            return False
        
        try:
            # Restore previous status
            success = self.task_manager.update_task_status(
                event.task_id,
                event.from_status,
                f"Rollback from transition {event.to_status.value} -> {event.from_status.value}"
            )
            
            if success:
                logger.info(f"Rolled back task {event.task_id} to status {event.from_status.value}")
                return True
                
        except Exception as e:
            logger.error(f"Error rolling back task {event.task_id}: {e}")
        
        return False
    
    def _trigger_cascade_evaluation(self, completed_task_id: str) -> None:
        """Trigger evaluation for tasks that depend on the completed task"""
        for task in self.task_manager.tasks_cache.values():
            if completed_task_id in task.dependencies:
                self.evaluate_transitions(task.id)
    
    def process_pending_transitions(self) -> List[TransitionEvent]:
        """Process transitions that are queued for execution"""
        executed_transitions = []
        now = datetime.now()
        
        for task_id, queued_transitions in list(self.pending_transitions.items()):
            remaining_transitions = []
            
            for rule, execute_time in queued_transitions:
                if now >= execute_time:
                    task = self.task_manager.get_task(task_id)
                    if task and self._evaluate_conditions(task, rule):
                        event = self._execute_transition(task, rule)
                        if event:
                            executed_transitions.append(event)
                else:
                    remaining_transitions.append((rule, execute_time))
            
            if remaining_transitions:
                self.pending_transitions[task_id] = remaining_transitions
            else:
                del self.pending_transitions[task_id]
        
        return executed_transitions
    
    def get_transition_statistics(self) -> Dict[str, Any]:
        """Get statistics about transitions"""
        if not self.transition_history:
            return {"total_transitions": 0}
        
        total = len(self.transition_history)
        automated = len([e for e in self.transition_history if e.automated])
        
        # Count by trigger type
        trigger_counts = {}
        for event in self.transition_history:
            trigger_counts[event.trigger.value] = trigger_counts.get(event.trigger.value, 0) + 1
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_transitions = [e for e in self.transition_history if e.timestamp >= recent_cutoff]
        
        return {
            "total_transitions": total,
            "automated_transitions": automated,
            "automation_rate": automated / total if total > 0 else 0,
            "trigger_distribution": trigger_counts,
            "recent_transitions_24h": len(recent_transitions),
            "pending_transitions": sum(len(queued) for queued in self.pending_transitions.values())
        }
    
    def add_custom_rule(self, rule: TransitionRule) -> None:
        """Add a custom transition rule"""
        self.transition_rules.append(rule)
        logger.info(f"Added custom transition rule: {rule.from_status.value} -> {rule.to_status.value}")
    
    def remove_rule(self, from_status: TaskStatus, to_status: TaskStatus, trigger: TransitionTrigger) -> bool:
        """Remove a transition rule"""
        for i, rule in enumerate(self.transition_rules):
            if (rule.from_status == from_status and 
                rule.to_status == to_status and 
                rule.trigger == trigger):
                del self.transition_rules[i]
                logger.info(f"Removed transition rule: {from_status.value} -> {to_status.value}")
                return True
        return False