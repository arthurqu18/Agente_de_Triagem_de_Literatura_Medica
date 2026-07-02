import json
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class Run:
    def __init__(self, pergunta: str):
        self.pergunta = pergunta

    def executar(self):
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

        prompt_pico = ChatPromptTemplate.from_template(template)
        chain_decompositor = prompt_pico | llm

        template_sintetizador = """
        Você é um médico cientista sênior especialista em Medicina Baseada em Evidências.
        Sua tarefa é responder à pergunta clínica do usuário utilizando APENAS os estudos fornecidos abaixo como contexto.

        Regras estritas:
        1. Responda em Português.
        2. Identifique e sinalize explicitamente se os estudos recuperados são contraditórios ou se a evidência é insuficiente.
        3. Avalie a certeza da informação com base no contexto.

        Estudos recuperados:
        {contexto_estudos}

        Pergunta Clínica Original: {pergunta_original}

        Gere seu relatório estruturado da seguinte forma:
        - **RESUMO DA EVIDÊNCIA**: (Sua síntese dos fatos encontrados)
        - **SINALIZAÇÃO DE CONFLITOS/CONTRADIÇÕES**: (Diga claramente se os estudos concordam, divergem ou se faltam dados)
        - **GRAU DE CERTEZA DA RECOMENDAÇÃO**: (Alto, Médio ou Baixo, justificando brevemente)
        """
        prompt_sintese = ChatPromptTemplate.from_template(template_sintetizador)
        chain_sintetizador = prompt_sintese | llm

        # pipeline
        pergunta_medica = self.pergunta
        resposta_decompositor = chain_decompositor.invoke({"pergunta": pergunta_medica})

        resposta_geral = {}

        try:
            dados = json.loads(resposta_decompositor.strip())
            #print(json.dumps(dados, indent=4, ensure_ascii=False))

            # agente 2 de busca
            termo_busca = f"{dados['population']} {dados['intervention']}"
            #print(f"termo buscado: {termo_busca}")

            artigos = db_salvo.similarity_search(termo_busca, k=4)
            #print("Artigos encontrados:")
            # for doc in artigos:
            #     print(f"Titulo: {doc.metadata.get('titulo', 'Sem titulo')}\nTrecho: {doc.page_content[:300]}...")
            #     print("-" * 60)

            # agente 3 sintetizador
            contexto_texto = ""
            for i, doc in enumerate(artigos, start=1):
                contexto_texto += f"\nEstudo[{i}]: {doc.page_content}\n"

            resposta_sintetizador = chain_sintetizador.invoke({
                "contexto_estudos": contexto_texto,
                "pergunta_original": pergunta_medica
            })

            #print(f"relatório final: {resposta_sintetizador}")
            
            resposta_geral['artigos_encontrados'] = [
                {
                    "titulo": doc.metadata.get("titulo", "Sem titulo"),
                    "id_pubmed": doc.metadata.get("id_pubmed"),
                    "trecho": doc.page_content,
                }
                for doc in artigos
            ]
            resposta_geral['resposta_sintetizador'] = resposta_sintetizador

        except json.JSONDecodeError:
            print(f"\n[Erro] O modelo não retornou um JSON limpo. resposta_decompositor bruta da IA: {resposta_decompositor}")

        return resposta_geral