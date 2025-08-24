from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import (
    CustomUser,
    PerfilInterno,
    PerfilSubcontratado,
    PerfilClient,
    PerfilFornecedor
)
from .choice_types import NivelAcesso, Cargo, Departamento

# ✅ ADICIONAR ESTA NOVA FUNÇÃO


@receiver(post_save, sender=CustomUser)
def create_superuser_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente PerfilInterno para superusers
    """
    # Se é superuser E tipo interno E não tem perfil
    if instance.is_superuser and instance.tipo_usuario and instance.tipo_usuario.code == 'INTERNO':
        if not hasattr(instance, 'perfil_interno'):
            try:
                # Buscar dados padrão para superuser
                nivel_executivo = NivelAcesso.objects.get(code='EXECUTIVO')
                cargo_ceo = Cargo.objects.get(code='CEO')
                depto_executivo = Departamento.objects.get(code='EXECUTIVO')

                # Criar perfil
                PerfilInterno.objects.create(
                    user=instance,
                    cargo=cargo_ceo,
                    departamento=depto_executivo,
                    nivel_acesso=nivel_executivo
                )
                print(
                    f"✅ PerfilInterno criado automaticamente para superuser: {instance.email}")

            except Exception as e:
                print(
                    f"⚠️ Erro ao criar perfil para superuser {instance.email}: {e}")


@receiver(post_save, sender=CustomUser)
def ensure_internal_profile(sender, instance, **kwargs):
    """
    Garante que usuários INTERNOS sempre tenham perfil
    """
    # Se é INTERNO (criado ou alterado) e não tem perfil
    if (instance.tipo_usuario and 
        instance.tipo_usuario.code == 'INTERNO' and 
        not hasattr(instance, 'perfil_interno')):
        
        try:
            # Dados padrão baseados no tipo
            if instance.is_superuser:
                nivel = NivelAcesso.objects.get(code='EXECUTIVO')
                cargo = Cargo.objects.get(code='CEO')
                depto = Departamento.objects.get(code='EXECUTIVO')
            else:
                nivel = NivelAcesso.objects.get(code='BASICO')
                cargo = Cargo.objects.get(code='ADMINISTRATIVO')  
                depto = Departamento.objects.get(code='RH')
            
            PerfilInterno.objects.create(
                user=instance,
                cargo=cargo,
                departamento=depto,
                nivel_acesso=nivel
            )
            
        except Exception as e:
            print(f"⚠️ Erro ao criar perfil para {instance.email}: {e}")