from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuração do app Core
    
    FEATURES:
    - Models compartilhados (County, ChoiceTypeBase)
    - Utilitários e middlewares
    - Dados mestres do sistema
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = 'Core System'

    def ready(self):
        """Executado quando app é carregado"""
        # Import signals se necessário
        pass
