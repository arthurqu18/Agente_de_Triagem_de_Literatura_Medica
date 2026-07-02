# Agente de Triagem de Literatura Médica

Este projeto implementa um assistente para triagem de literatura médica com apoio de IA generativa, busca semântica e uma interface web.

A ideia do trabalho é receber uma pergunta clínica, extrair seus componentes no formato PICO, consultar um banco vetorial construído a partir do PubMedQA e, por fim, sintetizar uma resposta em linguagem natural com base nos estudos recuperados.

## O que o projeto faz

O fluxo principal do sistema é o seguinte:

1. O usuário envia uma pergunta clínica.
2. O backend usa o Ollama para decompor a pergunta em PICO.
3. O sistema consulta um banco vetorial local com artigos do PubMedQA.
4. Os estudos mais próximos são recuperados por similaridade.
5. Outro prompt do modelo gera uma resposta resumida em português.
6. O frontend em Next.js consome a API e exibe a resposta.

## Estrutura do projeto

O repositório está dividido em duas partes principais:

- backend: API em FastAPI, pipeline de busca e geração, e script para montar o banco vetorial.
- frontend: aplicação web em Next.js para interface com o usuário.

## Pré-requisitos

Para executar o projeto, você precisa ter:

- Python 3.10 ou superior.
- Um ambiente virtual Python já criado na pasta do projeto.
- Ollama instalado e em execução localmente.
- Um modelo disponível no Ollama, como llama3.1.
- Node.js 20.9.0 ou superior para o frontend.
- npm instalado junto com o Node.

## Backend

A API principal está em backend/api.py e usa FastAPI.

### Como iniciar a API

A partir da pasta do projeto:

    cd /home/arthur_qu/Agente_de_Triagem_de_Literatura_Medica/backend
    ../venv/bin/uvicorn api:app --reload

Se o seu ambiente virtual estiver em outro caminho, ajuste o executável do Python/uvicorn conforme necessário.

### Documentação interativa

Com a API rodando, a documentação aparece nestes endereços:

- /docs para Swagger UI
- /redoc para ReDoc

Exemplo:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

### Endpoint disponível

- POST /executar

Esse endpoint recebe uma pergunta clínica e devolve os artigos recuperados e a síntese gerada pelo pipeline.

## Geração do banco vetorial

Antes de usar o sistema, é necessário criar o banco local de embeddings a partir do PubMedQA.

O script responsável por isso é backend/feed_db.py.

### Como gerar o banco

    cd /home/arthur_qu/Agente_de_Triagem_de_Literatura_Medica/backend
    ../venv/bin/python feed_db.py

Esse processo baixa o dataset PubMedQA da Hugging Face, seleciona uma amostra de artigos e grava os vetores na pasta backend/diretorio_chroma.

## Frontend

A interface web está em frontend e foi criada com Next.js.

### Como instalar dependências

Se ainda não tiver instalado os pacotes do frontend:

    cd /home/arthur_qu/Agente_de_Triagem_de_Literatura_Medica/frontend
    npm install

### Como iniciar em modo desenvolvimento

    cd /home/arthur_qu/Agente_de_Triagem_de_Literatura_Medica/frontend
    npm run dev

O frontend espera um Node.js compatível com a versão do Next usada no projeto. Se aparecer erro de versão, atualize o Node para 20.9.0 ou superior.

## Dependências principais

Backend:

- fastapi
- uvicorn
- langchain-community
- langchain-core
- langchain-chroma
- langchain-huggingface
- datasets
- chromadb
- sentence-transformers

Frontend:

- next
- react
- react-dom
- tailwindcss
- typescript

## Observações importantes

- O Ollama precisa estar rodando localmente para o pipeline funcionar.
- O banco vetorial é salvo em backend/diretorio_chroma.
- Se você recriar o banco com backend/feed_db.py, ele pode sobrescrever a base local existente.
- O projeto foi pensado para uso local e desenvolvimento.

## Fluxo rápido de execução

1. Garanta que o Ollama esteja ativo.
2. Gere o banco vetorial com backend/feed_db.py.
3. Inicie a API com FastAPI.
4. Inicie o frontend com Next.js.
5. Acesse a interface e teste uma pergunta clínica.

## Exemplo de uso

Pergunta de teste sugerida:

    Qual a eficácia da metformina em idosos com diabetes tipo 2 comparada à dieta?

Esse tipo de pergunta permite testar a decomposição PICO, a busca semântica e a síntese final do modelo.
