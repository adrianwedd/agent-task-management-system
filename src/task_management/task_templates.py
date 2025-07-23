"""
Task Templates System

Provides predefined task templates for common agent workflows,
ensuring consistency and reducing setup time for recurring task types.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .task_manager import Task, TaskStatus, TaskPriority


@dataclass
class TaskTemplate:
    """Represents a task template"""
    id: str
    name: str
    description: str
    agent: str
    priority: TaskPriority
    estimated_hours: Optional[float] = None
    tags: List[str] = None
    dependencies_pattern: List[str] = None  # Patterns for common dependencies
    description_template: str = ""
    checklist: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies_pattern is None:
            self.dependencies_pattern = []
        if self.checklist is None:
            self.checklist = []


class TaskTemplates:
    """Manages task templates for the project"""
    
    def __init__(self):
        self.templates = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self) -> None:
        """Initialize default task templates for common workflows"""
        
        # Research and Analysis Templates
        self.add_template(TaskTemplate(
            id="research-investigation",
            name="Research Investigation",
            description="""Research and investigate {topic}.""",
            agent="ResearchOracle",
            priority=TaskPriority.MEDIUM,
            estimated_hours=8.0,
            tags=["research", "analysis"],
            description_template="""
Research and investigate {topic}.

## Objectives
- Understand current state of {topic}
- Identify key challenges and opportunities
- Gather relevant data and evidence
- Provide actionable recommendations

## Deliverables
- [ ] Research brief document
- [ ] Key findings summary
- [ ] Recommendations with rationale
- [ ] References and sources

## Research Areas
{research_areas}

## Timeline
- Literature review: 2-3 hours
- Data gathering: 3-4 hours  
- Analysis and synthesis: 2-3 hours
""",
            checklist=[
                "Define research scope and objectives",
                "Conduct literature review",
                "Gather primary and secondary data",
                "Analyze findings",
                "Document recommendations",
                "Review and validate results"
            ]
        ))
        
        # Code Development Templates
        self.add_template(TaskTemplate(
            id="feature-implementation",
            name="Feature Implementation",
            description="Implement new feature {feature_name}.",
            agent="CODEFORGE",
            priority=TaskPriority.HIGH,
            estimated_hours=16.0,
            tags=["development", "feature"],
            dependencies_pattern=["design-{feature_name}", "requirements-{feature_name}"],
            description_template="""
Implement {feature_name} feature.

## Requirements
{requirements}

## Technical Specifications
- Architecture: {architecture}
- Technologies: {technologies}
- Integration points: {integrations}

## Implementation Plan
- [ ] Set up development environment
- [ ] Implement core functionality
- [ ] Add error handling and validation
- [ ] Write unit tests
- [ ] Integration testing
- [ ] Documentation
- [ ] Code review

## Acceptance Criteria
{acceptance_criteria}

## Testing Strategy
- Unit tests for core logic
- Integration tests for API endpoints
- End-to-end tests for user workflows
""",
            checklist=[
                "Review requirements and design",
                "Set up development branch",
                "Implement core functionality",
                "Add comprehensive error handling",
                "Write unit tests (>90% coverage)",
                "Perform integration testing",
                "Update documentation",
                "Submit for code review",
                "Deploy to staging environment"
            ]
        ))
        
        # Testing Templates
        self.add_template(TaskTemplate(
            id="testing-suite",
            name="Testing Suite Development",
            description="Develop comprehensive testing suite for {feature_name}.",
            agent="TESTCRAFTERPRO",
            priority=TaskPriority.HIGH,
            estimated_hours=12.0,
            tags=["testing", "qa"],
            dependencies_pattern=["implementation-{feature_name}"],
            description_template="""
Develop comprehensive testing suite for {feature_name}.

## Testing Scope
{testing_scope}

## Test Types
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Performance tests
- [ ] Security tests

## Test Scenarios
{test_scenarios}

## Coverage Requirements
- Minimum 90% code coverage
- All critical paths tested
- Edge cases and error conditions covered

## Tools and Frameworks
{testing_tools}
""",
            checklist=[
                "Analyze testing requirements",
                "Design test strategy",
                "Implement unit tests",
                "Develop integration tests",
                "Create end-to-end test scenarios",
                "Set up automated test execution",
                "Generate coverage reports",
                "Document test procedures"
            ]
        ))
        
        # Compliance and Regulatory Templates
        self.add_template(TaskTemplate(
            id="compliance-review",
            name="Compliance Review",
            description="Review compliance for {subject}.",
            agent="COMPLIANCE_SENTINEL", 
            priority=TaskPriority.HIGH,
            estimated_hours=6.0,
            tags=["compliance", "regulatory", "review"],
            description_template="""
Conduct compliance review for {subject}.

## Regulatory Framework
{regulatory_framework}

## Review Areas
- [ ] Regulatory compliance assessment
- [ ] Risk identification and mitigation
- [ ] Documentation review
- [ ] Process validation
- [ ] Stakeholder impact analysis

## Compliance Checklist
{compliance_checklist}

