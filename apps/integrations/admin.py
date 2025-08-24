# integrations/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from .models import (
    BrokermintTransaction,
    BrokermintActivity,
    BrokermintDocument
)
import json


@admin.register(BrokermintTransaction)
class BrokermintTransactionAdmin(admin.ModelAdmin):
    """Admin para transações do Brokermint"""

    list_display = [
        'brokermint_id',
        'custom_id_display',
        'address_display',
        'status_display',
        'parcel_id_display',
        'has_detailed_data',
        'last_synced',
    ]

    list_filter = [
        'status',
        'representing',
        'transaction_type',
        'has_detailed_data',
        'state',
        'last_synced',
    ]

    search_fields = [
        'brokermint_id',
        'custom_id',
        'parcel_id',
        'address',
        'city',
        'transaction_name',
    ]

    readonly_fields = [
        'brokermint_id',
        'last_synced',
        'created_at',
    ]

    ordering = ['-last_synced']

    fieldsets = (
        ('Identificação', {
            'fields': (
                'brokermint_id',
                'custom_id',
                'transaction_name',
                'transaction_type',
            )
        }),
        ('Localização', {
            'fields': (
                'address',
                'city',
                'state',
                'zip',
                'county',
                'parcel_id',
            )
        }),
        ('Características', {
            'fields': (
                'bedrooms',
                'full_baths',
                'half_baths',
                'building_sqft',
                'home_model',
            ),
            'classes': ('collapse',)
        }),
        ('Financeiro', {
            'fields': (
                'price',
                'sales_volume',
                'total_gross_commission',
                'soft_costs',
                'hard_costs',
            ),
            'classes': ('collapse',)
        }),
        ('Status e Controle', {
            'fields': (
                'status',
                'representing',
                'has_detailed_data',
                'last_synced',
                'created_at',
            )
        }),
    )

    def custom_id_display(self, obj):
        return obj.custom_id or '-'
    custom_id_display.short_description = 'Custom ID'

    def address_display(self, obj):
        return f"{obj.address}, {obj.city}"
    address_display.short_description = 'Endereço'

    def status_display(self, obj):
        color_map = {
            'active': '#28a745',
            'pending': '#ffc107',
            'closed': '#6c757d',
            'cancelled': '#dc3545',
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_display.short_description = 'Status'

    def parcel_id_display(self, obj):
        if obj.parcel_id:
            return obj.parcel_id
        return '-'
    parcel_id_display.short_description = 'Parcel ID'

    actions = ['update_transaction_details']

    def update_transaction_details(self, request, queryset):
        """Atualiza detalhes das transações selecionadas"""
        from integrations.sync_service import BrokermintSyncService

        service = BrokermintSyncService()
        updated = 0
        errors = 0

        for transaction in queryset:
            try:
                # Buscar detalhes completos
                details = service.client.get_transaction_details(
                    transaction.brokermint_id)

                if details:
                    # Atualizar todos os campos detalhados
                    transaction.parcel_id = details.get('Parcel ID', '')
                    transaction.county = details.get('County', '')
                    transaction.legal_description = details.get(
                        'Legal description', '')
                    transaction.address = details.get('Address', '')
                    transaction.city = details.get('City', '')
                    transaction.state = details.get('State', '')
                    transaction.zip = details.get('ZIP', '')
                    transaction.price = details.get('Price', 0)
                    # TODO: colocar os demais itens do modelo.
                    transaction.has_detailed_data = True
                    transaction.save()
                    updated += 1
                else:
                    errors += 1

            except Exception:
                errors += 1

        self.message_user(
            request,
            f'Detalhes atualizados: {updated} sucesso, {errors} erros'
        )

    update_transaction_details.short_description = "🔄 Atualizar detalhes das transações"


@admin.register(BrokermintActivity)
class BrokermintActivityAdmin(admin.ModelAdmin):
    """Admin para atividades de assinatura"""

    list_display = [
        'brokermint_id',
        'event_label',
        'transaction_link',
        'document_id',
        'signers_display',
        'created_at_formatted',
    ]

    list_filter = [
        'event_label',
        'synced_at',
    ]

    search_fields = [
        'brokermint_id',
        'bm_transaction_id',
        'document_id',
        'content',
    ]

    readonly_fields = [
        'brokermint_id',
        'bm_transaction_id',
        'document_id',
        'created_at_brokermint',
        'synced_at',
    ]

    ordering = ['-created_at_brokermint']

    def transaction_link(self, obj):
        return format_html(
            '<a href="/admin/integrations/brokenminttransaction/?q={}" target="_blank">{}</a>',
            obj.bm_transaction_id,
            obj.bm_transaction_id
        )
    transaction_link.short_description = 'Transação'

    def signers_display(self, obj):
        if obj.signers:
            return ', '.join(obj.signers[:2])  # Mostrar apenas 2 primeiros
        return '-'
    signers_display.short_description = 'Signatários'

    def created_at_formatted(self, obj):
        if obj.created_at_brokermint:
            # Converter timestamp para datetime
            import datetime
            dt = datetime.datetime.fromtimestamp(
                obj.created_at_brokermint / 1000)
            return dt.strftime('%d/%m/%Y %H:%M')
        return '-'
    created_at_formatted.short_description = 'Criado em'


@admin.register(BrokermintDocument)
class BrokermintDocumentAdmin(admin.ModelAdmin):
    """Admin para documentos assinados"""

    list_display = [
        'brokermint_id',
        'name_display',
        'transaction_link',
        'content_type',
        'pages',
        'download_link',
        'refresh_button',
        'synced_at',
    ]

    list_filter = [
        'content_type',
        'synced_at',
    ]

    search_fields = [
        'name',
        'bm_transaction_id',
        'brokermint_id',
    ]

    readonly_fields = [
        'brokermint_id',
        'bm_transaction_id',
        'task_id',
        'synced_at',
        'refresh_button'
    ]

    ordering = ['-synced_at']

    def name_display(self, obj):
        if 'contract' in obj.name.lower() or 'app' in obj.name.lower():
            return format_html(
                '<strong style="color: #28a745;">{}</strong>',
                obj.name
            )
        return obj.name
    name_display.short_description = 'Nome do Arquivo'

    def transaction_link(self, obj):
        return format_html(
            '<a href="/admin/integrations/brokenminttransaction/?q={}" target="_blank">{}</a>',
            obj.bm_transaction_id,
            obj.bm_transaction_id
        )
    transaction_link.short_description = 'Transação'

    def download_link(self, obj):
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff;">📄 Download</a>',
                obj.url
            )
        return '-'
    download_link.short_description = 'Arquivo'

    def has_add_permission(self, request):
        return False  # Não permitir criação manual
    actions = ['refresh_document_urls']

    def refresh_document_urls(self, request, queryset):
        """Atualiza URLs de documentos selecionados"""
        from integrations.sync_service import BrokermintSyncService

        service = BrokermintSyncService()
        updated = 0
        errors = 0

        for document in queryset:
            try:
                # Re-buscar dados do documento
                doc_data = service.client.get_document_details(
                    document.bm_transaction_id,
                    document.brokermint_id
                )

                if doc_data and doc_data.get('url'):
                    document.url = doc_data['url']
                    document.save()
                    updated += 1
                else:
                    errors += 1

            except Exception:
                errors += 1

        self.message_user(
            request,
            f'URLs atualizadas: {updated} sucesso, {errors} erros'
        )

    refresh_document_urls.short_description = "🔄 Atualizar URLs dos documentos"

    # integrations/admin.py - BOTÃO CHAMA API
    def refresh_button(self, obj):
        return format_html(
            '<a href="/api/integrations/documents/{}/refresh/" '
            'style="background: #007bff; color: white; padding: 5px 10px;">'
            '🔂 Sync</a>',
            obj.pk
        )
    # FIXME: CORRIGIR A CHAMADA DO BOTÃO E A API.
    refresh_button.short_description = 'Action'
