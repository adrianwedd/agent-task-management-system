# Agent Task Management System

A comprehensive, intelligent task management system designed for agent-based workflows with advanced automation, emoji-enhanced organization, and powerful CLI tools.

## 🚀 Key Features

### 🎯 **Intelligent Task Management**
- **Multi-Agent Workflow Support** - Coordinate tasks across multiple specialized agents
- **Smart Dependency Resolution** - Automatic blocking and unblocking based on dependencies
- **Priority-Based Routing** - Intelligent task placement in appropriate workflow stages
- **Auto-Fix System** - Automatic correction of common task issues and status conflicts

### 🎨 **Visual Organization**
- **Emoji Directory Structure** - Intuitive workflow visualization with emoji folders:
  - 📦 backlog - Future work queue
  - 🚫 blocked - Dependency-blocked tasks  
  - 📋 todo - Ready for immediate work
  - 🔄 in-progress - Currently active tasks
  - ✅ done - Completed work
  - ❌ cancelled - Cancelled tasks

### 🛠️ **Powerful CLI Interface**
- **Comprehensive Commands** - Create, update, list, validate, and analyze tasks
- **Rich Formatting** - Color-coded output with emoji indicators for quick recognition
- **Flexible Filtering** - Filter by agent, status, priority, tags, or custom criteria
- **Smart Defaults** - Hides completed tasks by default, includes when needed

### 📊 **Analytics & Reporting**
- **Performance Metrics** - Task completion rates, cycle times, and velocity trends
- **Agent Analytics** - Individual and team performance insights
- **Bottleneck Detection** - Identify workflow impediments and resource constraints
- **Dependency Analysis** - Critical path analysis and dependency risk assessment

### 🔧 **Advanced Automation**
- **Validation System** - Comprehensive task integrity checking with configurable rules
- **Automated Status Updates** - Smart status transitions based on dependency resolution
- **File Organization** - Automatic file placement and movement based on status changes
- **Enhanced Logging** - Emoji-enhanced logging for better UX and debugging

## 📁 Project Structure

```
📦 agent-task-management-system/
├── 📋 src/
│   └── task_management/
│       ├── task_manager.py      # Core task management logic
│       ├── cli.py              # Command-line interface
│       ├── task_validator.py   # Validation and auto-fix system
│       ├── task_analytics.py   # Analytics and reporting
│       └── task_templates.py   # Task template system
├── 📂 tasks/                   # Task storage (emoji directories)
│   ├── 📦 backlog/            # Future work
│   ├── 🚫 blocked/            # Dependency-blocked
│   ├── 📋 todo/               # Ready to work
│   ├── 🔄 in-progress/        # Active work
│   ├── ✅ done/               # Completed
│   └── ❌ cancelled/          # Cancelled
├── 📊 utils/
│   └── logger.py              # Enhanced logging system
└── 📄 requirements.txt        # Dependencies
```

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/agent-task-management-system.git
   cd agent-task-management-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

**List active tasks:**
```bash
python -m src.task_management.cli list
```

**Create a new task:**
```bash
python -m src.task_management.cli create \
  --id my-task \
  --title "My New Task" \
  --description "Task description" \
  --agent DEVELOPER \
  --priority high
```

**Update task status:**
```bash
python -m src.task_management.cli status my-task in_progress
```

**View system analytics:**
```bash
python -m src.task_management.cli analytics --type overview
```

**Validate and auto-fix issues:**
```bash
python -m src.task_management.cli validate
python -m src.task_management.cli auto-fix
```

## 🎯 Advanced Features

### Smart Filtering & Views
```bash
# View tasks by agent
python -m src.task_management.cli list --agent DEVELOPER

# Show only high-priority tasks
python -m src.task_management.cli list --priority high

# Include completed tasks in output
python -m src.task_management.cli list --include-completed

# Show tasks in table format
python -m src.task_management.cli list --format table
```

### Analytics & Insights
```bash
# Agent performance analysis
python -m src.task_management.cli analytics --type agents

# Velocity and trend analysis  
python -m src.task_management.cli analytics --type velocity

# Bottleneck identification
python -m src.task_management.cli analytics --type bottlenecks

# Dependency analysis
python -m src.task_management.cli analytics --type dependencies
```

### Task Templates & Automation
```bash
# List available templates
python -m src.task_management.cli templates

# Create from template
python -m src.task_management.cli create \
  --template bug-fix \
  --template-vars severity=high component=api

# Auto-transition ready tasks
python -m src.task_management.cli auto-transition
```

## 🏗️ Agent Types

The system supports specialized agent types with specific capabilities:

- **DEVELOPER** - Implementation, coding, technical tasks
- **ARCHITECT** - System design, architecture planning
- **DESIGNER** - UI/UX, visual design, user experience
- **DOCUMENTER** - Documentation, guides, technical writing
- **ANALYST** - Research, analysis, data investigation
- **TESTCRAFTERPRO** - Testing, QA, validation
- **DEVOPS** - Deployment, infrastructure, CI/CD
- **AUTOMATION** - Process automation, scripting
- **REVIEWER** - Code review, auditing, quality checks

## 📈 System Intelligence

### Auto-Fix Capabilities
- **Dependency Status Correction** - Automatically blocks tasks with unmet dependencies
- **Agent Assignment Validation** - Suggests appropriate agents based on task content
- **File Organization** - Moves tasks to correct directories based on status
- **Tag Validation** - Enforces tag limits and suggests corrections

### Smart Prioritization
- **Dependency-Based Promotion** - Elevates priority of tasks blocking high-priority work
- **Workload Balancing** - Identifies agent overallocation and suggests redistribution
- **Critical Path Detection** - Highlights tasks on the critical path to completion

## 🔧 Configuration

The system uses intelligent defaults but supports customization:

- **Validation Rules** - Configurable limits and validation criteria
- **Agent Capabilities** - Customizable agent skill mappings
- **Directory Structure** - Flexible folder organization
- **Logging Levels** - Adjustable logging detail and emoji usage

## 📊 Performance Metrics

Track your team's performance with built-in analytics:

- **Completion Rates** - Weekly/monthly completion trends
- **Cycle Times** - Average time from creation to completion
- **Agent Utilization** - Individual and team workload analysis
- **Dependency Impact** - How dependencies affect delivery times
- **Quality Metrics** - Validation pass rates and auto-fix frequency

## 🤝 Contributing

This system is designed for professional workflows and portfolio demonstration. Key areas for contribution:

1. **Testing** - Comprehensive pytest coverage (target: 80%+)
2. **Documentation** - Enhanced guides and examples
3. **Features** - New automation and intelligence capabilities
4. **Integration** - API connections and external tool support

## 📄 License

[Add your license information here]

## 🎯 Roadmap

Planned enhancements include:
- **Text Deconstruction** - Automatic task creation from documents
- **Advanced Analytics** - ML-powered insights and predictions  
- **Mobile Interface** - Responsive web interface for mobile access
- **Integration APIs** - Connect with Jira, GitHub, Slack, and other tools
- **Real-time Collaboration** - Live updates and team coordination

---

*Built with ❤️ for intelligent task management and agent coordination*