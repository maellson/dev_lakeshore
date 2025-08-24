from django.db import models
from core.models.county import County
from simple_history.models import HistoricalRecords


class HOA(models.Model):
    """ Homeowners Association (HOA) model
    Represents a Homeowners Association with details about its location,
    permit requirements, and contact information.   
    
    """
    name = models.CharField(
        max_length=200,
        verbose_name="HOA Name",
        help_text="Name of the Homeowners Association"
    )
    county = models.ForeignKey(
        County,
        on_delete=models.PROTECT,
        related_name='hoas',
        verbose_name="County",
        help_text="County where the HOA is located")
    has_special_permit_rules = models.BooleanField(
        default=False,
        verbose_name="Special Permit Rules",
        help_text="Does this HOA have special permit requirements?"
    )
    permit_requirements = models.TextField(
        blank=True,
        verbose_name="Permit Requirements",
        help_text="Details of any special permit requirements for this HOA"
    )
    contact_info = models.TextField(
        blank=True,
        verbose_name="Contact Information",
        help_text="Contact information for the HOA management or board"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active HOA",
        help_text="Is this HOA currently active?"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Date and time when the HOA was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="Date and time when the HOA was last updated"
    )
    history = HistoricalRecords(inherit=True) # testando historical records and versions
    class Meta:
        verbose_name = 'Homeowners Association'
        verbose_name_plural = 'Homeowners Associations'
        ordering = ['name'] 