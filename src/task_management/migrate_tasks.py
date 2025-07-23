#!/usr/bin/env python3
"""
Task Migration Script

Fixes existing task files to match the expected YAML frontmatter format.
"""

import os
import yaml
from pathlib import Path
import re
from typing import Dict, Any

def fix_task_file(file_path: Path) -> bool:
    """Fix a single task file to proper YAML frontmatter format"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Skip if already has proper YAML frontmatter
        if content.startswith('---') and '---' in content[3:]:
            return False
        
        # Parse existing content assuming it's YAML without delimiters
        lines = content.split('\n')
        yaml_lines = []
        markdown_lines = []
        in_yaml = True
        
        for line in lines:
            if in_yaml and (line.strip() == '' or ':' in line or line.startswith(' ') or line.startswith('-')):
                yaml_lines.append(line)
            elif in_yaml and line.strip() and not (':' in line or line.startswith(' ') or line.startswith('-')):
                # End of YAML, start of markdown
                in_yaml = False
                markdown_lines.append(line)
            else:
                markdown_lines.append(line)
        
        # Try to parse the YAML part
        yaml_content = '\n'.join(yaml_lines)
        try:
            task_data = yaml.safe_load(yaml_content)
            if not isinstance(task_data, dict):
                return False
        except:
            return False
        
        # Remove problematic fields that aren't in the Task schema
        problematic_fields = ['Steps', 'epic_type', 'Tasks requiring updates']
        for field in problematic_fields:
            if field in task_data:
                # Move to description if it's Steps
                if field == 'Steps' and 'description' in task_data:
                    if isinstance(task_data['description'], str):
                        task_data['description'] += f"\n\nSteps:\n{task_data[field]}"
                del task_data[field]
        
        # Ensure required fields
        if 'id' not in task_data:
            task_data['id'] = file_path.stem.lower().replace('_', '-')
        if 'title' not in task_data:
            task_data['title'] = file_path.stem.replace('_', ' ').title()
        if 'description' not in task_data:
            task_data['description'] = 'Task description needed'
        if 'agent' not in task_data:
            task_data['agent'] = 'ARCHAIOS_PRIME'
        if 'status' not in task_data:
            # Infer from directory
            parent_name = file_path.parent.name
            if parent_name == 'backlog':
                task_data['status'] = 'blocked'
            elif parent_name == 'todo':
                task_data['status'] = 'todo'
            elif parent_name == 'done':
                task_data['status'] = 'complete'
            else:
                task_data['status'] = 'pending'
        if 'priority' not in task_data:
            task_data['priority'] = 'medium'
        
        # Write the fixed content
        new_content = "---\n"
        new_content += yaml.dump(task_data, default_flow_style=False, sort_keys=False)
        new_content += "---\n"
        
        if markdown_lines:
            new_content += "\n" + '\n'.join(markdown_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Fixed: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def migrate_all_tasks(tasks_root: str = "tasks"):
    """Migrate all task files in the tasks directory"""
    tasks_path = Path(tasks_root)
    if not tasks_path.exists():
        print(f"❌ Tasks directory not found: {tasks_path}")
        return
    
    fixed_count = 0
    total_count = 0
    
    for md_file in tasks_path.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        
        total_count += 1
        if fix_task_file(md_file):
            fixed_count += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"   Total files: {total_count}")
    print(f"   Fixed files: {fixed_count}")
    print(f"   Unchanged files: {total_count - fixed_count}")

if __name__ == "__main__":
    migrate_all_tasks()