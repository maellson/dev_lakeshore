# integrations/serializers.py - CRIAR ARQUIVO
from rest_framework import serializers
from .models import BrokermintDocument

class BrokermintDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokermintDocument
        fields = ['brokermint_id', 'name', 'bm_transaction_id', 'pages', 'content_type', 'url', 'synced_at']
        read_only_fields = ['synced_at']

class DocumentRefreshSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    document = BrokermintDocumentSerializer(required=False)