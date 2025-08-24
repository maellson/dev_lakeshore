from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from decimal import Decimal

User = get_user_model()


class TaskResource(models.Model):
    """
    Basic resource requirements for model tasks
    BUSINESS LOGIC:
    - Defines what resources are needed for each template task
    - Materials, equipment, labor, services required
    - Used as template for real resource specifications
    """

    RESOURCE_TYPE_CHOICES = [
        ('MATERIAL', 'Material/Supply'),
        ('EQUIPMENT', 'Equipment/Tool'),
        ('LABOR', 'Labor/Human Resource'),
        ('SERVICE', 'Subcontracted Service'),
        ('OTHER', 'Other'),
    ]

    # Relationship with model task
    model_task = models.ForeignKey(
        'projects.ModelTask',
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name="Model Task"
    )

    # Basic resource information
    resource_name = models.CharField(
        max_length=200,
        verbose_name="Resource Name",
        help_text="Descriptive name of the required resource"
    )

    resource_type = models.CharField(
        max_length=15,
        choices=RESOURCE_TYPE_CHOICES,
        verbose_name="Resource Type"
    )

    # Quantity and cost
    required_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Required Quantity",
        help_text="Amount needed of this resource"
    )

    unit_measure = models.CharField(
        max_length=20,
        verbose_name="Unit of Measure",
        help_text="Ex: pieces, hours, kg, m2",
        default="UN"
    )

    estimated_unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Estimated Unit Cost",
        help_text="Estimated cost per unit",
        default=Decimal('0.00')
    )

    # Control
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name="Is Mandatory",
        help_text="Whether this resource is mandatory for the task"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active"
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
        related_name='created_task_resources',
        verbose_name="Created By"
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Task Resource"
        verbose_name_plural = "Task Resources"
        ordering = ['model_task', 'resource_type', 'resource_name']
        indexes = [
            models.Index(fields=['model_task']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['is_mandatory']),
        ]

    def __str__(self):
        return f"{self.resource_name} ({self.required_quantity} {self.unit_measure})"

    @property
    def estimated_total_cost(self):
        """Calculates total estimated cost"""
        return self.required_quantity * self.estimated_unit_cost
