# apps/account/management/commands/populate_groups_permissions.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import transaction

# =============================================================================
# CONFIGURAÇÃO CENTRAL DE PERMISSÕES
# =============================================================================
# Estrutura:
# 'app_label.model_name': {
#     'GroupName': ['add', 'change', 'delete', 'view'],
# }
# Use os nomes dos modelos em minúsculo, conforme definido nos arquivos models.py
# O script irá construir os codenames corretos (ex: 'add_project') dinamicamente.

PERMISSIONS_CONFIG = {
    # App: Projects
    'projects.project': {
        'Administradores': ['add', 'change', 'delete', 'view'],
        'Gerentes': ['add', 'change', 'view'],
        'Operacionais': ['view', 'change'],
        'Financeiro': ['view'],
        'Subcontratados': ['view'],
        'Clientes': ['view'],
        'Funcionários': ['view'],
    },
    'projects.contract': {
        'Administradores': ['add', 'change', 'delete', 'view'],
        'Gerentes': ['add', 'change', 'view'],
    },
    'projects.taskproject': {
        'Administradores': ['add', 'change', 'delete', 'view'],
        'Gerentes': ['view'],
        'Operacionais': ['add', 'change', 'view'],
        'Subcontratados': ['view', 'change'],
    },
    # App: Account (Exemplo para CustomUser)
    'account.customuser': {
        'Administradores': ['add', 'change', 'delete', 'view'],
        'Gerentes': ['view', 'change'],
    },
    # Adicione outros apps e modelos aqui conforme necessário
    # Ex: 'purchases.purchaseorder': { ... }
}

# =============================================================================
# GRUPOS A SEREM CRIADOS
# =============================================================================
# Garante que todos os grupos sejam criados, mesmo que não tenham permissões de modelo definidas acima.
GROUPS = [
    'Administradores', 'Gerentes', 'Operacionais', 'Financeiro',
    'Subcontratados', 'Fornecedores', 'Clientes', 'Funcionários'
]

# =============================================================================
# PERMISSÕES CUSTOMIZADAS
# =============================================================================
# Estrutura:
# 'codename': {
#     'name': 'Descrição da Permissão',
#     'models': ['app_label.model_name', ...], # Modelos aos quais a permissão se aplica
#     'groups': ['GroupName1', 'GroupName2'] # Grupos que receberão a permissão
# }
CUSTOM_PERMISSIONS_CONFIG = {
    'can_approve_orders': {
        'name': 'Pode aprovar ordens de compra/serviço',
        'models': ['projects.project'],  # Exemplo, ajuste para o modelo correto
        'groups': ['Administradores', 'Gerentes']
    },
    'can_manage_budgets': {
        'name': 'Pode gerenciar orçamentos',
        'models': ['projects.project'], # Exemplo, ajuste para o modelo correto
        'groups': ['Administradores', 'Gerentes', 'Financeiro']
    },
    'can_view_financial_reports': {
        'name': 'Pode visualizar relatórios financeiros',
        'models': ['account.customuser'], # Associado a um modelo genérico
        'groups': ['Administradores', 'Gerentes', 'Financeiro']
    },
    'can_access_client_portal': {
        'name': 'Pode acessar portal do cliente',
        'models': ['account.customuser'],
        'groups': ['Clientes']
    }
}


class Command(BaseCommand):
    help = 'Cria grupos e atribui permissões dinamicamente a partir dos modelos existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            '🚀 Iniciando configuração dinâmica de grupos e permissões...'))

        # 1. Criar todos os grupos definidos
        for group_name in GROUPS:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'  ✅ Grupo "{group_name}" criado.')
            group.permissions.clear() # Limpa permissões para garantir um estado fresco

        # 2. Atribuir permissões de modelo (padrão)
        self.assign_model_permissions()

        # 3. Criar e atribuir permissões customizadas
        self.assign_custom_permissions()

        self.stdout.write(self.style.SUCCESS(
            '🎉 Configuração de grupos e permissões concluída!'))

    def assign_model_permissions(self):
        """Itera sobre a configuração e atribui permissões de modelo existentes."""
        self.stdout.write(self.style.HTTP_INFO(
            '\n🔗 Atribuindo permissões de modelos...'))

        for model_identifier, group_perms in PERMISSIONS_CONFIG.items():
            try:
                app_label, model_name = model_identifier.split('.')
                model = apps.get_model(app_label, model_name)
                content_type = ContentType.objects.get_for_model(model)
            except (LookupError, ValueError):
                self.stdout.write(self.style.WARNING(
                    f'  ⚠️  Modelo "{model_identifier}" não encontrado. Pulando.'))
                continue

            for group_name, perms in group_perms.items():
                try:
                    group = Group.objects.get(name=group_name)
                    permissions_to_add = []
                    for perm_action in perms:
                        codename = f'{perm_action}_{model_name}'
                        try:
                            permission = Permission.objects.get(
                                content_type=content_type,
                                codename=codename
                            )
                            permissions_to_add.append(permission)
                        except Permission.DoesNotExist:
                            self.stdout.write(self.style.WARNING(
                                f'    - Permissão "{codename}" não encontrada para o modelo "{model_identifier}".'))
                    
                    group.permissions.add(*permissions_to_add)
                    if permissions_to_add:
                        self.stdout.write(
                            f'  ✓ {len(permissions_to_add)} permissões de "{model_name}" adicionadas ao grupo "{group_name}".')

                except Group.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠️  Grupo "{group_name}" não encontrado ao configurar permissões para "{model_identifier}".'))

    def assign_custom_permissions(self):
        """Cria e atribui permissões customizadas a partir da configuração."""
        self.stdout.write(self.style.HTTP_INFO(
            '\n✨ Criando e atribuindo permissões customizadas...'))

        for codename, config in CUSTOM_PERMISSIONS_CONFIG.items():
            name = config['name']
            model_identifiers = config['models']
            group_names = config['groups']

            # Usa o primeiro modelo da lista para associar o ContentType
            # Permissões customizadas precisam de um ContentType, mas não precisam estar logicamente ligadas a ele.
            try:
                app_label, model_name = model_identifiers[0].split('.')
                model = apps.get_model(app_label, model_name)
                content_type = ContentType.objects.get_for_model(model)

                permission, created = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': name}
                )

                if created:
                    self.stdout.write(f'  ✅ Permissão customizada "{name}" criada.')

                # Atribuir a permissão aos grupos
                for group_name in group_names:
                    try:
                        group = Group.objects.get(name=group_name)
                        group.permissions.add(permission)
                    except Group.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f'  ⚠️  Grupo "{group_name}" não encontrado ao atribuir permissão customizada "{name}".'))
                
                self.stdout.write(f'    ✓ Atribuída aos grupos: {", ".join(group_names)}')

            except (LookupError, ValueError, IndexError):
                self.stdout.write(self.style.ERROR(
                    f'  ❌ Erro: Modelo "{model_identifiers[0]}" para a permissão "{name}" não foi encontrado. A permissão não foi criada.'))