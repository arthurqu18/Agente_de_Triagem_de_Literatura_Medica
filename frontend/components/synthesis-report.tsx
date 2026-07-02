"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { ShieldCheck } from "lucide-react"

interface SynthesisReportProps {
  content: string
}

type Certeza = "alto" | "medio" | "baixo" | null

function detectarCerteza(texto: string): Certeza {
  const lower = texto.toLowerCase()
  // Procura o trecho após "grau de certeza"
  const idx = lower.indexOf("grau de certeza")
  const escopo = idx >= 0 ? lower.slice(idx, idx + 120) : lower
  if (/\bbaix/.test(escopo)) return "baixo"
  if (/\bm[eé]di/.test(escopo)) return "medio"
  if (/\balt/.test(escopo)) return "alto"
  return null
}

const CERTEZA_STYLES: Record<
  Exclude<Certeza, null>,
  { label: string; className: string }
> = {
  alto: {
    label: "Certeza Alta",
    className: "bg-[var(--chart-2)]/15 text-[var(--chart-2)]",
  },
  medio: {
    label: "Certeza Média",
    className: "bg-[var(--chart-3)]/15 text-[var(--chart-3)]",
  },
  baixo: {
    label: "Certeza Baixa",
    className: "bg-[var(--chart-4)]/15 text-[var(--chart-4)]",
  },
}

export function SynthesisReport({ content }: SynthesisReportProps) {
  const certeza = detectarCerteza(content)

  return (
    <section
      aria-label="Relatório de evidências"
      className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8"
    >
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <ShieldCheck className="size-4" aria-hidden="true" />
          </span>
          <h2 className="font-heading text-xl font-medium text-card-foreground">
            Relatório de Evidências
          </h2>
        </div>
        {certeza && (
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${CERTEZA_STYLES[certeza].className}`}
          >
            {CERTEZA_STYLES[certeza].label}
          </span>
        )}
      </div>

      <div className="prose-report">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => (
              <h3 className="mb-2 mt-5 font-heading text-lg font-medium text-card-foreground first:mt-0">
                {children}
              </h3>
            ),
            h2: ({ children }) => (
              <h3 className="mb-2 mt-5 font-heading text-lg font-medium text-card-foreground first:mt-0">
                {children}
              </h3>
            ),
            h3: ({ children }) => (
              <h4 className="mb-2 mt-4 font-medium text-card-foreground first:mt-0">
                {children}
              </h4>
            ),
            p: ({ children }) => (
              <p className="mb-3 leading-relaxed text-muted-foreground">
                {children}
              </p>
            ),
            strong: ({ children }) => (
              <strong className="font-semibold text-card-foreground">
                {children}
              </strong>
            ),
            ul: ({ children }) => (
              <ul className="mb-3 flex list-disc flex-col gap-1.5 pl-5 text-muted-foreground">
                {children}
              </ul>
            ),
            ol: ({ children }) => (
              <ol className="mb-3 flex list-decimal flex-col gap-1.5 pl-5 text-muted-foreground">
                {children}
              </ol>
            ),
            li: ({ children }) => (
              <li className="leading-relaxed">{children}</li>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </section>
  )
}
