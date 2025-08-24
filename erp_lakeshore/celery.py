# erp_lakeshore/celery.py (CRIAR ARQUIVO)
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_lakeshore.settings')

app = Celery('erp_lakeshore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuração das tarefas periódicas
app.conf.beat_schedule = {
    'check-signatures-every-hour': {
        'task': 'integrations.tasks.sync_signature_activities_only',
        'schedule': 60.0 * 60.0,  # 1 hora
        'kwargs': {'hours_back': 2}  # Verificar últimas 2h
    },
    'minimal-sync-every-6-hours': {
        'task': 'integrations.tasks.sync_minimal_transactions_task',
        'schedule': 60.0 * 60.0 * 6,  # 6 horas
    },
}


app.conf.task_routes = {
    'integrations.tasks.*': {'queue': 'brokermint_sync'},
}
