# apps/core/management/commands/load_florida_counties.py
from django.core.management.base import BaseCommand
from core.models import County


class Command(BaseCommand):
    """
    Management command para carregar os 67 counties da Florida

    USAGE:
    python manage.py load_florida_counties
    python manage.py load_florida_counties --clear  # Limpa antes de criar
    """

    help = 'Load Florida counties into database'

    # Lista completa dos 67 counties da Florida
    FLORIDA_COUNTIES = [
        ('Alachua', 'ALA'),
        ('Baker', 'BAK'),
        ('Bay', 'BAY'),
        ('Bradford', 'BRA'),
        ('Brevard', 'BRE'),
        ('Broward', 'BRO'),
        ('Calhoun', 'CAL'),
        ('Charlotte', 'CHA'),
        ('Citrus', 'CIT'),
        ('Clay', 'CLA'),
        ('Collier', 'COL'),
        ('Columbia', 'COM'),
        ('DeSoto', 'DES'),
        ('Dixie', 'DIX'),
        ('Duval', 'DUV'),
        ('Escambia', 'ESC'),
        ('Flagler', 'FLA'),
        ('Franklin', 'FRA'),
        ('Gadsden', 'GAD'),
        ('Gilchrist', 'GIL'),
        ('Glades', 'GLA'),
        ('Gulf', 'GUL'),
        ('Hamilton', 'HAM'),
        ('Hardee', 'HAR'),
        ('Hendry', 'HEN'),
        ('Hernando', 'HER'),
        ('Highlands', 'HIG'),
        ('Hillsborough', 'HIL'),
        ('Holmes', 'HOL'),
        ('Indian River', 'IND'),
        ('Jackson', 'JAC'),
        ('Jefferson', 'JEF'),
        ('Lafayette', 'LAF'),
        ('Lake', 'LAK'),
        ('Lee', 'LEE'),
        ('Leon', 'LEO'),
        ('Levy', 'LEV'),
        ('Liberty', 'LIB'),
        ('Madison', 'MAD'),
        ('Manatee', 'MAN'),
        ('Marion', 'MAR'),
        ('Martin', 'MAT'),
        ('Miami-Dade', 'MIA'),
        ('Monroe', 'MON'),
        ('Nassau', 'NAS'),
        ('Okaloosa', 'OKA'),
        ('Okeechobee', 'OKE'),
        ('Orange', 'ORA'),
        ('Osceola', 'OSC'),
        ('Palm Beach', 'PAL'),
        ('Pasco', 'PAS'),
        ('Pinellas', 'PIN'),
        ('Polk', 'POL'),
        ('Putnam', 'PUT'),
        ('Santa Rosa', 'SAN'),
        ('Sarasota', 'SAR'),
        ('Seminole', 'SEM'),
        ('St. Johns', 'STJ'),
        ('St. Lucie', 'STL'),
        ('Sumter', 'SUM'),
        ('Suwannee', 'SUW'),
        ('Taylor', 'TAY'),
        ('Union', 'UNI'),
        ('Volusia', 'VOL'),
        ('Wakulla', 'WAK'),
        ('Walton', 'WAL'),
        ('Washington', 'WAS'),
    ]

    def add_arguments(self, parser):
        """Argumentos do comando"""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing counties before loading new ones',
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        """Executar comando"""

        # Clear existing counties if requested
        if options['clear']:
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(
                        f'[DRY RUN] Would delete {County.objects.count()} existing counties')
                )
            else:
                deleted_count = County.objects.count()
                County.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(
                        f'✅ Deleted {deleted_count} existing counties')
                )

        # Create counties
        created_count = 0
        updated_count = 0

        for county_name, county_code in self.FLORIDA_COUNTIES:

            if options['dry_run']:
                self.stdout.write(
                    f'[DRY RUN] Would create: {county_name} ({county_code})')
                created_count += 1
                continue

            # Get or create county
            county, created = County.objects.get_or_create(
                name=county_name,
                defaults={
                    'code': county_code,
                    'state': 'FL',
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Created: {county.name} ({county.code})')
                )
            else:
                # Update existing if needed
                if county.code != county_code or county.state != 'FL' or not county.is_active:
                    county.code = county_code
                    county.state = 'FL'
                    county.is_active = True
                    county.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'🔄 Updated: {county.name} ({county.code})')
                    )
                else:
                    self.stdout.write(
                        f'⏭️  Exists: {county.name} ({county.code})')

        # Summary
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[DRY RUN SUMMARY] Would create {created_count} counties')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ COMPLETED!\n'
                    f'Created: {created_count} counties\n'
                    f'Updated: {updated_count} counties\n'
                    f'Total: {County.objects.count()} counties in database'
                )
            )

            # Show some sample counties
            self.stdout.write('\n📍 Sample counties:')
            for county in County.objects.all()[:5]:
                self.stdout.write(
                    f'  • {county.name} ({county.code}) - Active: {county.is_active}')

            if County.objects.count() > 5:
                self.stdout.write(
                    f'  ... and {County.objects.count() - 5} more')

    def validate_counties(self):
        """Validar se todos os counties foram criados corretamente"""
        total_expected = len(self.FLORIDA_COUNTIES)
        total_created = County.objects.filter(state='FL').count()

        if total_created == total_expected:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Validation passed: {total_created}/{total_expected} counties')
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Validation failed: {total_created}/{total_expected} counties')
            )
