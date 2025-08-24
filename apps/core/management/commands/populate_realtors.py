# apps/core/management/commands/populate_realtors.py
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Realtor, County
from decimal import Decimal


class Command(BaseCommand):
    help = 'Popula dados iniciais de Realtors'

    def handle(self, *args, **options):
        """Executa o comando de população dos realtors"""
        
        with transaction.atomic():
            self.stdout.write('🏠 Populando Realtors...\n')
            
            self.create_realtors()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Todos os Realtors criados com sucesso!')
            )

    def create_realtors(self):
        """Cria realtors de exemplo"""
        
        # Buscar alguns counties para associar aos realtors
        # Se não existirem, vamos criar counties básicos
        counties = self.ensure_counties()
        
        realtors_data = [
            {
                'name': 'Sarah Johnson',
                'phone': '+1-407-555-0123',
                'email': 'sarah.johnson@flrealty.com',
                'default_commission_rate': Decimal('3.00'),
                'counties': ['Miami-Dade', 'Broward'],
                'is_active': True
            },
            {
                'name': 'Michael Rodriguez',
                'phone': '+1-305-555-0156',
                'email': 'mrodriguez@sunshineproperties.com',
                'default_commission_rate': Decimal('2.75'),
                'counties': ['Orange', 'Seminole'],
                'is_active': True
            },
            {
                'name': 'Jennifer Smith',
                'phone': '+1-813-555-0189',
                'email': 'jsmith@tamparealty.com',
                'default_commission_rate': Decimal('3.25'),
                'counties': ['Hillsborough', 'Pinellas'],
                'is_active': True
            },
            {
                'name': 'David Wilson',
                'phone': '+1-561-555-0234',
                'email': 'dwilson@palmbeachproperties.com',
                'default_commission_rate': Decimal('3.50'),
                'counties': ['Palm Beach', 'Martin'],
                'is_active': True
            },
            {
                'name': 'Lisa Anderson',
                'phone': '+1-904-555-0267',
                'email': 'landerson@northflrealty.com',
                'default_commission_rate': Decimal('2.90'),
                'counties': ['Duval', 'Clay', 'St. Johns'],
                'is_active': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for realtor_data in realtors_data:
            # Separar counties dos outros dados
            county_names = realtor_data.pop('counties')
            
            # Criar ou atualizar realtor
            realtor, created = Realtor.objects.get_or_create(
                name=realtor_data['name'],
                defaults=realtor_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Criado: {realtor.name}')
            else:
                # Atualizar campos se necessário
                updated = False
                for field, value in realtor_data.items():
                    if getattr(realtor, field) != value:
                        setattr(realtor, field, value)
                        updated = True
                
                if updated:
                    realtor.save()
                    updated_count += 1
                    self.stdout.write(f'  🔄 Atualizado: {realtor.name}')
                else:
                    self.stdout.write(f'  ⏭️  Já existe: {realtor.name}')
            
            # Associar counties
            self.associate_counties(realtor, county_names, counties)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Realtors: {created_count} criados, {updated_count} atualizados\n'
            )
        )

        

    def ensure_counties(self):
        """Garante que existam counties básicos da Florida"""
        
        basic_counties = [
            {'name': 'Miami-Dade', 'code': 'MDC'},
            {'name': 'Broward', 'code': 'BRD'},
            {'name': 'Orange', 'code': 'ORA'},
            {'name': 'Seminole', 'code': 'SEM'},
            {'name': 'Hillsborough', 'code': 'HIL'},
            {'name': 'Pinellas', 'code': 'PIN'},
            {'name': 'Palm Beach', 'code': 'PBC'},
            {'name': 'Martin', 'code': 'MAR'},
            {'name': 'Duval', 'code': 'DUV'},
            {'name': 'Clay', 'code': 'CLA'},
            {'name': 'St. Johns', 'code': 'STJ'},
        ]
        
        counties = {}
        for county_data in basic_counties:
            county, created = County.objects.get_or_create(
                name=county_data['name'],
                defaults={
                    'code': county_data['code'],
                    'state': 'FL',
                    'is_active': True
                }
            )
            counties[county.name] = county
            
            if created:
                self.stdout.write(f'  🏛️  County criado: {county.name}')
        
        return counties

    def associate_counties(self, realtor, county_names, counties_dict):
        """Associa counties ao realtor"""
        
        # Limpar associações existentes
        realtor.usually_works_in.clear()
        
        # Adicionar novos counties
        for county_name in county_names:
            if county_name in counties_dict:
                county = counties_dict[county_name]
                realtor.usually_works_in.add(county)
                self.stdout.write(f'    📍 {realtor.name} → {county.name}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'    ⚠️  County não encontrado: {county_name}')
                )