export interface Artigo {
  titulo: string
  id_pubmed: string | null
  trecho: string
}

export interface RespostaAgente {
  artigos_encontrados?: Artigo[]
  resposta_sintetizador?: string
}
