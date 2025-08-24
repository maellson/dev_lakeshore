#commands/populate_initial_data.py
"""
Comando Django para popular dados iniciais do sistema
Execução: python manage.py populate_initial_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from account.choice_types import (
    TipoUsuario, Idioma, NivelAcesso, Cargo, Departamento,
    MetodoContato, FrequenciaAtualizacao, FonteClient, CondicaoPagamento
)


class Command(BaseCommand):
    help = 'Popula dados iniciais obrigatórios do sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando população de dados...'))
        
        with transaction.atomic():
            self.populate_tipos_usuario()
            self.populate_idiomas()
            self.populate_niveis_acesso()
            self.populate_cargos()
            self.populate_departamentos()
            self.populate_metodos_contato()
            self.populate_frequencias_atualizacao()
            self.populate_fontes_cliente()
            self.populate_condicoes_pagamento()
        
        self.stdout.write(self.style.SUCCESS('✅ Dados iniciais populados com sucesso!'))

    def populate_tipos_usuario(self):
        """Popula tipos de usuário básicos"""
        tipos = [
            {
                'code': 'INTERNO',
                'name': 'Funcionário Interno',
                'description': 'Funcionários da empresa',
                'icon': '👤',
                'color': '#2563eb',
                'order': 1
            },
            {
                'code': 'CLIENT',
                'name': 'Client',
                'description': 'Clientes da empresa',
                'icon': '🏠',
                'color': '#059669',
                'order': 2
            },
            {
                'code': 'SUBCONTRATADO',
                'name': 'Subcontratado',
                'description': 'Prestadores de serviços terceirizados',
                'icon': '🔧',
                'color': '#dc2626',
                'order': 3
            },
            {
                'code': 'FORNECEDOR',
                'name': 'Fornecedor',
                'description': 'Fornecedores de materiais',
                'icon': '📦',
                'color': '#7c3aed',
                'order': 4
            }
        ]
        
        for tipo_data in tipos:
            tipo, created = TipoUsuario.objects.get_or_create(
                code=tipo_data['code'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'✓ Criado TipoUsuario: {tipo.name}')

    def populate_idiomas(self):
        """Popula idiomas disponíveis"""
        idiomas = [
            {
                'code': 'PT',
                'name': 'Português',
                'description': 'Português do Brasil',
                'locale_code': 'pt-BR',
                'icon': '🇧🇷',
                'color': '#10b981',
                'order': 1
            },
            {
                'code': 'EN',
                'name': 'English',
                'description': 'American English',
                'locale_code': 'en-US',
                'icon': '🇺🇸',
                'color': '#3b82f6',
                'order': 2
            },
            {
                'code': 'ES',
                'name': 'Español',
                'description': 'Español Internacional',
                'locale_code': 'es-ES',
                'icon': '🇪🇸',
                'color': '#ef4444',
                'order': 3
            }
        ]
        
        for idioma_data in idiomas:
            idioma, created = Idioma.objects.get_or_create(
                code=idioma_data['code'],
                defaults=idioma_data
            )
            if created:
                self.stdout.write(f'✓ Criado Idioma: {idioma.name}')

    def populate_niveis_acesso(self):
        """Popula níveis de acesso hierárquicos"""
        niveis = [
            {
                'code': 'EXECUTIVO',
                'name': 'Executivo',
                'description': 'Nível executivo - acesso completo',
                'nivel': 5,
                'icon': '👑',
                'color': '#dc2626',
                'order': 1
            },
            {
                'code': 'GERENCIAL',
                'name': 'Gerencial',
                'description': 'Nível gerencial - gestão de projetos',
                'nivel': 4,
                'icon': '📊',
                'color': '#ea580c',
                'order': 2
            },
            {
                'code': 'SUPERVISAO',
                'name': 'Supervisão',
                'description': 'Nível de supervisão - coordenação',
                'nivel': 3,
                'icon': '🎯',
                'color': '#ca8a04',
                'order': 3
            },
            {
                'code': 'OPERACIONAL',
                'name': 'Operacional',
                'description': 'Nível operacional - execução',
                'nivel': 2,
                'icon': '⚡',
                'color': '#16a34a',
                'order': 4
            },
            {
                'code': 'BASICO',
                'name': 'Básico',
                'description': 'Acesso básico ao sistema',
                'nivel': 1,
                'icon': '📝',
                'color': '#6b7280',
                'order': 5
            }
        ]
        
        for nivel_data in niveis:
            nivel, created = NivelAcesso.objects.get_or_create(
                code=nivel_data['code'],
                defaults=nivel_data
            )
            if created:
                self.stdout.write(f'✓ Criado NivelAcesso: {nivel.name}')

    def populate_cargos(self):
        """Popula cargos básicos"""
        # Buscar níveis para associação
        nivel_executivo = NivelAcesso.objects.get(code='EXECUTIVO')
        nivel_gerencial = NivelAcesso.objects.get(code='GERENCIAL')
        nivel_supervisao = NivelAcesso.objects.get(code='SUPERVISAO')
        nivel_operacional = NivelAcesso.objects.get(code='OPERACIONAL')
        
        cargos = [
            {
                'code': 'CEO',
                'name': 'CEO',
                'description': 'Chief Executive Officer',
                'nivel_acesso': nivel_executivo,
                'icon': '👑',
                'color': '#dc2626',
                'order': 1
            },
            {
                'code': 'GERENTE_GERAL',
                'name': 'Gerente Geral',
                'description': 'Gerente Geral da Empresa',
                'nivel_acesso': nivel_gerencial,
                'icon': '🏢',
                'color': '#ea580c',
                'order': 2
            },
            {
                'code': 'GERENTE_PROJETOS',
                'name': 'Gerente de Projetos',
                'description': 'Responsável pela gestão de projetos',
                'nivel_acesso': nivel_gerencial,
                'icon': '📋',
                'color': '#ca8a04',
                'order': 3
            },
            {
                'code': 'SUPERVISOR_OBRA',
                'name': 'Supervisor de Obra',
                'description': 'Supervisão de obras e projetos',
                'nivel_acesso': nivel_supervisao,
                'icon': '🏗️',
                'color': '#16a34a',
                'order': 4
            },
            {
                'code': 'ADMINISTRATIVO',
                'name': 'Administrativo',
                'description': 'Funções administrativas',
                'nivel_acesso': nivel_operacional,
                'icon': '📄',
                'color': '#6b7280',
                'order': 5
            }
        ]
        
        for cargo_data in cargos:
            cargo, created = Cargo.objects.get_or_create(
                code=cargo_data['code'],
                defaults=cargo_data
            )
            if created:
                self.stdout.write(f'✓ Criado Cargo: {cargo.name}')

    def populate_departamentos(self):
        """Popula departamentos básicos"""
        departamentos = [
            {
                'code': 'EXECUTIVO',
                'name': 'Executivo',
                'description': 'Diretoria e alta administração',
                'icon': '🏛️',
                'color': '#dc2626',
                'order': 1
            },
            {
                'code': 'PROJETOS',
                'name': 'Projetos',
                'description': 'Gestão e execução de projetos',
                'icon': '🏗️',
                'color': '#ea580c',
                'order': 2
            },
            {
                'code': 'FINANCEIRO',
                'name': 'Financeiro',
                'description': 'Gestão financeira e contábil',
                'icon': '💰',
                'color': '#16a34a',
                'order': 3
            },
            {
                'code': 'COMPRAS',
                'name': 'Compras',
                'description': 'Aquisição de materiais e serviços',
                'icon': '🛒',
                'color': '#7c3aed',
                'order': 4
            },
            {
                'code': 'RH',
                'name': 'Recursos Humanos',
                'description': 'Gestão de pessoas',
                'icon': '👥',
                'color': '#06b6d4',
                'order': 5
            }
        ]
        
        for depto_data in departamentos:
            depto, created = Departamento.objects.get_or_create(
                code=depto_data['code'],
                defaults=depto_data
            )
            if created:
                self.stdout.write(f'✓ Criado Departamento: {depto.name}')

    def populate_metodos_contato(self):
        """Popula métodos de contato"""
        metodos = [
            {
                'code': 'EMAIL',
                'name': 'E-mail',
                'description': 'Contato via e-mail',
                'icon': '📧',
                'color': '#3b82f6',
                'order': 1
            },
            {
                'code': 'TELEFONE',
                'name': 'Telefone',
                'description': 'Contato via telefone',
                'icon': '📞',
                'color': '#16a34a',
                'order': 2
            },
            {
                'code': 'SMS',
                'name': 'SMS',
                'description': 'Mensagens de texto',
                'icon': '💬',
                'color': '#ca8a04',
                'order': 3
            },
            {
                'code': 'WHATSAPP',
                'name': 'WhatsApp',
                'description': 'Mensagens via WhatsApp',
                'icon': '📱',
                'color': '#16a34a',
                'order': 4
            }
        ]
        
        for metodo_data in metodos:
            metodo, created = MetodoContato.objects.get_or_create(
                code=metodo_data['code'],
                defaults=metodo_data
            )
            if created:
                self.stdout.write(f'✓ Criado MetodoContato: {metodo.name}')

    def populate_frequencias_atualizacao(self):
        """Popula frequências de atualização"""
        frequencias = [
            {
                'code': 'DIARIA',
                'name': 'Diária',
                'description': 'Atualizações diárias',
                'dias': 1,
                'icon': '📅',
                'color': '#dc2626',
                'order': 1
            },
            {
                'code': 'SEMANAL',
                'name': 'Semanal',
                'description': 'Atualizações semanais',
                'dias': 7,
                'icon': '📆',
                'color': '#ea580c',
                'order': 2
            },
            {
                'code': 'QUINZENAL',
                'name': 'Quinzenal',
                'description': 'Atualizações quinzenais',
                'dias': 15,
                'icon': '🗓️',
                'color': '#16a34a',
                'order': 3
            },
            {
                'code': 'MENSAL',
                'name': 'Mensal',
                'description': 'Atualizações mensais',
                'dias': 30,
                'icon': '📋',
                'color': '#3b82f6',
                'order': 4
            }
        ]
        
        for freq_data in frequencias:
            freq, created = FrequenciaAtualizacao.objects.get_or_create(
                code=freq_data['code'],
                defaults=freq_data
            )
            if created:
                self.stdout.write(f'✓ Criado FrequenciaAtualizacao: {freq.name}')

    def populate_fontes_cliente(self):
        """Popula fontes de clientes"""
        fontes = [
            {
                'code': 'INDICACAO',
                'name': 'Indicação',
                'description': 'Cliente indicado por outro cliente',
                'icon': '👥',
                'color': '#16a34a',
                'order': 1
            },
            {
                'code': 'INTERNET',
                'name': 'Internet',
                'description': 'Pesquisa na internet',
                'icon': '🌐',
                'color': '#3b82f6',
                'order': 2
            },
            {
                'code': 'REDES_SOCIAIS',
                'name': 'Redes Sociais',
                'description': 'Instagram, Facebook, etc.',
                'icon': '📱',
                'color': '#ec4899',
                'order': 3
            },
            {
                'code': 'PUBLICIDADE',
                'name': 'Publicidade',
                'description': 'Anúncios pagos',
                'icon': '📢',
                'color': '#ca8a04',
                'order': 4
            }
        ]
        
        for fonte_data in fontes:
            fonte, created = FonteClient.objects.get_or_create(
                code=fonte_data['code'],
                defaults=fonte_data
            )
            if created:
                self.stdout.write(f'✓ Criado FonteClient: {fonte.name}')

    def populate_condicoes_pagamento(self):
        """Popula condições de pagamento"""
        condicoes = [
            {
                'code': 'A_VISTA',
                'name': 'À Vista',
                'description': 'Pagamento à vista',
                'prazo_dias': 0,
                'desconto_percentual': 5.00,
                'icon': '💵',
                'color': '#16a34a',
                'order': 1
            },
            {
                'code': '30_DIAS',
                'name': '30 dias',
                'description': 'Pagamento em 30 dias',
                'prazo_dias': 30,
                'desconto_percentual': 0.00,
                'icon': '📅',
                'color': '#3b82f6',
                'order': 2
            },
            {
                'code': '60_DIAS',
                'name': '60 dias',
                'description': 'Pagamento em 60 dias',
                'prazo_dias': 60,
                'desconto_percentual': 0.00,
                'icon': '🗓️',
                'color': '#ca8a04',
                'order': 3
            },
            {
                'code': '90_DIAS',
                'name': '90 dias',
                'description': 'Pagamento em 90 dias',
                'prazo_dias': 90,
                'desconto_percentual': 0.00,
                'icon': '📋',
                'color': '#dc2626',
                'order': 4
            }
        ]
        
        for cond_data in condicoes:
            cond, created = CondicaoPagamento.objects.get_or_create(
                code=cond_data['code'],
                defaults=cond_data
            )
            if created:
                self.stdout.write(f'✓ Criado CondicaoPagamento: {cond.name}')