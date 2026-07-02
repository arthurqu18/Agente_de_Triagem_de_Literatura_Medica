from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pipeline import Run

app = FastAPI(title="Agente de Triagem Médica")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/executar")
async def responder_pergunta(question: str):
    """
    Recebe uma pergunta e responde com os artigos encontrados e um resumo
    """
    if not question:
        raise HTTPException(status_code=400, detail="Faça uma pergunta")
    
    model = Run(question).executar()

    return model