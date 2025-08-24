# integrations/management/commands/sync_brokermint.py
from django.core.management.base import BaseCommand
from integrations.tasks import manual_full_sync

class Command(BaseCommand):
    help = 'Sincronização manual completa do Brokermint'
    
    def handle(self, *args, **options):
        result = manual_full_sync.delay()
        self.stdout.write(f'Task iniciada: {result.id}')