## Deliverables
- Compliance assessment report
- Risk register updates
- Mitigation action plan
- Approval recommendations
""",
            checklist=[
                "Review applicable regulations",
                "Assess current compliance status",
                "Identify gaps and risks",
                "Develop mitigation strategies",
                "Document findings and recommendations",
                "Present to governance team"
            ]
        ))
        
        # Security Assessment Templates
        self.add_template(TaskTemplate(
            id="security-assessment",
            name="Security Assessment",
            description="Conduct security assessment for {target_system}.",
            agent="SECSENTINEL",
            priority=TaskPriority.HIGH,
            estimated_hours=10.0,
            tags=["security", "assessment", "audit"],
            description_template="""
Conduct security assessment for {target_system}.

## Assessment Scope
{assessment_scope}

## Security Domains
- [ ] Authentication and authorization
- [ ] Data protection and encryption
- [ ] Network security
- [ ] Application security
- [ ] Infrastructure security
- [ ] Incident response readiness

## Threat Model
{threat_model}

## Assessment Methods
- Automated vulnerability scanning
- Manual security testing
- Configuration review
- Code security analysis
""",
            checklist=[
                "Define assessment scope and objectives",
                "Conduct automated vulnerability scans",
                "Perform manual security testing",
                "Review security configurations",
                "Analyze code for security issues",
                "Document findings and recommendations",
                "Create remediation action plan"
            ]
        ))
        
        # Environmental Monitoring Templates
        self.add_template(TaskTemplate(
            id="environmental-assessment",
            name="Environmental Assessment",
            description="Conduct environmental assessment for {project_area}.",
            agent="ECOSENTRY",
            priority=TaskPriority.MEDIUM,
            estimated_hours=12.0,
            tags=["environmental", "monitoring", "sustainability"],
            description_template="""
Conduct environmental assessment for {project_area}.

## Assessment Areas
- [ ] Biodiversity impact analysis
- [ ] Water resource assessment
- [ ] Soil quality evaluation
- [ ] Air quality monitoring
- [ ] Waste impact assessment
- [ ] Carbon footprint analysis

## Methodology
{methodology}

## Data Collection
- Site surveys and measurements
- Historical data analysis
- Stakeholder consultations
- Regulatory database review

## Deliverables
- Environmental impact report
- Mitigation recommendations
- Monitoring protocol
- Compliance verification
""",
            checklist=[
                "Plan assessment methodology",
                "Conduct site surveys",
                "Collect environmental data",
                "Analyze impacts and risks",
                "Develop mitigation strategies",
                "Create monitoring protocols",
                "Prepare compliance documentation"
            ]
        ))
        
        # Agent Coordination Templates
        self.add_template(TaskTemplate(
            id="agent-coordination",
            name="Agent Coordination Task",
            description="Coordinate decision-making process for {decision_topic}.",
            agent="CONSENSUS_ENGINE",
            priority=TaskPriority.HIGH,
            estimated_hours=4.0,
            tags=["coordination", "consensus", "decision"],
            description_template="""
Coordinate decision-making process for {decision_topic}.

## Decision Context
{decision_context}

## Stakeholder Agents
{stakeholder_agents}

## Decision Criteria
{decision_criteria}

## Coordination Process
- [ ] Gather agent input and recommendations
- [ ] Facilitate consensus-building discussions
- [ ] Apply decision-making framework
- [ ] Document consensus or escalation
- [ ] Communicate decision to all stakeholders

## Timeline
- Input gathering: {input_timeline}
- Consensus building: {consensus_timeline}
- Decision finalization: {decision_timeline}
""",
            checklist=[
                "Define decision scope and criteria",
                "Identify stakeholder agents",
                "Gather input from all agents",
                "Facilitate consensus discussions",
                "Apply voting/weighting if needed",
                "Document final decision",
                "Communicate to all stakeholders",
                "Update relevant documentation"
            ]
        ))
        
        # Workload Redistribution Template
        self.add_template(TaskTemplate(
            id="workload-redistribution",
            name="Agent Workload Redistribution",
            description="Redistribute tasks from overloaded agent {overloaded_agent} to optimize system throughput.",
            agent="TASK_VERIFIER_REWRITER",
            priority=TaskPriority.HIGH,
            estimated_hours=3.0,
            tags=["workload-balancing", "agent-coordination", "system-optimization"],
            description_template="""
Redistribute tasks from overloaded agent {overloaded_agent} to optimize system throughput.

## Current Workload Analysis
- Overloaded agent: {overloaded_agent}
- Current task count: {current_task_count}
- Target agents: {target_agents}
- Redistribution strategy: {redistribution_strategy}

## Task Redistribution Plan
- [ ] Analyze task types and agent capabilities
- [ ] Identify suitable target agents for each task type
- [ ] Update task assignments maintaining context
- [ ] Verify dependency chains remain intact
- [ ] Update agent workload tracking

## Quality Assurance
- [ ] Validate task continuity
- [ ] Confirm agent capability matches
- [ ] Test dependency resolution
- [ ] Monitor system performance post-redistribution

