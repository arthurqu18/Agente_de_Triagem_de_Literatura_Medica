import json
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

llm = Ollama(model="llama3.1")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db_salvo = Chroma(persist_directory="./diretorio_chroma", embedding_function=embeddings)

# agente decompositor PICO
template = """
Você é um assistente de pesquisa médica especialista na metodologia PICO.
Sua tarefa é receber uma pergunta clínica e extrair os componentes em INGLÊS (para facilitar a busca nos artigos do PubMed).
Responda APENAS com um objeto JSON válido, sem comentários, explicações ou tags markdown (como ```json).

Exemplo de formato de saída:
{{
    "population": "elderly diabetes type 2",
    "intervention": "metformin",
    "comparison": "diet",
    "outcome": "glycemic control"
}}

Pergunta: {pergunta}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

# pipeline
pergunta_teste = "Qual a eficácia da metformina em idosos com diabetes tipo 2 comparada à dieta?"
resposta = chain.invoke({"pergunta": pergunta_teste})
print(resposta)

try:
    dados = json.loads(resposta.strip())
    print(json.dumps(dados, indent=4, ensure_ascii=False))

    # agente 2 de busca
    termo_busca = f"{dados['population']} {dados['intervention']}"
    print(f"termo buscado: {termo_busca}")

    artigos = db_salvo.similarity_search(termo_busca, k=2)
    print("Artigos encontrados:")
    for doc in artigos:
        print(f"Titulo: {doc.metadata.get('titulo', 'Sem titulo')}\nTrecho: {doc.page_content[:300]}...")
        print("-" * 60)

except json.JSONDecodeError:
    print(f"\n[Erro] O modelo não retornou um JSON limpo. Resposta bruta da IA: {resposta}")
