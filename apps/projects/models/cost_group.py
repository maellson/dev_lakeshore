from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()


class CostGroup(models.Model):
    """
    Cost Group model for organizing construction costs
    BUSINESS LOGIC:
    - Main categories for cost classification
    - Helps in budget organization and reporting
    - Used for financial analysis and control
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
        help_text="Name of the cost group"
    )
    
    description = models.TextField(
        verbose_name="Description",
        help_text="Description of the cost group",
        blank=True
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
        related_name='created_cost_groups',
        verbose_name="Created By"
    )
    
    history = HistoricalRecords(inherit=True)
    
    class Meta:
        verbose_name = "Cost Group"
        verbose_name_plural = "Cost Groups"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def total_subgroups(self):
        """Total number of subgroups in this cost group"""
        return self.subgroups.count()
    
    @property
    def active_subgroups(self):
        """Active subgroups in this cost group"""
        return self.subgroups.filter(is_active=True)