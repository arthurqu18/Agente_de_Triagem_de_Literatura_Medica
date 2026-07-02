"use client"

import { useState } from "react"
import { ChevronDown, ExternalLink, FileText } from "lucide-react"
import type { Artigo } from "@/lib/types"

interface ArticleCardProps {
  artigo: Artigo
  index: number
}

export function ArticleCard({ artigo, index }: ArticleCardProps) {
  const [expanded, setExpanded] = useState(false)
  const trecho = artigo.trecho ?? ""
  const isLong = trecho.length > 320
  const preview = isLong && !expanded ? `${trecho.slice(0, 320)}...` : trecho

  return (
    <article className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-md bg-accent text-xs font-semibold text-accent-foreground">
          {index}
        </span>
        <div className="min-w-0 flex-1">
          <h4 className="text-pretty font-medium leading-snug text-card-foreground">
            {artigo.titulo || "Sem título"}
          </h4>

          {artigo.id_pubmed && (
            <a
              href={`https://pubmed.ncbi.nlm.nih.gov/${artigo.id_pubmed}/`}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
            >
              PubMed ID: {artigo.id_pubmed}
              <ExternalLink className="size-3" />
            </a>
          )}
        </div>
        <FileText
          className="size-4 shrink-0 text-muted-foreground"
          aria-hidden="true"
        />
      </div>

      <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
        {preview}
      </p>

      {isLong && (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
        >
          {expanded ? "Ver menos" : "Ver trecho completo"}
          <ChevronDown
            className={`size-3 transition-transform ${expanded ? "rotate-180" : ""}`}
          />
        </button>
      )}
    </article>
  )
}
