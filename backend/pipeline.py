import json
import os
import re

from dotenv import load_dotenv

# Carrega variáveis de um arquivo .env na raiz do projeto (um nível acima de backend/),
# funcionando igual no Windows e no WSL sem precisar exportar variáveis na mão.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ---------------------------------------------------------------------------
# Configuração (tudo pode ser sobrescrito por variáveis de ambiente / .env)
# ---------------------------------------------------------------------------
# Caminho do banco vetorial calculado a partir da localização deste arquivo,
# para funcionar mesmo se o script for chamado de outra pasta.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_CHROMA = os.getenv(
    "CHROMA_DIR", os.path.join(_BASE_DIR, "diretorio_chroma")
)

# Nome do modelo no Ollama (ex.: "llama3.1", "llama3.1:8b", "llama3.2").
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Endereço do servidor Ollama. No Windows nativo e no WSL2 com espelhamento de
# rede, "http://localhost:11434" funciona. Se o código roda no WSL e o Ollama
# está no Windows sem espelhamento, aponte para o IP do host do Windows.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Modelo de embeddings usado tanto na ingestão (feed_db.py) quanto na busca.
# TEM que ser o MESMO nos dois lugares, senão a busca vira ruído (alucinação).
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# Quantos artigos recuperar do banco por pergunta. Este é o número que você
# aumenta "até ele responder direito". Padrão elevado de 4 (default do Chroma)
# para 8.
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "8"))

# Janela de contexto do Ollama EM TOKENS. Este é o parâmetro mais importante
# contra a sensação de que "ele só lê 2 a 4 artigos": o padrão do Ollama é
# num_ctx=2048, então mesmo recuperando 8 artigos, o texto excedente é
# silenciosamente cortado e o modelo só "enxerga" os primeiros. Aumentamos
# para 8192 para caber vários resumos do PubMed de uma vez.
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

# Máximo de tokens gerados na resposta final. O padrão do Ollama (128) corta
# o relatório no meio. -1 = sem limite; usamos um teto generoso.
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "1024"))

# Quantos caracteres de cada artigo entram no contexto do sintetizador.
# Limita o tamanho para não estourar a janela de contexto com poucos artigos.
MAX_CHARS_POR_ARTIGO = int(os.getenv("MAX_CHARS_POR_ARTIGO", "1600"))


