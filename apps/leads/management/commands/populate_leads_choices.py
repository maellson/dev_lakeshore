# apps/leads/management/commands/populate_leads_choices.py

from django.core.management.base import BaseCommand
from django.db import transaction
from leads.models.lead_types import StatusChoice, ElevationChoice


class Command(BaseCommand):
    help = 'Popula choice types do módulo Leads'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('👥 Populando Choice Types do módulo Leads...\n')

            self.create_status_choices()
            self.create_elevation_choices()

            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Choice Types de Leads criados com sucesso!')
            )

    def create_status_choices(self):
        """Cria status de leads"""
        status_choices = [
            {
                'code': 'PENDING',
                'name': 'Pending',
                'description': 'Lead aguardando qualificação inicial',
                'icon': '⏳',
                'color': '#fbbf24',  # yellow
                'order': 1
            },
            {
                'code': 'QUALIFIED',
                'name': 'Qualified',
                'description': 'Lead qualificado e aprovado para conversão',
                'icon': '✅',
                'color': '#3b82f6',  # blue
                'order': 2
            },
            {
                'code': 'CONVERTED',
                'name': 'Converted',
                'description': 'Lead convertido em contrato',
                'icon': '🎯',
                'color': '#10b981',  # green
                'order': 3
            },
            {
                'code': 'REJECTED',
                'name': 'Rejected',
                'description': 'Lead rejeitado ou cancelado',
                'icon': '❌',
                'color': '#ef4444',  # red
                'order': 4
            },
            {
                'code': 'FOLLOW_UP',
                'name': 'Follow Up',
                'description': 'Lead em acompanhamento adicional',
                'icon': '📞',
                'color': '#8b5cf6',  # purple
                'order': 5
            },
            {
                'code': 'ON_HOLD',
                'name': 'On Hold',
                'description': 'Lead pausado temporariamente',
                'icon': '⏸️',
                'color': '#6b7280',  # gray
                'order': 6
            },
        ]

        self._create_choices(StatusChoice, status_choices, 'Lead Status')

    def create_elevation_choices(self):
        """Cria tipos de elevação"""
        elevation_choices = [
            {
                'code': 'CONTEMPORARY',
                'name': 'Contemporary',
                'description': 'Estilo contemporâneo moderno',
                'icon': '🏠',
                'color': '#3b82f6',
                'locale_code': 'CONT',
                'order': 1
            },
            {
                'code': 'FARM',
                'name': 'Farm House',
                'description': 'Estilo casa de fazenda tradicional',
                'icon': '🏡',
                'color': '#22c55e',
                'locale_code': 'FARM',
                'order': 2
            },
            {
                'code': 'TRADITIONAL',
                'name': 'Traditional',
                'description': 'Estilo tradicional clássico',
                'icon': '🏘️',
                'color': '#f59e0b',
                'locale_code': 'TRAD',
                'order': 3
            },
            {
                'code': 'NA',
                'name': 'N/A',
                'description': 'Não aplicável ou não definido',
                'icon': '❓',
                'color': '#6b7280',
                'locale_code': 'NA',
                'order': 99
            },
        ]

        self._create_choices(ElevationChoice, elevation_choices, 'Elevations')

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
