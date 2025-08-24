# apps/projects/management/commands/populate_incorporation_bradford.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from projects.models import Incorporation
from projects.models.choice_types import IncorporationType, IncorporationStatus
from core.models import County
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria uma incorporação de exemplo: Bradford Gardens Phase 1'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='Bradford Gardens Phase 1',
            help='Nome da incorporação'
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('🏘️  Criando incorporação Bradford Gardens...\n')

            # Obter dependências
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True).first()

            # Dados da incorporação
            incorporation_data = {
                'name': options['name'],
                'incorporation_type': IncorporationType.objects.get(code='BUILD_SIMPLE'),
                'county': County.objects.get(id=52),  # Bradford, FL
                'project_description': (
                    'Loteamento residencial Bradford Gardens Phase 1 - '
                    'Desenvolvimento de 25 casas individuais de padrão médio '
                    'em Bradford County, Florida. Projeto contempla casas '
                    'de 3 quartos, 2 banheiros, garagem para 2 carros, '
                    'área construída de aproximadamente 150m². '
                    'Infraestrutura completa com água, esgoto, energia elétrica '
                    'e pavimentação asfáltica.'
                ),
                'launch_date': date.today() + timedelta(days=30),  # Lançamento em 30 dias
                'incorporation_status': IncorporationStatus.objects.get(code='PLANNING'),
                'is_active': True,
                'created_by': admin_user
            }

            # Criar incorporação
            incorporation, created = Incorporation.objects.get_or_create(
                name=incorporation_data['name'],
                county=incorporation_data['county'],
                defaults=incorporation_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Incorporação criada com sucesso!\n'
                        f'📋 Nome: {incorporation.name}\n'
                        f'🏢 Tipo: {incorporation.incorporation_type.name}\n'
                        f'📍 County: {incorporation.county.name}\n'
                        f'📅 Launch Date: {incorporation.launch_date}\n'
                        f'📊 Status: {incorporation.incorporation_status.name}\n'
                    )
                )

                # Mostrar próximos passos
                self.stdout.write(
                    self.style.WARNING(
                        f'\n🎯 PRÓXIMOS PASSOS:\n'
                        f'1. Criar projetos individuais usando modelo M01 - CIC\n'
                        f'2. Associar projetos a esta incorporação\n'
                        f'3. Mudar status para "SALES" quando pronto\n'
                        f'4. Criar contratos para os projetos vendidos\n'
                    )
                )

                # Sugestão de command para projetos
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f'\n💡 SUGESTÃO - Criar projetos automaticamente:\n'
                        f'python manage.py create_projects_for_incorporation {incorporation.id}\n'
                    )
                )

            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'ℹ️  Incorporação já existe: {incorporation.name}\n'
                        f'ID: {incorporation.id}\n'
                        f'Status: {incorporation.incorporation_status.name}'
                    )
                )

            return f"Incorporação '{incorporation.name}' criada com ID {incorporation.id}"
