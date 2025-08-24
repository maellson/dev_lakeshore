# management/commands/populate_sample_users.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from account.models import (
    PerfilInterno, PerfilClient, PerfilSubcontratado, PerfilFornecedor
)
from account.choice_types import (
    TipoUsuario, Idioma, NivelAcesso, Cargo, Departamento,
    MetodoContato, FrequenciaAtualizacao, FonteClient, CondicaoPagamento
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula usuários de exemplo para todos os tipos. Use --clear para remover os usuários existentes antes de popular.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os usuários de exemplo antes de criar novos.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_sample_data()

        self.stdout.write(self.style.SUCCESS(
            '👥 Populando usuários de exemplo...'))

        with transaction.atomic():
            self.create_internal_users()
            self.create_clients()
            self.create_subcontractors()
            self.create_suppliers()

        self.stdout.write(self.style.SUCCESS(
            '✅ Usuários de exemplo criados com sucesso!'))

    def create_internal_users(self):
        """Cria usuários internos com diferentes níveis hierárquicos"""
        self.stdout.write('\n🏢 Criando usuários internos...')

        # Buscar tipos necessários
        tipo_interno = TipoUsuario.objects.get(code='INTERNO')
        idioma_en = Idioma.objects.get(code='EN')
        idioma_pt = Idioma.objects.get(code='PT')

        # Buscar cargos e departamentos
        cargo_ceo = Cargo.objects.get(code='CEO')
        cargo_gerente_geral = Cargo.objects.get(code='GERENTE_GERAL')
        cargo_gerente_projetos = Cargo.objects.get(code='GERENTE_PROJETOS')
        cargo_supervisor = Cargo.objects.get(code='SUPERVISOR_OBRA')
        cargo_admin = Cargo.objects.get(code='ADMINISTRATIVO')

        depto_executivo = Departamento.objects.get(code='EXECUTIVO')
        depto_projetos = Departamento.objects.get(code='PROJETOS')
        depto_financeiro = Departamento.objects.get(code='FINANCEIRO')
        depto_rh = Departamento.objects.get(code='RH')

        nivel_executivo = NivelAcesso.objects.get(code='EXECUTIVO')
        nivel_gerencial = NivelAcesso.objects.get(code='GERENCIAL')
        nivel_supervisao = NivelAcesso.objects.get(code='SUPERVISAO')
        nivel_operacional = NivelAcesso.objects.get(code='OPERACIONAL')

        internal_users = [
            # NÍVEL 5 - EXECUTIVO
            {
                'user_data': {
                    'email': 'ana.lira@lakeshore.com',
                    'username': 'ana.lira',
                    'first_name': 'Ana',
                    'last_name': 'Lira',
                    'phone': '+1-407-555-0001',
                    'tipo_usuario': tipo_interno,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                    'is_staff': True,
                },
                'perfil_data': {
                    'cargo': cargo_ceo,
                    'departamento': depto_executivo,
                    'nivel_acesso': nivel_executivo,
                }
            },

            # NÍVEL 4 - GERENCIAL
            {
                'user_data': {
                    'email': 'mario.santos@lakeshore.com',
                    'username': 'mario.santos',
                    'first_name': 'Mario',
                    'last_name': 'Santos',
                    'phone': '+1-407-555-0002',
                    'tipo_usuario': tipo_interno,
                    'preferencia_idioma': idioma_pt,
                    'is_active': True,
                    'is_staff': True,
                },
                'perfil_data': {
                    'cargo': cargo_gerente_geral,
                    'departamento': depto_executivo,
                    'nivel_acesso': nivel_gerencial,
                }
            },
            {
                'user_data': {
                    'email': 'carlos.silva@lakeshore.com',
                    'username': 'carlos.silva',
                    'first_name': 'Carlos',
                    'last_name': 'Silva',
                    'phone': '+1-407-555-0003',
                    'tipo_usuario': tipo_interno,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                    'is_staff': True,
                },
                'perfil_data': {
                    'cargo': cargo_gerente_projetos,
                    'departamento': depto_projetos,
                    'nivel_acesso': nivel_gerencial,
                }
            },

            # NÍVEL 3 - SUPERVISÃO
            {
                'user_data': {
                    'email': 'joao.oliveira@lakeshore.com',
                    'username': 'joao.oliveira',
                    'first_name': 'João',
                    'last_name': 'Oliveira',
                    'phone': '+1-407-555-0004',
                    'tipo_usuario': tipo_interno,
                    'preferencia_idioma': idioma_pt,
                    'is_active': True,
                },
                'perfil_data': {
                    'cargo': cargo_supervisor,
                    'departamento': depto_projetos,
                    'nivel_acesso': nivel_supervisao,
                }
            },

            # NÍVEL 2 - OPERACIONAL
            {
                'user_data': {
                    'email': 'pedro.lima@lakeshore.com',
                    'username': 'pedro.lima',
                    'first_name': 'Pedro',
                    'last_name': 'Lima',
                    'phone': '+1-407-555-0005',
                    'tipo_usuario': tipo_interno,
                    'preferencia_idioma': idioma_pt,
                    'is_active': True,
                },
                'perfil_data': {
                    'cargo': cargo_admin,
                    'departamento': depto_rh,
                    'nivel_acesso': nivel_operacional,
                }
            },
            {
                'user_data': {
                    'email': 'sofia.torres@lakeshore.com',
                    'username': 'sofia.torres',
                    'first_name': 'Sofia',
                    'last_name': 'Torres',
                    'phone': '+1-407-555-0006',
                    'tipo_usuario': tipo_interno,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'cargo': cargo_admin,
                    'departamento': depto_financeiro,
                    'nivel_acesso': nivel_operacional,
                }
            }
        ]

        for user_config in internal_users:
            user = self.create_user_if_not_exists(user_config['user_data'])
            if user:
                # Criar/atualizar perfil interno
                perfil, created = PerfilInterno.objects.get_or_create(
                    user=user,
                    defaults=user_config['perfil_data']
                )
                action = 'criado' if created else 'atualizado'
                self.stdout.write(
                    f'  ✓ {user.get_full_name()} ({user.email}) - {action}')

    def create_clients(self):
        """Cria clientes com diferentes perfis"""
        self.stdout.write('\n🏠 Criando clientes...')

        # Buscar tipos necessários
        tipo_client = TipoUsuario.objects.get(code='CLIENT')
        idioma_en = Idioma.objects.get(code='EN')

        metodo_whatsapp = MetodoContato.objects.get(code='WHATSAPP')
        metodo_email = MetodoContato.objects.get(code='EMAIL')
        metodo_telefone = MetodoContato.objects.get(code='TELEFONE')

        freq_semanal = FrequenciaAtualizacao.objects.get(code='SEMANAL')
        freq_quinzenal = FrequenciaAtualizacao.objects.get(code='QUINZENAL')
        freq_mensal = FrequenciaAtualizacao.objects.get(code='MENSAL')

        fonte_indicacao = FonteClient.objects.get(code='INDICACAO')
        fonte_internet = FonteClient.objects.get(code='INTERNET')
        fonte_redes = FonteClient.objects.get(code='REDES_SOCIAIS')

        clients = [
            {
                'user_data': {
                    'email': 'robert.johnson@gmail.com',
                    'username': 'robert.johnson',
                    'first_name': 'Robert',
                    'last_name': 'Johnson',
                    'phone': '+1-407-555-1001',
                    'tipo_usuario': tipo_client,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'main_address': '1234 Oak Street, Orlando, FL 32801',
                    'metodo_contato_preferido': metodo_whatsapp,
                    'frequencia_atualizacao': freq_semanal,
                    'fonte_client': fonte_indicacao,
                    'notas_importantes': 'Cliente familiar, primeira casa. Prefere atualizações frequentes.',
                }
            },
            {
                'user_data': {
                    'email': 'jennifer.davis@davislaw.com',
                    'username': 'jennifer.davis',
                    'first_name': 'Jennifer',
                    'last_name': 'Davis',
                    'phone': '+1-407-555-1002',
                    'tipo_usuario': tipo_client,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'main_address': '5678 Business Blvd, Suite 200, Orlando, FL 32804',
                    'metodo_contato_preferido': metodo_email,
                    'frequencia_atualizacao': freq_quinzenal,
                    'fonte_client': fonte_internet,
                    'notas_importantes': 'Advogada, projeto comercial. Comunicação formal por email.',
                }
            },
            {
                'user_data': {
                    'email': 'michael.brown@brownproperties.com',
                    'username': 'michael.brown',
                    'first_name': 'Michael',
                    'last_name': 'Brown',
                    'phone': '+1-407-555-1003',
                    'tipo_usuario': tipo_client,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'main_address': '9999 Investment Ave, Orlando, FL 32806',
                    'metodo_contato_preferido': metodo_telefone,
                    'frequencia_atualizacao': freq_mensal,
                    'fonte_client': fonte_redes,
                    'notas_importantes': 'Investidor com múltiplas propriedades. Foco em ROI.',
                }
            }
        ]

        for client_config in clients:
            user = self.create_user_if_not_exists(client_config['user_data'])
            if user:
                # Criar/atualizar perfil client
                perfil, created = PerfilClient.objects.get_or_create(
                    user=user,
                    defaults=client_config['perfil_data']
                )
                action = 'criado' if created else 'atualizado'
                self.stdout.write(
                    f'  ✓ {user.get_full_name()} ({user.email}) - {action}')

    def create_subcontractors(self):
        """Cria subcontratados especializados"""
        self.stdout.write('\n🔧 Criando subcontratados...')

        # Buscar tipos necessários
        tipo_sub = TipoUsuario.objects.get(code='SUBCONTRATADO')
        idioma_en = Idioma.objects.get(code='EN')

        subcontractors = [
            {
                'user_data': {
                    'email': 'contact@electricpro.com',
                    'username': 'electricpro',
                    'first_name': 'James',
                    'last_name': 'Electric',
                    'phone': '+1-407-555-2001',
                    'tipo_usuario': tipo_sub,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'empresa': 'ElectricPro LLC',
                    'classificacao': 4.5,
                    'documentos_verificados': True,
                }
            },
            {
                'user_data': {
                    'email': 'service@quickplumbing.com',
                    'username': 'quickplumbing',
                    'first_name': 'Maria',
                    'last_name': 'Rodriguez',
                    'phone': '+1-407-555-2002',
                    'tipo_usuario': tipo_sub,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'empresa': 'QuickPlumbing Inc',
                    'classificacao': 4.8,
                    'documentos_verificados': True,
                }
            },
            {
                'user_data': {
                    'email': 'info@roofmasters.com',
                    'username': 'roofmasters',
                    'first_name': 'David',
                    'last_name': 'Thompson',
                    'phone': '+1-407-555-2003',
                    'tipo_usuario': tipo_sub,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'empresa': 'RoofMasters',
                    'classificacao': 4.2,
                    'documentos_verificados': True,
                }
            }
        ]

        for sub_config in subcontractors:
            user = self.create_user_if_not_exists(sub_config['user_data'])
            if user:
                try:
                    # Criar/atualizar perfil subcontratado
                    perfil, created = PerfilSubcontratado.objects.get_or_create(
                        user=user,
                        defaults=sub_config['perfil_data']
                    )
                    action = 'criado' if created else 'atualizado'
                    self.stdout.write(
                        f'  ✓ {sub_config["perfil_data"]["empresa"]} ({user.email}) - {action}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'  ❌ Erro ao criar perfil para {user.email}: {e}'))

    def create_suppliers(self):
        """Cria fornecedores de materiais"""
        self.stdout.write('\n📦 Criando fornecedores...')

        # Buscar tipos necessários
        tipo_fornecedor = TipoUsuario.objects.get(code='FORNECEDOR')
        idioma_en = Idioma.objects.get(code='EN')

        cond_a_vista = CondicaoPagamento.objects.get(code='A_VISTA')
        cond_30_dias = CondicaoPagamento.objects.get(code='30_DIAS')
        cond_60_dias = CondicaoPagamento.objects.get(code='60_DIAS')

        suppliers = [
            {
                'user_data': {
                    'email': 'commercial@homedepot.com',
                    'username': 'homedepot',
                    'first_name': 'Home',
                    'last_name': 'Depot',
                    'phone': '+1-407-555-3001',
                    'tipo_usuario': tipo_fornecedor,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'empresa': 'The Home Depot',
                    'prazo_medio_entrega': 2,
                    'condicoes_pagamento': cond_30_dias,
                }
            },
            {
                'user_data': {
                    'email': 'sales@lowes.com',
                    'username': 'lowes',
                    'first_name': 'Lowes',
                    'last_name': 'Company',
                    'phone': '+1-407-555-3002',
                    'tipo_usuario': tipo_fornecedor,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'empresa': "Lowe's Companies Inc",
                    'prazo_medio_entrega': 3,
                    'condicoes_pagamento': cond_a_vista,
                }
            },
            {
                'user_data': {
                    'email': 'orders@localsupply.com',
                    'username': 'localsupply',
                    'first_name': 'Local',
                    'last_name': 'Supply',
                    'phone': '+1-407-555-3003',
                    'tipo_usuario': tipo_fornecedor,
                    'preferencia_idioma': idioma_en,
                    'is_active': True,
                },
                'perfil_data': {
                    'empresa': 'Local Construction Supply',
                    'prazo_medio_entrega': 7,
                    'condicoes_pagamento': cond_60_dias,
                }
            }
        ]

        for supplier_config in suppliers:
            user = self.create_user_if_not_exists(supplier_config['user_data'])
            if user:
                # Criar/atualizar perfil fornecedor
                perfil, created = PerfilFornecedor.objects.get_or_create(
                    user=user,
                    defaults=supplier_config['perfil_data']
                )
                action = 'criado' if created else 'atualizado'
                self.stdout.write(
                    f'  ✓ {supplier_config["perfil_data"]["empresa"]} ({user.email}) - {action}')

    def create_user_if_not_exists(self, user_data):
        """Cria usuário se não existir"""
        try:
            # Verificar se usuário já existe
            user = User.objects.get(email=user_data['email'])
            return user
        except User.DoesNotExist:
            # Criar novo usuário
            password = 'LakeShore2024!'  # Senha padrão para todos
            user = User.objects.create_user(
                password=password,
                **user_data
            )
            return user
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Erro ao criar usuário {user_data["email"]}: {str(e)}')
            )
            return None

    def clear_sample_data(self):
        """Remove todos os usuários e perfis de exemplo."""
        self.stdout.write(self.style.WARNING('🔥 Removendo dados de exemplo...'))
        
        # Lista de emails de exemplo para identificar os usuários a serem removidos
        sample_emails = [
            'ana.lira@lakeshore.com', 'mario.santos@lakeshore.com', 'carlos.silva@lakeshore.com',
            'joao.oliveira@lakeshore.com', 'pedro.lima@lakeshore.com', 'sofia.torres@lakeshore.com',
            'robert.johnson@gmail.com', 'jennifer.davis@davislaw.com', 'michael.brown@brownproperties.com',
            'contact@electricpro.com', 'service@quickplumbing.com', 'info@roofmasters.com',
            'commercial@homedepot.com', 'sales@lowes.com', 'orders@localsupply.com'
        ]
        
        try:
            deleted_count, _ = User.objects.filter(email__in=sample_emails).delete()
            self.stdout.write(self.style.SUCCESS(f'  ✓ {deleted_count} usuários de exemplo removidos.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Erro ao remover usuários: {e}'))
