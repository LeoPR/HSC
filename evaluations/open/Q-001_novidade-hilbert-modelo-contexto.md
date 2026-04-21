---
id: Q-001
titulo: Novidade: Hilbert como modelo de contexto probabilístico
categoria: novidade
prioridade: critica
criado: 2026-03-29
relacionado: [Q-003, Q-007]
---

## Pergunta

O uso de curvas de Hilbert como **modelo de contexto probabilístico do tipo Markov**
(estimando P(s_t | s_{t-1}) a partir do percurso espacial da curva) é uma contribuição
original, ou já foi publicado de forma equivalente?

---

## Contexto

A literatura identificada até agora usa curvas de Hilbert para:
- **Reordenação espacial:** reindexar pixels/voxels antes de codificadores existentes
- **Indexação de banco de dados:** preservar localidade em queries multidimensionais
- **Aceleração de busca fractal:** reduzir espaço de busca de blocos similares

Nenhum dos 8 papers identificados (1996–2021) propõe usar a curva como:
1. Modelo dinâmico de probabilidade de transição simbólica
2. Mecanismo de seleção automática de dimensão/topologia ótima
3. Framework unificado lossy/lossless via tolerância de erro configurável

A hipótese de novidade do projeto está inteiramente apoiada nessa distinção.

**Risco:** Se a busca sistemática encontrar trabalho equivalente, Q1 do SIAC passa de
"contribuição nova" para "refinamento de abordagem existente" — o que altera o escopo,
mas não invalida o projeto.

---

## Hipótese de Trabalho

**H1:** O uso de curvas de Hilbert como modelo de contexto Markov para estimação de
probabilidades de transição simbólica **não foi publicado** de forma equivalente até 2025.

**H2 (alternativa):** Se encontrado trabalho semelhante, a contribuição pode ser delimitada
à seleção adaptativa de dimensão + framework unificado lossy/lossless.

---

## Plano de Investigação

### 1. Busca bibliográfica sistemática

**Bases a cobrir:**
- IEEE Xplore
- ACM Digital Library
- arXiv (cs.IT, cs.LG, eess.SP)
- Google Scholar
- Semantic Scholar

**Queries primárias (executar todas):**
```
"Hilbert curve" AND "context model" AND "compression"
"Hilbert curve" AND "probabilistic model" AND "entropy coding"
"space-filling curve" AND "Markov model" AND "compression"
"Hilbert scan" AND "adaptive" AND "context"
"Hilbert" AND "order-1 context" AND compression
"space-filling" AND "transition probability" AND encoding
```

**Queries para seleção adaptativa:**
```
"Hilbert" AND "dimension selection" AND "compression"
"space-filling" AND "optimal dimension" AND "entropy"
"curve order selection" AND "adaptive compression"
```

**Período:** 1990–2025 (busca completa)

### 2. Critério de triagem

Para cada paper encontrado, verificar:
- [ ] Usa Hilbert como modelo de contexto para estimar P(s|contexto)?
- [ ] A curva define a estrutura probabilística (não apenas a ordem de leitura)?
- [ ] Inclui seleção automática de parâmetros da curva?
- [ ] Unifica lossy/lossless?

Se **todos** os itens forem "não" → paper usa reordenação, não modelo de contexto → não invalida H1.

### 3. Documentação dos resultados

Para cada paper relevante, registrar:
```
- Autores, ano, título, DOI
- Como a curva é usada (reordenação vs contexto)
- Sobreposição com nossa proposta (score 0-3)
- Implicação para Q1
```

---

## Critério de Conclusão

- **H1 confirmada:** Busca completa nas 5 bases, queries primárias sem resultado equivalente.
  → Migrar para A-001, declarar novidade em Q1 com respaldo bibliográfico.

- **H1 refutada:** Encontrado paper com uso equivalente de Hilbert como modelo probabilístico.
  → Ajustar escopo (H2), reabrir SIAC Q1 com delimitação precisa.

---

## Status da Busca

| Base | Queries executadas | Papers triados | Equivalentes encontrados |
|------|-------------------|---------------|--------------------------|
| IEEE Xplore | ⏳ parcial | 8 (S1 SIAC) | 0 |
| ACM DL | ❌ pendente | — | — |
| arXiv | ❌ pendente | — | — |
| Google Scholar | ❌ pendente | — | — |
| Semantic Scholar | ❌ pendente | — | — |

**Observação:** Os 8 papers do S1 usam Hilbert exclusivamente como reordenação/scan,
sem modelo probabilístico associado. Busca ainda incompleta.
