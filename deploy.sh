#!/bin/bash
# deploy.sh - Script para deploy manual rápido

set -e  # Para se algum comando falhar

echo "🚀 Iniciando deploy do ERP Lakeshore..."

# Variáveis
ECR_REGISTRY="460044121130.dkr.ecr.us-east-2.amazonaws.com"
ECR_REPOSITORY="erp-lakeshore"
AWS_REGION="us-east-2"
ECS_CLUSTER="erp-lakeshore"
ECS_SERVICE="erp-lakeshore-task-service"

# 1. Login no ECR
echo "🔐 Fazendo login no ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# 2. Build da imagem
echo "🏗️ Building imagem Docker..."
docker build --platform linux/amd64 -f docker/Dockerfile -t django_lakeshore .

# 3. Tag da imagem
echo "🏷️ Taggeando imagem..."
docker tag django_lakeshore:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest

# 4. Push para ECR
echo "📤 Enviando para ECR..."
docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

# 5. Force deployment no ECS
echo "🚢 Deployando no ECS..."
aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment --region $AWS_REGION

echo "✅ Deploy concluído!"
echo "📋 Acompanhar logs: aws logs tail /ecs/erp-lakeshore --follow --region $AWS_REGION"
echo "🌐 URL: http://erp-lakeshore-alb-842248284.us-east-2.elb.amazonaws.com"