# AGENT_INIT.md

# Phase 0: Introduction and Systematic Analysis
  🔍 Repository Analysis and AGENTS.md Creation Prompt

  Use this systematic approach to analyze any codebase and create a comprehensive AGENTS.md file for future AI agent interactions.

  Phase 1: Initial Repository Exploration

  Goal: Understand the project structure and basic configuration

  1. List the root directory to see overall structure

  2. Read core configuration files:
     - README.md (project overview)
     - requirements.txt / package.json / Cargo.toml (dependencies)
     - LICENSE (licensing information)
     - .gitignore (excluded files/patterns)

  3. Check for existing documentation:
     - docs/ directory contents
     - Any existing AGENTS.md or similar files (CLAUDE.md, GEMINI.md or similar)
     - API documentation files

  Phase 2: Architecture Deep Dive

  Goal: Understand the codebase organization and key components

  4. Explore source code structure:
     - Main source directories (src/, lib/, app/, etc.)
     - Read __init__.py / index files to understand exports
     - Identify core modules/components

  5. Read key implementation files (first 50-100 lines):
     - Main entry points
     - Core business logic files
     - Configuration/setup files

  6. Search for development infrastructure:
     - Test files (**/*test*, **/test_*, **/*.spec.*)
     - Build configuration (setup.py, pyproject.toml, Makefile, etc.)
     - CI/CD files (.github/, .gitlab-ci.yml, etc.)
     - Development rules (.cursorrules, .cursor/rules/, etc.)

  Phase 3: Project Context Analysis

  Goal: Understand the project's purpose, dependencies, and usage patterns

  7. Analyze project type and domain:
     - Read existing documentation for context
     - Check for example files or sample data
     - Look for configuration templates or examples

  8. Identify key dependencies and integrations:
     - External libraries and frameworks used
     - Database connections or data storage
     - API integrations or external services

  9. Check for operational considerations:
     - Deployment configurations
     - Environment setup requirements
     - Logging and monitoring setup

  Phase 4: Development Workflow Discovery

  Goal: Understand how developers work with this codebase

  10. Look for development commands and scripts:
      - Build commands
      - Test execution methods
      - Linting and formatting tools
      - Development server startup

  11. Identify common development patterns:
      - Code organization conventions
      - Testing strategies
      - Documentation generation methods
      - Release/deployment processes

  Phase 5: AGENTS.md Creation

  Goal: Create a comprehensive guide for future AI agents

  12. Create AGENTS.md with these sections:

  # AGENTS.md
  This file provides guidance to AGENTS when working with code in this repository.

  ## Project Overview
  - Brief description of what the project does
  - Key technologies and frameworks used
  - Architecture overview (if complex)

  ## Development Commands
  - How to install dependencies
  - How to run/build the project
  - How to run tests
  - How to lint/format code
  - How to generate documentation

  ## Architecture
  - Directory structure explanation
  - Key components and their relationships
  - Data flow or system design (if applicable)
  - Important design patterns or conventions

  ## Dependencies
  - Key external dependencies and their purposes
  - Development vs production dependencies
  - Any special setup requirements

  ## Development Notes
  - Code style conventions
  - Testing strategies
  - Common gotchas or important considerations
  - Integration points with external systems

  ## Current Status
  - Implementation completeness
  - Known issues or limitations
  - Areas for improvement

  Example Tool Usage Pattern

  When implementing this process, use tools in this sequence:

  # Phase 1: Basic exploration
  LS(.)
  READ(README.md)
  READ(requirements.txt) # or package.json, Cargo.toml, etc.

  # Phase 2: Architecture discovery  
  READ(docs/main-documentation.md) # if exists
  LS(src/) # or main source directory
  READ(src/__init__.py) # or main entry point

  # Phase 3: Implementation sampling
  READ(src/core-module.py, limit=50) # sample key files
  GLOB(**/*test*)  # find test files
  GLOB(**/setup.py) # find build configs

  # Phase 4: Context gathering
  READ(examples/sample.config) # if examples exist
  BASH(find . -name "Makefile" -o -name "*.yml") # find build/CI files

  # Phase 5: Documentation creation
  WRITE(AGENTS.md) # create comprehensive guide

  Quality Checklist

  Before completing the analysis, ensure:

  - Project purpose is clearly understood and documented
  - Key development commands are identified and tested (if possible)
  - Architecture is explained at appropriate level of detail
  - Dependencies and their roles are documented
  - Any special setup or gotchas are noted
  - AGENTS.md is comprehensive but concise
  - Focus is on practical information for development work

  Adaptive Analysis

  For different project types, emphasize:

  - Web applications: API endpoints, database schema, deployment
  - Libraries/packages: Public API, usage examples, integration patterns
  - CLI tools: Command structure, configuration options, usage patterns
  - Data/ML projects: Data pipeline, model architecture, training/inference
  - Infrastructure: Configuration management, deployment patterns, monitoring

  This systematic approach ensures thorough analysis while creating actionable documentation for future AI agent interactions.