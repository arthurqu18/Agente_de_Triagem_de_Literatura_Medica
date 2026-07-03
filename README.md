# Agente de Triagem de Literatura Médica

Assistente para triagem de literatura médica com IA generativa local (Ollama),
busca semântica (ChromaDB + embeddings) e interface web (Next.js).

Você faz uma **pergunta clínica**, o sistema a decompõe no formato **PICO**,
busca artigos relevantes do **PubMedQA** num banco vetorial local e sintetiza
uma resposta em português baseada apenas nos estudos recuperados.

---

## Como funciona (fluxo)

1. O usuário envia uma pergunta clínica pelo frontend.
2. O backend (FastAPI) chama o **Ollama** para decompor a pergunta em PICO
   (Population, Intervention, Comparison, Outcome).
3. Os termos PICO viram uma busca semântica no **ChromaDB**.
4. Os artigos mais próximos são recuperados (parâmetro `RETRIEVER_K`).
5. Um segundo prompt do modelo sintetiza a resposta **usando apenas** esses artigos.
6. O frontend em Next.js exibe o relatório e os artigos.

## Estrutura

```
Agente_de_Triagem_de_Literatura_Medica/
├── .env.example          # modelo de configuração (copie para .env)
├── requirements.txt      # dependências Python do backend
├── backend/
│   ├── api.py            # API FastAPI (endpoint POST /executar)
│   ├── pipeline.py       # pipeline PICO + busca + síntese
│   ├── feed_db.py        # gera o banco vetorial a partir do PubMedQA
│   └── diretorio_chroma/ # banco vetorial persistido (gerado por feed_db.py)
└── frontend/             # aplicação Next.js
```

---

## Pré-requisitos

- **Ollama** (roda o LLM localmente) — instalado no Windows.
- **Python 3.10+**.
- **Node.js 20.9+** e **npm** (para o frontend).
- ~6 GB livres de disco (modelo `llama3.1` 8B ≈ 4,7 GB + dependências).

> Você pode rodar **tudo no Windows nativo** ou **tudo no WSL2**. As duas
> trilhas estão descritas abaixo. Escolha uma e siga só ela para o backend.

---

## Passo 1 — Instalar o Ollama e o modelo

O Ollama é o servidor que executa o `llama3.1`. Ele precisa estar **rodando**
sempre que você usar o backend.

### No Windows

1. Baixe e instale em <https://ollama.com/download/windows>.
2. Abra o **PowerShell** e baixe o modelo:

   ```powershell
   ollama pull llama3.1
   ```

3. Confirme que o servidor responde (o instalador já sobe o Ollama em segundo
   plano, escutando em `http://localhost:11434`):

   ```powershell
   ollama list
   curl http://localhost:11434/api/tags
   ```

### No WSL2 (alternativa: Ollama dentro do próprio Linux)

Se você vai rodar o backend no WSL, o caminho **mais simples e sem dor de
cabeça de rede** é instalar o Ollama também dentro do WSL:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &          # sobe o servidor em segundo plano
ollama pull llama3.1
```

Assim, dentro do WSL, `http://localhost:11434` já aponta para o Ollama local e
você não precisa configurar nada de rede. (Se preferir usar o Ollama que já
está no Windows, veja a seção **"WSL → Ollama no Windows"** mais abaixo.)

---

## Passo 2 — Backend

Escolha **UMA** das duas trilhas.

### Trilha A — Windows (PowerShell)

Abra o PowerShell **na pasta do projeto** e rode, nesta ordem:

```powershell
# 1. Criar e ativar o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Atualizar o pip
python -m pip install --upgrade pip

# 3. Instalar o PyTorch CPU ANTES do resto (evita baixar ~GBs de CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 4. Instalar o restante das dependências
pip install -r requirements.txt

# 5. Criar o arquivo de configuração
Copy-Item .env.example .env
```

> Se o PowerShell bloquear a ativação do venv com erro de *"execution policy"*,
> rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> e ative de novo.

### Trilha B — WSL2 (Ubuntu)

O projeto está no drive do Windows; dentro do WSL ele aparece em `/mnt/...`.
Exemplo para um projeto no `E:`:

