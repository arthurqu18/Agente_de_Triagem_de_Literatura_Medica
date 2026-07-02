"use client"

import { useState } from "react"
import { ArrowUp, Loader2 } from "lucide-react"

const EXEMPLOS = [
  "Metformina melhora o controle glicêmico em idosos com diabetes tipo 2?",
  "Estatinas reduzem o risco de infarto em pacientes com colesterol alto?",
  "Exercício físico ajuda no tratamento da depressão leve?",
]

interface SearchFormProps {
  onSubmit: (question: string) => void
  loading: boolean
}

export function SearchForm({ onSubmit, loading }: SearchFormProps) {
  const [value, setValue] = useState("")

  function submit() {
    const q = value.trim()
    if (!q || loading) return
    onSubmit(q)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.nativeEvent.isComposing || e.keyCode === 229) return
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="relative rounded-2xl border border-border bg-card shadow-sm transition-colors focus-within:border-primary">
        <label htmlFor="pergunta" className="sr-only">
          Pergunta clínica
        </label>
        <textarea
          id="pergunta"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
          disabled={loading}
          placeholder="Digite sua pergunta clínica... (Enter para enviar, Shift+Enter para nova linha)"
          className="w-full resize-none rounded-2xl bg-transparent px-4 py-4 pr-14 text-base leading-relaxed text-card-foreground outline-none placeholder:text-muted-foreground disabled:opacity-60"
        />
        <button
          type="button"
          onClick={submit}
          disabled={loading || !value.trim()}
          aria-label="Enviar pergunta"
          className="absolute bottom-3 right-3 flex size-9 items-center justify-center rounded-full bg-primary text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <ArrowUp className="size-4" />
          )}
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {EXEMPLOS.map((ex) => (
          <button
            key={ex}
            type="button"
            disabled={loading}
            onClick={() => {
              setValue(ex)
              onSubmit(ex)
            }}
            className="rounded-full border border-border bg-card px-3 py-1.5 text-left text-xs text-muted-foreground transition-colors hover:border-primary hover:text-foreground disabled:opacity-50"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  )
}
