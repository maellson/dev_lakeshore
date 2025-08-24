# apps/account/admin_permissions.py - VERSÃO FINAL

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from django.db.models import Count


class EnhancedPermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'app_label', 'model_name']
    list_filter = ['content_type__app_label']
    search_fields = ['name', 'codename']
    ordering = ['content_type__app_label', 'codename']

    def app_label(self, obj):
        return obj.content_type.app_label
    app_label.short_description = 'App'

    def model_name(self, obj):
        return obj.content_type.model
    model_name.short_description = 'Model'


class EnhancedGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_count', 'permission_count']
    search_fields = ['name']
    filter_horizontal = ['permissions']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            user_count=Count('user', distinct=True),
            permission_count=Count('permissions', distinct=True)
        )

    def user_count(self, obj):
        return format_html('<strong>{}</strong>', obj.user_count)
    user_count.short_description = 'Usuários'

    def permission_count(self, obj):
        return format_html('<span style="background: green; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>', obj.permission_count)
    permission_count.short_description = 'Permissões'


# Registrar
admin.site.unregister(Group)
admin.site.register(Group, EnhancedGroupAdmin)
admin.site.register(Permission, EnhancedPermissionAdmin)
