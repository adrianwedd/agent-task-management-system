# Harmonize Status Names with Folder Names and Enable File Move Automation

**ID:** harmonize-status-folder-automation  
**Title:** Harmonize Status Names with Folder Names and Enable File Move Automation  
**Agent:** DEVELOPER  
**Status:** pending  
**Priority:** high  
**Estimated Hours:** 8  
**Created:** 2025-07-24 05:20  
**Updated:** 2025-07-24 05:20  

## Description

Create a comprehensive system to harmonize task status names with their corresponding folder structures and implement automation that automatically updates task status when files are moved between folders. This will ensure consistency between the file system organization and internal task status tracking.

## Current Status-Folder Mapping Issues

1. **Status vs Folder Name Mismatches:**
   - Status: `in_progress` vs Folder: `in-progress/`
   - Status: `complete` vs Folder: `completed/` 
   - Inconsistent naming conventions between internal enums and directory structure

2. **Manual Status Updates:**
   - Moving files between folders requires separate manual status updates
   - Risk of status/location inconsistencies
   - No automated synchronization mechanism

## Requirements

### 1. Status-Folder Name Harmonization
- Audit all current status names vs folder names
- Decide on consistent naming convention (snake_case vs kebab-case)
- Update either TaskStatus enum or folder structure for consistency
- Ensure backward compatibility with existing tasks

### 2. File Move Detection & Automation
- Implement file system monitoring for task file moves
- Automatic status updates when files are moved between status folders
- Validation to ensure moves are to valid status directories
- Logging of automated status changes

### 3. Bidirectional Synchronization
- Status changes in CLI/API should optionally move files to correct folders
- File moves should update internal task status
- Conflict resolution for simultaneous changes
- Configuration options for automation level

### 4. Migration Strategy
- Safe migration of existing tasks to new harmonized structure
- Rollback capability in case of issues
- Preservation of task history and metadata during moves

## Technical Implementation

### Phase 1: Analysis & Planning
- Map current status values to folder names
- Identify naming inconsistencies
- Design unified naming convention
- Plan migration strategy

### Phase 2: Core Infrastructure
- Update TaskStatus enum if needed
- Implement file move detection (using watchdog or similar)
- Create status-folder mapping configuration
- Add automated status update logic

### Phase 3: Bidirectional Sync
- Extend TaskManager with folder move capabilities
- Add CLI options for automatic file organization
- Implement conflict resolution logic
- Add comprehensive logging for all moves

### Phase 4: Migration & Testing
- Create migration script for existing tasks
- Comprehensive testing of automation
- Documentation and user guidelines
- Rollback procedures

## Acceptance Criteria

- [ ] All status names match their corresponding folder names exactly
- [ ] Moving a task file between folders automatically updates its status
- [ ] Status changes via CLI/API optionally move files to correct folders
- [ ] No existing tasks are lost or corrupted during migration
- [ ] Comprehensive logging of all automated changes
- [ ] Configuration options for automation level (off/semi/full)
- [ ] Full backward compatibility maintained
- [ ] Performance impact is minimal (< 100ms for status changes)

## Dependencies

- Current task management system must be stable
- File system permissions for monitoring and moving files
- Backup system should be in place before migration

## Tags

file-system, automation, status-management, synchronization, consistency

## Notes

This enhancement will significantly improve the user experience by eliminating the need for manual status updates when organizing tasks via file system operations. It's a key step toward making the task management system more intuitive and less error-prone.