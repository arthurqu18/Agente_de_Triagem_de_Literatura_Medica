from datasets import load_dataset
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Carrega a versão 'pqa_labeled' do PubMedQA (contém dados validados por especialistas)
dataset = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train")
amostra = dataset.select(range(50))

documentos = []
for item in amostra:
    # O PubMedQA guarda os parágrafos do artigo dentro de uma lista em 'context'
    texto_artigo = " ".join(item['context']['contexts'])
    titulo_artigo = item['question'] # Usamos a pergunta original como metadado/título
    
    # Criamos um objeto Document do LangChain para o banco entender
    doc = Document(
        page_content=texto_artigo,
        metadata={"titulo": titulo_artigo, "id_pubmed": item['pubid']}
    )
    documentos.append(doc)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = Chroma.from_documents(
    documents=documentos,
    embedding=embeddings,
    persist_directory="./diretorio_chroma"
)