from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class CostSubGroup(models.Model):
    """
    Cost SubGroup model for detailed cost classification
    BUSINESS LOGIC:
    - Subcategories within cost groups
    - Provides detailed cost breakdown
    - Used for precise budget tracking and analysis
    """

    cost_group = models.ForeignKey(
        'projects.CostGroup',
        on_delete=models.CASCADE,
        related_name='subgroups',
        verbose_name="Cost Group"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Name",
        help_text="Name of the cost subgroup"
    )

    description = models.TextField(
        verbose_name="Description",
        help_text="Description of the cost subgroup",
        blank=True
    )

    value_stimated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Estimated Value",
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Estimated value of the cost subgroup",
        default=0.00
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
        related_name='created_cost_subgroups',
        verbose_name="Created By"
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Cost SubGroup"
        verbose_name_plural = "Cost SubGroups"
        ordering = ['cost_group', 'name']
        unique_together = [
            ['cost_group', 'name']
        ]
        indexes = [
            models.Index(fields=['cost_group']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.cost_group.name} - {self.name}"

    @property
    def total_tasks(self):
        """Total number of tasks using this cost subgroup"""
        return self.tasks.count()

    @property
    def active_tasks(self):
        """Active tasks using this cost subgroup"""
        return self.tasks.filter(is_active=True)
