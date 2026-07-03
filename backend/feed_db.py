import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from datasets import load_dataset
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Configuração (mesmas variáveis usadas pelo pipeline.py)
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_CHROMA = os.getenv("CHROMA_DIR", os.path.join(_BASE_DIR, "diretorio_chroma"))

# O modelo de embeddings TEM que ser o mesmo do pipeline.py, senão a busca
# semântica não bate com o que foi indexado (principal causa de "alucinação").
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Quantos artigos indexar. O split 'pqa_labeled' tem 1000 exemplos validados por
# especialistas. Quanto mais artigos no banco, maior a chance de recuperar algo
# relevante. Padrão: usar todos os 1000. Reduza (ex.: 200) se quiser indexar
# mais rápido para testar.
TAMANHO_AMOSTRA = int(os.getenv("TAMANHO_AMOSTRA", "1000"))

print("Carregando o dataset PubMedQA (pqa_labeled)...")
dataset = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train")

total = min(TAMANHO_AMOSTRA, len(dataset))
amostra = dataset.select(range(total))
print(f"Indexando {total} de {len(dataset)} artigos disponíveis.")

documentos = []
for item in amostra:
    # O PubMedQA guarda os parágrafos do artigo dentro de uma lista em 'context'
    texto_artigo = " ".join(item['context']['contexts'])
    titulo_artigo = item['question']  # Usamos a pergunta original como metadado/título

    # Criamos um objeto Document do LangChain para o banco entender
    doc = Document(
        page_content=texto_artigo,
        metadata={"titulo": titulo_artigo, "id_pubmed": item['pubid']}
    )
    documentos.append(doc)

print(f"Gerando embeddings com '{EMBEDDING_MODEL}' (a primeira execução baixa o modelo)...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

db = Chroma.from_documents(
    documents=documentos,
    embedding=embeddings,
    persist_directory=DIRETORIO_CHROMA,
)

print(f"Banco vetorial criado em: {DIRETORIO_CHROMA}")
print(f"Total de documentos indexados: {len(documentos)}")