```bash
cd /mnt/e/PROJ_IA/Agente_de_Triagem_de_Literatura_Medica

# 1. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Atualizar o pip
python -m pip install --upgrade pip

# 3. Instalar o PyTorch CPU ANTES do resto
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 4. Instalar o restante das dependências
pip install -r requirements.txt

# 5. Criar o arquivo de configuração
cp .env.example .env
```

> **Por que instalar o torch separado:** o `sentence-transformers` depende do
> PyTorch. Por padrão o pip baixa a build com CUDA (vários GB de pacotes NVIDIA)
> mesmo sem GPU — é o que trava a instalação por horas. Instalando a build
> **CPU-only** primeiro, o `pip install -r requirements.txt` reaproveita ela.
> Se o venv travou numa tentativa anterior, **apague a pasta `venv`** e recomece.

---

## Passo 3 — Gerar o banco vetorial

Só precisa rodar **uma vez** (ou quando quiser reindexar). Baixa o PubMedQA da
Hugging Face e grava os vetores em `backend/diretorio_chroma`.

Com o venv ativado, a partir da pasta `backend`:

**Windows:**
```powershell
cd backend
..\venv\Scripts\python.exe feed_db.py
```

**WSL/Linux:**
```bash
cd backend
../venv/bin/python feed_db.py
```

Por padrão indexa **1000 artigos** (todo o split validado por especialistas).
Para indexar menos e testar mais rápido, ajuste `TAMANHO_AMOSTRA` no `.env`.

---

## Passo 4 — Iniciar a API

Com o Ollama rodando e o banco gerado, a partir da pasta `backend`:

**Windows:**
```powershell
cd backend
..\venv\Scripts\uvicorn.exe api:app --reload --port 8000
```

**WSL/Linux:**
```bash
cd backend
../venv/bin/uvicorn api:app --reload --port 8000
```

A API sobe em `http://localhost:8000`. Teste rápido pelo terminal:

```bash
curl -X POST "http://localhost:8000/executar?question=Metformina%20melhora%20o%20controle%20glicemico%20em%20idosos%3F"
```

---

## Passo 5 — Frontend

Em **outro terminal**, a partir da pasta `frontend`:

```bash
cd frontend
npm install
npm run dev
```

Acesse <http://localhost:3000>. O frontend fala com a API em
`http://localhost:8000` por padrão. Para apontar para outro endereço, crie
`frontend/.env.local` com:

```
BACKEND_URL=http://localhost:8000
```

Se aparecer erro de versão do Node, atualize para **20.9.0+**.

---

## Configuração (arquivo `.env`)

Todas as opções ficam no `.env` na raiz do projeto (veja `.env.example`).
As mais importantes:

| Variável             | Padrão                                    | Para que serve |
|----------------------|-------------------------------------------|----------------|
| `OLLAMA_MODEL`       | `llama3.1`                                 | Modelo carregado no Ollama. |
| `OLLAMA_BASE_URL`    | `http://localhost:11434`                   | Onde o Ollama está escutando. |
| `RETRIEVER_K`        | `8`                                        | **Quantos artigos recuperar por pergunta.** |
| `OLLAMA_NUM_CTX`     | `8192`                                      | **Janela de contexto (tokens)** — faz o modelo ler todos os artigos. |
| `OLLAMA_NUM_PREDICT` | `1024`                                      | Tamanho máximo do relatório. |
| `EMBEDDING_MODEL`    | `sentence-transformers/all-MiniLM-L6-v2`   | Modelo de embeddings (o mesmo na indexação e na busca). |
| `TAMANHO_AMOSTRA`    | `1000`                                      | Quantos artigos o `feed_db.py` indexa. |

Depois de mudar o `.env`, **reinicie o uvicorn** para as mudanças valerem.

---

## Ajustando a qualidade das respostas (por que estava "alucinando")

O sistema respondia mal e parecia "ler só 2 a 4 artigos" por três motivos, todos
já corrigidos no código:

1. **Recuperava só 4 artigos.** A busca usava o `k` padrão do Chroma (4). Agora é
   configurável por `RETRIEVER_K` (padrão 8).
2. **Janela de contexto pequena — a causa principal.** O padrão do Ollama é
   `num_ctx=2048` tokens. Mesmo recuperando vários artigos, o texto que passava
   disso era **cortado silenciosamente**, e o modelo só "via" os 2-3 primeiros —
   exatamente o sintoma que você notou. Agora fixamos `OLLAMA_NUM_CTX=8192`.
