# apps/leads/management/commands/populate_sample_leads.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from leads.models import Lead
from leads.models.lead_types import StatusChoice, ElevationChoice
from core.models import County, Realtor, HOA
from projects.models import ModelProject
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula leads de exemplo com dados realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=15,
            help='Número de leads para criar (padrão: 15)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os leads existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️  Removendo leads existentes...')
            Lead.objects.all().delete()
            self.stdout.write(self.style.WARNING('Leads removidos.'))

        with transaction.atomic():
            self.stdout.write(
                f'👥 Criando {options["count"]} leads de exemplo...\n')

            # Obter dependências necessárias
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True).first()

            # Verificar se dependências existem
            if not self.check_dependencies():
                return

            # Criar leads
            created_count = 0
            for i in range(options['count']):
                lead_data = self.generate_lead_data(admin_user)
                lead = Lead.objects.create(**lead_data)
                created_count += 1

                self.stdout.write(
                    f'  ✅ Lead {i+1}: {lead.client_full_name} - '
                    f'{lead.county.name} ({lead.status.name})'
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 {created_count} leads criados com sucesso!\n'
                    f'📊 Distribuição por status:\n'
                    f'{self.get_status_distribution()}'
                )
            )

    def check_dependencies(self):
        """Verifica se todas as dependências existem"""
        missing = []

        if not StatusChoice.objects.exists():
            missing.append(
                'StatusChoice (execute: python manage.py populate_leads_choices)')

        if not ElevationChoice.objects.exists():
            missing.append(
                'ElevationChoice (execute: python manage.py populate_leads_choices)')

        if not County.objects.exists():
            missing.append('Counties (já devem existir)')

        if not ModelProject.objects.filter(code='M01').exists():
            missing.append(
                'ModelProject M01-CIC (execute: python manage.py populate_model_m01_cic)')

        if missing:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Dependências faltando:\n' +
                    '\n'.join(f'  - {item}' for item in missing)
                )
            )
            return False

        return True

    def generate_lead_data(self, admin_user):
        """Gera dados realistas para um lead"""

        # Dados de clientes americanos realistas
        sample_clients = [
            {
                'company': 'Smith Family Trust',
                'name': 'Robert Smith',
                'email': 'robert.smith@email.com',
                'phone': '+1-941-555-0123'
            },
            {
                'company': 'Johnson Enterprises LLC',
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@gmail.com',
                'phone': '+1-863-555-0156'
            },
            {
                'company': 'Rodriguez Realty',
                'name': 'Michael Davis',
                'email': 'mike.davis@yahoo.com',
                'phone': '+1-407-555-0189'
            },
            {
                'company': 'Williams Investment Group',
                'name': 'Jennifer Williams',
                'email': 'j.williams@outlook.com',
                'phone': '+1-321-555-0234'
            },
            {
                'company': 'Manalytics.AI',
                'name': 'David Brown',
                'email': 'david.brown@hotmail.com',
                'phone': '+1-386-555-0267'
            },
            {
                'company': 'Garcia Properties Inc',
                'name': 'Maria Garcia',
                'email': 'maria.garcia@email.com',
                'phone': '+1-954-555-0298'
            },
            {
                'company': 'Bravobot',
                'name': 'James Wilson',
                'email': 'james.wilson@gmail.com',
                'phone': '+1-850-555-0321'
            },
            {
                'company': 'Miller Development Co',
                'name': 'Lisa Miller',
                'email': 'lisa.miller@company.com',
                'phone': '+1-239-555-0354'
            },
            {
                'company': 'Bravonix',
                'name': 'Christopher Taylor',
                'email': 'chris.taylor@email.com',
                'phone': '+1-727-555-0387'
            },
            {
                'company': 'Anderson Family Holdings',
                'name': 'Amanda Anderson',
                'email': 'amanda.anderson@gmail.com',
                'phone': '+1-813-555-0412'
            },
            {
                'company': 'LGPDNOW',
                'name': 'Matthew Thomas',
                'email': 'matt.thomas@yahoo.com',
                'phone': '+1-904-555-0445'
            },
            {
                'company': 'Rodriguez Investments',
                'name': 'Carlos Rodriguez',
                'email': 'carlos.rodriguez@email.com',
                'phone': '+1-561-555-0478'
            },
            {
                'company': 'AgentsAI',
                'name': 'Ashley Martinez',
                'email': 'ashley.martinez@gmail.com',
                'phone': '+1-305-555-0501'
            },
            {
                'company': 'Thompson Realty Group',
                'name': 'Brian Thompson',
                'email': 'brian.thompson@outlook.com',
                'phone': '+1-941-555-0534'
            },
            {
                'company': 'San Claud Realty',
                'name': 'Michelle White',
                'email': 'michelle.white@hotmail.com',
                'phone': '+1-352-555-0567'
            },
        ]

        # Notas de exemplo realistas
        sample_notes = [
            'Interested in energy-efficient features and smart home technology.',
            'Looking for move-in ready home by Q3 2025. Has specific HOA requirements.',
            'First-time homebuyer, needs guidance through the process.',
            'Relocating from Georgia for job. Timeline flexible.',
            'Investment property for rental purposes. Cash buyer.',
            'Retiring couple downsizing from larger home.',
            'Young family needs 3+ bedrooms and good school district.',
            'Referred by previous customer. High priority lead.',
            'Interested in custom modifications to standard plan.',
            'Budget-conscious buyer, looking for best value options.',
            'Prefers contemporary style with open floor plan.',
            'Has specific lot requirements due to HOA restrictions.',
            'Military family with VA loan pre-approval.',
            'Looking for quick closing within 60 days.',
            ''  # Alguns sem notas
        ]

        # Parcel IDs realistas da Florida
        sample_parcel_ids = [
            '12-34-56-789-012-345',
            '98-76-54-321-098-765',
            '11-22-33-444-555-666',
            '87-65-43-210-987-654',
            '55-66-77-888-999-000',
            '44-33-22-111-000-999',
            '77-88-99-000-111-222',
            '33-44-55-666-777-888',
            '66-77-88-999-000-111',
            '22-33-44-555-666-777',
            '99-00-11-222-333-444',
            '88-99-00-111-222-333',
            '00-11-22-333-444-555',
            '77-66-55-444-333-222',
            '55-44-33-222-111-000',
        ]

        # Selecionar cliente aleatório
        client = random.choice(sample_clients)

        # Obter objetos necessários
        counties = list(County.objects.all())
        status_choices = list(StatusChoice.objects.all())
        elevation_choices = list(ElevationChoice.objects.all())
        model_project = ModelProject.objects.get(code='M01')

        # Realtors e HOAs (podem não existir)
        realtors = list(Realtor.objects.all()
                        ) if Realtor.objects.exists() else []
        hoas = list(HOA.objects.all()) if HOA.objects.exists() else []

        # Decidir se terá realtor (30% de chance)
        has_realtor = random.choice([True, False, False, False])  # 25% chance

        # Decidir se terá HOA (40% de chance)
        has_hoa = random.choice(
            [True, True, False, False, False])  # 40% chance

        # Gerar valor do contrato baseado em faixas realistas
        contract_values = [
            Decimal('180000.00'), Decimal('195000.00'), Decimal('210000.00'),
            Decimal('225000.00'), Decimal('240000.00'), Decimal('255000.00'),
            Decimal('270000.00'), Decimal('285000.00'), Decimal('300000.00'),
            Decimal('320000.00'), Decimal('340000.00'), Decimal('365000.00'),
            Decimal('385000.00'), Decimal('410000.00'), Decimal('435000.00'),
        ]

        # Distribuição de status mais realista
        status_weights = {
            'PENDING': 40,      # 40% - maioria dos leads
            'QUALIFIED': 25,    # 25% - qualificados
            'FOLLOW_UP': 15,    # 15% - em follow up
            'CONVERTED': 10,    # 10% - convertidos
            'ON_HOLD': 7,       # 7% - pausados
            'REJECTED': 3,      # 3% - rejeitados
        }

        # Selecionar status baseado nos pesos
        status_codes = list(status_weights.keys())
        status_probs = list(status_weights.values())
        selected_status_code = random.choices(
            status_codes, weights=status_probs)[0]
        selected_status = StatusChoice.objects.get(code=selected_status_code)

        return {
            'client_company_name': client['company'],
            'client_full_name': client['name'],
            'client_phone': client['phone'],
            'client_email': client['email'],
            'note': random.choice(sample_notes),
            'is_realtor': has_realtor,
            'realtor': random.choice(realtors) if has_realtor and realtors else None,
            'state': 'FL',
            'county': random.choice(counties),
            'parcel_id': random.choice(sample_parcel_ids),
            'house_model': model_project,
            'other_model': '',  # Não usando "Other" neste exemplo
            'elevation': random.choice(elevation_choices),
            'has_hoa': has_hoa,
            'hoa': random.choice(hoas) if has_hoa and hoas else None,
            'contract_value': random.choice(contract_values),
            'status': selected_status,
            'created_by': admin_user,
        }

    def get_status_distribution(self):
        """Retorna distribuição de leads por status"""
        distribution = []
        for status in StatusChoice.objects.all():
            count = Lead.objects.filter(status=status).count()
            if count > 0:
                distribution.append(f'  - {status.name}: {count} leads')

        return '\n'.join(distribution) if distribution else '  - Nenhum lead criado'
