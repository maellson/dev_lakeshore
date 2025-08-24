from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from decimal import Decimal

User = get_user_model()


class ModelTask(models.Model):
    """
    Template model for tasks - reusable patterns  
    BUSINESS LOGIC:
    - Defines specific tasks that should be executed in each phase
    - Templates for consistent task execution across projects
    - Resource requirements and skill specifications
    - Quality control and safety measures
    """

    TASK_TYPE_CHOICES = [
        ('PREPARATION', 'Preparation'),
        ('MATERIAL', 'Material/Supplies'),
        ('INTERNAL_SERVICE', 'Internal Service'),
        ('SUBCONTRACTED', 'Subcontracted Service'),
        ('INSPECTION', 'Inspection'),
        ('DOCUMENTATION', 'Documentation'),
        ('ADMINISTRATIVE', 'Administrative'),
        ('CLEANUP', 'Cleanup/Organization'),
        ('QUALITY_CONTROL', 'Quality Control'),
    ]

    SKILL_CATEGORY_CHOICES = [
        ('BASIC', 'Basic'),
        ('SPECIALIZED', 'Specialized'),
        ('TECHNICAL', 'Technical'),
        ('MANAGERIAL', 'Managerial'),
    ]

    # Relationship with model phase
    model_phase = models.ForeignKey(
        'projects.ModelPhase',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Model Phase"
    )

    # Task identification
    task_name = models.CharField(
        max_length=200,
        verbose_name="Task Name",
        help_text="Descriptive name of the task"
    )

    task_code = models.CharField(
        max_length=20,
        verbose_name="Task Code",
        help_text="Unique code for identification"
    )

    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        verbose_name="Task Type"
    )

    # Detailed description
    detailed_description = models.TextField(
        verbose_name="Detailed Description",
        help_text="Complete description of how to execute the task"
    )

    task_objective = models.TextField(
        verbose_name="Task Objective",
        help_text="What should be achieved with this task",
        blank=True
    )

    # Time and execution
    estimated_duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.1)],
        verbose_name="Estimated Duration (hours)",
        help_text="Estimated time for execution in hours"
    )

    execution_order = models.IntegerField(
        verbose_name="Execution Order",
        help_text="Execution order within the phase",
        validators=[MinValueValidator(1)]
    )

    # Task characteristics
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name="Is Mandatory",
        help_text="Whether this task is mandatory for the phase"
    )

    allows_parallel = models.BooleanField(
        default=True,
        verbose_name="Allows Parallel Execution",
        help_text="Whether it can be executed in parallel with other tasks"
    )

    requires_specialization = models.BooleanField(
        default=False,
        verbose_name="Requires Specialization",
        help_text="Whether it requires specialized labor"
    )

    skill_category = models.CharField(
        max_length=15,
        choices=SKILL_CATEGORY_CHOICES,
        default='BASIC',
        verbose_name="Required Skill Category"
    )

    # Dependencies
    prerequisite_tasks = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_tasks',
        verbose_name="Prerequisite Tasks",
        help_text="Tasks that must be completed before this one"
    )

    # Human resources
    required_people = models.IntegerField(
        verbose_name="Required People",
        help_text="Number of people needed to execute",
        validators=[MinValueValidator(1)],
        default=1
    )

    required_skills = models.TextField(
        verbose_name="Required Skills",
        help_text="Description of specific skills needed",
        blank=True
    )

    # Special requirements
    special_requirements = models.TextField(
        verbose_name="Special Requirements",
        help_text="Special requirements for executing this task",
        blank=True
    )

    execution_conditions = models.TextField(
        verbose_name="Execution Conditions",
        help_text="Required conditions for execution (weather, time, etc.)",
        blank=True
    )

    required_equipment = models.TextField(
        verbose_name="Required Equipment",
        help_text="List of required equipment",
        blank=True
    )

    # Quality control
    acceptance_criteria = models.TextField(
        verbose_name="Acceptance Criteria",
        help_text="Criteria to consider the task completed",
        blank=True
    )

    checkpoints = models.TextField(
        verbose_name="Quality Checkpoints",
        help_text="Points to verify during/after execution",
        blank=True
    )

    # Safety and risks
    identified_risks = models.TextField(
        verbose_name="Identified Risks",
        help_text="Main risks associated with this task",
        blank=True
    )

    safety_measures = models.TextField(
        verbose_name="Safety Measures",
        help_text="Safety measures to be observed",
        blank=True
    )

    required_ppe = models.TextField(
        verbose_name="Required PPE",
        help_text="Required personal protective equipment",
        blank=True
    )

    cost_subgroup = models.ForeignKey(
        'projects.CostSubGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name="Cost SubGroup",
        help_text="Cost subgroup for this task"
    )

    # Estimated costs
    estimated_labor_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Estimated Labor Cost",
        help_text="Estimated labor cost for this task",
        default=0
    )

    # Status and control
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this task is active in the model"
    )

    version = models.CharField(
        max_length=10,
        verbose_name="Version",
        default="1.0"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_model_tasks',
        verbose_name="Created By"
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Model Task"
        verbose_name_plural = "Model Tasks"
        ordering = ['model_phase', 'execution_order']
        unique_together = [
            ['model_phase', 'task_code'],
            ['model_phase', 'execution_order']
        ]
        indexes = [
            models.Index(fields=['model_phase']),
            models.Index(fields=['task_code']),
            models.Index(fields=['task_type']),
            models.Index(fields=['execution_order']),
            models.Index(fields=['is_mandatory']),
            models.Index(fields=['requires_specialization']),
        ]

    def __str__(self):
        return f"{self.execution_order:02d}. {self.task_name} ({self.model_phase.phase_name})"

    @property
    def total_resources(self):
        """Total resources defined for this task"""
        return self.resources.count()

    @property
    def material_resources(self):
        """Material type resources"""
        return self.resources.filter(resource_type='MATERIAL')

    @property
    def equipment_resources(self):
        """Equipment type resources"""
        return self.resources.filter(resource_type='EQUIPMENT')

    @property
    def human_resources(self):
        """Human type resources"""
        return self.resources.filter(resource_type='HUMAN')

    @property
    def total_resource_cost(self):
        """Total cost of required resources"""
        total = Decimal('0.00')

        for resource in self.resources.all():
            total += resource.estimated_total_cost

        return total + self.estimated_labor_cost

    @property
    def total_time_hours(self):
        """Total time including setup and cleanup"""
        base_time = self.estimated_duration_hours
        if base_time is None:
            return Decimal('0.0')
        # Add 10% for setup and cleanup
        return base_time * Decimal('1.1')

    def get_blocking_tasks(self):
        """Returns tasks that prevent this task from starting"""
        return self.prerequisite_tasks.filter(is_active=True)

    def get_dependent_tasks(self):
        """Returns tasks that depend on this task"""
        return self.dependent_tasks.filter(is_active=True)

    def can_execute_parallel_with(self, other_task):
        """Checks if can be executed in parallel with another task"""
        if not self.allows_parallel or not other_task.allows_parallel:
            return False

        # Check if one is prerequisite of the other
        if (self in other_task.get_blocking_tasks() or
                other_task in self.get_blocking_tasks()):
            return False

        # Check if they compete for same specialized resources
        if (self.requires_specialization and other_task.requires_specialization and
                self.skill_category == other_task.skill_category):
            return False

        return True

    def duplicate_to_phase(self, new_phase):
        """Duplicates this task to another phase"""
        new_task = ModelTask.objects.create(
            model_phase=new_phase,
            task_name=self.task_name,
            task_code=self.task_code,
            task_type=self.task_type,
            detailed_description=self.detailed_description,
            task_objective=self.task_objective,
            estimated_duration_hours=self.estimated_duration_hours,
            execution_order=self.execution_order,
            is_mandatory=self.is_mandatory,
            allows_parallel=self.allows_parallel,
            requires_specialization=self.requires_specialization,
            skill_category=self.skill_category,
            required_people=self.required_people,
            required_skills=self.required_skills,
            special_requirements=self.special_requirements,
            execution_conditions=self.execution_conditions,
            required_equipment=self.required_equipment,
            acceptance_criteria=self.acceptance_criteria,
            checkpoints=self.checkpoints,
            identified_risks=self.identified_risks,
            safety_measures=self.safety_measures,
            required_ppe=self.required_ppe,
            cost_subgroup=self.cost_subgroup,
            estimated_labor_cost=self.estimated_labor_cost,
            version="1.0"
        )
        # Duplicate resources
        for resource in self.resources.all():
            from .task_resource import TaskResource
            TaskResource.objects.create(
                model_task=new_task,
                resource_name=resource.resource_name,
                resource_type=resource.resource_type,
                required_quantity=resource.required_quantity,
                unit_measure=resource.unit_measure,
                estimated_unit_cost=resource.estimated_unit_cost,
                is_mandatory=resource.is_mandatory,
                created_by=resource.created_by
            )

        return new_task
