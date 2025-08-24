# integrations/tasks.py
from celery import shared_task
from .sync_service import BrokermintSyncService
from .models import BrokermintTransaction
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def sync_signature_activities_only(self, hours_back=2):
    """
    ÚNICA TASK IMPORTANTE - A CADA 1 HORA
    Verifica APENAS assinaturas de contratos
    """
    try:
        service = BrokermintSyncService()
        result = service.sync_only_signature_activities(hours_back=hours_back)

        message = f"ASSINATURAS: {len(result['new_activities'])} novas, {len(result['signed_contracts'])} contratos assinados"
        logger.info(message)

        # Se encontrou contratos assinados, notificar!
        if result['signed_contracts']:
            # TODO: Enviar notificações via email/slack
            logger.warning(
                f"✍🏾 CONTRATOS ASSINADOS: {result['signed_contracts']}")

        return message

    except Exception as e:
        logger.error(f"Erro na sincronização de assinaturas: {str(e)}")
        raise self.retry(countdown=60 * 10, max_retries=3)


@shared_task(bind=True)
def sync_minimal_transactions_task(self):
    """
    Task LEVE - A CADA 6 HORAS
    Apenas identifica transações novas (sem detalhes)
    """
    try:
        service = BrokermintSyncService()
        # Contar antes
        count_before = BrokermintTransaction.objects.count()
        
        result = service.sync_minimal_transactions()
        
        # Contar depois  
        count_after = BrokermintTransaction.objects.count()
        
        # LOG DE SEGURANÇA
        if count_after < count_before:
            logger.error(f"🚨 PERDA DE DADOS: {count_before} → {count_after}")
            
        logger.info(f"Transações: {count_before} → {count_after} (+{len(result)} novas)")
        return f"SUCCESS: {len(result)} novas, total: {count_after}"

    except Exception as e:
        logger.error(f"Erro na sincronização mínima: {str(e)}")
        raise self.retry(countdown=60 * 30, max_retries=3)


@shared_task
def check_specific_transactions(transaction_ids):
    """
    Task MANUAL - Para verificar transações específicas
    """
    service = BrokermintSyncService()
    result = service.sync_only_signature_activities(
        transaction_ids=transaction_ids)

    return f"Verificadas {len(transaction_ids)} transações: {len(result['new_activities'])} assinaturas"
