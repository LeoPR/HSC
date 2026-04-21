# Evaluations — Sistema de Controle de Perguntas Científicas

Este diretório centraliza o controle de perguntas, hipóteses e conclusões do projeto HSC.
Cada pergunta existe como um arquivo Markdown independente, permitindo rastreamento
do estado do projeto e evolução das conclusões ao longo das fases SIAC.

---

## Estrutura de Diretórios

```
evaluations/
├── README.md          ← este arquivo
├── open/              ← perguntas em aberto (hipóteses, planos de teste)
│   └── Q-NNN_titulo.md
└── answered/          ← perguntas concluídas (evidências, conclusão científica)
    └── A-NNN_titulo.md
```

---

## Workflow

```
Observação / Hipótese
        ↓
   Criar Q-NNN         →  open/
        ↓
 Pesquisar / Testar
        ↓
  Conclusão sólida     →  answered/ (renomear para A-NNN, preencher seções de resultado)
```

Uma pergunta só migra para `answered/` quando possui **evidência direta** (experimental,
bibliográfica, ou formal) suficiente para sustentação científica.

---

## Convenção de Nomenclatura

| Prefixo | Status | Exemplo |
|---------|--------|---------|
| `Q-NNN` | Em aberto | `Q-002_datasets-canonicos.md` |
| `A-NNN` | Respondida | `A-001_texto-sequencial-raster.md` |

O número `NNN` é sequencial dentro de cada categoria. `Q-` e `A-` compartilham o
mesmo namespace de IDs (Q-001 respondida vira A-001, não um novo A com número diferente).

---

## Frontmatter de Q (Pergunta em Aberto)

```markdown
---
id: Q-NNN
titulo: Título curto e descritivo
categoria: novidade | metodologia | empirico | design | dataset
prioridade: critica | alta | media | baixa
criado: YYYY-MM-DD
relacionado: [Q-NNN, Q-NNN]
---
```

## Frontmatter de A (Respondida)

```markdown
---
id: A-NNN
titulo: Título curto e descritivo
categoria: novidade | metodologia | empirico | design | dataset
prioridade: critica | alta | media | baixa
criado: YYYY-MM-DD
concluido: YYYY-MM-DD
---
```

---

## Categorias

| Categoria | Descrição |
|-----------|-----------|
| `novidade` | Verificação de contribuição original frente à literatura |
| `metodologia` | Decisões sobre design do experimento ou do método |
| `empirico` | Perguntas respondíveis por testes mensuráveis |
| `design` | Escolhas de implementação e arquitetura |
| `dataset` | Seleção, qualidade e representatividade dos dados de teste |

---

## Perguntas Abertas — Índice Rápido

| ID | Título | Categoria | Prioridade |
|----|--------|-----------|-----------|
| [Q-001](open/Q-001_novidade-hilbert-modelo-contexto.md) | Novidade: Hilbert como modelo de contexto probabilístico | novidade | critica |
| [Q-002](open/Q-002_datasets-canonicos-benchmark.md) | Seleção de datasets canônicos para benchmark | dataset | alta |
| [Q-003](open/Q-003_hilbert-vs-raster-dados-2d-reais.md) | Hilbert reduz entropia em dados 2D espaciais reais? | empirico | critica |
| [Q-004](open/Q-004_selecao-adaptativa-topologia-dimensao.md) | Seleção adaptativa de topologia × dimensão é efetiva? | empirico | alta |
| [Q-005](open/Q-005_smoothing-alpha-otimizacao.md) | Parâmetro α de suavização afeta os resultados? | empirico | media |
| [Q-006](open/Q-006_ordem-modelo-contexto.md) | Modelo de contexto de ordem >1 melhora discriminação? | empirico | media |
| [Q-007](open/Q-007_pipeline-completo-vs-compressores.md) | Pipeline completo Hilbert→BWT→MTF→RLE→Entropia bate referências? | empirico | alta |
| [Q-008](open/Q-008_framework-perspectivas-feature-space.md) | Framework HSC cobre quais perspectivas de feature space? | metodologia | alta |
| [Q-009](open/Q-009_indice-invertido-bitmask-hilbert.md) | Índice invertido bitmask + Hilbert clustering é efetivo? | empirico | alta |
| [Q-010](open/Q-010_compressao-por-dobragem-xor-simetria.md) | Framework de alinhamento aproximado elástico (fold-XOR) generaliza LZ? | novidade | critica |
| [Q-011](open/Q-011_homeomorfismo-topologico-como-compressao.md) | Compressão como homeomorfismo φ: C → D — arquivo é a função, não o dado | novidade | critica |
| [Q-012](open/Q-012_algebra-fuzzy-residuos-continuos.md) | Álgebra fuzzy melhora compressão de resíduos de dados de origem contínua? | empirico | alta |
| [Q-013](open/Q-013_substrate-independence-compressao-abstrata.md) | Framework é formulável como compressão independente de substrato? | novidade | alta |
| [Q-014](open/Q-014_arquivo-autopoietico-auto-descritivo.md) | Design do arquivo auto-descritivo (autopoiético) que carrega φ + decoder | design | alta |

## Perguntas Respondidas — Índice Rápido

| ID | Título | Categoria | Concluído |
|----|--------|-----------|-----------|
| [A-001](answered/A-001_texto-sequencial-raster-supera-espacial.md) | Texto sequencial favorece ordenamento raster | empirico | 2026-03-29 |
| [A-002](answered/A-002_dados-2d-sinteticos-favorecem-hilbert-morton.md) | Dados 2D sintéticos favorecem Hilbert/Morton vs raster | empirico | 2026-03-29 |
| [A-003](answered/A-003_prototipo-5-pipelines-funcional.md) | Protótipo implementa corretamente os 5 pipelines | design | 2026-03-29 |
