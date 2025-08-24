# apps/core/models/base.py
from django.db import models


class ChoiceTypeBase(models.Model):
    """
    Model base abstrato para tipos de choices normalizados
    Design Pattern: Template Method + Strategy
    
    USAGE:
    - Base para todos os tipos de choice (TipoUsuario, Idioma, etc.)
    - Padroniza estrutura: code, name, description, icon, color
    - Métodos utilitários para choices e defaults
    - Soft delete com is_active
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code",
        help_text="Unique code for system reference"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Name", 
        help_text="Display name for users"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Detailed description"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icon",
        help_text="Icon code or emoji"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name="Color",
        help_text="Hex color code (#000000)"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Display order (lower first)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this option is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @classmethod
    def get_choices(cls):
        """Template Method: Retorna choices para usar em outros models"""
        return [(item.code, item.name) for item in cls.objects.filter(is_active=True)]

    @classmethod
    def get_default(cls):
        """Strategy Pattern: Retorna item padrão"""
        return cls.objects.filter(is_active=True).first()
    
    @classmethod
    def get_active_objects(cls):
        """Retorna queryset de objetos ativos"""
        return cls.objects.filter(is_active=True)
    
    def deactivate(self):
        """Soft delete - marca como inativo"""
        self.is_active = False
        self.save()
    
    def activate(self):
        """Reativa objeto"""
        self.is_active = True
        self.save()