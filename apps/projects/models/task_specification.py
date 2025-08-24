from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from decimal import Decimal

User = get_user_model()


class TaskSpecification(models.Model):
    """
    Real resource usage specifications for project tasks
    BUSINESS LOGIC:
    - Records how resources were actually used in real projects
    - Links planned resources (TaskResource) with actual usage
    - Tracks quantities, costs, suppliers used
    - Performance tracking: planned vs actual
    """
    
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('REQUESTED', 'Requested'),
        ('AVAILABLE', 'Available'),
        ('IN_USE', 'In Use'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Main relationships
    task_project = models.ForeignKey(
        'projects.TaskProject',
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name="Task Project"
    )
    
    task_resource = models.ForeignKey(
        'projects.TaskResource',
        on_delete=models.PROTECT,
        related_name='usage_specifications',
        verbose_name="Task Resource",
        help_text="Template resource being specified"
    )
    
    # Usage description
    usage_description = models.TextField(
        verbose_name="Usage Description",
        help_text="How the resource was actually used in this task",
        blank=True
    )
    
    # Planned vs actual quantities
    planned_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Planned Quantity",
        help_text="Originally planned quantity"
    )
    
    actual_quantity_used = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name="Actual Quantity Used",
        help_text="Quantity actually used",
        default=Decimal('0.000')
    )
    
    # Status and control
    specification_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLANNED',
        verbose_name="Specification Status"
    )
    
    # Real costs
    actual_unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Actual Unit Cost",
        help_text="Actual cost per unit paid",
        default=Decimal('0.00')
    )
    
    actual_total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Actual Total Cost",
        help_text="Total cost actually spent",
        default=Decimal('0.00')
    )
    
    # Supplier information
    supplier_used = models.CharField(
        max_length=200,
        verbose_name="Supplier Used",
        help_text="Supplier or vendor used",
        blank=True
    )
    
    # Basic notes
    notes = models.TextField(
        verbose_name="Notes",
        help_text="General notes about resource usage",
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
        related_name='created_task_specifications',
        verbose_name="Created By"
    )
    
    history = HistoricalRecords(inherit=True)
    
    class Meta:
        verbose_name = "Task Specification"
        verbose_name_plural = "Task Specifications"
        ordering = ['task_project', 'task_resource']
        unique_together = ['task_project', 'task_resource']
        indexes = [
            models.Index(fields=['task_project']),
            models.Index(fields=['task_resource']),
            models.Index(fields=['specification_status']),
        ]
    
    def __str__(self):
        return f"{self.task_project.task_name} - {self.task_resource.resource_name}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total cost"""
        if (self.actual_unit_cost is not None and self.actual_unit_cost > 0 and 
            self.actual_quantity_used is not None):
            self.actual_total_cost = self.actual_quantity_used * self.actual_unit_cost
        super().save(*args, **kwargs)
    
    @property
    def quantity_variance(self):
        """Quantity variance percentage between planned and actual"""
        if self.planned_quantity is None or self.planned_quantity == 0:
            return Decimal('0.00')
        
        if self.actual_quantity_used is None:
            return Decimal('0.00')
        
        difference = self.actual_quantity_used - self.planned_quantity
        return (difference / self.planned_quantity) * 100
    
    @property
    def cost_variance(self):
        """Cost variance between estimated and actual"""
        if self.task_resource is None or self.planned_quantity is None:
            return Decimal('0.00')
        
        estimated_cost = self.task_resource.estimated_unit_cost * self.planned_quantity
        if estimated_cost == 0:
            return Decimal('0.00')
        
        if self.actual_total_cost is None:
            return Decimal('0.00')
        
        difference = self.actual_total_cost - estimated_cost
        return (difference / estimated_cost) * 100