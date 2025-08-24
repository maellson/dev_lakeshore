# apps/core/models/county.py
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Count
from simple_history.models import HistoricalRecords

class RealtorQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def autocomplete(self, text):
        return self.filter(name__icontains=text)[:10] #Hugo pode precisar

class RealtorManager(models.Manager):
    def get_queryset(self):
        return RealtorQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def autocomplete(self, text):
        return self.get_queryset().autocomplete(text)

class Realtor(models.Model):
    """
    Realtor que trazem leads para a empresa

    BUSINESS LOGIC:
    - Lista de realtors ativos na empresa
    - Base para relatórios regionais
    - Usado por leads, contratos e métricas em relatórios financeiros
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Realtor Name",
        help_text="Realtor full name"
    )
    phone = PhoneNumberField(
        verbose_name="Realtor Phone",
        help_text="Primary phone number"
    )
    email = models.EmailField(
        verbose_name="Realtor Email",
        help_text="Primary email address"
    )
    usually_works_in = models.ManyToManyField(
        'County',
        verbose_name="Counties",
        help_text="Counties where realtor works"
    )
    # campo de comissão para o realtor

    default_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Realtor Commission Rate",
        help_text="Usually Realtor commission rate"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether county is available for selection"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords(inherit=True) # testando historical records and versions

    class Meta:
        verbose_name = 'Realtor'
        verbose_name_plural = 'Realtors'
        ordering = ['name']

    objects = RealtorManager()
    def __str__(self):
        return f"{self.name} ({self.email})"

    @classmethod
    def get_active(cls):
        """Retorna apenas condados ativos da Florida"""
        return cls.objects.filter(is_active=True).order_by('name')
