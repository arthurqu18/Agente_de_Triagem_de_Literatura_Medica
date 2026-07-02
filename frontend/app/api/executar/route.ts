import { NextResponse } from "next/server"

// URL da sua API FastAPI. Configure BACKEND_URL nas variáveis de ambiente
// para apontar para onde o uvicorn está rodando. Padrão: localhost:8000.
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000"

// O pipeline usa um LLM local (Ollama), que pode demorar. Damos folga no tempo.
export const maxDuration = 300

export async function POST(request: Request) {
  let question: string

  try {
    const body = await request.json()
    question = typeof body?.question === "string" ? body.question.trim() : ""
  } catch {
    return NextResponse.json(
      { detail: "Corpo da requisição inválido." },
      { status: 400 },
    )
  }

  if (!question) {
    return NextResponse.json(
      { detail: "Faça uma pergunta." },
      { status: 400 },
    )
  }

  // O FastAPI espera `question` como query parameter no endpoint /executar.
  const target = `${BACKEND_URL.replace(/\/$/, "")}/executar?question=${encodeURIComponent(
    question,
  )}`

  try {
    const res = await fetch(target, {
      method: "POST",
      headers: { Accept: "application/json" },
    })

    const contentType = res.headers.get("content-type") ?? ""
    const payload = contentType.includes("application/json")
      ? await res.json()
      : await res.text()

    if (!res.ok) {
      const detail =
        typeof payload === "object" && payload !== null && "detail" in payload
          ? (payload as { detail: string }).detail
          : "O backend retornou um erro."
      return NextResponse.json({ detail }, { status: res.status })
    }

    return NextResponse.json(payload)
  } catch (error) {
    console.log("[v0] Erro ao conectar ao backend:", error)
    return NextResponse.json(
      {
        detail:
          "Não foi possível conectar ao backend. Verifique se a API FastAPI está rodando e se a variável BACKEND_URL está correta.",
      },
      { status: 502 },
    )
  }
}
