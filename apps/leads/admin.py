# apps/leads/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Lead
from .models.lead_types import StatusChoice, ElevationChoice
from django import forms
from django.contrib import messages
from django.shortcuts import render


class ConvertLeadsForm(forms.Form):
    """Formulário para escolher parâmetros de conversão"""

    incorporation = forms.ModelChoiceField(
        queryset=None,  # Será preenchido no __init__
        label="Incorporation",
        help_text="Choose the incorporation for the contracts"
    )

    management_company = forms.ChoiceField(
        choices=[
            ('L. Lira', 'L. Lira'),
            ('H & S', 'H & S')
        ],
        initial='L. Lira',
        label="Management Company"
    )

    payment_method = forms.ModelChoiceField(
        queryset=None,  # Será preenchido no __init__
        label="Payment Method",
        help_text="Choose the payment method for the contracts"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Carregar dados dinâmicos
        from projects.models import Incorporation
        from projects.models.choice_types import PaymentMethod

        self.fields['incorporation'].queryset = Incorporation.objects.filter(
            is_active=True)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            is_active=True)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """
    Interface administrativa para gerenciar leads

    FEATURES:
    - Filtros por status, condado, data
    - Busca por nome, email, phone
    - Actions para mudança em massa de status
    - Display customizado com cores por status
    - Links diretos para conversão
    """

    # Display configuration
    list_display = [
        'client_full_name',
        'client_company_name',
        'client_email',
        'county',
        'get_display_model',
        'contract_value_formatted',
        'status_badge',
        'days_old',
        'created_at_formatted',
        'action_buttons'
    ]

    list_filter = [
        'status',
        'county',
        'house_model',
        'elevation',
        'has_hoa',
        'hoa',
        'hoa_name',
        'is_realtor',
        'realtor__name',
        'created_at',
    ]

    search_fields = [
        'client_full_name',
        'client_company_name',
        'client_email',
        'client_phone',
        'parcel_id',
        'realtor__name',
        'hoa__name',
        'has_hoa',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'converted_at',
        # Removido 'days_since_created' - usar como method no display -- lembrar de ativar
    ]

    fieldsets = (
        ('Client Information', {
            'fields': (
                'client_company_name',
                'client_full_name',
                'client_email',
                'client_phone',
                'note',
            )
        }),
        ('Realtor Information', {
            'fields': ('is_realtor', 'realtor', 'realtor_name', 'realtor_phone', 'realtor_email')
        }),
        ('Property Information', {
            'fields': (
                'state',
                'county',
                'parcel_id',
                'house_model',
                'other_model',
                'elevation',
                'has_hoa',
                'hoa_name',
                'hoa',
                'contract_value',
            )
        }),
        ('Workflow & Status', {
            'fields': (
                'status',
                'created_by',
                'created_at',
                'updated_at',
                'converted_at',
            )
        }),
    )

    # Custom display methods
    # apps/leads/admin.py - ALTERAÇÕES SUGERIDAS

    def status_badge(self, obj):
        """Exibe status com cores usando dados da choice"""
        status_choice = obj.status
        color = getattr(status_choice, 'color', '#6b7280')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{} {}</span>',
            color,
            getattr(status_choice, 'icon', ''),
            status_choice.name
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    actions = [
        'mark_as_qualified',
        'mark_as_rejected',
        'mark_as_pending',
        'convert_to_contracts',
    ]

    def convert_to_contracts(self, request, queryset):
        """Converte leads com formulário dinâmico"""
        from .services import LeadConversionService
        from django.contrib.admin import helpers

        # Se é POST, processar conversão
        if 'apply' in request.POST:
            form = ConvertLeadsForm(request.POST)

            if form.is_valid():
                incorporation = form.cleaned_data['incorporation']
                management_company = form.cleaned_data['management_company']
                payment_method = form.cleaned_data['payment_method']

                converted = 0
                failed = 0

                for lead in queryset:
                    if not lead.is_convertible:
                        messages.warning(
                            request, f"Lead {lead.client_full_name} não pode ser convertido")
                        failed += 1
                        continue

                    try:
                        result = LeadConversionService.convert_lead_to_contract(
                            lead=lead,
                            incorporation_id=incorporation.id,
                            management_company=management_company,
                            payment_method_id=payment_method.id,
                            user=request.user
                        )

                        if result.success:
                            messages.success(
                                request, f"✅ {lead.client_full_name} → {result.contract.contract_number}")
                            converted += 1
                        else:
                            messages.error(
                                request, f"❌ {lead.client_full_name}: {', '.join(result.errors)}")
                            failed += 1

                    except Exception as e:
                        messages.error(
                            request, f"💥 {lead.client_full_name}: {str(e)}")
                        failed += 1

                # Mensagem final
                if converted > 0:
                    self.message_user(
                        request, f"🎉 {converted} lead(s) convertido(s)!")
                return

        # Se é GET, mostrar formulário
        form = ConvertLeadsForm()

        return render(request, 'admin/convert_leads.html', {
            'form': form,
            'leads': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        })

    convert_to_contracts.short_description = "🔄 Convert to contracts"

    @admin.register(StatusChoice)
    class StatusChoiceAdmin(admin.ModelAdmin):
        list_display = ['code', 'name', 'color_badge',
                        'icon', 'order', 'is_active']
        list_filter = ['is_active']
        search_fields = ['code', 'name']
        ordering = ['order', 'name']

        def color_badge(self, obj):
            if obj.color:
                return format_html(
                    '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                    obj.color, obj.name
                )
            return obj.name
        color_badge.short_description = 'Color'

    @admin.register(ElevationChoice)
    class ElevationChoiceAdmin(admin.ModelAdmin):
        list_display = ['code', 'name', 'locale_code',
                        'color_badge', 'icon', 'order', 'is_active']
        list_filter = ['is_active']
        search_fields = ['code', 'name', 'locale_code']
        ordering = ['order', 'name']

        def color_badge(self, obj):
            if obj.color:
                return format_html(
                    '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                    obj.color, obj.name
                )
            return obj.name
        color_badge.short_description = 'Color'

    def contract_value_formatted(self, obj):
        """Formata valor do contrato"""
        return f"${obj.contract_value:,.2f}"
    contract_value_formatted.short_description = 'Contract Value'
    contract_value_formatted.admin_order_field = 'contract_value'

    def created_at_formatted(self, obj):
        """Data formatada de criação"""
        return obj.created_at.strftime('%m/%d/%Y %H:%M')
    created_at_formatted.short_description = 'Created'
    created_at_formatted.admin_order_field = 'created_at'

    def days_old(self, obj):
        """Dias desde criação com cores"""
        days = obj.days_since_created
        if days <= 3:
            color = '#10b981'  # green
        elif days <= 7:
            color = '#fbbf24'  # yellow
        else:
            color = '#ef4444'  # red

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color,
            days
        )
    days_old.short_description = 'Age'

    def action_buttons(self, obj):
        """Botões de ação customizados"""
        buttons = []

        if obj.is_convertible:
            # Botão para converter (link para contracts admin)
            buttons.append(
                f'<a href="/admin/contracts/contract/add/?lead_id={obj.id}" '
                f'style="background: #10b981; color: white; padding: 2px 6px; '
                f'border-radius: 3px; text-decoration: none; font-size: 11px;">Convert</a>'
            )

        # Botão para visualizar detalhes
        detail_url = reverse('admin:leads_lead_change', args=[obj.id])
        buttons.append(
            f'<a href="{detail_url}" '
            f'style="background: #3b82f6; color: white; padding: 2px 6px; '
            f'border-radius: 3px; text-decoration: none; font-size: 11px;">View</a>'
        )

        return format_html(' '.join(buttons))
    action_buttons.short_description = 'Actions'

    # Bulk actions
    actions = [
        'mark_as_qualified',
        'mark_as_rejected',
        'mark_as_pending',
        'convert_to_contracts',
    ]

    def mark_as_qualified(self, request, queryset):
        """Marca leads selecionados como qualificados"""
        try:
            qualified_status = StatusChoice.objects.get(code='QUALIFIED')
            updated = queryset.filter(status__code='PENDING').update(
                status=qualified_status)
            self.message_user(request, f'{updated} leads marked as qualified.')
        except StatusChoice.DoesNotExist:
            self.message_user(
                request, "Status 'QUALIFIED' not found.", level=messages.ERROR)
    mark_as_qualified.short_description = "Mark selected leads as qualified"

    def mark_as_rejected(self, request, queryset):
        """Marca leads selecionados como rejeitados"""
        try:
            rejected_status = StatusChoice.objects.get(code='REJECTED')
            updated = queryset.exclude(
                status__code='CONVERTED').update(status=rejected_status)
            self.message_user(request, f'{updated} leads marked as rejected.')
        except StatusChoice.DoesNotExist:
            self.message_user(
                request, "Status 'REJECTED' not found.", level=messages.ERROR)
    mark_as_rejected.short_description = "Mark selected leads as rejected"

    def mark_as_pending(self, request, queryset):
        """Volta leads para pending"""
        try:
            pending_status = StatusChoice.objects.get(code='PENDING')
            updated = queryset.exclude(
                status__code='CONVERTED').update(status=pending_status)
            self.message_user(request, f'{updated} leads marked as pending.')
        except StatusChoice.DoesNotExist:
            self.message_user(
                request, "Status 'PENDING' not found.", level=messages.ERROR)
    mark_as_pending.short_description = "Mark selected leads as pending"

    # Override save to set created_by
    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