class Run:
    def __init__(self, pergunta: str):
        self.pergunta = pergunta

    def _construir_llm(self, *, formato_json: bool = False, num_predict: int | None = None) -> Ollama:
        """Cria uma instância do Ollama já com os parâmetros que reduzem alucinação."""
        kwargs = dict(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,            # determinístico => menos invenção
            num_ctx=OLLAMA_NUM_CTX,   # janela grande => enxerga todos os artigos
        )
        if num_predict is not None:
            kwargs["num_predict"] = num_predict
        if formato_json:
            kwargs["format"] = "json"  # força o decompositor a devolver JSON
        return Ollama(**kwargs)

    def _deduplicar_artigos(self, artigos):
        vistos = set()
        artigos_unicos = []

        for doc in artigos:
            chave = (
                doc.metadata.get("id_pubmed")
                or doc.metadata.get("titulo")
                or doc.page_content.strip()
            )

            if chave in vistos:
                continue

            vistos.add(chave)
            artigos_unicos.append(doc)

        return artigos_unicos

    @staticmethod
    def _extrair_json(texto: str) -> dict:
        """Extrai um objeto JSON mesmo que o modelo devolva com ```json ... ``` ou texto extra."""
        texto = texto.strip()
        # Remove cercas de markdown, se houver.
        texto = re.sub(r"^```(?:json)?", "", texto).strip()
        texto = re.sub(r"```$", "", texto).strip()
        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            # Última tentativa: pegar o primeiro bloco {...} do texto.
            match = re.search(r"\{.*\}", texto, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def executar(self):
        llm_json = self._construir_llm(formato_json=True)
        llm_texto = self._construir_llm(num_predict=OLLAMA_NUM_PREDICT)

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        db_salvo = Chroma(
            persist_directory=DIRETORIO_CHROMA,
            embedding_function=embeddings,
        )

        # agente decompositor PICO
        template = """
        Você é um assistente de pesquisa médica especialista na metodologia PICO.
        Sua tarefa é receber uma pergunta clínica (tanto em portugues quanto em ingles) e extrair os componentes em INGLÊS (fazer a tradução
        se necessário), para facilitar a busca nos artigos do PubMed.
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
        chain_decompositor = prompt_pico | llm_json

        template_sintetizador = """
        Você é um médico cientista sênior especialista em Medicina Baseada em Evidências.
        Sua tarefa é responder à pergunta clínica do usuário utilizando APENAS os estudos fornecidos abaixo como contexto.
        Não use nenhum conhecimento externo; se os estudos não trouxerem a resposta, diga explicitamente que a evidência disponível é insuficiente.
        Não cite de forma alguma explicitamente os estudos, artigos, números, rótulos ou colchetes na resposta.
        Descreva apenas a síntese das evidências, sem mencionar "Estudo", "Artigo", "[1]" ou qualquer variação semelhante.

        Regras estritas:
        1. Responda em Português.
        2. Fale se os estudos recuperados são contraditórios ou se a evidência é insuficiente.
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
        chain_sintetizador = prompt_sintese | llm_texto

        # pipeline
        pergunta_medica = self.pergunta
        resposta_decompositor = chain_decompositor.invoke({"pergunta": pergunta_medica})

        resposta_geral = {}

        try:
            dados = self._extrair_json(resposta_decompositor)

            # agente 2 de busca — usa TODOS os componentes PICO disponíveis
            # (antes usava só population + intervention, o que empobrecia a busca)
            termo_busca = " ".join(
                str(dados.get(campo, "")).strip()
                for campo in ("population", "intervention", "comparison", "outcome")
            ).strip()
            if not termo_busca:
                termo_busca = pergunta_medica
            print(f"termo buscado: {termo_busca}")

            artigos = db_salvo.similarity_search(termo_busca, k=RETRIEVER_K)
            artigos_final = self._deduplicar_artigos(artigos)
            print(f"TAMANHOS: {len(artigos)} e {len(artigos_final)}")

            print("Artigos encontrados:")
            for doc in artigos_final:
                print(f"Titulo: {doc.metadata.get('titulo', 'Sem titulo')}\nTrecho: {doc.page_content[:300]}...")
                print("-" * 60)

            # agente 3 sintetizador
            contexto_texto = ""
            for i, doc in enumerate(artigos_final, start=1):
                trecho = doc.page_content[:MAX_CHARS_POR_ARTIGO]
                contexto_texto += f"\n[Estudo {i}] {trecho}\n"

            resposta_sintetizador = chain_sintetizador.invoke({
                "contexto_estudos": contexto_texto,
                "pergunta_original": pergunta_medica
            })

            resposta_geral['artigos_encontrados'] = [
                {
                    "titulo": doc.metadata.get("titulo", "Sem titulo"),
                    "id_pubmed": doc.metadata.get("id_pubmed"),
                    "trecho": doc.page_content,
                }
                for doc in artigos_final
            ]
            resposta_geral['resposta_sintetizador'] = resposta_sintetizador

        except json.JSONDecodeError:
            print(f"\n[Erro] O modelo não retornou um JSON limpo. resposta_decompositor bruta da IA: {resposta_decompositor}")
            resposta_geral['erro'] = "O decompositor PICO não retornou JSON válido. Tente novamente."

        return resposta_geral


if __name__ == "__main__":
    pergunta = "Metformina melhora o controle glicêmico em idosos com diabetes tipo 2?"
    model = Run(pergunta).executar()
    print("\n===== RESPOSTA FINAL =====")
    print(model.get("resposta_sintetizador", model))
