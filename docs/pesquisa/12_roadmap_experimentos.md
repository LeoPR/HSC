# 12 — Roadmap de Experimentos: Caminho Feliz para Publicação

## Diagnóstico: Onde Estamos

### O que temos

| Artefato | Estado | Valor |
|----------|--------|-------|
| Protótipo funcional (5 pipelines A-E) | ✅ Validado | Mede model_bps e zlib_ratio por topologia |
| Modelo de entropia adaptativo ordem-1 | ✅ Correto | Proxy teórico para qualidade de contexto |
| Resultado A-001: texto → raster ganha | ✅ Confirmado | Controle negativo válido |
| Resultado A-002: sintético 2D → Hilbert ganha | ✅ Confirmado | Prova de princípio |
| 11 docs de pesquisa + framework teórico | ✅ Denso | Cobre SFC, fuzzy, topologia, INR, AIT |
| 14 perguntas abertas (Q-001 a Q-014) | ⚠️ Muitas | Precisam de priorização |
| Sistema de evaluations Q&A | ✅ Operacional | Rastreamento científico formal |

### O que falta

| Lacuna | Bloqueio | Criticidade |
|--------|----------|-------------|
| **Datasets canônicos** | Nenhum arquivo Silesia/Calgary baixado | 🔴 Bloqueia tudo |
| **Teste em dados 2D reais** | Q-003 não testada | 🔴 Hipótese central |
| **Busca bibliográfica completa** | Q-001 parcial | 🔴 Novidade não verificada |
| **Nenhuma implementação nova** desde o protótipo | Código parado em compare_orders.py | 🟡 |

### O problema de escopo

Temos 14 perguntas abertas, 4 delas teóricas profundas (Q-010 a Q-013), e nenhum
resultado experimental novo desde o protótipo inicial. O risco é **divergir na teoria
sem convergir nos dados**.

---

## Decisão de Escopo: O Que Entra no Paper

### Opção A — Paper de Framework Teórico
Publicar Q-010/Q-011 como contribuição teórica (compressão como homeomorfismo).
**Problema:** Sem validação empírica, difícil de publicar em venue de compressão.

### Opção B — Paper Empírico Focado ✅ RECOMENDADO
Publicar resultados empíricos de Hilbert vs. topologias em datasets canônicos,
com contribuição de seleção adaptativa de topologia/dimensão.
**Vantagem:** Dados concretos, reproduzíveis, comparáveis com literatura.

### Opção C — Paper Híbrido (Método + Validação)
Framework de compressão via feature-space + validação em Silesia/Canterbury.
**Risco:** Escopo grande, mais tempo, mas paper mais impactante.

**Recomendação:** Começar com **Opção B**, com framework teórico (docs 10-11)
como motivação na introdução e Q-010/Q-011 como trabalho futuro. Se os resultados
forem fortes, expandir para C.

---

## Ciclos de Experimento: 4 Sprints

### Sprint 0 — Infraestrutura (1-2 dias)

**Objetivo:** Ter tudo no lugar para rodar experimentos.

**Tarefas:**
1. **Baixar datasets** (prioridade absoluta):
   - Silesia: `mr` (MRI), `x-ray`, `dickens`
   - Calgary: `pic` (fax bitmap)
   - Canterbury: `alice29.txt`, `ptt5`
   - Colocar em `datasets/silesia/`, `datasets/calgary/`, `datasets/canterbury/`

2. **Gerar dados sintéticos controlados** (novo módulo):
   ```
   prototype/data/synthetic.py
     generate_2d_gaussian_blobs(side, n_blobs, sigma) → bytes
     generate_2d_gradient(side) → bytes
     generate_2d_noise(side) → bytes
     generate_1d_walk(length) → bytes
   ```

3. **Adicionar saída CSV** ao compare_orders.py:
   ```
   --csv results.csv   →   salva resultados em CSV para análise
   ```
   Permitir rodar batch de datasets e consolidar.

4. **Script de batch** para rodar todos os datasets:
   ```
   prototype/run_benchmark.py
     Para cada arquivo em datasets/*:
       Rodar pipelines A/B/C/D/E
       Salvar em results/benchmark_YYYYMMDD.csv
   ```

**Entrega:** `python prototype/run_benchmark.py` roda e gera CSV com todos os resultados.

---

### Sprint 1 — Hipótese Central (2-3 dias)

**Objetivo:** Responder Q-003 (Hilbert reduz entropia em dados 2D reais?).

**Tarefas:**
1. Rodar pipelines A/B/C em `mr`, `x-ray`, `pic`, `ptt5` (imagens 2D)
2. Rodar pipelines A/B/C em `dickens`, `alice29.txt` (texto — controle negativo)
3. Rodar em dados sintéticos (blobs, gradient, noise — controles)
4. Pipeline E em todos os datasets
5. Documentar resultados em tabela:

```
| Dataset     | Tipo | A_raster_bps | B_morton_bps | C_hilbert_bps | E_melhor | Δ(C-A)% |
|-------------|------|-------------|-------------|--------------|----------|---------|
| mr          | 2D   | ?           | ?           | ?            | ?        | ?       |
| x-ray       | 2D   | ?           | ?           | ?            | ?        | ?       |
| pic         | 2D   | ?           | ?           | ?            | ?        | ?       |
| dickens     | 1D   | ?           | ?           | ?            | ?        | ?       |
| alice29.txt | 1D   | ?           | ?           | ?            | ?        | ?       |
| synth_blobs | 2D   | ?           | ?           | ?            | ?        | ?       |
| synth_noise | 2D   | ?           | ?           | ?            | ?        | ?       |
```

6. **Fechar Q-003:** Hilbert é melhor que raster em ≥ 3 datasets 2D reais? Sim → A-003. Não → rever hipótese.
7. **Fechar Q-004:** Pipeline E seleciona topologia correta por tipo? Documentar.

**Entrega:** Tabela completa. Q-003 e Q-004 respondidas. Decisão: seguir ou pivotar.

---

### Sprint 2 — Aprofundamento do Modelo (2-3 dias)

**Objetivo:** Medir sensibilidade do modelo e testar o mecanismo de dobragem.

**Tarefas:**

**2a — Ablação de α (Q-005):**
```python
# prototype/experiments/alpha_ablation.py
alphas = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0]
Para cada dataset × cada alpha:
    Rodar A/B/C
    Registrar ranking de topologias
Resultado: o ranking muda com α?
```

**2b — Modelo de contexto ordem-2 (Q-006):**
```python
# prototype/metrics/entropy.py — adicionar
def adaptive_order2_bits(seq: bytes, alpha: float = 1.0) -> float:
    """Contexto P(s_t | s_{t-2}, s_{t-1}) — sparse dict."""
    ctx = {}  # (prev2, prev1) → Counter
    ...
```
Medir: o gap Hilbert-raster aumenta com ordem 2? Se sim, Hilbert está
capturando mais estrutura do que ordem 1 revela.

**2c — Contagem de runs por símbolo (Q-009 parcial):**
```python
# prototype/experiments/run_count.py
def count_symbol_runs(seq: bytes) -> dict[int, int]:
    """Para cada byte-value, conta quantos runs contíguos ele forma."""
Para cada dataset × topologia:
    Registrar: run_count_medio, run_count_max
Resultado: Hilbert reduz o número de runs em dados 2D?
```
Isso testa a pré-condição do índice invertido (Q-009) sem implementar
o codec completo.

**2d — XOR-fold básico (Q-010 parcial):**
```python
# prototype/experiments/fold_xor.py
def fold_and_measure(seq: bytes, k: int) -> tuple[int, float]:
    """Dobra seq em offset k, retorna (n_runs_xor, sparsity)."""
    a = seq[:k]
    b = seq[k:2*k]
    diff = bytes(x ^ y for x, y in zip(a, b))
    # contar runs no diff, medir esparsidade (% zeros)
    return n_runs, sparsity

Para cada dataset, variar k em potências de 2:
    Registrar: melhor_k, sparsity, n_runs
```
Isso é o **primeiro teste empírico da ideia de dobragem** — sem codec,
só medição. Verifica H2 (XOR esparso com Hilbert) de forma barata.

**Entrega:** Q-005, Q-006 respondidas. Dados de run-count e fold-XOR coletados.
Decisão: quais extensões valem a pena implementar como codec.

---

### Sprint 3 — Pipeline Completo + Comparação (3-5 dias)

**Objetivo:** Ter um compressor funcional e compará-lo com referências.

**Tarefas:**

**3a — Implementar BWT+MTF+RLE (Q-007):**
```
prototype/transforms/bwt.py      # Burrows-Wheeler Transform
prototype/transforms/mtf.py      # Move-to-Front
prototype/transforms/rle.py      # Run-Length Encoding
prototype/pipeline.py            # Orquestrador: reorder → BWT → MTF → RLE → entropia
```

**3b — Benchmark contra referências:**
```
Para cada dataset:
  bzip2 -9
  gzip -9
  xz -9 (LZMA)
  zstd -19
  HSC pipeline: Hilbert → BWT → MTF → RLE → aritmético
```

Métricas: razão de compressão, tempo encode, tempo decode.

**3c — Tabela comparativa final:**
```
| Dataset | bzip2  | gzip   | xz     | zstd   | HSC (raster) | HSC (hilbert) | Δ(hilbert-bzip2) |
|---------|--------|--------|--------|--------|-------------|--------------|------------------|
| mr      | ?      | ?      | ?      | ?      | ?           | ?            | ?                |
```

**Entrega:** Tabela publicável. Q-007 respondida. Material para seção de resultados.

---

## Mapa de Dependências

