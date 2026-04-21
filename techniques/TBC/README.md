# TBC — TuringBitCompression

## Visão geral

TBC é uma técnica de compressão lossless baseada em **codificação por camadas de presença**
(indicator-plane coding) ordenadas por frequência decrescente de símbolo.

A ideia central: dado um fluxo binário, em vez de codificar símbolo a símbolo, codifica-se
**onde cada símbolo ocorre** — um plano de indicadores por símbolo, do mais frequente ao menos
frequente. O último símbolo é implícito (resíduo): não precisa de plano próprio.

O processo é aplicado recursivamente sobre os planos resultantes até não haver mais ganho.

---

## Algoritmo (formulação informal)

**Entrada:** sequência binária `S` de comprimento `N`

**Passo 1 — Agrupamento em n-gramas**
Agrupa `S` em janelas de `k` bits (padrão `k=2`), produzindo sequência de símbolos com alfabeto de
tamanho `2^k`.

**Passo 2 — Ranking de frequência**
Ordena os símbolos por frequência descendente: `σ₁ ≥ σ₂ ≥ … ≥ σₘ`.

**Passo 3 — Codificação por planos**
Para cada símbolo `σᵢ` (exceto o último):
- Emite um **plano de indicadores** `Pᵢ` sobre as posições ainda não preenchidas
- `Pᵢ[j] = 1` se a posição `j` contém `σᵢ`; `0` se não (e portanto será preenchida por `σᵢ₊₁..ₘ`)

O último símbolo (`σₘ`) não precisa de plano: sua posição é o resíduo de todos os zeros
remanescentes.

**Passo 4 — Recursão**
Cada plano `Pᵢ` é tratado como nova sequência binária e o processo recomeça do Passo 1,
até que nenhum plano produza representação menor que si mesmo.

**Passo 5 — Cabeçalho**
O arquivo comprimido contém:
- Mapa de frequências (símbolo → código de ranking)
- Planos comprimidos em ordem
- Metadados para reversão

---

## Exemplo

```
raw_data: 10 01 10 01 10 01 01 01 01 01 01 01 01 11
          (14 símbolos de 2 bits = 28 bits)

Frequências:
  01 → 10×   (σ₁)
  10 → 3×    (σ₂)
  11 → 1×    (σ₃)
  00 → 0×    (σ₄, resíduo implícito)

Plano P₁ (onde σ₁=01 ocorre):
  posições: 1,3,5,7,8,9,10,11,12,13  → 0 1 0 1 0 1 1 1 1 1 1 0 1 1   [10 bits compressíveis]

Plano P₂ (onde σ₂=10 ocorre, nos zeros restantes de P₁):
  posições restantes: 0,2,4,13 → 1 1 1 0   [4 bits]

Plano P₃ (onde σ₃=11 ocorre, nos zeros restantes de P₂):
  1 bit (única ocorrência de 11)

Resíduo (σ₄=00): posições remanescentes — 0 ocorrências, nada a armazenar.
```

---

## Estado atual

| Artefato | Status |
|---|---|
| Descrição informal da lógica | ✅ `compression_logic_03.md` |
| Implementação Python | ❌ não iniciada |
| Prova de corretude (losslessness) | ❌ pendente |
| Análise de complexidade | ❌ pendente |
| Benchmark vs. baselines | ❌ pendente |

---

## Conexão com literatura

A técnica é relacionada mas distinta de:

| Técnica | Relação |
|---|---|
| **Bitplane coding** (JBIG/JBIG2) | Decomposição por plano de bits — TBC usa planos por símbolo ordenados por frequência |
| **Symbol ranking** (Bentley et al. 1986; Ryabko 1987) | Rank dinâmico do vocabulário — TBC usa ranking estático por frequência global |
| **Move-to-Front (MTF)** | Reordena vocabulário por recência; análogo mas dinâmico |
| **BWT + MTF** | MTF produz bitmasks de posições, estrutura similar ao Passo 3 do TBC |
| **PPM / PAQ** | Modelos de contexto adaptativos — abordagem ortogonal |

Diferencial específico do TBC: **planos por símbolo em ranking de frequência global + recursão sobre os planos**. Não foi identificado equivalente direto na literatura.

---

## Referências

- Bentley, J.L. et al. (1986). *A locally adaptive data compression scheme*. CACM, 29(4).
- Ryabko, B.Y. (1987). *Data compression by means of a book stack*. Problems of Information Transmission.
- Witten, I., Neal, R., Cleary, J. (1987). *Arithmetic coding for data compression*. CACM, 30(6).
- Seong, S.W., Mishra, P. (2008). *Bitmask-based code compression for embedded systems*. ICCAD.