## Expected Outcomes
- Balanced workload across agents
- Improved system throughput by {throughput_improvement}
- Reduced bottlenecks in critical workflows
""",
            checklist=[
                "Analyze current workload distribution",
                "Identify task redistribution opportunities",
                "Map tasks to optimal agents based on capabilities",
                "Update task assignments systematically",
                "Validate dependency chains remain intact",
                "Monitor system performance improvements",
                "Document redistribution decisions"
            ]
        ))
        
        # Documentation Templates
        self.add_template(TaskTemplate(
            id="documentation-update",
            name="Documentation Update",
            description="Update project documentation for {documentation_area}.",
            agent="NARRATIVE_WARDEN",
            priority=TaskPriority.MEDIUM,
            estimated_hours=4.0,
            tags=["documentation", "communication"],
            description_template="""
Update project documentation for {documentation_area}.

## Documentation Scope
{documentation_scope}

## Update Requirements
- [ ] Content accuracy review
- [ ] Structural improvements
- [ ] Accessibility compliance
- [ ] Version control updates
- [ ] Cross-reference validation

## Target Audiences
{target_audiences}

## Documentation Standards
- Clear, concise language
- Consistent formatting
- Proper version control
- Accessibility compliance
- Regular review schedule
""",
            checklist=[
                "Review current documentation",
                "Identify update requirements",
                "Draft content updates",
                "Review for accuracy and clarity",
                "Validate cross-references",
                "Update version control",
                "Publish and communicate changes"
            ]
        ))
    
    def add_template(self, template: TaskTemplate) -> None:
        """Add a new task template"""
        self.templates[template.id] = template
    
    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, agent: str = None, tags: List[str] = None) -> List[TaskTemplate]:
        """List available templates, optionally filtered by agent or tags"""
        templates = list(self.templates.values())
        
        if agent:
            templates = [t for t in templates if t.agent == agent]
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        return templates
    
    def create_task_from_template(self, template_id: str, **kwargs) -> Optional[Task]:
        """Create a new task from a template with custom values"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Extract custom values
        task_id = kwargs.get('task_id', f"{template_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        title = kwargs.get('title', template.name)
        
        # Process description template
        description = template.description_template
        for key, value in kwargs.items():
            if isinstance(value, str):
                description = description.replace(f"{{{key}}}", value)
        
        # Process dependencies
        dependencies = kwargs.get('dependencies', [])
        for pattern in template.dependencies_pattern:
            for key, value in kwargs.items():
                if isinstance(value, str):
                    processed_dep = pattern.replace(f"{{{key}}}", value)
                    if processed_dep != pattern:  # Only add if pattern was replaced
                        dependencies.append(processed_dep)
        
        # Create task
        task = Task(
            id=task_id,
            title=title,
            description=description,
            agent=kwargs.get('agent', template.agent),
            status=TaskStatus.TODO,
            priority=kwargs.get('priority', template.priority),
            estimated_hours=kwargs.get('estimated_hours', template.estimated_hours),
            tags=kwargs.get('tags', template.tags.copy()),
            dependencies=dependencies,
            due_date=kwargs.get('due_date'),
            notes=kwargs.get('notes')
        )
        
        return task
    
    def get_template_suggestions(self, agent: str) -> List[TaskTemplate]:
        """Get template suggestions for a specific agent"""
        agent_templates = self.list_templates(agent=agent)
        
        # Sort by relevance (could be enhanced with ML)
        return sorted(agent_templates, key=lambda t: len(t.checklist), reverse=True)
    
    def validate_template(self, template: TaskTemplate) -> List[str]:
        """Validate a task template"""
        errors = []
        
        if not template.id:
            errors.append("Template ID is required")
        
        if not template.name:
            errors.append("Template name is required")
        
        if not template.agent:
            errors.append("Template agent is required")
        
        if not template.description_template:
            errors.append("Template description is required")
        
        # Check for placeholder consistency
        placeholders = set()
        import re
        placeholder_pattern = re.compile(r'\{([^}]+)\}')
        
        for match in placeholder_pattern.finditer(template.description_template):
            placeholders.add(match.group(1))
        
        if placeholders and not template.checklist:
            errors.append("Templates with placeholders should include a checklist")
        
        return errors
    
    def export_templates(self, filepath: str) -> bool:
        """Export templates to JSON file"""
        try:
            import json
            from dataclasses import asdict
            
            templates_data = {}
            for template_id, template in self.templates.items():
                template_dict = asdict(template)
                template_dict['priority'] = template.priority.value
                templates_data[template_id] = template_dict
            
            with open(filepath, 'w') as f:
                json.dump(templates_data, f, indent=2)
            
            return True
        except Exception as e:
            return False
    
    def import_templates(self, filepath: str) -> bool:
        """Import templates from JSON file"""
        try:
            import json
            
            with open(filepath, 'r') as f:
                templates_data = json.load(f)
            
            for template_id, template_dict in templates_data.items():
                template_dict['priority'] = TaskPriority(template_dict['priority'])
                template = TaskTemplate(**template_dict)
                self.add_template(template)
            
            return True
        except Exception as e:
            return False