"""
Tipos de escolha específicos para o módulo Account
Design Pattern: Factory + Strategy
"""
from django.db import models
from core.models.base import ChoiceTypeBase


class StatusChoice(ChoiceTypeBase):
    """Status de leads"""

    class Meta:
        verbose_name = 'Status of Lead'
        verbose_name_plural = 'Status of Leads'
        db_table = 'lead_statusChoice'


class ElevationChoice(ChoiceTypeBase):
    """Tipos de elevacao para leads"""
    locale_code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Elevtions Codes (Contemporary, Farm, N/A)"
    )

    class Meta:
        verbose_name = 'Elevation'
        verbose_name_plural = 'Elevations'
        db_table = 'LeadsElevation'