```
Sprint 0 ─────────────┐
  └─ datasets          │
  └─ synthetic.py      │
  └─ csv output        │
  └─ run_benchmark.py  │
                       ▼
Sprint 1 ─────────────────────────┐
  └─ Q-003 (Hilbert 2D real)      │
  └─ Q-004 (seleção adaptativa)   │
                                   ▼
Sprint 2 ──────────────────────────────────────┐
  ├─ Q-005 (ablação α)                         │
  ├─ Q-006 (ordem 2)                           │
  ├─ Q-009 parcial (contagem de runs)          │
  └─ Q-010 parcial (fold-XOR medição)          │
                                                ▼
Sprint 3 ──────────────────────────────────────────────┐
  ├─ Q-007 (pipeline BWT completo)                      │
  └─ Comparação com bzip2/gzip/xz/zstd                  │
                                                          ▼
                                                     PAPER
```

---

## Estrutura do Paper (Projetada)

### Se Opção B (Empírico Focado)

```
1. Introdução
   - Compressão depende da ordem de leitura dos dados
   - Curvas de Hilbert preservam localidade → hipótese: melhoram compressão
   - Contribuição: seleção adaptativa de topologia × dimensão

2. Trabalhos Relacionados
   - SFC em compressão (8 papers do S1 + completar busca Q-001)
   - BWT, MTF, RLE, codificação entrópica
   - Context mixing (motivação para perspectiva multi-modelo)

3. Método
   - 3.1 Framework: reordenação por curva como modelo de contexto
   - 3.2 Topologias testadas: raster, Morton, Hilbert
   - 3.3 Métricas: model_bps (teórica) + zlib/bzip2 (prática)
   - 3.4 Seleção adaptativa de topologia × dimensão (pipeline E)
   - 3.5 Pipeline completo: Hilbert → BWT → MTF → RLE → Entropia

4. Experimentos
   - 4.1 Datasets (Silesia, Calgary, Canterbury, sintéticos)
   - 4.2 Resultados A/B/C por estrato (texto, código, imagem, estruturado)
   - 4.3 Seleção adaptativa (pipeline D/E)
   - 4.4 Sensibilidade do modelo (α, ordem do contexto)
   - 4.5 Comparação com compressores de referência
   - 4.6 Análise de runs e XOR-fold (evidência para trabalho futuro)

5. Discussão
   - Quando Hilbert ajuda e quando não ajuda
   - O papel do tipo de dado na escolha de topologia
   - Custo computacional vs. ganho de compressão

6. Trabalho Futuro
   - Framework funcional topológico (doc 11, Q-011)
   - Dobragem elástica aproximada (Q-010)
   - Fuzzy residuals para dados contínuos (Q-012)
   - Independência de substrato (Q-013)

7. Conclusão
```

### Se Opção C (Híbrido — caso resultados fortes)

Expandir seções 3 e 4 com o framework teórico de docs 10-11, e incluir
experimentos de fold-XOR e run-count como evidência do framework mais amplo.

---

## Estimativa de Escopo por Sprint

| Sprint | Código novo | Linhas estimadas | Depende de |
|--------|------------|-----------------|-----------|
| 0 | synthetic.py, csv output, run_benchmark.py | ~150 | Downloads manuais |
| 1 | Nenhum (rodar o que já existe) | 0 | Sprint 0 |
| 2 | alpha_ablation.py, order2_bits, run_count.py, fold_xor.py | ~200 | Sprint 1 |
| 3 | bwt.py, mtf.py, rle.py, pipeline.py, compare_full.py | ~400 | Sprint 2 |

**Total de código novo: ~750 linhas Python.** Modesto, focado, testável.

---

## Critérios de Go/No-Go

### Após Sprint 1

| Resultado | Decisão |
|-----------|---------|
| Hilbert < raster em ≥ 3 datasets 2D com Δ ≥ 2% | ✅ Continuar para Sprint 2-3 |
| Hilbert ≈ raster (Δ < 1%) em todos os datasets 2D | ⚠️ Pivotar: testar ordem 2, fold-XOR; buscar onde Hilbert ajuda |
| Hilbert > raster em dados 2D (piora compressão) | 🔴 Parar e rever hipótese fundamental |

### Após Sprint 3

| Resultado | Decisão |
|-----------|---------|
| HSC pipeline comparável a bzip2 em ≥ 3 datasets | ✅ Paper viável (Opção B) |
| HSC pipeline supera bzip2 em ≥ 1 dataset | ✅ Paper forte (expandir para Opção C) |
| HSC pipeline sempre inferior a todos os baselines | ⚠️ Paper de análise negativa (ainda publicável se bem escrito) |

---

## O que NÃO fazer agora

1. ❌ Implementar SIREN/INR (Q-011) — trabalho futuro
2. ❌ Implementar compressão quântica (Q-013) — trabalho futuro
3. ❌ Implementar formato auto-descritivo (Q-014) — trabalho futuro
4. ❌ Implementar F-transform fuzzy (Q-012) — trabalho futuro (exceto se Sprint 2 sugerir)
5. ❌ Mais documentação teórica — temos 11 docs, suficiente
6. ❌ Buscar mais curves (Peano, Gosper) — Hilbert+Morton+raster são suficientes para o paper
