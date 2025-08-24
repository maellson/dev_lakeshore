from django.apps import AppConfig


class LeadsConfig(AppConfig):
    """
    Configuração do app Leads

    FEATURES:
    - Auto discovery de admin, models
    - Signals para logging/auditoria
    - Inicialização de dados padrão
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leads'
    verbose_name = 'Lead Management'

    def ready(self):
        """Executado quando app é carregado"""
        # Import signals se necessário
        # from . import signals
        pass
