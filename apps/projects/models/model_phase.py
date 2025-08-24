from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()


class ModelPhase(models.Model):
    """
    Template model for project phases - reusable patterns
    BUSINESS LOGIC:
    - Defines standard phases for each project model type
    - Templates can be reused across multiple projects
    - Sequence and dependencies between phases
    - Estimated duration and requirements per phase
    """
    
    # Relationship with project model
    project_model = models.ForeignKey(
        'projects.ModelProject',
        on_delete=models.CASCADE,
        related_name='phases',
        verbose_name="Project Model"
    )
    
    # Phase identification
    phase_name = models.CharField(
        max_length=200,
        verbose_name="Phase Name",
        help_text="Ex: Site Preparation, Foundation, Framing"
    )
    
    phase_code = models.CharField(
        max_length=20,
        verbose_name="Phase Code",
        help_text="Unique code for identification (ex: PREP, FOUND, FRAME)"
    )
    
    # Phase description
    phase_description = models.TextField(
        verbose_name="Phase Description",
        help_text="Detailed description of what should be done in this phase"
    )
    
    phase_objectives = models.TextField(
        verbose_name="Phase Objectives",
        help_text="Main objectives and deliverables of this phase",
        blank=True
    )
    
    # Execution order and timeline
    execution_order = models.IntegerField(
        verbose_name="Execution Order",
        help_text="Sequential execution order of this phase",
        validators=[MinValueValidator(1)]
    )
    
    estimated_duration_days = models.IntegerField(
        verbose_name="Estimated Duration (days)",
        help_text="Estimated duration of this phase in days",
        validators=[MinValueValidator(1)]
    )
    
    # Phase characteristics
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name="Is Mandatory",
        help_text="Whether this phase is mandatory for the project"
    )
    
    allows_parallel = models.BooleanField(
        default=False,
        verbose_name="Allows Parallel Execution",
        help_text="Whether this phase can be executed in parallel with others"
    )
    
    requires_inspection = models.BooleanField(
        default=False,
        verbose_name="Requires Inspection",
        help_text="Whether this phase requires official inspection"
    )
    
    # Prerequisites
    prerequisite_phases = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_phases',
        verbose_name="Prerequisite Phases",
        help_text="Phases that must be completed before this one"
    )
    
    initial_requirements = models.TextField(
        verbose_name="Initial Requirements",
        help_text="Requirements that must be met before starting this phase",
        blank=True
    )
    
    
    # Completion criteria
    completion_criteria = models.TextField(
        verbose_name="Completion Criteria",
        help_text="Criteria to consider the phase completed",
        blank=True
    )
    
    deliverables = models.TextField(
        verbose_name="Deliverables",
        help_text="List of deliverables from this phase",
        blank=True
    )
    
    # Status and control
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this phase is active in the model"
    )
    
    # Version control
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
        related_name='created_model_phases',
        verbose_name="Created By"
    )
    
    history = HistoricalRecords(inherit=True)
    
    class Meta:
        verbose_name = "Model Phase"
        verbose_name_plural = "Model Phases"
        ordering = ['project_model', 'execution_order']
        unique_together = [
            ['project_model', 'phase_code'],
            ['project_model', 'execution_order']
        ]
        indexes = [
            models.Index(fields=['project_model']),
            models.Index(fields=['phase_code']),
            models.Index(fields=['execution_order']),
            models.Index(fields=['is_mandatory']),
        ]
    
    def __str__(self):
        return f"{self.execution_order:02d}. {self.phase_name} ({self.project_model.name})"
    
    @property
    def total_tasks(self):
        """Returns total tasks in this phase"""
        return self.tasks.count()
    
    @property
    def mandatory_tasks(self):
        """Returns total mandatory tasks in this phase"""
        return self.tasks.filter(is_mandatory=True).count()
    
    @property
    def total_task_duration(self):
        """Calculates total duration summing all tasks"""
        return self.tasks.aggregate(
            total=models.Sum('estimated_duration_hours')
        )['total'] or 0
    
    @property
    def can_execute_parallel(self):
        """Checks if phase can be executed in parallel"""
        return self.allows_parallel and not self.requires_inspection
    
    def get_blocking_phases(self):
        """Returns phases that prevent this phase from starting"""
        return self.prerequisite_phases.filter(is_active=True)
    
    def get_dependent_phases(self):
        """Returns phases that depend on this phase"""
        return self.dependent_phases.filter(is_active=True)
    
    def duplicate_to_model(self, new_model):
        """Duplicates this phase to another project model"""
        new_phase = ModelPhase.objects.create(
            project_model=new_model,
            phase_name=self.phase_name,
            phase_code=self.phase_code,
            phase_description=self.phase_description,
            phase_objectives=self.phase_objectives,
            execution_order=self.execution_order,
            estimated_duration_days=self.estimated_duration_days,
            is_mandatory=self.is_mandatory,
            allows_parallel=self.allows_parallel,
            requires_inspection=self.requires_inspection,
            initial_requirements=self.initial_requirements,
            completion_criteria=self.completion_criteria,
            deliverables=self.deliverables,
            version="1.0"
        )
        
        # Duplicate tasks
        for task in self.tasks.all():
            task.duplicate_to_phase(new_phase)
        
        return new_phase