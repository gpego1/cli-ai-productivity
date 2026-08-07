# API AI Productivity

API serverless, construída em Python e executada como uma imagem de contêiner no **AWS Lambda**, exposta ao mundo através do **Amazon API Gateway**. A API usa Modelos de Linguagem (LLMs) para extrair insights de arquivos: resumir documentos, responder perguntas sobre seu conteúdo e gerar relatórios estatísticos detalhados a partir de arquivos CSV.

> Este projeto evoluiu de uma ferramenta de linha de comando (CLI) para uma API serverless, mantendo a mesma lógica de negócio (`commands/` e `utils/`), mas trocando o entrypoint local por um `handler` compatível com Lambda.

## Arquitetura

```
                         ┌──────────────────────┐
   Cliente HTTP  ─────►  │   Amazon API Gateway  │
   (POST /summarize,     │  (REST/HTTP API)      │
    /ask, /report...)    └──────────┬────────────┘
                                     │ invoca (proxy integration)
                                     ▼
                         ┌──────────────────────┐
                         │      AWS Lambda        │
                         │  (imagem de contêiner  │
                         │   publicada no ECR)    │
                         │                        │
                         │  main.main(event, ctx) │
                         │        │               │
                         │        ▼               │
                         │  handler.lambda_handler│
                         └──────────┬─────────────┘
                                    │ roteia para o comando certo
                                    ▼
                     ┌──────────────────────────────┐
                     │        commands/               │
                     │  ask.py · summarize.py · report.py │
                     └──────────────┬───────────────┘
                                    │ usa
                                    ▼
                     ┌──────────────────────────────┐
                     │          utils/                │
                     │  file_reader.py · call_llm.py  │
                     └──────────────┬───────────────┘
                                    │ chama
                                    ▼
                     ┌──────────────────────────────┐
                     │  API compatível com OpenAI     │
                     │  (OpenAI, LM Studio, Ollama...)│
                     └──────────────────────────────┘
```

### Fluxo de uma requisição

1. O cliente faz uma chamada HTTP para o **API Gateway** (ex.: `POST /summarize`).
2. O API Gateway invoca a função **Lambda** usando *proxy integration*, repassando o evento (headers, path, body, etc.) no formato padrão do API Gateway.
3. O runtime do Lambda chama o handler configurado na imagem — `main.main(event, context)` — que delega para `handler.lambda_handler`.
4. O `handler` interpreta o evento recebido e roteia a chamada para o comando correspondente em `commands/` (`summarize`, `ask` ou `report`).
5. O comando usa os utilitários em `utils/`:
   - `file_reader.py` extrai o conteúdo do arquivo recebido (`.txt`, `.md`, `.pdf`, `.csv`);
   - `call_llm.py` monta o prompt e chama a API compatível com OpenAI (OpenAI, LM Studio, Ollama, etc.).
6. A resposta do LLM é formatada e devolvida como retorno da função Lambda, que o API Gateway converte na resposta HTTP para o cliente.

## Empacotamento e deploy: imagem de contêiner no Lambda

Diferente de um deploy tradicional via `.zip`, este projeto empacota a API como uma **imagem de contêiner Docker**, publicada em um repositório do **Amazon ECR** e usada diretamente pela função Lambda.

`Dockerfile`:

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

RUN microdnf install -y file file-libs && microdnf clean all

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["main.main"]
```

Pontos importantes:

- A imagem parte da base oficial `public.ecr.aws/lambda/python:3.12`, que já inclui o **Lambda Runtime Interface Client (RIC)**.
- `CMD ["main.main"]` define `main.main` (função `main` dentro de `main.py`) como o **handler** que o Lambda invoca a cada evento.
- `main.py` apenas repassa `event` e `context` para `handler.lambda_handler`, mantendo a lógica de roteamento isolada da camada de entrada:

```python
from handler.handler import lambda_handler

def main(event, context):
    return lambda_handler(event, context)

if __name__ == '__main__':
    main()
