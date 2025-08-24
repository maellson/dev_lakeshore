"""
Comando customizado para criar superuser com campos ForeignKey
Execução: python manage.py create_superuser_custom
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from account.choice_types import TipoUsuario, Idioma
from account.models import PerfilInterno, Cargo, Departamento, NivelAcesso
import getpass


User = get_user_model()


class Command(BaseCommand):
    help = 'Cria um superuser com campos ForeignKey corretos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            '🔐 Criando superuser customizado...'))

        try:
            with transaction.atomic():
                # Coletar dados básicos
                email = input('Email: ')
                username = input('Username: ')
                first_name = input('First name: ')
                last_name = input('Last name: ')

                # Mostrar tipos de usuário disponíveis
                self.show_tipos_usuario()
                tipo_id = input('Tipo de Usuário ID: ')

                # Mostrar idiomas disponíveis
                self.show_idiomas()
                idioma_id = input('Idioma ID: ')

                # Senha
                password = getpass.getpass('Password: ')
                password2 = getpass.getpass('Password (again): ')

                if password != password2:
                    self.stdout.write(self.style.ERROR(
                        '❌ Senhas não coincidem!'))
                    return

                # Buscar instâncias dos ForeignKeys
                try:
                    tipo_usuario = TipoUsuario.objects.get(id=tipo_id)
                    idioma = Idioma.objects.get(id=idioma_id)
                except (TipoUsuario.DoesNotExist, Idioma.DoesNotExist):
                    self.stdout.write(self.style.ERROR(
                        '❌ Tipo de usuário ou idioma inválido!'))
                    return

                # Criar superuser
                user = User.objects.create_superuser(
                    email=email,
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    tipo_usuario=tipo_usuario,
                    preferencia_idioma=idioma,
                    is_staff=True,
                    is_superuser=True
                )

                # Se for usuário interno, criar perfil
                if tipo_usuario.code == 'INTERNO':
                    self.create_perfil_interno(user)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Superuser "{email}" criado com sucesso!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar superuser: {str(e)}')
            )

    def show_tipos_usuario(self):
        """Mostra tipos de usuário disponíveis"""
        self.stdout.write('\n📋 Tipos de Usuário disponíveis:')
        tipos = TipoUsuario.objects.filter(is_active=True)
        for tipo in tipos:
            self.stdout.write(f'  {tipo.id} - {tipo.name} ({tipo.code})')
        print()

    def show_idiomas(self):
        """Mostra idiomas disponíveis"""
        self.stdout.write('\n🌐 Idiomas disponíveis:')
        idiomas = Idioma.objects.filter(is_active=True)
        for idioma in idiomas:
            self.stdout.write(f'  {idioma.id} - {idioma.name} ({idioma.code})')
        print()

    def create_perfil_interno(self, user):
        """Cria perfil interno para superuser"""
        try:
            # Buscar cargo CEO e nível executivo
            cargo_ceo = Cargo.objects.get(code='CEO')
            nivel_executivo = NivelAcesso.objects.get(code='EXECUTIVO')
            depto_executivo = Departamento.objects.get(code='EXECUTIVO')

            PerfilInterno.objects.create(
                user=user,
                cargo=cargo_ceo,
                departamento=depto_executivo,
                nivel_acesso=nivel_executivo
            )

            self.stdout.write(
                self.style.SUCCESS('✅ Perfil interno criado (CEO/Executivo)')
            )

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Perfil interno não criado: {str(e)}')
            )
