# apps/projects/management/commands/populate_projects_choices.py
from django.core.management.base import BaseCommand
from django.db import transaction
from projects.models.choice_types import (
    ProjectType, ProjectStatus, IncorporationStatus, IncorporationType,
    StatusContract, PaymentMethod, ProductionCell, OwnerType
)


class Command(BaseCommand):
    help = 'Popula dados iniciais dos choice types do módulo Projects'

    def handle(self, *args, **options):
        """Executa o comando de população dos dados"""
        
        with transaction.atomic():
            self.stdout.write('🏗️  Populando Choice Types do módulo Projects...\n')
            
            # Popular cada tipo de choice
            self.create_project_types()
            self.create_project_status()
            self.create_incorporation_types()
            self.create_incorporation_status()
            self.create_contract_status()
            self.create_payment_methods()
            self.create_production_cells()
            self.create_owner_types()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Todos os Choice Types criados com sucesso!')
            )

    def create_project_types(self):
        """Cria tipos de projeto"""
        project_types = [
            {
                'code': 'LAND',
                'name': 'Land',
                'description': 'Terreno/lote para desenvolvimento',
                'icon': '🏞️',
                'color': '#22c55e',
                'order': 1
            },
            {
                'code': 'SIMPLE_HOUSE',
                'name': 'Simple House',
                'description': 'Casa individual simples',
                'icon': '🏠',
                'color': '#3b82f6',
                'order': 2
            },
            {
                'code': 'TOWNHOUSE_BLOCK',
                'name': 'Townhouse Block',
                'description': 'Bloco de casas geminadas',
                'icon': '🏘️',
                'color': '#8b5cf6',
                'order': 3
            },
            {
                'code': 'APARTMENT',
                'name': 'Apartment',
                'description': 'Unidade de apartamento',
                'icon': '🏢',
                'color': '#f59e0b',
                'order': 4
            },
            {
                'code': 'INFRASTRUCTURE',
                'name': 'Infrastructure',
                'description': 'Projeto de infraestrutura',
                'icon': '🛤️',
                'color': '#6b7280',
                'order': 5
            },
        ]
        
        self._create_choices(ProjectType, project_types, 'Project Types')

    def create_project_status(self):
        """Cria status de projetos"""
        project_status = [
            {
                'code': 'PLANNING',
                'name': 'Planning',
                'description': 'Projeto em fase de planejamento',
                'icon': '📋',
                'color': '#6b7280',
                'order': 1
            },
            {
                'code': 'IN_PROGRESS',
                'name': 'In Progress',
                'description': 'Projeto em execução',
                'icon': '🚧',
                'color': '#f59e0b',
                'order': 2
            },
            {
                'code': 'PAUSED',
                'name': 'Paused',
                'description': 'Projeto pausado temporariamente',
                'icon': '⏸️',
                'color': '#ef4444',
                'order': 3
            },
            {
                'code': 'COMPLETED',
                'name': 'Completed',
                'description': 'Projeto concluído',
                'icon': '✅',
                'color': '#22c55e',
                'order': 4
            },
            {
                'code': 'DELIVERED',
                'name': 'Delivered',
                'description': 'Projeto entregue ao cliente',
                'icon': '🎉',
                'color': '#16a34a',
                'order': 5
            },
            {
                'code': 'CANCELLED',
                'name': 'Cancelled',
                'description': 'Projeto cancelado',
                'icon': '❌',
                'color': '#dc2626',
                'order': 6
            },
        ]
        
        self._create_choices(ProjectStatus, project_status, 'Project Status')

    def create_incorporation_types(self):
        """Cria tipos de incorporação"""
        incorporation_types = [
            {
                'code': 'LAND_DEVELOPMENT',
                'name': 'Land Development',
                'description': 'Desenvolvimento de terreno',
                'icon': '🌱',
                'color': '#22c55e',
                'order': 1
            },
            {
                'code': 'BUILD_SIMPLE',
                'name': 'Simple Build (Single House)',
                'description': 'Construção simples de casa individual',
                'icon': '🏠',
                'color': '#3b82f6',
                'order': 2
            },
            {
                'code': 'TOWNHOUSE',
                'name': 'Townhouse (Apartment Block)',
                'description': 'Bloco de apartamentos tipo townhouse',
                'icon': '🏘️',
                'color': '#8b5cf6',
                'order': 3
            },
            {
                'code': 'CONDOMINIUM',
                'name': 'Condominium (Multiple Units)',
                'description': 'Condomínio com múltiplas unidades',
                'icon': '🏢',
                'color': '#f59e0b',
                'order': 4
            },
        ]
        
        self._create_choices(IncorporationType, incorporation_types, 'Incorporation Types')

    def create_incorporation_status(self):
        """Cria status de incorporação"""
        incorporation_status = [
            {
                'code': 'PLANNING',
                'name': 'Em Planejamento',
                'description': 'Incorporação em fase de planejamento',
                'icon': '📋',
                'color': '#6b7280',
                'order': 1
            },
            {
                'code': 'SALES',
                'name': 'Em Vendas',
                'description': 'Incorporação em fase de vendas',
                'icon': '💰',
                'color': '#f59e0b',
                'order': 2
            },
            {
                'code': 'CONSTRUCTION',
                'name': 'Em Construção',
                'description': 'Incorporação em fase de construção',
                'icon': '🚧',
                'color': '#3b82f6',
                'order': 3
            },
            {
                'code': 'DELIVERED',
                'name': 'Entregue',
                'description': 'Incorporação concluída e entregue',
                'icon': '🎉',
                'color': '#22c55e',
                'order': 4
            },
        ]
        
        self._create_choices(IncorporationStatus, incorporation_status, 'Incorporation Status')

    def create_contract_status(self):
        """Cria status de contratos"""
        contract_status = [
            {
                'code': 'ACTIVE',
                'name': 'Ativo',
                'description': 'Contrato ativo',
                'icon': '✅',
                'color': '#22c55e',
                'order': 1
            },
            {
                'code': 'COMPLETED',
                'name': 'Concluído',
                'description': 'Contrato concluído',
                'icon': '🎯',
                'color': '#16a34a',
                'order': 2
            },
            {
                'code': 'CANCELLED',
                'name': 'Cancelado',
                'description': 'Contrato cancelado',
                'icon': '❌',
                'color': '#dc2626',
                'order': 3
            },
            {
                'code': 'PAYED',
                'name': 'Pago',
                'description': 'Contrato totalmente pago',
                'icon': '💰',
                'color': '#059669',
                'order': 4
            },
            {
                'code': 'UNPAYED',
                'name': 'Não Pago',
                'description': 'Contrato com pagamento pendente',
                'icon': '⏳',
                'color': '#ef4444',
                'order': 5
            },
            {
                'code': 'SIGNED',
                'name': 'Assinado',
                'description': 'Contrato assinado',
                'icon': '📝',
                'color': '#3b82f6',
                'order': 6
            },
            {
                'code': 'SIGNED_PAYED',
                'name': 'Assinado e Pago',
                'description': 'Contrato assinado e totalmente pago',
                'icon': '🎉',
                'color': '#10b981',
                'order': 7
            },
        ]
        
        self._create_choices(StatusContract, contract_status, 'Contract Status')

    def create_payment_methods(self):
        """Cria métodos de pagamento"""
        payment_methods = [
            {
                'code': 'CASH',
                'name': 'À Vista',
                'description': 'Pagamento à vista',
                'icon': '💵',
                'color': '#22c55e',
                'order': 1
            },
            {
                'code': 'FINANCED',
                'name': 'Financiado',
                'description': 'Pagamento financiado',
                'icon': '🏦',
                'color': '#3b82f6',
                'order': 2
            },
            {
                'code': 'INSTALMENTS',
                'name': 'Parcelado',
                'description': 'Pagamento parcelado',
                'icon': '📅',
                'color': '#f59e0b',
                'order': 3
            },
            {
                'code': 'DRAWS',
                'name': 'Draws (Por Etapas)',
                'description': 'Pagamento por etapas de construção',
                'icon': '🔄',
                'color': '#8b5cf6',
                'order': 4
            },
        ]
        
        self._create_choices(PaymentMethod, payment_methods, 'Payment Methods')

    def create_production_cells(self):
        """Cria células de produção"""
        production_cells = [
            {
                'code': 'C1',
                'name': 'C1',
                'description': 'Célula de produção 1',
                'icon': '🔧',
                'color': '#3b82f6',
                'order': 1
            },
            {
                'code': 'C2',
                'name': 'C2',
                'description': 'Célula de produção 2',
                'icon': '🔨',
                'color': '#f59e0b',
                'order': 2
            },
            {
                'code': 'C3',
                'name': 'C3',
                'description': 'Célula de produção 3',
                'icon': '⚒️',
                'color': '#22c55e',
                'order': 3
            },
        ]
        
        self._create_choices(ProductionCell, production_cells, 'Production Cells')

    def create_owner_types(self):
        """Cria tipos de proprietário"""
        owner_types = [
            {
                'code': 'PRINCIPAL',
                'name': 'Proprietário Principal',
                'description': 'Proprietário principal do contrato',
                'icon': '👤',
                'color': '#3b82f6',
                'order': 1
            },
            {
                'code': 'CONJUGE',
                'name': 'Cônjuge',
                'description': 'Cônjuge do proprietário principal',
                'icon': '💑',
                'color': '#f59e0b',
                'order': 2
            },
            {
                'code': 'INVESTIDOR',
                'name': 'Investidor',
                'description': 'Investidor no projeto',
                'icon': '💰',
                'color': '#22c55e',
                'order': 3
            },
            {
                'code': 'EMPRESA',
                'name': 'Pessoa Jurídica',
                'description': 'Empresa ou pessoa jurídica',
                'icon': '🏢',
                'color': '#8b5cf6',
                'order': 4
            },
            {
                'code': 'HERDEIRO',
                'name': 'Herdeiro',
                'description': 'Herdeiro do proprietário',
                'icon': '👨‍👩‍👧‍👦',
                'color': '#6b7280',
                'order': 5
            },
            {
                'code': 'PROCURADOR',
                'name': 'Procurador',
                'description': 'Procurador legal',
                'icon': '⚖️',
                'color': '#dc2626',
                'order': 6
            },
        ]
        
        self._create_choices(OwnerType, owner_types, 'Owner Types')

    def _create_choices(self, model_class, choices_data, type_name):
        """Método auxiliar para criar/atualizar choices"""
        created_count = 0
        updated_count = 0
        
        for choice_data in choices_data:
            obj, created = model_class.objects.get_or_create(
                code=choice_data['code'],
                defaults=choice_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Criado: {obj.name}')
            else:
                # Atualizar campos se necessário
                updated = False
                for field, value in choice_data.items():
                    if field != 'code' and getattr(obj, field) != value:
                        setattr(obj, field, value)
                        updated = True
                
                if updated:
                    obj.save()
                    updated_count += 1
                    self.stdout.write(f'  🔄 Atualizado: {obj.name}')
                else:
                    self.stdout.write(f'  ⏭️  Já existe: {obj.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 {type_name}: {created_count} criados, {updated_count} atualizados\n'
            )
        )