
"""
Task Validation System

Validates task definitions, dependencies, and ensures data integrity
for the Agent Task management system.
"""

import re
from typing import List, Dict, Set, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .task_manager import Task, TaskStatus, TaskPriority
from .config import MAX_TAGS, AGENT_CAPABILITIES, VALID_TAGS


class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a validation error"""
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    task_id: Optional[str] = None


class TaskValidator:
    """Validates tasks and task system integrity"""
    
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.validation_rules = {
            'id_pattern': re.compile(r'^[a-zA-Z0-9_-]+$'),
            'max_title_length': 100,
            'max_description_length': 5000,
            'required_fields': ['id', 'title', 'description', 'agent', 'status'],
            'max_dependencies': 10,
            'max_tags': MAX_TAGS,
            'valid_tag_pattern': re.compile(r'^[a-zA-Z0-9_-]+$')
        }
    
    def validate_task(self, task: Task) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate a single task and return (warnings, errors)"""
        warnings = []
        errors = []
        
        all_validations = [
            self._validate_required_fields,
            self._validate_field_formats,
            self._validate_business_rules,
            self._validate_agent_assignment,
            self._validate_dates,
            self._validate_task_dependencies
        ]
        
        for validator_func in all_validations:
            results = validator_func(task)
            for result in results:
                if result.severity == ValidationSeverity.WARNING.value:
                    warnings.append(result)
                elif result.severity == ValidationSeverity.ERROR.value:
                    errors.append(result)
        
        return warnings, errors
    
    def _validate_required_fields(self, task: Task) -> List[ValidationError]:
        """Validate that all required fields are present"""
        results = []
        
        for field in self.validation_rules['required_fields']:
            value = getattr(task, field, None)
            if not value:
                results.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing or empty",
                    severity=ValidationSeverity.ERROR.value,
                    task_id=task.id if hasattr(task, 'id') else None
                ))
        
        return results
    
    def _validate_field_formats(self, task: Task) -> List[ValidationError]:
        """Validate field formats and constraints"""
        results = []
        
        # Validate ID format
        if task.id and not self.validation_rules['id_pattern'].match(task.id):
            results.append(ValidationError(
                field='id',
                message="Task ID must contain only letters, numbers, hyphens, and underscores",
                severity=ValidationSeverity.ERROR.value,
                task_id=task.id
            ))
        
        # Validate title length
        if task.title and len(task.title) > self.validation_rules['max_title_length']:
            results.append(ValidationError(
                field='title',
                message=f"Title exceeds maximum length of {self.validation_rules['max_title_length']} characters",
                severity=ValidationSeverity.WARNING.value,
                task_id=task.id
            ))
        
        # Validate description length
        if task.description and len(task.description) > self.validation_rules['max_description_length']:
            results.append(ValidationError(
                field='description',
                message=f"Description exceeds maximum length of {self.validation_rules['max_description_length']} characters",
                severity=ValidationSeverity.WARNING.value,
                task_id=task.id
            ))
        
        # Validate dependencies count
        if task.dependencies and len(task.dependencies) > self.validation_rules['max_dependencies']:
            results.append(ValidationError(
                field='dependencies',
                message=f"Task has too many dependencies (max: {self.validation_rules['max_dependencies']})",
                severity=ValidationSeverity.WARNING.value,
                task_id=task.id
            ))
        
        # Validate tags
        if task.tags:
            if len(task.tags) > self.validation_rules['max_tags']:
                results.append(ValidationError(
                    field='tags',
                    message=f"Too many tags (max: {self.validation_rules['max_tags']})",
                    severity=ValidationSeverity.WARNING.value,
                    task_id=task.id
                ))
            
            for tag in task.tags:
                if tag not in VALID_TAGS:
                    results.append(ValidationError(
                        field='tags',
                        message=f"Invalid tag: '{tag}'.",
                        severity=ValidationSeverity.WARNING.value,
                        task_id=task.id
                    ))
        
        return results
    
    def _validate_business_rules(self, task: Task) -> List[ValidationError]:
        """Validate business logic rules"""
        results = []
        
        # Validate status transitions based on dependencies
        if task.status == TaskStatus.TODO and task.dependencies:
            results.append(ValidationError(
                field='status',
                message="Tasks with unresolved dependencies should be BLOCKED or PENDING, not TODO",
                severity=ValidationSeverity.WARNING.value,
                task_id=task.id
            ))
        
        # Validate completion requirements
        if task.status == TaskStatus.COMPLETE:
            if not task.updated_at:
                results.append(ValidationError(
                    field='updated_at',
                    message="Completed tasks must have an updated_at timestamp",
                    severity=ValidationSeverity.ERROR.value,
                    task_id=task.id
                ))
        
        # Validate priority vs due date
        if task.priority == TaskPriority.CRITICAL and not task.due_date:
            results.append(ValidationError(
                field='due_date',
                message="Critical priority tasks should have a due date",
                severity=ValidationSeverity.WARNING.value,
                task_id=task.id
            ))
        
        # Validate estimated vs actual hours
        if task.actual_hours and task.estimated_hours:
            if task.actual_hours > task.estimated_hours * 2:
                results.append(ValidationError(
                    field='actual_hours',
                    message="Actual hours significantly exceed estimated hours - consider reviewing estimation process",
                    severity=ValidationSeverity.INFO.value,
                    task_id=task.id
                ))
        
        return results
    
    def _validate_agent_assignment(self, task: Task) -> List[ValidationError]:
        """Validate agent assignment with auto-migration suggestions"""
        results = []
        
        if task.agent and task.agent not in AGENT_CAPABILITIES:
            # Try to suggest an appropriate agent
            suggested_agent = self._suggest_agent_migration(task.agent, task)
            if suggested_agent:
                results.append(ValidationError(
                    field='agent',
                    message=f"Unknown agent '{task.agent}'. Suggested migration: '{suggested_agent}' (auto-fixable)",
                    severity=ValidationSeverity.WARNING.value,
                    task_id=task.id
                ))
            else:
                results.append(ValidationError(
                    field='agent',
                    message=f"Unknown agent '{task.agent}'. Valid agents: {', '.join(sorted(AGENT_CAPABILITIES.keys()))}",
                    severity=ValidationSeverity.ERROR.value,
                    task_id=task.id
                ))
        
        # Validate agent-task compatibility
        if task.agent in AGENT_CAPABILITIES:
            expected_keywords = AGENT_CAPABILITIES[task.agent]
            task_text = f"{task.title} {task.description}".lower()
            if not any(keyword in task_text for keyword in expected_keywords):
                results.append(ValidationError(
                    field='agent',
                    message=f"Task content may not match agent capabilities. Expected keywords: {', '.join(expected_keywords)}",
                    severity=ValidationSeverity.INFO.value,
                    task_id=task.id
                ))
        
        return results
    
    def _validate_dates(self, task: Task) -> List[ValidationError]:
        """Validate date fields"""
        results = []
        
        from datetime import timezone
        now = self._ensure_timezone_aware(datetime.now(timezone.utc))
        
        # Validate created_at is not in the future (allow a small tolerance)
        created_at_aware = self._ensure_timezone_aware(task.created_at)
        if created_at_aware and created_at_aware > now + timedelta(seconds=5):
            results.append(ValidationError(
                field='created_at',
                message="Created date cannot be in the future",
                severity=ValidationSeverity.ERROR.value,
                task_id=task.id
            ))
        
        # Validate updated_at is not before created_at
        updated_at_aware = self._ensure_timezone_aware(task.updated_at)
        if created_at_aware and updated_at_aware and updated_at_aware < created_at_aware:
            results.append(ValidationError(
                field='updated_at',
                message="Updated date cannot be before created date",
                severity=ValidationSeverity.ERROR.value,
                task_id=task.id
            ))
        
        # Validate due_date is reasonable
        if task.due_date:
            due_date_aware = self._ensure_timezone_aware(task.due_date)
            if due_date_aware < now and task.status not in [TaskStatus.COMPLETE, TaskStatus.CANCELLED]:
                results.append(ValidationError(
                    field='due_date',
                    message="Task is overdue",
                    severity=ValidationSeverity.WARNING.value,
                    task_id=task.id
                ))
            
            # Check if due date is too far in the future (more than 1 year)
            if due_date_aware > now.replace(year=now.year + 1):
                results.append(ValidationError(
                    field='due_date',
                    message="Due date is more than 1 year in the future - consider breaking into smaller tasks",
                    severity=ValidationSeverity.INFO.value,
                    task_id=task.id
                ))
        
        return results
    
    def _ensure_timezone_aware(self, dt):
        from datetime import timezone
        if dt and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    
    def _validate_task_dependencies(self, task: Task) -> List[ValidationError]:
        """Validate task dependencies"""
        results = []
        
        if not task.dependencies:
            return results
        
        # Check for self-dependency
        if task.id in task.dependencies:
            results.append(ValidationError(
                field='dependencies',
                message="Task cannot depend on itself",
                severity=ValidationSeverity.ERROR.value,
                task_id=task.id
            ))
        
        # Check for duplicate dependencies
        if len(task.dependencies) != len(set(task.dependencies)):
            results.append(ValidationError(
                field='dependencies',
                message="Duplicate dependencies found",
                severity=ValidationSeverity.WARNING.value,
                task_id=task.id
            ))
        
        # Validate dependency ID formats
        for dep_id in task.dependencies:
            if not self.validation_rules['id_pattern'].match(dep_id):
                results.append(ValidationError(
                    field='dependencies',
                    message=f"Invalid dependency ID format: '{dep_id}'.",
                    severity=ValidationSeverity.ERROR.value,
                    task_id=task.id
                ))
        
        return results
    
    def _suggest_agent_migration(self, unknown_agent: str, task: Task) -> Optional[str]:
        """Suggest an appropriate agent for migration based on task content and agent mapping"""
        # Direct agent mapping for known legacy agents
        agent_migration_map = {
            'ARCHAIOS_PRIME': 'ARCHITECT',
            'CONSENSUS_ENGINE': 'MANAGER', 
            'TheArchitect': 'ARCHITECT',
            'GOVERNANCE_ADVISOR': 'MANAGER',
            'BUILDFLOW': 'DEVOPS',
            'AUTOSYNTH': 'AUTOMATION',
            'DesignSynth': 'DESIGNER',
            'CODEFORGE': 'DEVELOPER',
            'OpsMind': 'DEVOPS',
            'COMPLIANCE_SENTINEL': 'REVIEWER',
            'PERMIT_WATCHDOG': 'SECURITY',
            'JurisMind': 'ANALYST',
            'LegalSentinel': 'ANALYST',
            'RISK_DOCTOR': 'ANALYST',
            'GRANT_WRANGLER': 'MANAGER',
            'ResearchOracle': 'RESEARCHER',
            'SCENARIO_SMITH': 'ANALYST',
            'TRACE_SYNTHESIZER': 'DEVELOPER',
            'MemoryWeaver': 'DEVELOPER',
            'SECSENTINEL': 'SECURITY',
            'SIM_ENGINEER': 'DEVELOPER',
            'TESTCRAFTERPRO': 'TESTER',
            'STAKEHOLDERVOICE': 'MANAGER',
            'NARRATIVE_WARDEN': 'DOCUMENTER',
            'TASK_VERIFIER_REWRITER': 'REVIEWER',
            'EthosGolem': 'ANALYST',
            'ECOSENTRY': 'SECURITY',
            'FINANCEORACLE': 'ANALYST',
            'DEVELOPER': 'DEVELOPER',  # Already valid but ensure consistency
        }
        
        # Check direct mapping first
        if unknown_agent in agent_migration_map:
            return agent_migration_map[unknown_agent]
        
        # Fallback: analyze task content to suggest appropriate agent
        task_text = f"{task.title} {task.description}".lower()
        
        content_mappings = AGENT_CAPABILITIES
        
        # Score each agent based on keyword matches
        agent_scores = {}
        for agent, keywords in content_mappings.items():
            score = sum(1 for keyword in keywords if keyword in task_text)
            if score > 0:
                agent_scores[agent] = score
        
        # Return highest scoring agent, or DEVELOPER as default
        if agent_scores:
            return max(agent_scores, key=agent_scores.get)
        
        return 'DEVELOPER'  # Default fallback
    
    def auto_fix_agent_issues(self, tasks: Dict[str, Task]) -> Dict[str, str]:
        """Automatically fix agent assignment issues and return mapping of changes"""
        fixes = {}
        
        for task in tasks.values():
            if task.agent and task.agent not in AGENT_CAPABILITIES:
                suggested_agent = self._suggest_agent_migration(task.agent, task)
                if suggested_agent:
                    old_agent = task.agent
                    task.agent = suggested_agent
                    fixes[task.id] = f"{old_agent} -> {suggested_agent}"
                    # logger.info(f"Auto-migrated task {task.id} agent: {old_agent} -> {suggested_agent}")
        
        return fixes
    
    def validate_task_system(self, tasks: Dict[str, Task]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate the entire task system for consistency"""
        all_warnings = []
        all_errors = []
        
        # Validate individual tasks first
        for task in tasks.values():
            warnings, errors = self.validate_task(task)
            all_warnings.extend(warnings)
            all_errors.extend(errors)
        
        # Validate system-wide constraints
        system_warnings, system_errors = self._validate_system_dependencies(tasks)
        all_warnings.extend(system_warnings)
        all_errors.extend(system_errors)

        system_warnings, system_errors = self._validate_system_consistency(tasks)
        all_warnings.extend(system_warnings)
        all_errors.extend(system_errors)

        system_warnings, system_errors = self._validate_agent_workload(tasks)
        all_warnings.extend(system_warnings)
        all_errors.extend(system_errors)
        
        return all_warnings, all_errors
    
    def _validate_system_dependencies(self, tasks: Dict[str, Task]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate dependencies across the entire system"""
        warnings = []
        errors = []
        
        # Check for missing dependency targets
        all_task_ids = set(tasks.keys())
        for task in tasks.values():
            for dep_id in task.dependencies:
                if dep_id not in all_task_ids:
                    errors.append(ValidationError(
                        field='dependencies',
                        message=f"Dependency '{dep_id}' does not exist",
                        severity=ValidationSeverity.ERROR.value,
                        task_id=task.id
                    ))
        
        # Check for circular dependencies
        circular_deps = self._find_circular_dependencies(tasks)
        for cycle in circular_deps:
            cycle_str = ' -> '.join(cycle + [cycle[0]])
            errors.append(ValidationError(
                field='dependencies',
                message=f"Circular dependency detected: {cycle_str}",
                severity=ValidationSeverity.ERROR.value,
                task_id=cycle[0]
            ))
        
        return warnings, errors
    
    def _validate_system_consistency(self, tasks: Dict[str, Task]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate system-wide consistency"""
        warnings = []
        errors = []
        
        # Check for orphaned tasks (no incoming dependencies)
        has_dependents = set()
        for task in tasks.values():
            has_dependents.update(task.dependencies)
        
        orphaned_tasks = []
        for task_id, task in tasks.items():
            if (task_id not in has_dependents and 
                task.status not in [TaskStatus.COMPLETE, TaskStatus.CANCELLED] and
                not task.dependencies):
                orphaned_tasks.append(task_id)
        
        if len(orphaned_tasks) > len(tasks) * 0.5:  # More than 50% orphaned
            warnings.append(ValidationError(
                field='system',
                message=f"High number of orphaned tasks ({len(orphaned_tasks)}). Consider reviewing task organization.",
                severity=ValidationSeverity.INFO.value
            ))
        
        # Check for status inconsistencies
        blocked_without_deps = []
        for task in tasks.values():
            if task.status == TaskStatus.BLOCKED and not task.dependencies:
                blocked_without_deps.append(task.id)
        
        if blocked_without_deps:
            warnings.append(ValidationError(
                field='status',
                message=f"Tasks blocked without dependencies: {', '.join(blocked_without_deps)}",
                severity=ValidationSeverity.WARNING.value
            ))
        
        return warnings, errors
    
    def _validate_agent_workload(self, tasks: Dict[str, Task]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate agent workload distribution"""
        warnings = []
        errors = []
        
        # Count active tasks per agent
        agent_workload = {}
        for task in self.task_manager.tasks_cache.values():
            if task.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]:
                agent_workload[task.agent] = agent_workload.get(task.agent, 0) + 1
        
        # Check for overloaded agents (more than 10 active tasks)
        for agent, count in agent_workload.items():
            if count > 10:
                warnings.append(ValidationError(
                    field='agent',
                    message=f"Agent '{agent}' has {count} active tasks - consider redistributing workload",
                    severity=ValidationSeverity.WARNING.value
                ))
        
        # Check for idle agents (no active tasks)
        active_agents = set(agent_workload.keys())
        all_agents_with_tasks = set(task.agent for task in self.task_manager.tasks_cache.values())
        idle_agents = all_agents_with_tasks - active_agents
        
        if idle_agents:
            warnings.append(ValidationError(
                field='agent',
                message=f"Agents with no active tasks: {', '.join(idle_agents)}",
                severity=ValidationSeverity.INFO.value
            ))
        
        return warnings, errors
    
    def _find_circular_dependencies(self, tasks: Dict[str, Task]) -> List[List[str]]:
        """Find circular dependencies in the task system"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(task_id: str, path: List[str]) -> None:
            if task_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(task_id)
                cycle = path[cycle_start:]
                cycles.append(cycle)
                return
            
            if task_id in visited:
                return
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = tasks.get(task_id)
            if task:
                for dep_id in task.dependencies:
                    if dep_id in tasks:
                        dfs(dep_id, path + [dep_id])
            
            rec_stack.remove(task_id)
        
        for task_id in tasks:
            if task_id not in visited:
                dfs(task_id, [task_id])
        
        return cycles
    
    def generate_validation_report(self, warnings: List[ValidationError], errors: List[ValidationError]) -> str:
        """Generate a human-readable validation report"""
        total_issues = len(warnings) + len(errors)
        if total_issues == 0:
            return "✅ All validations passed successfully!"
        
        report = []
        report.append(f"🔍 Task Validation Report - {total_issues} issues found")
        report.append("=" * 50)
        
        # Group by severity
        by_severity = {'error': [], 'warning': [], 'info': []}
        for error in errors:
            by_severity[error.severity].append(error)
        for warning in warnings:
            by_severity[warning.severity].append(warning)
        
        for severity in ['error', 'warning', 'info']:
            issues = by_severity[severity]
            if not issues:
                continue
            
            icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[severity]
            report.append(f"\n{icon} {severity.upper()} ({len(issues)} issues)")
            report.append("-" * 30)
            
            for issue in issues:
                task_info = f" (Task: {issue.task_id})" if issue.task_id else ""
                report.append(f"  • {issue.field}: {issue.message}{task_info}")
        
        return "\n".join(report)
