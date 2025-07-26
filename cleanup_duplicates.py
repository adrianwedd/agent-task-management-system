#!/usr/bin/env python3
"""
Cleanup script to resolve duplicate task files across status directories.
Keeps the most recent version based on the status in YAML frontmatter.
"""

import os
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def parse_task_file(file_path):
    """Parse task file and extract metadata"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                yaml_content = parts[1]
                task_data = yaml.safe_load(yaml_content)
                return task_data
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    return None

def main():
    base_dir = Path('/Users/adrian/repos/agent-task-management-system/tasks')
    
    # Status directory mapping
    status_dirs = {
        'pending': base_dir / '📦 backlog',
        'blocked': base_dir / '🚫 blocked', 
        'blocked_by': base_dir / '🔗 blocked_by',
        'todo': base_dir / '📋 todo',
        'in_progress': base_dir / '🔄 in-progress',
        'complete': base_dir / '✅ done',
        'cancelled': base_dir / '❌ cancelled'
    }
    
    # Find all task files and group by task ID
    task_files = defaultdict(list)
    
    for status_dir in base_dir.iterdir():
        if status_dir.is_dir() and not status_dir.name.startswith('.'):
            for task_file in status_dir.glob('*.md'):
                task_data = parse_task_file(task_file)
                if task_data and 'id' in task_data:
                    task_files[task_data['id']].append((task_file, task_data))
    
    # Process duplicates
    duplicates_found = 0
    files_removed = 0
    
    for task_id, file_list in task_files.items():
        if len(file_list) > 1:
            duplicates_found += 1
            print(f"\n🔍 Processing task: {task_id} ({len(file_list)} copies)")
            
            # Find the canonical version (most recent updated_at with correct status)
            canonical_file = None
            canonical_data = None
            latest_update = None
            
            for file_path, task_data in file_list:
                updated_at = task_data.get('updated_at')
                status = task_data.get('status', 'unknown')
                
                print(f"  📄 {file_path.parent.name}/{file_path.name}: status={status}, updated={updated_at}")
                
                # Parse updated_at
                if isinstance(updated_at, str):
                    try:
                        if updated_at.endswith('+00:00'):
                            update_time = datetime.fromisoformat(updated_at.replace('+00:00', ''))
                        else:
                            update_time = datetime.fromisoformat(updated_at)
                    except:
                        update_time = datetime.min
                elif isinstance(updated_at, datetime):
                    update_time = updated_at
                else:
                    update_time = datetime.min
                
                # Check if this should be the canonical version
                if latest_update is None or update_time > latest_update:
                    # Verify the file is in the correct directory for its status
                    expected_dir = status_dirs.get(status)
                    if expected_dir and file_path.parent == expected_dir:
                        canonical_file = file_path
                        canonical_data = task_data
                        latest_update = update_time
                        print(f"    ✅ This is canonical (correct location + latest)")
            
            # If no canonical version found in correct location, use most recent
            if canonical_file is None:
                for file_path, task_data in file_list:
                    updated_at = task_data.get('updated_at')
                    if isinstance(updated_at, str):
                        try:
                            update_time = datetime.fromisoformat(updated_at.replace('+00:00', ''))
                        except:
                            update_time = datetime.min
                    else:
                        update_time = datetime.min
                    
                    if latest_update is None or update_time > latest_update:
                        canonical_file = file_path
                        canonical_data = task_data
                        latest_update = update_time
                
                print(f"    ⚠️  Using most recent as canonical: {canonical_file}")
            
            # Remove duplicate files
            for file_path, task_data in file_list:
                if file_path != canonical_file:
                    print(f"    🗑️  Removing duplicate: {file_path}")
                    file_path.unlink()
                    files_removed += 1
    
    print(f"\n📊 Summary:")
    print(f"  Duplicated tasks found: {duplicates_found}")
    print(f"  Duplicate files removed: {files_removed}")
    print(f"  Tasks cleaned up: {duplicates_found}")

if __name__ == '__main__':
    main()