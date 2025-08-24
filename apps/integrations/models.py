# integrations/models.py
from django.db import models
from django.utils import timezone
import uuid


class BrokermintTransaction(models.Model):
    """Transações completas sincronizadas do Brokermint"""

    # ID único
    brokermint_id = models.BigIntegerField(
        unique=True, verbose_name="ID Brokermint")

    # DADOS BÁSICOS (da listagem)
    address = models.CharField(
        max_length=200, verbose_name="Endereço", null=True)
    city = models.CharField(max_length=100, verbose_name="Cidade", null=True)
    state = models.CharField(max_length=10, verbose_name="Estado", null=True)
    zip = models.CharField(max_length=20, verbose_name="CEP", null=True)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Preço", null=True, blank=True)
    status = models.CharField(max_length=50, verbose_name="Status")
    representing = models.CharField(
        max_length=50, verbose_name="Representando", null=True, blank=True)
    transaction_name = models.CharField(max_length=200, null=True, blank=True)

    # DADOS DETALHADOS (da consulta individual) ← NOVOS CAMPOS!
    county = models.CharField(
        max_length=100, blank=True, verbose_name="County", null=True)
    legal_description = models.TextField(
        blank=True, verbose_name="Descrição Legal", null=True)
    parcel_id = models.CharField(
        max_length=100, blank=True, verbose_name="Parcel ID", null=True)
    home_model = models.CharField(
        max_length=100, blank=True, verbose_name="Modelo Casa", null=True)
    bedrooms = models.CharField(
        max_length=10, blank=True, verbose_name="Quartos", null=True)
    full_baths = models.CharField(
        max_length=10, blank=True, verbose_name="Banheiros", null=True)
    half_baths = models.CharField(
        max_length=10, blank=True, verbose_name="Lavabos", null=True)
    building_sqft = models.CharField(
        max_length=20, blank=True, verbose_name="SQFT Construção", null=True)

    # Dados financeiros
    soft_costs = models.CharField(
        max_length=20, blank=True, verbose_name="Soft Costs", null=True)
    hard_costs = models.CharField(
        max_length=20, blank=True, verbose_name="Hard Costs", null=True)
    estimated_construction_cost = models.CharField(
        max_length=20, blank=True, null=True)
    builder_fee = models.CharField(
        max_length=20, blank=True, verbose_name="Taxa Builder", null=True)

    # Draws
    draw_1 = models.CharField(
        max_length=20, blank=True, verbose_name="Draw 1", null=True)
    draw_2 = models.CharField(
        max_length=20, blank=True, verbose_name="Draw 2", null=True)
    draw_3 = models.CharField(
        max_length=20, blank=True, verbose_name="Draw 3", null=True)
    draw_4 = models.CharField(
        max_length=20, blank=True, verbose_name="Draw 4", null=True)
    draw_5 = models.CharField(
        max_length=20, blank=True, verbose_name="Draw 5", null=True)

    # Localização detalhada
    lot = models.CharField(max_length=20, blank=True,
                           verbose_name="Lote", null=True)
    block = models.CharField(max_length=20, blank=True,
                             verbose_name="Quadra", null=True)
    unit = models.CharField(max_length=20, blank=True,
                            verbose_name="Unidade", null=True)
    sec = models.CharField(max_length=20, blank=True,
                           verbose_name="SEC", null=True)
    twp = models.CharField(max_length=20, blank=True,
                           verbose_name="TWP", null=True)
    rge = models.CharField(max_length=20, blank=True,
                           verbose_name="RGE", null=True)
    subdivision = models.CharField(
        max_length=200, blank=True, verbose_name="Subdivisão", null=True)

    # Datas importantes
    acceptance_date = models.BigIntegerField(
        null=True, blank=True, verbose_name="Data Aceitação")
    expiration_date = models.BigIntegerField(
        null=True, blank=True, verbose_name="Data Expiração")
    closing_date = models.BigIntegerField(
        null=True, blank=True, verbose_name="Data Fechamento")
    listing_date = models.BigIntegerField(
        null=True, blank=True, verbose_name="Data Listagem")
    buyer_agreement_date = models.BigIntegerField(null=True, blank=True)
    buyer_expiration_date = models.BigIntegerField(null=True, blank=True)

    # Dados adicionais
    custom_id = models.CharField(
        max_length=100, blank=True, verbose_name="ID Customizado", null=True)
    transaction_type = models.CharField(
        max_length=50, blank=True, verbose_name="Tipo Transação", null=True)
    external_id = models.CharField(
        max_length=100, blank=True, verbose_name="ID Externo", null=True)
    total_gross_commission = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, null=True)
    sales_volume = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, null=True)

    # Controle
    has_detailed_data = models.BooleanField(
        default=False, verbose_name="Dados Detalhados Carregados", null=True)
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # CAMPOS PARA CONTROLE EFICIENTE
    last_activity_check = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última verificação de atividades"
    )
    has_signature_activity = models.BooleanField(
        default=False,
        verbose_name="Tem atividade de assinatura"
    )
    is_contract_signed = models.BooleanField(
        default=False,
        verbose_name="Contrato assinado"
    )

    class Meta:
        verbose_name = "Transação Brokermint"
        indexes = [
            models.Index(fields=['brokermint_id']),
            # ← ÍNDICE PARA BUSCAR POR PARCEL
            models.Index(fields=['parcel_id']),
            models.Index(fields=['custom_id']),
            models.Index(fields=['status']),
            models.Index(fields=['last_activity_check']),
            models.Index(fields=['is_contract_signed']),
        ]

    def __str__(self):
        return f"{self.custom_id or self.brokermint_id} - {self.address}"


class BrokermintActivity(models.Model):
    """Atividades de assinatura do Brokermint"""

    brokermint_id = models.BigIntegerField(unique=True)
    content = models.TextField()
    bm_transaction_id = models.BigIntegerField()
    created_at_brokermint = models.BigIntegerField()  # timestamp original
    originator_id = models.BigIntegerField()
    document_id = models.BigIntegerField()
    event_label = models.CharField(max_length=100)
    signers = models.JSONField(default=list)  # emails dos signatários

    # Metadados
    synced_at = models.DateTimeField(auto_now_add=True)


class BrokermintDocument(models.Model):
    """Documentos assinados do Brokermint"""

    brokermint_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=500)
    bm_transaction_id = models.BigIntegerField()
    task_id = models.BigIntegerField(null=True)
    pages = models.IntegerField()
    content_type = models.CharField(max_length=100)
    url = models.URLField(max_length=1000)

    synced_at = models.DateTimeField(auto_now_add=True)
