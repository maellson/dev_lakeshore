# integrations/brokermint_client.py
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class BrokermintClient:
    def __init__(self):
        self.api_key = settings.BROKERMINT_API_KEY
        self.base_url_v3 = "https://my.brokermint.com/api/v3"
        self.base_url_v1 = "https://my.brokermint.com/api/v1"

    def get_all_transactions(self):
        """GET /api/v3/transactions - Lista todas as transações"""
        url = f"{self.base_url_v3}/transactions"
        params = {'api_key': self.api_key, 'count': 1000}

        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else []

    def get_transaction_details(self, transaction_id):
        """GET /api/v3/transactions/{id} - Detalhes de uma transação"""
        url = f"{self.base_url_v3}/transactions/{transaction_id}"
        params = {'api_key': self.api_key}

        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None

    def get_signature_activities(self, transaction_ids):
        """GET /api/v1/activities - Atividades de assinatura"""
        url = f"{self.base_url_v1}/activities"

        params = {
            "api_key": self.api_key,
            "event_types": "document_signature_complete",
            # Como string separada por vírgula
            "bm_transaction_ids": ",".join(map(str, transaction_ids))
        }

        response = requests.get(url, params=params)  # ← GET ao invés de POST
        return response.json() if response.status_code == 200 else []

    def get_document_details(self, transaction_id, document_id):
        """GET /api/v1/transactions/{id}/documents/{doc_id}"""
        url = f"{self.base_url_v1}/transactions/{transaction_id}/documents/{document_id}"
        params = {'api_key': self.api_key}

        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None
