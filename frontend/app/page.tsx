"use client"

import { useState } from "react"
import { Activity, AlertCircle, Stethoscope } from "lucide-react"
import type { RespostaAgente } from "@/lib/types"
import { SearchForm } from "@/components/search-form"
import { SynthesisReport } from "@/components/synthesis-report"
import { ArticleCard } from "@/components/article-card"
import { LoadingReport } from "@/components/loading-report"

export default function Page() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resultado, setResultado] = useState<RespostaAgente | null>(null)
  const [perguntaAtual, setPerguntaAtual] = useState<string | null>(null)

  async function handleSubmit(question: string) {
    setLoading(true)
    setError(null)
    setResultado(null)
    setPerguntaAtual(question)

    try {
      const res = await fetch("/api/executar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      })
      const data = await res.json()

      if (!res.ok) {
        setError(data?.detail ?? "Ocorreu um erro ao processar a pergunta.")
        return
      }

      if (!data?.resposta_sintetizador && !data?.artigos_encontrados?.length) {
        setError(
          "O agente não conseguiu gerar uma resposta para esta pergunta. Tente reformular.",
        )
        return
      }

      setResultado(data as RespostaAgente)
    } catch {
      setError("Falha de conexão. Tente novamente.")
    } finally {
      setLoading(false)
    }
  }

  const artigos = resultado?.artigos_encontrados ?? []

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col px-4 py-10 sm:py-16">
        <header className="flex flex-col items-center text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
            <Stethoscope className="size-6" aria-hidden="true" />
          </span>
          <h1 className="mt-5 text-balance font-heading text-3xl font-medium tracking-tight text-foreground sm:text-4xl">
            Agente de Triagem Médica
          </h1>
          <p className="mt-3 max-w-xl text-pretty leading-relaxed text-muted-foreground">
            Faça uma pergunta clínica e receba uma síntese baseada em evidências
            dos artigos científicos que melhor a respondem.
          </p>
          <div className="mt-4 inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground">
            <Activity className="size-3.5 text-primary" aria-hidden="true" />
            Metodologia PICO · Medicina Baseada em Evidências
          </div>
        </header>

        <div className="mt-10">
          <SearchForm onSubmit={handleSubmit} loading={loading} />
        </div>

        <div className="mt-8 flex-1">
          {perguntaAtual && (
            <div className="mb-6 rounded-xl border border-border bg-secondary/50 px-4 py-3">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Pergunta
              </p>
              <p className="mt-1 text-pretty font-medium text-foreground">
                {perguntaAtual}
              </p>
            </div>
          )}

          {loading && <LoadingReport />}

          {error && !loading && (
            <div
              role="alert"
              className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4"
            >
              <AlertCircle className="mt-0.5 size-5 shrink-0 text-destructive" />
              <div>
                <p className="font-medium text-foreground">
                  Não foi possível responder
                </p>
                <p className="mt-1 text-sm text-muted-foreground">{error}</p>
              </div>
            </div>
          )}

          {resultado && !loading && (
            <div className="flex flex-col gap-8">
              {resultado.resposta_sintetizador && (
                <SynthesisReport content={resultado.resposta_sintetizador} />
              )}

              {artigos.length > 0 && (
                <section aria-label="Artigos encontrados">
                  <h2 className="mb-4 font-heading text-xl font-medium text-foreground">
                    Artigos encontrados{" "}
                    <span className="text-base font-normal text-muted-foreground">
                      ({artigos.length})
                    </span>
                  </h2>
                  <div className="flex flex-col gap-4">
                    {artigos.map((artigo, i) => (
                      <ArticleCard
                        key={`${artigo.id_pubmed ?? "art"}-${i}`}
                        artigo={artigo}
                        index={i + 1}
                      />
                    ))}
                  </div>
                </section>
              )}
            </div>
          )}
        </div>

        <footer className="mt-12 border-t border-border pt-6 text-center text-xs text-muted-foreground">
          Ferramenta acadêmica de apoio. Não substitui avaliação médica
          profissional.
        </footer>
      </div>
    </main>
  )
}
