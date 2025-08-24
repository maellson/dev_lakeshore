# integrations/sync_service.py - VERSÃO INCREMENTAL
from .brokermint_client import BrokermintClient
from .models import BrokermintTransaction, BrokermintActivity, BrokermintDocument
from django.db import models
import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class BrokermintSyncService:
    def __init__(self):
        self.client = BrokermintClient()

    def sync_only_signature_activities(self, transaction_ids=None, hours_back=24):
        """
        FOCO TOTAL: Apenas atividades de assinatura

        Args:
            transaction_ids: Lista específica de IDs (opcional)
            hours_back: Quantas horas atrás verificar (padrão 24h)
        """
        logger.info("🎯 Sincronizando APENAS atividades de assinatura...")

        if transaction_ids:
            # Busca específica por IDs fornecidos
            target_transactions = list(transaction_ids)
            logger.info(
                f"Verificando {len(target_transactions)} transações específicas")
        else:
            # Busca inteligente: transações que precisam de verificação
            cutoff_time = timezone.now() - timedelta(hours=hours_back)
            target_transactions = list(
                BrokermintTransaction.objects.filter(
                    # Nunca verificadas OU verificadas há mais de X horas
                    models.Q(last_activity_check__isnull=True) |
                    models.Q(last_activity_check__lt=cutoff_time)
                ).values_list('brokermint_id', flat=True)[:50]  # Limite de 50 por vez
            )
            logger.info(
                f"Verificando {len(target_transactions)} transações desatualizadas")

        if not target_transactions:
            logger.info("✅ Nenhuma transação precisa de verificação")
            return []

        # ÚNICA REQUISIÇÃO: Buscar atividades de assinatura
        activities_data = self.client.get_signature_activities(
            target_transactions)

        new_activities = []
        signed_contracts = []

        for activity_data in activities_data:
            # Salvar atividade
            activity, created = BrokermintActivity.objects.update_or_create(
                brokermint_id=activity_data['id'],
                defaults={
                    'content': activity_data.get('content', ''),
                    'bm_transaction_id': activity_data.get('bm_transaction_id'),
                    'created_at_brokermint': activity_data.get('created_at'),
                    'originator_id': activity_data.get('originator_id'),
                    'document_id': activity_data.get('document_id'),
                    'event_label': activity_data.get('event_label', ''),
                    'signers': activity_data.get('metadata', {}).get('signers', []),
                }
            )

            if created:
                new_activities.append(activity)

                # Marcar transação como tendo assinatura
                BrokermintTransaction.objects.filter(
                    brokermint_id=activity.bm_transaction_id
                ).update(
                    has_signature_activity=True,
                    is_contract_signed=True,
                    last_activity_check=timezone.now()
                )

                signed_contracts.append(activity.bm_transaction_id)
                logger.info(
                    f"🎉 CONTRATO ASSINADO: Transação {activity.bm_transaction_id}")

        # Marcar transações verificadas (mesmo sem atividades)
        BrokermintTransaction.objects.filter(
            brokermint_id__in=target_transactions
        ).update(last_activity_check=timezone.now())

        logger.info(
            f"✅ Verificação concluída: {len(new_activities)} assinaturas, {len(signed_contracts)} contratos")

        return {
            'new_activities': new_activities,
            'signed_contracts': signed_contracts,
            'checked_transactions': len(target_transactions)
        }

    def sync_minimal_transactions(self):
        """
        Sincronização MÍNIMA: Apenas identificar IDs novos
        Não busca detalhes completos!
        """
        logger.info("📋 Sincronização mínima de transações...")

        transactions_data = self.client.get_all_transactions()
        existing_ids = set(
            BrokermintTransaction.objects.values_list(
                'brokermint_id', flat=True)
        )

        new_transactions = []
        for tx_data in transactions_data:
            if tx_data['id'] not in existing_ids:
                # Criar registro MÍNIMO
                tx = BrokermintTransaction.objects.create(
                    brokermint_id=tx_data['id'],
                    address=tx_data.get('address', ''),
                    city=tx_data.get('city', ''),
                    state=tx_data.get('state', ''),
                    status=tx_data.get('status', ''),
                    # NÃO buscar detalhes ainda!
                    has_detailed_data=False
                )
                new_transactions.append(tx)
            else:
                # ATUALIZAR apenas campos básicos, manter has_detailed_data
                BrokermintTransaction.objects.filter(
                    brokermint_id=tx_data['id']
                ).update(
                    address=tx_data.get('address', ''),
                    city=tx_data.get('city', ''),
                    state=tx_data.get('state', ''),
                    status=tx_data.get('status', ''),
                    # NÃO mexer em has_detailed_data
                )

        logger.info(
            f"📋 {len(new_transactions)} novas transações identificadas")
        return new_transactions
    
    def sync_transaction_details(self):
        """
        CORREÇÃO: Verificar se dados estão realmente completos
        """
        transactions_without_details = BrokermintTransaction.objects.filter(
            models.Q(has_detailed_data=False) | 
            models.Q(parcel_id__isnull=True) |  # Verificação extra
            models.Q(parcel_id='')
        )

    def get_transaction_details_on_demand(self, transaction_id):
        """
        Buscar detalhes APENAS quando necessário
        Usado quando alguém acessa uma transação específica
        """
        try:
            transaction = BrokermintTransaction.objects.get(
                brokermint_id=transaction_id)

            if transaction.has_detailed_data:
                logger.info(f"Transação {transaction_id} já tem detalhes")
                return transaction

            # Buscar detalhes da API
            details = self.client.get_transaction_details(transaction_id)
            if details:
                    # Atualizar com dados completos
                    transaction.county = details.get('County', '')
                    transaction.legal_description = details.get('Legal description', '')
                    transaction.parcel_id = details.get('Parcel ID', '')  # ← CAMPO IMPORTANTE!
                    transaction.home_model = details.get('Home Model', '')
                    transaction.bedrooms = str(details.get('Bedrooms', ''))
                    transaction.full_baths = str(details.get('Full baths', ''))
                    transaction.half_baths = str(details.get('Half baths', ''))
                    transaction.building_sqft = str(details.get('Building SQFT', ''))
                    
                    # Dados financeiros
                    transaction.soft_costs = str(details.get('Soft Costs', ''))
                    transaction.hard_costs = str(details.get('Hard Costs', ''))
                    transaction.estimated_construction_cost = str(details.get('Estimated Construction Cost', ''))
                    transaction.builder_fee = str(details.get('Builder Fee', ''))
                    
                    # Draws
                    transaction.draw_1 = str(details.get('Draw 1', ''))
                    transaction.draw_2 = str(details.get('Draw 2', ''))
                    transaction.draw_3 = str(details.get('Draw 3', ''))
                    transaction.draw_4 = str(details.get('Draw 4', ''))
                    transaction.draw_5 = str(details.get('Draw 5', ''))
                    
                    # Localização
                    transaction.lot = str(details.get('Lot', ''))
                    transaction.block = str(details.get('Block', ''))
                    transaction.unit = str(details.get('Unit', ''))
                    transaction.sec = str(details.get('SEC', ''))
                    transaction.twp = str(details.get('Twp', ''))
                    transaction.rge = str(details.get('Rge', ''))
                    transaction.subdivision = details.get('Subdivision', '')
                    
                    # Datas
                    transaction.acceptance_date = details.get('acceptance_date')
                    transaction.expiration_date = details.get('expiration_date')
                    transaction.closing_date = details.get('closing_date')
                    transaction.listing_date = details.get('listing_date')
                    transaction.buyer_agreement_date = details.get('buyer_agreement_date')
                    transaction.buyer_expiration_date = details.get('buyer_expiration_date')
                    
                    # Dados adicionais
                    transaction.custom_id = details.get('custom_id', '')
                    transaction.transaction_type = details.get('transaction_type', '')
                    transaction.external_id = details.get('external_id', '')
                    transaction.total_gross_commission = details.get('total_gross_commission', 0)
                    transaction.sales_volume = details.get('sales_volume', 0)
                    
                    # Marcar como tendo dados detalhados
                    transaction.has_detailed_data = True
                    transaction.save()
                    
                    logger.info(f"Detalhes sincronizados: {transaction.brokermint_id} - Parcel: {transaction.parcel_id}")
                

            return transaction

        except BrokermintTransaction.DoesNotExist:
            logger.error(f"Transação {transaction_id} não encontrada")
            return None
