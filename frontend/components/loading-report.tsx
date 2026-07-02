"use client"

import { useEffect, useState } from "react"
import { Loader2 } from "lucide-react"

const ETAPAS = [
  "Decompondo a pergunta com a metodologia PICO...",
  "Buscando artigos relevantes na base vetorial...",
  "Sintetizando a evidência com o modelo clínico...",
]

export function LoadingReport() {
  const [etapa, setEtapa] = useState(0)

  useEffect(() => {
    const timers = [
      setTimeout(() => setEtapa(1), 4000),
      setTimeout(() => setEtapa(2), 9000),
    ]
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8">
      <div className="flex items-center gap-3">
        <Loader2 className="size-5 shrink-0 animate-spin text-primary" />
        <p className="text-sm font-medium text-card-foreground">
          {ETAPAS[etapa]}
        </p>
      </div>

      <ol className="mt-5 flex flex-col gap-2">
        {ETAPAS.map((texto, i) => (
          <li
            key={texto}
            className={`flex items-center gap-2 text-xs ${
              i <= etapa ? "text-foreground" : "text-muted-foreground"
            }`}
          >
            <span
              className={`size-1.5 rounded-full ${
                i < etapa
                  ? "bg-[var(--chart-2)]"
                  : i === etapa
                    ? "bg-primary"
                    : "bg-border"
              }`}
            />
            {texto}
          </li>
        ))}
      </ol>

      <div className="mt-6 space-y-3">
        <div className="h-3 w-1/3 animate-pulse rounded bg-muted" />
        <div className="h-3 w-full animate-pulse rounded bg-muted" />
        <div className="h-3 w-5/6 animate-pulse rounded bg-muted" />
        <div className="h-3 w-2/3 animate-pulse rounded bg-muted" />
      </div>

      <p className="mt-6 text-xs text-muted-foreground">
        O modelo roda localmente e pode levar alguns instantes.
      </p>
    </div>
  )
}
