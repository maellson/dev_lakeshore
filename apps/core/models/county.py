# apps/core/models/county.py
from django.db import models


class County(models.Model):
    """
    Condados da Florida - dados compartilhados por todo sistema
    
    BUSINESS LOGIC:
    - Lista estática dos 67 condados da Florida
    - Referência para filtros geográficos
    - Base para relatórios regionais
    - Usado por leads, contracts, subcontractors, suppliers
    """
    
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="County Name",
        help_text="Official county name"
    )
    code = models.CharField(
        max_length=10, 
        unique=True,
        verbose_name="County Code", 
        help_text="Short code for county"
    )
    state = models.CharField(
        max_length=2, 
        default='FL',
        verbose_name="State",
        help_text="State abbreviation"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether county is available for selection"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'County'
        verbose_name_plural = 'Counties'
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.state})"
    
    @classmethod
    def get_florida_counties(cls):
        """Retorna apenas condados ativos da Florida"""
        return cls.objects.filter(state='FL', is_active=True).order_by('name')
    
    @classmethod
    def get_choices(cls):
        """Retorna choices para forms/serializers"""
        return [(county.id, county.name) for county in cls.get_florida_counties()]