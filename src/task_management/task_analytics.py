"""
Task Analytics System

Provides comprehensive analytics and reporting for task management,
including performance metrics, trend analysis, and predictive insights.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics

from .task_manager import Task, TaskStatus, TaskPriority
from utils.logger import logger


class TaskAnalytics:
    """Analytics engine for task management system"""
    
    def __init__(self, tasks: Dict[str, Task]):
        self.tasks = tasks
        self.analytics_cache = {}
        self.last_update = datetime.now()
    
    def update_tasks(self, tasks: Dict[str, Task]) -> None:
        """Update tasks and clear cache"""
        self.tasks = tasks
        self.analytics_cache.clear()
        self.last_update = datetime.now()
    
    def get_completion_rate(self, days: int = 30) -> Dict[str, float]:
        """Calculate task completion rate over specified period"""
        cache_key = f"completion_rate_{days}"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        total_tasks = 0
        completed_tasks = 0
        
        for task in self.tasks.values():
            if task.created_at:
                # Handle both timezone-aware and naive datetimes
                created_at = task.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                
                if created_at >= cutoff_date:
                    total_tasks += 1
                    if task.status == TaskStatus.COMPLETE:
                        completed_tasks += 1
        
        rate = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
            'period_days': days
        }
        
        self.analytics_cache[cache_key] = rate
        return rate
    
    def get_agent_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance metrics by agent"""
        cache_key = "agent_performance"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        agent_stats = defaultdict(lambda: {
            'total_tasks': 0,
            'completed_tasks': 0,
            'in_progress_tasks': 0,
            'overdue_tasks': 0,
            'avg_completion_time': 0,
            'completion_rate': 0,
            'priority_distribution': Counter(),
            'recent_activity': 0
        })
        
        now = datetime.now()
        recent_cutoff = now - timedelta(days=7)
        completion_times = defaultdict(list)
        
        for task in self.tasks.values():
            agent = task.agent
            stats = agent_stats[agent]
            
            stats['total_tasks'] += 1
            stats['priority_distribution'][task.priority.value] += 1
            
            if task.status == TaskStatus.COMPLETE:
                stats['completed_tasks'] += 1
                
                # Calculate completion time
                if task.created_at and task.updated_at:
                    completion_time = (task.updated_at - task.created_at).total_seconds() / 3600
                    completion_times[agent].append(completion_time)
            
            elif task.status == TaskStatus.IN_PROGRESS:
                stats['in_progress_tasks'] += 1
            
            # Check for overdue tasks
            if (task.due_date and task.due_date < now and 
                task.status not in [TaskStatus.COMPLETE, TaskStatus.CANCELLED]):
                stats['overdue_tasks'] += 1
            
            # Check recent activity
            if task.updated_at and task.updated_at >= recent_cutoff:
                stats['recent_activity'] += 1
        
        # Calculate derived metrics
        for agent, stats in agent_stats.items():
            if stats['total_tasks'] > 0:
                stats['completion_rate'] = stats['completed_tasks'] / stats['total_tasks']
            
            if completion_times[agent]:
                stats['avg_completion_time'] = statistics.mean(completion_times[agent])
        
        result = dict(agent_stats)
        self.analytics_cache[cache_key] = result
        return result
    
    def get_velocity_trends(self, weeks: int = 12) -> Dict[str, List[Dict[str, Any]]]:
        """Calculate velocity trends over time"""
        cache_key = f"velocity_trends_{weeks}"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        now = datetime.now()
        weekly_data = []
        
        for week in range(weeks):
            week_start = now - timedelta(weeks=week+1)
            week_end = now - timedelta(weeks=week)
            
            week_stats = {
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'completed_tasks': 0,
                'created_tasks': 0,
                'total_story_points': 0,  # Could be based on estimated_hours
                'agents_active': set()
            }
            
            for task in self.tasks.values():
                # Tasks completed this week
                if (task.status == TaskStatus.COMPLETE and task.updated_at and
                    week_start <= task.updated_at < week_end):
                    week_stats['completed_tasks'] += 1
                    if task.estimated_hours:
                        week_stats['total_story_points'] += task.estimated_hours
                    week_stats['agents_active'].add(task.agent)
                
                # Tasks created this week
                if (task.created_at and week_start <= task.created_at < week_end):
                    week_stats['created_tasks'] += 1
            
            week_stats['agents_active'] = len(week_stats['agents_active'])
            weekly_data.append(week_stats)
        
        # Calculate trends
        if len(weekly_data) >= 2:
            recent_velocity = statistics.mean([w['completed_tasks'] for w in weekly_data[:4]])
            older_velocity = statistics.mean([w['completed_tasks'] for w in weekly_data[4:8]]) if len(weekly_data) >= 8 else recent_velocity
            
            trend_data = {
                'weekly_data': list(reversed(weekly_data)),  # Most recent first
                'velocity_trend': (recent_velocity - older_velocity) / older_velocity if older_velocity > 0 else 0,
                'avg_weekly_completion': recent_velocity,
                'peak_week': max(weekly_data, key=lambda x: x['completed_tasks']),
                'current_trajectory': 'improving' if recent_velocity > older_velocity else 'declining' if recent_velocity < older_velocity else 'stable'
            }
        else:
            trend_data = {'weekly_data': list(reversed(weekly_data)), 'insufficient_data': True}
        
        self.analytics_cache[cache_key] = trend_data
        return trend_data
    
    def get_bottleneck_analysis(self) -> Dict[str, Any]:
        """Identify bottlenecks in the task flow"""
        cache_key = "bottleneck_analysis"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        # Analyze task status distribution
        status_counts = Counter(task.status for task in self.tasks.values())
        
        # Identify blocked tasks and their causes
        blocked_tasks = [task for task in self.tasks.values() if task.status == TaskStatus.BLOCKED]
        blocking_dependencies = Counter()
        
        for task in blocked_tasks:
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if dep_task and dep_task.status != TaskStatus.COMPLETE:
                    blocking_dependencies[dep_id] += 1
        
        # Analyze agent workload distribution
        agent_active_tasks = defaultdict(int)
        for task in self.tasks.values():
            if task.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]:
                agent_active_tasks[task.agent] += 1
        
        # Identify overdue tasks
        now = datetime.now()
        overdue_tasks = [
            task for task in self.tasks.values()
            if task.due_date and task.due_date < now and 
            task.status not in [TaskStatus.COMPLETE, TaskStatus.CANCELLED]
        ]
        
        # Calculate cycle times
        cycle_times = []
        for task in self.tasks.values():
            if (task.status == TaskStatus.COMPLETE and task.created_at and task.updated_at):
                cycle_time = (task.updated_at - task.created_at).total_seconds() / 3600
                cycle_times.append(cycle_time)
        
        analysis = {
            'status_distribution': dict(status_counts),
            'blocked_tasks_count': len(blocked_tasks),
            'top_blocking_dependencies': blocking_dependencies.most_common(5),
            'agent_workload_imbalance': {
                'max_tasks': max(agent_active_tasks.values()) if agent_active_tasks else 0,
                'min_tasks': min(agent_active_tasks.values()) if agent_active_tasks else 0,
                'avg_tasks': statistics.mean(agent_active_tasks.values()) if agent_active_tasks else 0,
                'overloaded_agents': [agent for agent, count in agent_active_tasks.items() if count > 10]
            },
            'overdue_tasks': {
                'count': len(overdue_tasks),
                'by_agent': Counter(task.agent for task in overdue_tasks),
                'by_priority': Counter(task.priority.value for task in overdue_tasks)
            },
            'cycle_time_stats': {
                'avg_hours': statistics.mean(cycle_times) if cycle_times else 0,
                'median_hours': statistics.median(cycle_times) if cycle_times else 0,
                'max_hours': max(cycle_times) if cycle_times else 0,
                'tasks_analyzed': len(cycle_times)
            }
        }
        
        # Identify specific bottlenecks
        bottlenecks = []
        
        if analysis['blocked_tasks_count'] > len(self.tasks) * 0.1:  # More than 10% blocked
            bottlenecks.append({
                'type': 'high_blocked_ratio',
                'severity': 'high',
                'description': f"{analysis['blocked_tasks_count']} tasks blocked ({analysis['blocked_tasks_count']/len(self.tasks)*100:.1f}%)"
            })
        
        if analysis['agent_workload_imbalance']['overloaded_agents']:
            bottlenecks.append({
                'type': 'agent_overload',
                'severity': 'medium',
                'description': f"Agents overloaded: {', '.join(analysis['agent_workload_imbalance']['overloaded_agents'])}"
            })
        
        if analysis['overdue_tasks']['count'] > 0:
            bottlenecks.append({
                'type': 'overdue_tasks',
                'severity': 'high' if analysis['overdue_tasks']['count'] > 5 else 'medium',
                'description': f"{analysis['overdue_tasks']['count']} tasks overdue"
            })
        
        analysis['identified_bottlenecks'] = bottlenecks
        
        self.analytics_cache[cache_key] = analysis
        return analysis
    
    def get_priority_analysis(self) -> Dict[str, Any]:
        """Analyze task priority distribution and handling"""
        cache_key = "priority_analysis"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        priority_stats = defaultdict(lambda: {
            'total': 0,
            'completed': 0,
            'in_progress': 0,
            'overdue': 0,
            'avg_age_days': 0
        })
        
        now = datetime.now()
        
        for task in self.tasks.values():
            priority = task.priority.value
            stats = priority_stats[priority]
            
            stats['total'] += 1
            
            if task.status == TaskStatus.COMPLETE:
                stats['completed'] += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                stats['in_progress'] += 1
            
            if (task.due_date and task.due_date < now and 
                task.status not in [TaskStatus.COMPLETE, TaskStatus.CANCELLED]):
                stats['overdue'] += 1
            
            # Calculate age
            if task.created_at:
                age_days = (now - task.created_at).days
                stats['avg_age_days'] = ((stats['avg_age_days'] * (stats['total'] - 1)) + age_days) / stats['total']
        
        # Calculate completion rates
        for priority, stats in priority_stats.items():
            if stats['total'] > 0:
                stats['completion_rate'] = stats['completed'] / stats['total']
                stats['overdue_rate'] = stats['overdue'] / stats['total']
        
        analysis = {
            'priority_distribution': dict(priority_stats),
            'priority_balance': {
                'critical_ratio': priority_stats['critical']['total'] / len(self.tasks) if self.tasks else 0,
                'high_ratio': priority_stats['high']['total'] / len(self.tasks) if self.tasks else 0,
                'recommendations': []
            }
        }
        
        # Generate recommendations
        if analysis['priority_balance']['critical_ratio'] > 0.2:
            analysis['priority_balance']['recommendations'].append(
                "High ratio of critical tasks - consider reviewing priority assignment criteria"
            )
        
        if priority_stats['critical']['overdue'] > 0:
            analysis['priority_balance']['recommendations'].append(
                f"{priority_stats['critical']['overdue']} critical tasks are overdue - immediate attention required"
            )
        
        if priority_stats['high']['completion_rate'] < priority_stats['medium']['completion_rate']:
            analysis['priority_balance']['recommendations'].append(
                "High priority tasks have lower completion rate than medium priority - investigate bottlenecks"
            )
        
        self.analytics_cache[cache_key] = analysis
        return analysis
    
    def get_dependency_analysis(self) -> Dict[str, Any]:
        """Analyze task dependencies and their impact"""
        cache_key = "dependency_analysis"
        if cache_key in self.analytics_cache:
            return self.analytics_cache[cache_key]
        
        # Build dependency graph
        dependency_count = Counter()
        dependent_count = Counter()
        
        for task in self.tasks.values():
            dependency_count[task.id] = len(task.dependencies)
            for dep_id in task.dependencies:
                dependent_count[dep_id] += 1
        
        # Find critical path tasks (many dependents)
        critical_tasks = [task_id for task_id, count in dependent_count.most_common(10)]
        
        # Analyze dependency depth
        max_depth = 0
        avg_depth = 0
        
        def get_depth(task_id: str, visited: set = None) -> int:
            if visited is None:
                visited = set()
            if task_id in visited:
                return 0  # Avoid cycles
            
            visited.add(task_id)
            task = self.tasks.get(task_id)
            if not task or not task.dependencies:
                return 0
            
            max_dep_depth = max((get_depth(dep_id, visited.copy()) for dep_id in task.dependencies), default=0)
            return max_dep_depth + 1
        
        depths = [get_depth(task_id) for task_id in self.tasks.keys()]
        if depths:
            max_depth = max(depths)
            avg_depth = statistics.mean(depths)
        
        analysis = {
            'total_dependencies': sum(dependency_count.values()),
            'avg_dependencies_per_task': statistics.mean(dependency_count.values()) if dependency_count else 0,
            'max_dependencies': max(dependency_count.values()) if dependency_count else 0,
            'tasks_with_no_dependencies': sum(1 for count in dependency_count.values() if count == 0),
            'critical_path_tasks': critical_tasks,
            'most_dependent_tasks': dependent_count.most_common(5),
            'dependency_depth': {
                'max_depth': max_depth,
                'avg_depth': avg_depth
            },
            'blocked_by_dependencies': len([
                task for task in self.tasks.values()
                if task.status == TaskStatus.BLOCKED and task.dependencies
            ])
        }
        
        # Risk analysis
        risks = []
        for task_id in critical_tasks[:3]:  # Top 3 critical tasks
            task = self.tasks.get(task_id)
            if task and task.status not in [TaskStatus.COMPLETE, TaskStatus.IN_PROGRESS]:
                risks.append({
                    'task_id': task_id,
                    'risk': 'critical_path_not_progressing',
                    'impact': f"{dependent_count[task_id]} tasks depend on this"
                })
        
        analysis['dependency_risks'] = risks
        
        self.analytics_cache[cache_key] = analysis
        return analysis
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        return {
            'overview': {
                'total_tasks': len(self.tasks),
                'completion_rate_30d': self.get_completion_rate(30),
                'last_updated': self.last_update.isoformat()
            },
            'agent_performance': self.get_agent_performance(),
            'velocity_trends': self.get_velocity_trends(8),  # 8 weeks
            'bottlenecks': self.get_bottleneck_analysis(),
            'priority_analysis': self.get_priority_analysis(),
            'dependency_analysis': self.get_dependency_analysis()
        }
    
    def export_analytics(self, filepath: str) -> bool:
        """Export analytics data to JSON file"""
        try:
            dashboard_data = self.generate_dashboard_data()
            with open(filepath, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            logger.info(f"Analytics exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            return False
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights based on historical data"""
        velocity_data = self.get_velocity_trends(12)
        bottlenecks = self.get_bottleneck_analysis()
        
        insights = {
            'completion_forecast': {},
            'bottleneck_predictions': {},
            'resource_recommendations': {}
        }
        
        # Predict completion times based on velocity
        if not velocity_data.get('insufficient_data'):
            recent_velocity = velocity_data.get('avg_weekly_completion', 0)
            remaining_tasks = len([t for t in self.tasks.values() 
                                 if t.status not in [TaskStatus.COMPLETE, TaskStatus.CANCELLED]])
            
            if recent_velocity > 0:
                weeks_to_completion = remaining_tasks / recent_velocity
                insights['completion_forecast'] = {
                    'remaining_tasks': remaining_tasks,
                    'current_velocity': recent_velocity,
                    'estimated_weeks': weeks_to_completion,
                    'projected_completion': (datetime.now() + timedelta(weeks=weeks_to_completion)).isoformat()
                }
        
        # Predict potential bottlenecks
        agent_performance = self.get_agent_performance()
        for agent, perf in agent_performance.items():
            if perf['in_progress_tasks'] > 5 and perf['completion_rate'] < 0.7:
                insights['bottleneck_predictions'][agent] = {
                    'risk_level': 'high',
                    'reason': 'High workload with low completion rate',
                    'recommendation': 'Consider redistributing tasks or providing additional support'
                }
        
        return insights