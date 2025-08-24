from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from decimal import Decimal

User = get_user_model()


class TaskProject(models.Model):
    """
    Real project task execution instance
    BUSINESS LOGIC:
    - Specific task being executed in a real project
    - Based on ModelTask template but customizable
    - Tracks actual execution time, resources, costs
    - Manages task assignment and completion
    - Quality control and approval workflow
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('WAITING_RESOURCES', 'Waiting Resources'),
        ('WAITING_PREREQUISITES', 'Waiting Prerequisites'),
        ('READY_TO_START', 'Ready to Start'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED', 'Paused'),
        ('WAITING_APPROVAL', 'Waiting Approval'),
        ('REWORK_NEEDED', 'Rework Needed'),
        ('COMPLETED', 'Completed'),
        ('BLOCKED', 'Blocked'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
        ('URGENT', 'Urgent'),
    ]
    
    QUALITY_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('SATISFACTORY', 'Satisfactory'),
        ('UNSATISFACTORY', 'Unsatisfactory'),
        ('REQUIRES_REWORK', 'Requires Rework'),
    ]
    
    # Main relationships
    phase_project = models.ForeignKey(
        'projects.PhaseProject',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Phase Project"
    )
    
    model_task = models.ForeignKey(
        'projects.ModelTask',
        on_delete=models.PROTECT,
        related_name='project_instances',
        verbose_name="Model Task",
        help_text="Template base for this task"
    )
    
    # Task information (can be customized)
    task_name = models.CharField(
        max_length=200,
        verbose_name="Task Name"
    )
    
    task_code = models.CharField(
        max_length=20,
        verbose_name="Task Code"
    )
    
    task_description = models.TextField(
        verbose_name="Task Description",
        help_text="Specific description for this task in the project"
    )
    
    # Status and control
    task_status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Task Status"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        verbose_name="Priority"
    )
    
    # Execution and schedule
    execution_order = models.IntegerField(
        verbose_name="Execution Order",
        validators=[MinValueValidator(1)]
    )
    
    planned_start_date = models.DateTimeField(
        verbose_name="Planned Start Date/Time",
        null=True,
        blank=True
    )
    
    planned_end_date = models.DateTimeField(
        verbose_name="Planned End Date/Time",
        null=True,
        blank=True
    )
    
    actual_start_date = models.DateTimeField(
        verbose_name="Actual Start Date/Time",
        null=True,
        blank=True
    )
    
    actual_end_date = models.DateTimeField(
        verbose_name="Actual End Date/Time",
        null=True,
        blank=True
    )
    
    estimated_duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.1)],
        verbose_name="Estimated Duration (hours)"
    )
    
    actual_duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Actual Duration (hours)",
        default=Decimal('0.00')
    )
    
    # Responsible parties
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name="Assigned To"
    )
    
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_tasks',
        verbose_name="Supervisor"
    )
    
    # Team assignment
    team_members = models.ManyToManyField(
        User,
        blank=True,
        related_name='team_tasks',
        verbose_name="Team Members",
        help_text="People assigned to execute this task"
    )
    
    # Quality control
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
    
    quality_rating = models.CharField(
        max_length=15,
        choices=QUALITY_CHOICES,
        verbose_name="Quality Rating",
        blank=True
    )
    
    # Costs
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Estimated Cost",
        default=Decimal('0.00')
    )
    
    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Actual Cost",
        default=Decimal('0.00')
    )
    
    # Detailed information
    notes = models.TextField(
        verbose_name="Notes",
        help_text="Specific notes about task execution",
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
    
    lessons_learned = models.TextField(
        verbose_name="Lessons Learned",
        help_text="Lessons learned during execution",
        blank=True
    )
    
    # Approval and verification
    requires_approval = models.BooleanField(
        default=False,
        verbose_name="Requires Approval"
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_tasks',
        verbose_name="Approved By"
    )
    
    approval_date = models.DateTimeField(
        verbose_name="Approval Date",
        null=True,
        blank=True
    )
    
    approval_notes = models.TextField(
        verbose_name="Approval Notes",
        blank=True
    )
    
    # Specific location
    specific_location = models.CharField(
        max_length=200,
        verbose_name="Specific Location",
        help_text="Specific location where task is executed",
        blank=True
    )
    
    # Conditions during execution
    weather_conditions = models.CharField(
        max_length=100,
        verbose_name="Weather Conditions",
        help_text="Weather conditions during execution",
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
        related_name='created_task_projects',
        verbose_name="Created By"
    )
    
    history = HistoricalRecords(inherit=True)
    
    class Meta:
        verbose_name = "Task Project"
        verbose_name_plural = "Task Projects"
        ordering = ['phase_project', 'execution_order']
        unique_together = [
            ['phase_project', 'task_code'],
            ['phase_project', 'execution_order']
        ]
        indexes = [
            models.Index(fields=['phase_project']),
            models.Index(fields=['task_status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['planned_start_date']),
            models.Index(fields=['planned_end_date']),
        ]
    
    def __str__(self):
        # Fallback defensivo para project identifier
        project_identifier = getattr(self.phase_project.project, 'code', None) or self.phase_project.project.project_name
        return f"{project_identifier} - {self.task_name} ({self.task_status})"
    
    @property
    def project(self):
        """Direct access to project"""
        return self.phase_project.project
    
    @property
    def total_specifications(self):
        """Total specifications for this task"""
        return self.specifications.count()
    
    @property
    def completed_specifications(self):
        """Completed specifications"""
        return self.specifications.filter(specification_status='COMPLETED').count()
    
    @property
    def time_variance(self):
        """Time variance percentage between estimated and actual"""
        if self.estimated_duration_hours == 0:
            return Decimal('0.00')
        
        if self.actual_duration_hours == 0:
            return Decimal('0.00')
        
        difference = self.actual_duration_hours - self.estimated_duration_hours
        return (difference / self.estimated_duration_hours) * 100
    
    @property
    def cost_variance(self):
        """Cost variance percentage between estimated and actual"""
        if self.estimated_cost == 0:
            return Decimal('0.00')
        
        difference = self.actual_cost - self.estimated_cost
        return (difference / self.estimated_cost) * 100
    
    @property
    def is_delayed(self):
        """Checks if task is delayed"""
        if not self.planned_end_date:
            return False
        
        from django.utils import timezone
        return (
            self.task_status not in ['COMPLETED', 'CANCELLED'] and
            timezone.now() > self.planned_end_date
        )
    
    @property
    def remaining_time_hours(self):
        """Calculates remaining time based on completion percentage"""
        if self.completion_percentage >= 100:
            return Decimal('0.00')
        
        consumed_time = (self.estimated_duration_hours * self.completion_percentage) / 100
        return self.estimated_duration_hours - consumed_time
    
    def can_start(self):
        """Checks if task can be started"""
        if self.task_status != 'READY_TO_START':
            return False
        
        # Check model prerequisites
        prerequisites = self.model_task.get_blocking_tasks()
        for prereq in prerequisites:
            prereq_task = TaskProject.objects.filter(
                phase_project=self.phase_project,
                model_task=prereq
            ).first()
            
            if not prereq_task or prereq_task.task_status != 'COMPLETED':
                return False
        
        # Check if resources are available
        return self.check_resource_availability()
    
    def start_task(self, user=None):
        """Starts task execution"""
        if self.can_start():
            from django.utils import timezone
            self.task_status = 'IN_PROGRESS'
            self.actual_start_date = timezone.now()
            if user:
                self.assigned_to = user
            self.save()
            
            # Create specifications based on model
            self.create_specifications_from_model()
            return True
        return False
    
    def pause_task(self, reason="", user=None):
        """Pauses task execution"""
        if self.task_status == 'IN_PROGRESS':
            self.task_status = 'PAUSED'
            if reason:
                self.notes += f"\nPaused: {reason}"
            self.save()
            return True
        return False
    
    def resume_task(self, user=None):
        """Resumes task execution"""
        if self.task_status == 'PAUSED':
            self.task_status = 'IN_PROGRESS'
            self.save()
            return True
        return False
    
    def complete_task(self, user=None):
        """Completes task"""
        if self.task_status in ['IN_PROGRESS', 'PAUSED']:
            from django.utils import timezone
            self.task_status = 'COMPLETED'
            self.actual_end_date = timezone.now()
            self.completion_percentage = Decimal('100.00')
            
            # Calculate actual duration
            if self.actual_start_date:
                delta = self.actual_end_date - self.actual_start_date
                self.actual_duration_hours = Decimal(str(delta.total_seconds() / 3600))
            
            self.save()
            
            # Release dependent tasks
            self.release_dependent_tasks()
            
            # Check if phase can be completed
            self.check_phase_completion()
            return True
        return False
    
    def check_resource_availability(self):
        """Checks if all required resources are available"""
        # Implement resource verification logic
        # For now, always return True
        return True
    
    def create_specifications_from_model(self):
        """Creates specifications based on model resources"""
        from .task_specification import TaskSpecification
        
        # Verificar se já existem especificações para evitar duplicatas
        if self.specifications.exists():
            return
        
        # Filtrar recursos ativos (com fallback se não houver campo is_active)
        try:
            resources = self.model_task.resources.filter(is_active=True)
        except:
            resources = self.model_task.resources.all()
        
        for resource in resources:
            TaskSpecification.objects.create(
                task_project=self,
                task_resource=resource,
                planned_quantity=resource.required_quantity,
                created_by=self.created_by
            )
    
    def release_dependent_tasks(self):
        """Updates status of tasks that depend on this one"""
        dependent_tasks = TaskProject.objects.filter(
            phase_project=self.phase_project,
            model_task__in=self.model_task.get_dependent_tasks()
        )
        
        for task in dependent_tasks:
            if task.can_start():
                task.task_status = 'READY_TO_START'
                task.save()
    
    def check_phase_completion(self):
        """Checks if phase can be completed"""
        phase = self.phase_project
        if phase.tasks_completion_percentage == 100:
            phase.complete_phase()