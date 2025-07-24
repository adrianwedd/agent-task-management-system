#!/usr/bin/env python3
"""
Task Deduplication and Merging System

Provides automated and manual task deduplication functionality to maintain
data hygiene and reduce redundancy in the task management system.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timezone
from dataclasses import dataclass
from difflib import SequenceMatcher

from .task_manager import Task, TaskManager, TaskStatus, TaskPriority
from utils.logger import logger


@dataclass
class DuplicateMatch:
    """Represents a potential duplicate task match"""
    task1: Task
    task2: Task
    similarity_score: float
    match_criteria: List[str]
    confidence: str  # 'high', 'medium', 'low'
    auto_mergeable: bool


@dataclass
class MergeStrategy:
    """Defines how to merge two tasks"""
    keep_task_id: str
    remove_task_id: str
    field_sources: Dict[str, str]  # field_name -> task_id to use as source
    merge_notes: bool = True
    merge_dependencies: bool = True
    merge_tags: bool = True


class TaskDeduplicator:
    """Handles automated and manual task deduplication"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        
        # Similarity thresholds
        self.title_similarity_threshold = 0.85
        self.description_similarity_threshold = 0.75
        self.high_confidence_threshold = 0.90
        self.medium_confidence_threshold = 0.70
        
        # Auto-merge criteria
        self.auto_merge_threshold = 0.95
        self.auto_merge_exact_title = True
        
        logger.info("🔍 TaskDeduplicator initialized")
    
    def find_duplicates(self, include_completed: bool = False) -> List[DuplicateMatch]:
        """Find potential duplicate tasks"""
        logger.info("🔍 Scanning for duplicate tasks...")
        
        tasks = list(self.task_manager.tasks_cache.values())
        
        # Filter out completed tasks unless requested
        if not include_completed:
            tasks = [t for t in tasks if t.status != TaskStatus.COMPLETE]
        
        duplicates = []
        processed_pairs = set()
        
        for i, task1 in enumerate(tasks):
            for j, task2 in enumerate(tasks[i+1:], i+1):
                pair_key = tuple(sorted([task1.id, task2.id]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)
                
                match = self._analyze_similarity(task1, task2)
                if match:
                    duplicates.append(match)
        
        # Sort by confidence and similarity score
        duplicates.sort(key=lambda x: (x.confidence, x.similarity_score), reverse=True)
        
        logger.info(f"🔍 Found {len(duplicates)} potential duplicates")
        return duplicates
    
    def _analyze_similarity(self, task1: Task, task2: Task) -> Optional[DuplicateMatch]:
        """Analyze similarity between two tasks"""
        criteria = []
        scores = []
        
        # Title similarity
        title_sim = self._text_similarity(task1.title, task2.title)
        if title_sim > self.title_similarity_threshold:
            criteria.append("title")
            scores.append(title_sim)
        
        # Description similarity
        if task1.description and task2.description:
            desc_sim = self._text_similarity(task1.description, task2.description)
            if desc_sim > self.description_similarity_threshold:
                criteria.append("description")
                scores.append(desc_sim)
        
        # Exact matches
        if task1.agent == task2.agent:
            criteria.append("agent")
            scores.append(1.0)
        
        if task1.priority == task2.priority:
            criteria.append("priority")
            scores.append(0.8)
        
        # Tag overlap
        if task1.tags and task2.tags:
            tag_overlap = len(set(task1.tags) & set(task2.tags)) / len(set(task1.tags) | set(task2.tags))
            if tag_overlap > 0.5:
                criteria.append("tags")
                scores.append(tag_overlap)
        
        # Dependencies overlap
        if task1.dependencies and task2.dependencies:
            dep_overlap = len(set(task1.dependencies) & set(task2.dependencies)) / len(set(task1.dependencies) | set(task2.dependencies))
            if dep_overlap > 0.5:
                criteria.append("dependencies")
                scores.append(dep_overlap)
        
        # Must have at least title or description similarity
        if not any(c in criteria for c in ["title", "description"]):
            return None
        
        # Calculate overall similarity score
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Determine confidence
        if overall_score >= self.high_confidence_threshold:
            confidence = "high"
        elif overall_score >= self.medium_confidence_threshold:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Determine if auto-mergeable
        auto_mergeable = (
            overall_score >= self.auto_merge_threshold or
            (self.auto_merge_exact_title and title_sim == 1.0 and task1.agent == task2.agent)
        )
        
        return DuplicateMatch(
            task1=task1,
            task2=task2,
            similarity_score=overall_score,
            match_criteria=criteria,
            confidence=confidence,
            auto_mergeable=auto_mergeable
        )
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize text
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        return SequenceMatcher(None, text1, text2).ratio()
    
    def auto_merge_duplicates(self, duplicates: List[DuplicateMatch] = None) -> List[str]:
        """Automatically merge duplicates that meet auto-merge criteria"""
        if duplicates is None:
            duplicates = self.find_duplicates()
        
        auto_mergeable = [d for d in duplicates if d.auto_mergeable]
        
        if not auto_mergeable:
            logger.info("🔍 No auto-mergeable duplicates found")
            return []
        
        merged_tasks = []
        
        for duplicate in auto_mergeable:
            try:
                strategy = self._create_auto_merge_strategy(duplicate)
                success = self._execute_merge(strategy)
                
                if success:
                    merged_tasks.append(f"{strategy.remove_task_id} → {strategy.keep_task_id}")
                    logger.info(f"✅ Auto-merged: {strategy.remove_task_id} → {strategy.keep_task_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to auto-merge {duplicate.task1.id} & {duplicate.task2.id}: {e}")
        
        logger.info(f"✅ Auto-merged {len(merged_tasks)} duplicate pairs")
        return merged_tasks
    
    def _create_auto_merge_strategy(self, duplicate: DuplicateMatch) -> MergeStrategy:
        """Create automatic merge strategy for a duplicate pair"""
        task1, task2 = duplicate.task1, duplicate.task2
        
        # Keep the more recent task or the one with more complete information
        keep_task = task1
        remove_task = task2
        
        # Prefer task with more recent update
        if task2.updated_at and task1.updated_at and task2.updated_at > task1.updated_at:
            keep_task, remove_task = task2, task1
        
        # Or prefer task with more information
        elif self._task_completeness_score(task2) > self._task_completeness_score(task1):
            keep_task, remove_task = task2, task1
        
        # Field-specific merge rules
        field_sources = {}
        
        # Use most complete/recent values for each field
        for field in ['title', 'description', 'agent', 'priority', 'estimated_hours', 'due_date']:
            val1 = getattr(task1, field)
            val2 = getattr(task2, field)
            
            if val2 and not val1:
                field_sources[field] = task2.id
            elif val1 and not val2:
                field_sources[field] = task1.id
            else:
                field_sources[field] = keep_task.id
        
        return MergeStrategy(
            keep_task_id=keep_task.id,
            remove_task_id=remove_task.id,
            field_sources=field_sources,
            merge_notes=True,
            merge_dependencies=True,
            merge_tags=True
        )
    
    def _task_completeness_score(self, task: Task) -> float:
        """Calculate how complete a task's information is"""
        score = 0.0
        total_fields = 10
        
        # Required fields
        if task.title: score += 1
        if task.description: score += 1
        if task.agent: score += 1
        
        # Optional but valuable fields
        if task.estimated_hours: score += 1
        if task.due_date: score += 1
        if task.tags: score += 1
        if task.dependencies: score += 1
        if task.notes: score += 1
        if task.assignee: score += 1
        if task.priority != TaskPriority.MEDIUM: score += 1  # Non-default priority
        
        return score / total_fields
    
    def manual_merge_preview(self, task1_id: str, task2_id: str) -> Dict:
        """Preview what a manual merge would look like"""
        task1 = self.task_manager.get_task(task1_id)
        task2 = self.task_manager.get_task(task2_id)
        
        if not task1 or not task2:
            raise ValueError(f"Task not found: {task1_id if not task1 else task2_id}")
        
        preview = {
            'task1': task1.to_dict(),
            'task2': task2.to_dict(),
            'suggested_merge': self._create_auto_merge_strategy(
                DuplicateMatch(task1, task2, 1.0, [], 'manual', True)
            ),
            'conflicts': self._identify_conflicts(task1, task2)
        }
        
        return preview
    
    def _identify_conflicts(self, task1: Task, task2: Task) -> List[Dict]:
        """Identify conflicts between two tasks"""
        conflicts = []
        
        for field in ['title', 'description', 'agent', 'priority', 'estimated_hours', 'due_date', 'status']:
            val1 = getattr(task1, field)
            val2 = getattr(task2, field)
            
            if val1 != val2 and val1 and val2:
                conflicts.append({
                    'field': field,
                    'task1_value': str(val1),
                    'task2_value': str(val2)
                })
        
        # Check for tag conflicts
        if task1.tags and task2.tags:
            unique_tags1 = set(task1.tags) - set(task2.tags)
            unique_tags2 = set(task2.tags) - set(task1.tags)
            
            if unique_tags1 or unique_tags2:
                conflicts.append({
                    'field': 'tags',
                    'task1_value': list(unique_tags1),
                    'task2_value': list(unique_tags2)
                })
        
        return conflicts
    
    def execute_manual_merge(self, strategy: MergeStrategy) -> bool:
        """Execute a manual merge strategy"""
        return self._execute_merge(strategy)
    
    def _execute_merge(self, strategy: MergeStrategy) -> bool:
        """Execute a merge strategy"""
        try:
            keep_task = self.task_manager.get_task(strategy.keep_task_id)
            remove_task = self.task_manager.get_task(strategy.remove_task_id)
            
            if not keep_task or not remove_task:
                logger.error(f"❌ Task not found for merge: {strategy.keep_task_id} or {strategy.remove_task_id}")
                return False
            
            # Apply field merges
            for field, source_task_id in strategy.field_sources.items():
                source_task = keep_task if source_task_id == keep_task.id else remove_task
                setattr(keep_task, field, getattr(source_task, field))
            
            # Merge notes
            if strategy.merge_notes and remove_task.notes:
                merge_note = f"[{datetime.now().isoformat()}] Merged from task {remove_task.id}: {remove_task.notes}"
                if keep_task.notes:
                    keep_task.notes = f"{keep_task.notes}\n\n{merge_note}"
                else:
                    keep_task.notes = merge_note
            
            # Merge dependencies
            if strategy.merge_dependencies and remove_task.dependencies:
                merged_deps = list(set(keep_task.dependencies + remove_task.dependencies))
                # Remove self-references
                merged_deps = [d for d in merged_deps if d not in [keep_task.id, remove_task.id]]
                keep_task.dependencies = merged_deps
            
            # Merge tags
            if strategy.merge_tags and remove_task.tags:
                keep_task.tags = list(set(keep_task.tags + remove_task.tags))
            
            # Update timestamps
            keep_task.updated_at = datetime.now(timezone.utc)
            
            # Save the merged task
            success = self.task_manager.save_task(keep_task)
            
            if success:
                # Remove the duplicate task file
                remove_task_dir = self.task_manager.status_dirs[remove_task.status]
                remove_task_file = remove_task_dir / f"{remove_task.id}.md"
                
                if remove_task_file.exists():
                    remove_task_file.unlink()
                    logger.info(f"🗑️ Removed duplicate task file: {remove_task_file}")
                
                # Remove from cache
                if remove_task.id in self.task_manager.tasks_cache:
                    del self.task_manager.tasks_cache[remove_task.id]
                
                if remove_task.id in self.task_manager.dependency_graph:
                    del self.task_manager.dependency_graph[remove_task.id]
                
                # Update dependencies in other tasks that referenced the removed task
                self._update_references(remove_task.id, keep_task.id)
                
                logger.info(f"✅ Successfully merged {remove_task.id} into {keep_task.id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to execute merge: {e}")
            return False
    
    def _update_references(self, old_task_id: str, new_task_id: str):
        """Update references to a merged task in other tasks"""
        for task in self.task_manager.tasks_cache.values():
            if old_task_id in task.dependencies:
                task.dependencies = [
                    new_task_id if dep == old_task_id else dep
                    for dep in task.dependencies
                ]
                # Remove duplicates
                task.dependencies = list(dict.fromkeys(task.dependencies))
                self.task_manager.save_task(task)
                logger.info(f"🔗 Updated dependency reference in {task.id}: {old_task_id} → {new_task_id}")
    
    def get_duplicate_stats(self) -> Dict:
        """Get statistics about duplicates in the system"""
        duplicates = self.find_duplicates()
        
        stats = {
            'total_duplicates': len(duplicates),
            'auto_mergeable': len([d for d in duplicates if d.auto_mergeable]),
            'high_confidence': len([d for d in duplicates if d.confidence == 'high']),
            'medium_confidence': len([d for d in duplicates if d.confidence == 'medium']),
            'low_confidence': len([d for d in duplicates if d.confidence == 'low']),
            'by_criteria': {}
        }
        
        # Count by criteria
        all_criteria = set()
        for dup in duplicates:
            all_criteria.update(dup.match_criteria)
        
        for criteria in all_criteria:
            stats['by_criteria'][criteria] = len([d for d in duplicates if criteria in d.match_criteria])
        
        return stats