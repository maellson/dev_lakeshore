from django.contrib import admin

# Register your models here.
# apps/core/admin.py
from django.contrib import admin
from .models import County, Realtor, HOA


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    """
    Admin interface para Counties

    FEATURES:
    - Lista com filtros por estado e status
    - Busca por nome e código
    - Campos organizados
    - Apenas leitura para campos auto
    """

    list_display = [
        'name',
        'code',
        'state',
        'is_active',
        'created_at_formatted'
    ]

    list_filter = [
        'state',
        'is_active',
        'created_at',
    ]

    search_fields = [
        'name',
        'code',
    ]

    list_editable = [
        'is_active',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('County Information', {
            'fields': (
                'name',
                'code',
                'state',
                'is_active',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    # Custom display methods
    def created_at_formatted(self, obj):
        """Data formatada de criação"""
        return obj.created_at.strftime('%m/%d/%Y')
    created_at_formatted.short_description = 'Created'
    created_at_formatted.admin_order_field = 'created_at'

    # Bulk actions for activating/deactivating counties
    # These actions will be available in the admin interface
    # when multiple counties are selected
    actions_selection_counter = True
    actions_selection_counter_help_text = "Select multiple counties to perform bulk actions."
    actions_selection_counter_title = "Counties selected"
    actions = [
        'activate_counties',
        'deactivate_counties',
    ]

    def activate_counties(self, request, queryset):
        """Ativar counties selecionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} counties activated.')
    activate_counties.short_description = "Activate selected counties"

    def deactivate_counties(self, request, queryset):
        """Desativar counties selecionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} counties deactivated.')
    deactivate_counties.short_description = "Deactivate selected counties"


@admin.register(Realtor)
class RealtorAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'phone', 'default_commission_rate',
        'counties_list', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'usually_works_in', 'created_at']
    search_fields = ['name', 'email', 'phone']
    filter_horizontal = ['usually_works_in']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Configurações Comerciais', {
            'fields': ('default_commission_rate', 'is_active')
        }),
        ('Áreas de Atuação', {
            'fields': ('usually_works_in',)
        }),
        ('Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def counties_list(self, obj):
        """Mostra lista de counties que o realtor atende"""
        counties = obj.usually_works_in.filter(is_active=True)
        if counties.exists():
            county_names = [county.name for county in counties[:3]]
            if counties.count() > 3:
                county_names.append(f'... +{counties.count() - 3} mais')
            return ', '.join(county_names)
        return 'Nenhum county'
    counties_list.short_description = 'Counties'




@admin.register(HOA)
class HOAAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'has_special_permit_rules', 'is_active']
    list_filter = ['county', 'is_active', 'has_special_permit_rules']
    search_fields = ['name', 'county__name', 'contact_info']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('HOA Information', {
            'fields': (
                'name',
                'county',
                'has_special_permit_rules',
                'permit_requirements',
                'contact_info',
                'is_active',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    list_editable = ['is_active', 'has_special_permit_rules']
