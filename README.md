# Pipeline de Análise de Vendas com Apache Beam e Dataflow

Este projeto implementa um pipeline de dados ETL (Extração, Transformação e Carga) que processa um arquivo CSV de vendas, realiza a sanitização e limpeza dos dados, e calcula a soma total de fretes, agrupada por categoria, para pedidos entregues e cancelados.

O pipeline é construído com Apache Beam em Python e projetado para ser executado de forma escalável no Google Cloud Dataflow.

## Arquitetura

O fluxo de dados segue uma arquitetura simples e robusta na nuvem:

**Google Cloud Storage (GCS)** ➔ **Google Cloud Dataflow** ➔ **Google Cloud Storage (GCS)**

1.  **Extração:** O pipeline lê o arquivo `vendas_faker.csv` de uma pasta `input` no GCS.
2.  **Transformação:** Um job do Dataflow executa a lógica do Beam para limpar, validar, transformar e agregar os dados em memória.
3.  **Carga:** O resultado agregado é escrito como um novo arquivo CSV numa pasta `output` no GCS.

---

## 4. Pré-requisitos

Antes de começar, garanta que você tem as seguintes ferramentas instaladas e configuradas:

* **Python 3.12+**
* **`uv`**: Um instalador e gerenciador de pacotes Python extremamente rápido. (Instruções em [astral.sh/uv](https://astral.sh/uv))
* **Google Cloud SDK (`gcloud`)**: Instalado e autenticado na sua conta Google.
* Um projeto ativo no Google Cloud Platform com o faturamento ativado.

---

## 5. Configuração do Ambiente (GCP)

Siga estes passos para configurar a infraestrutura necessária no Google Cloud.

### 5.1. Configuração do Projeto GCP

Defina o seu projeto ativo no `gcloud`:
```bash
gcloud config set project SEU-PROJECT-ID
```

### 5.2. Criação da Service Account

O Dataflow precisa de uma identidade (Service Account) para operar.
```bash
# Crie a Service Account
gcloud iam service-accounts create dataflow-vendas-sa --display-name="Service Account para Pipeline de Vendas"

# Dê as permissões necessárias (substitua SEU-PROJECT-ID)
gcloud projects add-iam-policy-binding SEU-PROJECT-ID --member="serviceAccount:dataflow-vendas-sa@SEU-PROJECT-ID.iam.gserviceaccount.com" --role="roles/dataflow.worker"
gcloud projects add-iam-policy-binding SEU-PROJECT-ID --member="serviceAccount:dataflow-vendas-sa@SEU-PROJECT-ID.iam.gserviceaccount.com" --role="roles/dataflow.admin"
gcloud projects add-iam-policy-binding SEU-PROJECT-ID --member="serviceAccount:dataflow-vendas-sa@SEU-PROJECT-ID.iam.gserviceaccount.com" --role="roles/storage.admin"
```

### 5.3. Criação do Bucket no Google Cloud Storage

O pipeline precisa de um bucket para armazenar todos os seus arquivos.
```bash
# Crie o bucket (escolha um nome único globalmente)
gsutil mb gs://SEU-BUCKET-NAME

# (Opcional) Crie as pastas dentro do bucket
gsutil mkdir gs://SEU-BUCKET-NAME/input/ gs://SEU-BUCKET-NAME/output/ gs://SEU-BUCKET-NAME/temp/ gs://SEU-BUCKET-NAME/staging/ gs://SEU-BUCKET-NAME/models/
```

### 5.4. Autenticação Local

Para que seu script Python possa interagir com o GCP, gere uma chave de autenticação.
```bash
# Crie e faça o download de uma chave para a Service Account
gcloud iam service-accounts keys create gcp-credentials.json --iam-account="dataflow-vendas-sa@SEU-PROJECT-ID.iam.gserviceaccount.com"

# Defina a variável de ambiente para que as bibliotecas do Google a encontrem
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-credentials.json"
```
**Importante:** Adicione `gcp-credentials.json` ao seu ficheiro `.gitignore` para nunca enviar esta chave para um repositório!

---

## 6. Configuração do Ambiente Local com `uv`

Com o ambiente na nuvem pronto, configure o projeto na sua máquina.

```bash
# 1. Clone este repositório
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>

# 2. Crie um ambiente virtual com uv
uv venv

# 3. Ative o ambiente virtual (o comando é o mesmo)
source .venv/bin/activate

# 4. Instale as dependências com uv
uv pip install -r requirements.txt

# 5. Configure as variáveis de ambiente locais
# Copie o ficheiro de exemplo e preencha com os seus dados
cp .env.example .env
nano .env  # ou use seu editor preferido para preencher os valores
```

---

## 7. Como Executar o Pipeline

Com tudo configurado, siga estes passos:

### 7.1. Preparar os Dados de Entrada

Gere os dados de exemplo e envie para o GCS.
```bash
# Gere o ficheiro de dados localmente
python generator-data.py

# Envie o ficheiro para a pasta 'input' no seu bucket
gsutil cp vendas_faker.csv gs://SEU-BUCKET-NAME/input/
```

### 7.2. Executar o Pipeline

Execute o script `main.py`. Ele lerá as configurações do seu ficheiro `.env` e submeterá o job para o Dataflow.
```bash
python main.py
```
Acompanhe o job na interface do Dataflow no Console do Google Cloud.

### 7.3. Verificar a Saída

Após a conclusão do job, os resultados estarão na pasta de saída do seu bucket.
```bash
gsutil ls gs://SEU-BUCKET-NAME/output/
```

---

## 8. Estrutura do Projeto

```
.
├── .env                  # Suas configurações locais (NÃO ENVIAR PARA O GIT)
├── .env.example          # Exemplo de configuração para outros desenvolvedores
├── .gitignore
├── README.md             # Esta documentação
├── gcp-credentials.json  # Chave de autenticação (NÃO ENVIAR PARA O GIT)
├── generator-data.py     # Script para gerar dados de teste
├── main.py               # Script principal que executa o pipeline
├── requirements.txt      # Dependências Python do projeto
└── pipeline/
    ├── __init__.py
    └── transforms.py     # Módulo com as classes DoFn de transformação
```

### 9 Executar o Job a Partir do Template

Com o template publicado, qualquer pessoa com as permissões corretas pode executar o pipeline usando este comando `gcloud`. Note que ele é muito mais limpo, pois a complexidade já está "empacotada" no template.

```bash
PROJECT_ID="seu-project-id"
BUCKET_NAME="seu-bucket-name"
REGION="us-east1"
JOB_NAME="vendas-processing-job"
SERVICE_ACCOUNT_EMAIL="dataflow-vendas-sa@${PROJECT_ID}.iam.gserviceaccount.com"
TEMPLATE_PATH="gs://${BUCKET_NAME}/models/template_vendas.json"

# Comando para executar o job
gcloud dataflow flex-template run ${JOB_NAME} \
    --template-file-gcs-location ${TEMPLATE_PATH} \
    --project ${PROJECT_ID} \
    --region ${REGION} \
    --staging-location "gs://${BUCKET_NAME}/staging/" \
    --temp-location "gs://${BUCKET_NAME}/temp/" \
    --service-account-email ${SERVICE_ACCOUNT_EMAIL} \
    --max-workers 1 \
    --num-workers 1 \
    --parameters input_path="gs://${BUCKET_NAME}/input/vendas_faker.csv" \
    --parameters output_path="gs://${BUCKET_NAME}/output/totals_aggregates"
```
