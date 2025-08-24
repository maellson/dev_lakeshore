# Etapa 1: Builder
FROM python:3.11-slim-bookworm AS builder

# Diretório de trabalho
WORKDIR /app

# Copia dependências
COPY  requirements.txt .

# Atualiza pip e instala dependências no diretório /install
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Etapa 2: Final
FROM python:3.11-slim-bookworm

# Segurança: cria usuário não-root
RUN adduser --disabled-password --gecos '' django_user

WORKDIR /app

# Copia dependências da etapa builder
COPY --from=builder /install /usr/local

# Copia o restante do código
COPY . .

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=erp_lakeshore.settings

# AQUI: Fazer collectstatic ANTES de mudar usuário
RUN python manage.py collectstatic --noinput

# Ajusta permissões para usuário não-root
RUN chown -R django_user:django_user /app

# Troca para o usuário não-root
USER django_user

# Exposição da porta
EXPOSE 8000

# Comando padrão: Gunicorn
#CMD ["gunicorn", "erp_lakeshore.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120"]
CMD ["gunicorn", "erp_lakeshore.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "60", "--graceful-timeout", "60", "--workers", "2"]

