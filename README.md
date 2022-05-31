# API
Esse repositório tem como intuito conter os códigos da API em Python (usando FastAPI e Boto3)
que cria os scripts em Terraform e faz a implementação (deploy) da infraestrutura.

## Features
- Listagem das pastas de usuários do Bucket S3 usando AWS CLI
- Criação de novas pastas para usuários e projetos no Bucket S3
- Cadastro das credenciais de acesso à conta Azure
- Criação do script em terraform para os seguintes recursos:
  - Resource Group (Grupo de recursos)
  - Virtual Networks (Redes virtuais)
  - Subnets (Sub-redes)
  - Network Security Groups (Grupos de Segurança de Rede)
  - NAT Gateway
  - Chaves SSH (criação e uso de chaves existentes)
  - Linux Virtual Machine (Máquina Virtual Linux)
  - Windows Virtual Machine (Máquina Virtual Windows)
- Implementação dos recursos na nuvem Azure
- Criação de links pré-assinados com AWS CLI para que o usuário baixe seu script