3. **Modelo "criativo" demais.** A `temperature` estava no padrão (~0.8), o que
   induz o modelo a inventar. Agora usamos `temperature=0` (determinístico) e o
   prompt reforça responder **apenas** com os estudos, admitindo quando a
   evidência é insuficiente.

Também melhoramos a busca (usa os quatro componentes PICO, não só dois),
aumentamos o `num_predict` (o relatório não é mais cortado no meio) e deixamos o
parsing do JSON tolerante a blocos markdown.

**Como aumentar o número de artigos "até ele responder direito":** edite o
`.env` e suba os dois juntos — recuperar mais artigos sem aumentar a janela não
adianta:

```
RETRIEVER_K=12
OLLAMA_NUM_CTX=12288
```

Regra prática: cada artigo do PubMed ocupa ~300–500 tokens. Mantenha
`OLLAMA_NUM_CTX` folgado em relação a `RETRIEVER_K × ~500` + o tamanho do prompt.
Se aumentar demais, a resposta fica mais lenta na CPU. Reinicie o uvicorn após
alterar.

---

## WSL → Ollama no Windows (se NÃO instalou o Ollama dentro do WSL)

Se o backend roda no WSL mas o Ollama está no Windows:

1. No **Windows**, faça o Ollama escutar em todas as interfaces. Defina a
   variável de ambiente do sistema `OLLAMA_HOST=0.0.0.0` e **reinicie o Ollama**
   (feche pelo ícone da bandeja e abra de novo). Confira:
   ```powershell
   curl http://localhost:11434/api/tags
   ```

2. No **WSL**, descubra o IP do host Windows e aponte o `.env` para ele:
   ```bash
   # Em WSL2 no modo NAT, o host aparece no resolv.conf:
   cat /etc/resolv.conf | grep nameserver
   # ex.: nameserver 172.20.0.1
   ```
   No `.env`:
   ```
   OLLAMA_BASE_URL=http://172.20.0.1:11434
   ```
   > Em Windows 11 com **rede espelhada** (`networkingMode=mirrored` no
   > `.wslconfig`), `http://localhost:11434` já funciona direto do WSL e você
   > pode pular esse passo.

3. Teste do WSL antes de subir a API:
   ```bash
   curl http://SEU_IP_OU_LOCALHOST:11434/api/tags
   ```

---

## Solução de problemas

- **`Connection refused` / `Max retries exceeded` ao chamar a API:** o Ollama não
  está rodando ou o `OLLAMA_BASE_URL` está errado. Rode `ollama list` e teste
  `curl .../api/tags`.
- **`model 'llama3.1' not found`:** rode `ollama pull llama3.1` (no mesmo
  ambiente onde o Ollama serve).
- **Respostas ainda pobres / genéricas:** aumente `RETRIEVER_K` e `OLLAMA_NUM_CTX`
  juntos (ver seção acima) e confirme que o banco foi gerado (`feed_db.py`).
- **Banco vazio / "0 artigos":** rode o `feed_db.py` antes da API e verifique se
  a pasta `backend/diretorio_chroma` foi criada.
- **Instalação do venv travando/demorando horas:** você pulou o passo do PyTorch
  CPU. Apague a pasta `venv` e refaça na ordem do Passo 2.
- **`Activate.ps1` bloqueado no PowerShell:**
  `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.
- **Erro de versão no `npm run dev`:** atualize o Node para 20.9.0+.
- **Mudei o `.env` e nada mudou:** reinicie o uvicorn (o `--reload` recarrega o
  código, mas variáveis de ambiente são lidas na inicialização).

---

## Fluxo rápido (resumo)

1. `ollama pull llama3.1` e garanta o Ollama rodando.
2. Backend: criar venv → `torch` CPU → `pip install -r requirements.txt` → copiar `.env.example` para `.env`.
3. Gerar banco: `python feed_db.py` (dentro de `backend`).
4. Subir API: `uvicorn api:app --reload --port 8000` (dentro de `backend`).
5. Frontend: `npm install` → `npm run dev` → abrir <http://localhost:3000>.
