from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from account.models import CustomUser


class Command(BaseCommand):
    help = 'Configurar grupos e permissões padrão do sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando configuração de grupos e permissões...')
        
        # Definir grupos e suas permissões
        groups_permissions = {
            'Administradores': [
                # Permissões de usuário
                'add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',
                # Permissões de projetos (quando implementado)
                'add_projeto', 'change_projeto', 'delete_projeto', 'view_projeto',
                # Permissões financeiras (quando implementado)
                'add_orcamento', 'change_orcamento', 'delete_orcamento', 'view_orcamento',
                'add_pagamento', 'change_pagamento', 'delete_pagamento', 'view_pagamento', #orcamento e pagamento sao coisas diferentes me atentar aqui
                # Permissões de compras (quando implementado)
                'add_ordemcompra', 'change_ordemcompra', 'delete_ordemcompra', 'view_ordemcompra',
            ],
            
            'Gerentes': [
                # Usuários (limitado)
                'view_customuser', 'change_customuser',
                # Projetos
                'add_projeto', 'change_projeto', 'view_projeto',
                # Financeiro
                'add_orcamento', 'change_orcamento', 'view_orcamento',
                'view_pagamento', 'add_pagamento',
                # Compras
                'add_ordemcompra', 'change_ordemcompra', 'view_ordemcompra',
            ],
            
            'Operacionais': [
                # Projetos (limitado)
                'view_projeto', 'change_projeto',
                # Tarefas
                'add_tarefa', 'change_tarefa', 'view_tarefa',
                # Atividades
                'add_atividade', 'change_atividade', 'view_atividade',
            ],
            
            'Financeiro': [
                # Visualização de projetos
                'view_projeto',
                # Controle financeiro completo
                'add_orcamento', 'change_orcamento', 'view_orcamento', 'delete_orcamento',
                'add_pagamento', 'change_pagamento', 'view_pagamento', 'delete_pagamento',
                # Compras (aprovação)
                'view_ordemcompra', 'change_ordemcompra',
            ],
            
            'Subcontratados': [
                # Acesso limitado aos próprios projetos
                'view_projeto',
                # Tarefas próprias
                'view_tarefa', 'change_tarefa',
                # Atividades próprias
                'add_atividade', 'view_atividade',
            ],
            
            'Fornecedores': [
                # Visualização limitada
                'view_ordemcompra',
                # Materiais próprios
                'view_material', 'change_material',
            ],
            
            'Clientes': [
                # Acesso muito restrito via portal
                'view_projeto',  # Apenas próprios projetos
            ],
            
            'Funcionários': [
                # Grupo padrão para funcionários internos
                'view_projeto',
                'add_atividade', 'view_atividade',
            ]
        }
        
        # Criar grupos e atribuir permissões
        for group_name, permission_codenames in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(f'✅ Grupo "{group_name}" criado')
            else:
                self.stdout.write(f'📋 Grupo "{group_name}" já existe')
            
            # Limpar permissões existentes
            group.permissions.clear()
            
            # Adicionar permissões
            permissions_added = 0
            for codename in permission_codenames:
                try:
                    permission = Permission.objects.get(codename=codename)
                    group.permissions.add(permission)
                    permissions_added += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Permissão "{codename}" não encontrada')
                    )
            
            self.stdout.write(f'   └── {permissions_added} permissões adicionadas')
        
        # Criar permissões customizadas se necessário
        self.create_custom_permissions()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Configuração de grupos e permissões concluída!')
        )
    
    def create_custom_permissions(self):
        """Criar permissões customizadas específicas do sistema"""
        
        # Obter content type do usuário
        user_content_type = ContentType.objects.get_for_model(CustomUser)
        
        custom_permissions = [
            ('can_approve_orders', 'Pode aprovar ordens de compra/serviço'),
            ('can_manage_budgets', 'Pode gerenciar orçamentos'),
            ('can_view_financial_reports', 'Pode visualizar relatórios financeiros'),
            ('can_manage_subcontractors', 'Pode gerenciar subcontratados'),
            ('can_access_client_portal', 'Pode acessar portal do cliente'),
            ('can_manage_user_permissions', 'Pode gerenciar permissões de usuários'),
        ]
        
        for codename, name in custom_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=user_content_type,
            )
            
            if created:
                self.stdout.write(f'✅ Permissão customizada "{name}" criada')
        
        # Atribuir permissões customizadas aos grupos
        try:
            # Administradores recebem todas as permissões customizadas
            admin_group = Group.objects.get(name='Administradores')
            for codename, _ in custom_permissions:
                permission = Permission.objects.get(codename=codename)
                admin_group.permissions.add(permission)
            
            # Gerentes recebem algumas permissões específicas
            manager_group = Group.objects.get(name='Gerentes')
            manager_permissions = [
                'can_approve_orders', 'can_manage_budgets', 
                'can_view_financial_reports', 'can_manage_subcontractors'
            ]
            for codename in manager_permissions:
                permission = Permission.objects.get(codename=codename)
                manager_group.permissions.add(permission)
                
        except Group.DoesNotExist:
            pass


#TODO: PRECISA CRIAR AS REGRAS DE VERDADE PARA AS PERMISSIONS, LIGAR A PERMISSÃO COM A FUNCIONALIDADE OU ROTA DA API.
# AQUI TUDO É HARD CODED, PRECISA SER DINÂMICO.