```

### Passo a passo de deploy

1. **Build da imagem**
   ```bash
   docker build -t api-ai-productivity .
   ```

2. **Criar o repositório no ECR (se ainda não existir)**
   ```bash
   aws ecr create-repository --repository-name api-ai-productivity
   ```

3. **Autenticar o Docker no ECR e enviar (push) a imagem**
   ```bash
   aws ecr get-login-password --region <sua-regiao> \
     | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<sua-regiao>.amazonaws.com

   docker tag api-ai-productivity:latest \
     <account-id>.dkr.ecr.<sua-regiao>.amazonaws.com/api-ai-productivity:latest

   docker push <account-id>.dkr.ecr.<sua-regiao>.amazonaws.com/api-ai-productivity:latest
   ```

4. **Criar (ou atualizar) a função Lambda a partir da imagem**
   ```bash
   aws lambda create-function \
     --function-name api-ai-productivity \
     --package-type Image \
     --code ImageUri=<account-id>.dkr.ecr.<sua-regiao>.amazonaws.com/api-ai-productivity:latest \
     --role <arn-da-role-de-execucao>
   ```

5. **Configurar o API Gateway**
   - Criar uma API HTTP (ou REST) apontando as rotas desejadas (ex.: `/summarize`, `/ask`, `/report`) para a função Lambda com *Lambda proxy integration*.
   - Garantir que a role de execução do Lambda tenha permissão `apigateway.amazonaws.com` para invocar a função (`aws lambda add-permission`).

6. **Configurar variáveis de ambiente da função Lambda** (ver seção abaixo).

> Ajuste os comandos acima (nomes, região e ARNs) conforme a sua conta e infraestrutura. Se você usa IaC (Terraform, SAM, CDK ou Serverless Framework), o mesmo fluxo se aplica: build → push da imagem para o ECR → função Lambda apontando para essa imagem → integração com o API Gateway.

## Variáveis de ambiente

Configuradas diretamente na função Lambda (Console, IaC ou `aws lambda update-function-configuration`):

| Variável         | Descrição                                                              |
| ---------------- | ------------------------------------------------------------------------ |
| `BASE_URL`       | URL base da API compatível com OpenAI usada para inferência              |
| `OPENAI_API_KEY` | Chave de API (qualquer string não vazia para servidores locais/self-hosted) |
| `MODEL`          | Nome do modelo usado nas chamadas ao LLM                                 |

> **Dica:** para desenvolvimento local, essas mesmas variáveis podem ser definidas em um arquivo `.env` (não versionado) e carregadas antes de invocar `main.main` manualmente ou via `sam local` / `docker run`.

## Funcionalidades expostas pela API

### `summarize`
Extrai as informações-chave de um arquivo e retorna um resumo estruturado em tópicos. Suporta `.txt`, `.md`, `.pdf` e `.csv`.

### `ask`
Responde a uma pergunta em linguagem natural sobre o conteúdo de um arquivo. O LLM responde **apenas** com base no conteúdo do documento, garantindo respostas fundamentadas. Suporta `.txt`, `.md`, `.pdf` e `.csv`.

### `report`
Gera um relatório estatístico aprofundado a partir de um arquivo `.csv`. A função usa **pandas** para calcular estatísticas descritivas e contagens de valores, e então envia os dados ao LLM para uma interpretação especializada cobrindo qualidade dos dados, distribuições, anomalias e recomendações práticas.

### Tipos de arquivo suportados

| Extensão | Usado por               |
| -------- | ------------------------ |
| `.txt`   | summarize, ask            |
| `.md`    | summarize, ask            |
| `.pdf`   | summarize, ask            |
| `.csv`   | summarize, ask, report    |

## Estrutura do projeto

```
api-ai-productivity/
├── main.py                # Entrypoint do Lambda — repassa event/context para o handler
├── Dockerfile              # Imagem de contêiner baseada na runtime oficial do Lambda (Python 3.12)
├── handler/
│   └── handler.py          # lambda_handler — recebe o evento do API Gateway e roteia para o comando certo
├── commands/
│   ├── ask.py               # Lógica do comando "ask" — Q&A sobre o conteúdo do arquivo
│   ├── summarize.py         # Lógica do comando "summarize" — sumarização de documentos
│   └── report.py            # Lógica do comando "report" — análise estatística de CSV
├── utils/
│   ├── call_llm.py          # Client wrapper para a API compatível com OpenAI
│   └── file_reader.py       # Leitor multi-formato (.txt, .md, .pdf, .csv)
├── requirements.txt         # Dependências Python
└── .gitignore
```

## Executando e testando localmente

Como a imagem é baseada na runtime oficial do Lambda, é possível simular invocações localmente com o **Lambda Runtime Interface Emulator (RIE)**, incluso na imagem base:

```bash
docker build -t api-ai-productivity .

docker run -p 9000:8080 \
  -e BASE_URL=your_base_url \
  -e OPENAI_API_KEY=your_api_key \
  -e MODEL=your_model \
  api-ai-productivity
```

Em outro terminal, envie um evento de teste simulando o payload que o API Gateway enviaria:

```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"body": "{\"command\": \"summarize\", \"file\": \"...\"}"}'
```

> O formato exato do `body` (nomes dos campos, se o arquivo é enviado como base64, multipart, ou URL pré-assinada do S3) depende da implementação de `handler/handler.py`. Ajuste o payload de teste acima de acordo com o contrato real implementado no handler.

## Requisitos

- Docker (para build e testes locais da imagem Lambda)
- AWS CLI configurado com permissões para ECR, Lambda e API Gateway
- Python 3.12 (apenas para desenvolvimento/depuração local fora do contêiner)
- Uma API compatível com OpenAI (ex.: [LM Studio](https://lmstudio.ai/), [Ollama](https://ollama.com/) com compatibilidade OpenAI, ou a própria API da OpenAI)

## Licença

Projeto open source. Sinta-se livre para usar, modificar e distribuir.
