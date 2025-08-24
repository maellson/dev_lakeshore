from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from decimal import Decimal

User = get_user_model()


class PhaseProject(models.Model):
    """
    Real project phase execution instance
    BUSINESS LOGIC:
    - Specific phase being executed in a real project
    - Based on ModelPhase template but customizable
    - Tracks actual progress, dates, costs vs planned
    - Manages task execution workflow
    - Controls phase dependencies and approvals
    """
    
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('WAITING_PREREQUISITES', 'Waiting Prerequisites'),
        ('READY_TO_START', 'Ready to Start'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED', 'Paused'),
        ('WAITING_INSPECTION', 'Waiting Inspection'),
        ('INSPECTION_FAILED', 'Inspection Failed'),
        ('COMPLETED', 'Completed'),
        ('BLOCKED', 'Blocked'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    # Main relationships
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='phases',
        verbose_name="Project"
    )
    
    model_phase = models.ForeignKey(
        'projects.ModelPhase',
        on_delete=models.PROTECT,
        related_name='project_instances',
        verbose_name="Model Phase",
        help_text="Template base for this phase"
    )
    
    prerequisite_phases = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_phases',
        verbose_name="Prerequisite Phases",
        help_text="Phases within this project that must be completed before this one"
    )
    
    # Phase information (can be customized)
    phase_name = models.CharField(
        max_length=200,
        verbose_name="Phase Name",
        help_text="Specific name for this phase in the project"
    )
    
    phase_code = models.CharField(
        max_length=20,
        verbose_name="Phase Code"
    )
    
    # Status and execution
    phase_status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='NOT_STARTED',
        verbose_name="Phase Status"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='NORMAL',
        verbose_name="Priority"
    )
    
    # Planned dates (copied from model, but can be adjusted)
    planned_start_date = models.DateField(
        verbose_name="Planned Start Date",
        help_text="Planned date to start the phase",
        null=True,
        blank=True
    )
    
    planned_end_date = models.DateField(
        verbose_name="Planned End Date",
        help_text="Planned date to finish the phase",
        null=True,
        blank=True
    )
    
    # Actual execution dates
    actual_start_date = models.DateField(
        verbose_name="Actual Start Date",
        help_text="Actual date when phase started",
        null=True,
        blank=True
    )
    
    actual_end_date = models.DateField(
        verbose_name="Actual End Date",
        help_text="Actual date when phase finished",
        null=True,
        blank=True
    )
    
    # Execution control
    execution_order = models.IntegerField(
        verbose_name="Execution Order",
        help_text="Execution order in this specific project",
        validators=[MinValueValidator(1)]
    )
    
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        default=Decimal('0.00'),
        verbose_name="Completion Percentage (%)"
    )
    
    # Responsible parties
    technical_responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phases_tech_responsible',
        verbose_name="Technical Responsible"
    )
    
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phases_supervisor',
        verbose_name="Supervisor"
    )
    
    # Project specific information
    notes = models.TextField(
        verbose_name="Notes",
        help_text="Specific notes for this phase in the project",
        blank=True
    )
    
    issues_found = models.TextField(
        verbose_name="Issues Found",
        help_text="Specific issues found during execution",
        blank=True
    )
    
    solutions_applied = models.TextField(
        verbose_name="Solutions Applied",
        help_text="Solutions applied to resolve issues",
        blank=True
    )
    
    # Specific costs
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Estimated Cost",
        help_text="Estimated cost for this phase",
        default=Decimal('0.00')
    )
    
    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Actual Cost",
        help_text="Actual cost spent on this phase",
        default=Decimal('0.00')
    )
    
    # Inspections
    requires_inspection = models.BooleanField(
        default=False,
        verbose_name="Requires Inspection"
    )
    
    inspection_scheduled_date = models.DateField(
        verbose_name="Inspection Scheduled Date",
        null=True,
        blank=True
    )
    
    inspection_completed_date = models.DateField(
        verbose_name="Inspection Completed Date",
        null=True,
        blank=True
    )
    
    inspection_result = models.CharField(
        max_length=25,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('APPROVED_WITH_CONDITIONS', 'Approved with Conditions'),
        ],
        verbose_name="Inspection Result",
        blank=True
    )
    
    inspection_notes = models.TextField(
        verbose_name="Inspection Notes",
        blank=True
    )
    
    # System control
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
        related_name='created_phase_projects',
        verbose_name="Created By"
    )
    
    history = HistoricalRecords(inherit=True)
    
    class Meta:
        verbose_name = "Phase Project"
        verbose_name_plural = "Phase Projects"
        ordering = ['project', 'execution_order']
        unique_together = [
            ['project', 'phase_code'],
            ['project', 'execution_order']
        ]
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['phase_status']),
            models.Index(fields=['planned_start_date']),
            models.Index(fields=['planned_end_date']),
            models.Index(fields=['technical_responsible']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.project.project_name} - {self.phase_name} ({self.phase_status})"
    
    @property
    def total_tasks(self):
        """Total tasks in this phase"""
        return self.tasks.count()
    
    @property
    def completed_tasks(self):
        """Total completed tasks"""
        return self.tasks.filter(task_status='COMPLETED').count()
    
    @property
    def tasks_completion_percentage(self):
        """Percentage of completed tasks"""
        total = self.total_tasks
        if total == 0:
            return Decimal('0.00')
        return (Decimal(str(self.completed_tasks)) / Decimal(str(total))) * 100
    
    @property
    def planned_duration_days(self):
        """Planned duration in days"""
        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days + 1
        return 0
    
    @property
    def actual_duration_days(self):
        """Actual execution days"""
        if self.actual_start_date and self.actual_end_date:
            return (self.actual_end_date - self.actual_start_date).days + 1
        elif self.actual_start_date:
            from django.utils import timezone
            return (timezone.now().date() - self.actual_start_date).days + 1
        return 0
    
    @property
    def is_delayed(self):
        """Checks if phase is delayed"""
        if not self.planned_end_date:
            return False
        
        from django.utils import timezone
        return (
            self.phase_status not in ['COMPLETED', 'CANCELLED'] and
            timezone.now().date() > self.planned_end_date
        )
    
    @property
    def cost_variance(self):
        """Cost variance percentage between estimated and actual"""
        if self.estimated_cost == 0:
            return Decimal('0.00')
        
        difference = self.actual_cost - self.estimated_cost
        return (difference / self.estimated_cost) * 100
    
    def can_start(self):
        """Checks if phase can be started"""
        if self.phase_status != 'READY_TO_START':
            return False
        
        # Check if all prerequisite phases are completed
        prerequisites = self.model_phase.get_blocking_phases()
        for prereq in prerequisites:
            prereq_phase = PhaseProject.objects.filter(
                project=self.project,
                model_phase=prereq
            ).first()
            
            if not prereq_phase or prereq_phase.phase_status != 'COMPLETED':
                return False
        
        return True
    
    def start_phase(self, user=None):
        """Starts phase execution"""
        if self.can_start():
            from django.utils import timezone
            self.phase_status = 'IN_PROGRESS'
            self.actual_start_date = timezone.now().date()
            if user:
                self.technical_responsible = user
            self.save()
            
            # Create tasks based on model
            self.create_tasks_from_model()
            return True
        return False
    
    def complete_phase(self, user=None):
        """Completes phase if all tasks are done"""
        if self.tasks_completion_percentage == 100:
            from django.utils import timezone
            self.phase_status = 'COMPLETED'
            self.actual_end_date = timezone.now().date()
            self.completion_percentage = Decimal('100.00')
            self.save()
            
            # Release dependent phases
            self.release_dependent_phases()
            return True
        return False
    
    def create_tasks_from_model(self):
        """Creates tasks based on phase model"""
        from .task_project import TaskProject
        
        for model_task in self.model_phase.tasks.filter(is_active=True):
            TaskProject.objects.create(
                phase_project=self,
                model_task=model_task,
                task_name=model_task.task_name,
                task_description=model_task.detailed_description,
                execution_order=model_task.execution_order,
                estimated_duration_hours=model_task.estimated_duration_hours,
                estimated_cost=model_task.estimated_labor_cost,
                created_by=self.created_by
            )
    
    def release_dependent_phases(self):
        """Updates status of phases that depend on this one"""
        dependent_phases = PhaseProject.objects.filter(
            project=self.project,
            model_phase__in=self.model_phase.get_dependent_phases()
        )
        
        for phase in dependent_phases:
            if phase.can_start():
                phase.phase_status = 'READY_TO_START'
                phase.save()