# apps/projects/admin_360.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Prefetch
from .models.projects_360 import Projects360
from .models import Contact, ContractProject
from ..contracts.models import ContractOwner, Contract 

@admin.register(Projects360)
class Projects360Admin(admin.ModelAdmin):
    """
    Admin para visão 360° dos projetos
    Mostra TODAS as informações relacionadas em uma única tabela
    """
    
    # =====================================================
    # CONFIGURAÇÕES BÁSICAS
    # =====================================================
    
    list_display = [
        # Projeto principal
        'project_link', 'status_project_badge', 'completion_percentage_bar',
        
        # Incorporação
        'incorporation_name', 'incorporation_type_display',
        
        # Modelo e célula
        'model_project_name', 'production_cell_display',
        
        # Lead e contrato
        'lead_info', 'contract_number_link',
        
        # Valores financeiros
        'sale_value_formatted', 'contract_value_formatted',
        
        # Proprietários (resumo)
        'owners_summary',
        
        # Contatos (resumo)  
        'contacts_summary',
        
        # Datas importantes
        'expected_delivery_date', 'sign_date_display',
        
        # Localização
        'county_display', 'address_short',
    ]
    
    list_filter = [
        'status_project',
        'incorporation__incorporation_type',
        'incorporation__county',
        'production_cell',
        'model_project__project_type',
        'project_contracts__contract__status_contract',
        'project_contracts__contract__payment_method',
        'expected_delivery_date',
    ]
    
    search_fields = [
        'project_name',
        'address',
        'incorporation__name',
        'project_contracts__contract__contract_number',
        'project_contracts__contract__lead__client_email',
        'project_contracts__contract__lead__client_full_name',
        'project_contacts__contact__email',
        'project_contracts__contract__owners__client__email',
    ]
    
    ordering = ['-created_at']
    
    # Read-only (não permite edição)
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # =====================================================
    # OTIMIZAÇÃO DE QUERIES - CORRIGIDO
    # =====================================================
    
    def get_queryset(self, request):
        """Otimiza queries com todos os relacionamentos necessários"""
        return super().get_queryset(request).select_related(
            'incorporation',
            'incorporation__incorporation_type', 
            'incorporation__county',
            'model_project',
            'model_project__project_type',
            'status_project',
            'production_cell',
            'created_by'
        ).prefetch_related(
            # Prefetch para ContractProject com Contract otimizado
            Prefetch(
                'project_contracts',
                queryset=ContractProject.objects.select_related(
                    'contract',
                    'contract__lead', 
                    'contract__status_contract', 
                    'contract__payment_method'
                )
            ),
            # Prefetch para Owners do contrato
            Prefetch(
                'project_contracts__contract__owners',
                queryset=ContractOwner.objects.select_related(
                    'client', 
                    'owner_type'
                )
            ),
            # Prefetch para Contatos do projeto
            Prefetch(
                'project_contacts',
                queryset=Contact.objects.select_related(
                    'contact', 
                    'owner',
                    'owner__client'
                ).filter(is_active=True)
            ),
        )
    
    # =====================================================
    # MÉTODOS DE DISPLAY CUSTOMIZADOS
    # =====================================================
    
    def project_link(self, obj):
        """Link para editar o projeto"""
        url = reverse('admin:projects_project_change', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank"><strong>{}</strong></a><br>'
            '<small style="color: #666;">ID: {}</small>',
            url, obj.project_name, obj.id
        )
    project_link.short_description = 'Projeto'
    project_link.admin_order_field = 'project_name'
    
    def status_project_badge(self, obj):
        """Badge colorido para status"""
        if obj.status_project and obj.status_project.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
                obj.status_project.color,
                obj.status_project.name
            )
        return obj.status_project.name if obj.status_project else '-'
    status_project_badge.short_description = 'Status'
    
    def completion_percentage_bar(self, obj):
        """Barra de progresso visual"""
        percentage = float(obj.completion_percentage or 0)
        color = '#28a745' if percentage >= 80 else '#ffc107' if percentage >= 50 else '#dc3545'
        
        return format_html(
            '<div style="width: 100px; background: #e9ecef; border-radius: 10px;">'
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 10px; '
            'text-align: center; color: white; font-size: 11px; line-height: 20px;">'
            '{}%</div></div>',
            percentage, color, int(percentage)
        )
    completion_percentage_bar.short_description = 'Progresso'
    
    def incorporation_name(self, obj):
        """Nome da incorporação com tipo"""
        if obj.incorporation:
            return format_html(
                '<strong>{}</strong><br><small style="color: #666;">{}</small>',
                obj.incorporation.name,
                obj.incorporation.incorporation_type.name if obj.incorporation.incorporation_type else 'Tipo não definido'
            )
        return '-'
    incorporation_name.short_description = 'Incorporação'
    
    def incorporation_type_display(self, obj):
        """Tipo de incorporação"""
        return obj.incorporation.incorporation_type.name if obj.incorporation and obj.incorporation.incorporation_type else '-'
    incorporation_type_display.short_description = 'Tipo'
    
    def model_project_name(self, obj):
        """Nome do modelo de projeto"""
        return obj.model_project.name if obj.model_project else '-'
    model_project_name.short_description = 'Modelo'
    model_project_name.admin_order_field = 'model_project__name'
    
    def production_cell_display(self, obj):
        """Célula de produção"""
        return obj.production_cell.name if obj.production_cell else '-'
    production_cell_display.short_description = 'Célula'
    
    def lead_info(self, obj):
        """Informações do lead"""
        contract_project = obj.project_contracts.first()
        if contract_project and contract_project.contract and contract_project.contract.lead:
            lead = contract_project.contract.lead
            return format_html(
                '<strong>{}</strong><br>'
                '<small style="color: #666;">{}</small>',
                lead.client_full_name or 'Nome não informado',
                lead.client_email
            )
        return '-'
    lead_info.short_description = 'Lead'
    
    def contract_number_link(self, obj):
        """Link para o contrato"""
        contract_project = obj.project_contracts.first()
        if contract_project and contract_project.contract:
            contract = contract_project.contract
            url = reverse('admin:projects_contract_change', args=[contract.id])
            return format_html(
                '<a href="{}" target="_blank">{}</a><br>'
                '<small style="color: #666;">{}</small>',
                url,
                contract.contract_number,
                contract.status_contract.name if contract.status_contract else 'Status não definido'
            )
        return '-'
    contract_number_link.short_description = 'Contrato'
    
    
    def sale_value_formatted(self, obj):
        """Valor de venda formatado"""
        if obj.sale_value:
            try:
                value = float(obj.sale_value)
                return format_html(
                    '<strong style="color: #28a745;">${:,.2f}</strong>',
                    value
                )
            except (ValueError, TypeError):
                return '-'
        return '-'

    def contract_value_formatted(self, obj):
        """Valor do contrato formatado"""
        contract_project = obj.project_contracts.first()
        if contract_project and contract_project.contract and contract_project.contract.contract_value:
            try:
                value = float(contract_project.contract.contract_value)
                return format_html(
                    '<strong style="color: #007bff;">${:,.2f}</strong>',
                    value
                )
            except (ValueError, TypeError):
                return '-'
        return '-'
    
    def owners_summary(self, obj):
        """Resumo dos proprietários"""
        contract_project = obj.project_contracts.first()
        if contract_project and contract_project.contract:
            owners = contract_project.contract.owners.all()
            if owners:
                owner_list = []
                for owner in owners[:2]:  # Mostrar apenas os 2 primeiros
                    owner_list.append(
                        f"{owner.client.get_full_name()} ({owner.percentual_propriedade}%)"
                    )
                
                result = '<br>'.join(owner_list)
                if owners.count() > 2:
                    result += f'<br><small>... +{owners.count() - 2} mais</small>'
                
                return format_html(result)
        return '-'
    owners_summary.short_description = 'Proprietários'
    
    def contacts_summary(self, obj):
        """Resumo dos contatos"""
        contacts = obj.project_contacts.filter(is_active=True)
        if contacts:
            contact_list = []
            for contact in contacts[:2]:  # Mostrar apenas os 2 primeiros
                contact_list.append(
                    f"{contact.contact.get_full_name()} ({contact.get_contact_role_display()})"
                )
            
            result = '<br>'.join(contact_list)
            if contacts.count() > 2:
                result += f'<br><small>... +{contacts.count() - 2} mais</small>'
            
            return format_html(result)
        return '-'
    contacts_summary.short_description = 'Contatos'
    
    def sign_date_display(self, obj):
        """Data de assinatura do contrato"""
        contract_project = obj.project_contracts.first()
        if contract_project and contract_project.contract and contract_project.contract.sign_date:
            return contract_project.contract.sign_date.strftime('%m/%d/%Y')
        return '-'
    sign_date_display.short_description = 'Data Assinatura'
    
    def county_display(self, obj):
        """County da incorporação"""
        return obj.incorporation.county.name if obj.incorporation and obj.incorporation.county else '-'
    county_display.short_description = 'County'
    
    def address_short(self, obj):
        """Endereço resumido"""
        if obj.address:
            return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
        return '-'
    address_short.short_description = 'Endereço'
    
    # =====================================================
    # CONFIGURAÇÕES ADICIONAIS
    # =====================================================
    
    list_per_page = 25
    list_max_show_all = 100
    
    # Adicionar CSS customizado
    class Media:
        css = {
            'all': ('admin/css/projects_360.css',)
        }




#TODO: procurar contracts projects -- em contratos devolver todos os projetos relacionados