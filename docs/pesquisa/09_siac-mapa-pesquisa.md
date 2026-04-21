---
name: SIAC - Mapa de Pesquisa
description: Documentação do processo SIAC (Scientific Iterative Adversarial Convergence) aplicado à pesquisa sobre compressão usando curvas de Hilbert como modelo de contexto probabilístico
type: siac-framework
---

# SIAC — Mapa de Pesquisa: Compressão via Curvas de Hilbert

## Metadados da Sessão

| Atributo | Valor |
|----------|-------|
| **Modo** | A (Escrita do Zero) |
| **Fase Atual** | F1 — Planejamento (S1 em execução) |
| **Status** | S1 iniciada com triagem bibliográfica preliminar |
| **Data Início** | 2026-03-29 |

---

## Mapa das 10 Perguntas com Hierarquia Editorial

### 🔴 Críticas (bloqueiam avanço se não resolvidas)

| # | Pergunta | Status | Descrição |
|-|-|-|-|
| **1** | Qual a contribuição e o que traz de novo em relação ao que já foi feito? | ⚠️ **Lacuna Crítica** | Framework usa Hilbert como modelo de contexto probabilístico (análogo a Markov), não apenas reordenação. Seleção automática de dimensão ótima. Lossy/lossless unificado via tolerância ao erro. **CARECE de busca sistemática de literatura.** |
| **2** | Que metodologia foi adotada para conduzir o trabalho? | ✅ Coletado | Experimental — implementação modular (Python/Torch piloto → Rust/GPU produção). Piloto com texto 2D. Comparação contra corpus consagrados (e.g. Calgary/Canterbury/Silesia). Baselines: compressores existentes. |
| **3** | Qual o problema específico abordado? | ✅ Coletado | Em quais dimensões/ordens curvas de Hilbert funcionam eficazmente como modelo de contexto para compressão? Como selecionar automaticamente o espaço ótimo? |
| **4** | Quais as conclusões obtidas? | ✅ Coletado | Objetivo primário: prova de conceito — demonstrar viabilidade do framework. Superar compressores existentes seria resultado extraordinário (não esperado como objetivo primário). |

### 🟡 Importantes (degradam qualidade se não resolvidas)

| # | Pergunta | Status | Descrição |
|-|-|-|-|
| **5** | Quais trabalhos anteriores trataram desse tema? | ⚠️ **Lacuna** | Docs cobrem Hilbert como reordenação espacial antes de compressão. Não cobrem uso de Hilbert como modelo de contexto probabilístico. **Busca sistemática obrigatória em F1.** |
| **6** | Por que o tema é relevante? | ✅ Coletado | Framework agnóstico de compressão (qualquer tipo de dado). Unificação lossy/lossless dentro de um único paradigma. Aplicabilidade em áudio, vídeo, texto, dados estruturados. Controle fino via tolerância ao erro. |
| **7** | Quais as limitações da metodologia e do trabalho? | ✅ Coletado | Custo computacional da busca automática de dimensão. Piloto inicial restrito a 2D/texto como prova de conceito. |

### 🟢 Contextuais (preenchem quadro geral)

| # | Pergunta | Status | Descrição |
|-|-|-|-|
| **8** | Qual o tema? | ✅ Coletado | Compressão de dados usando curvas de Hilbert como modelo de contexto probabilístico para estimação de probabilidades de transição entre símbolos. |
| **9** | Qual a direção para trabalhos futuros? | ✅ Coletado | Extensão para dados não-textuais (imagens, volumes). Exploração de dimensões maiores (3D, nD). Otimização e implementação em Rust/GPU. Comparação com wavelets, DCT e outros modelos de contexto. |

---

## Síntese do Escopo

**O que o trabalho FAZ:**
- Propõe um framework de compressão baseado em curvas de Hilbert como modelo de contexto
- Implementa busca automática por dimensão/espaço ótimo
- Unifica lossy/lossless via controle de tolerância ao erro
- Valida com piloto em texto 2D contra corpus consagrados

**O que o trabalho NÃO FAZ (deliberadamente):**
- Não otimiza para performance em produção (fase piloto é funcionalidade primeiro)
- Não compara contra todos os compressores existentes (seleção de baselines)
- Não aborda dimensões > 2 na validação inicial (escopo de futuros)

---

## Lacunas Críticas Identificadas

### 🔴 Lacuna 1: Novidade não verificada (Q1)
**Problema:** Afirmação de que nenhum trabalho usa Hilbert como modelo de contexto probabilístico não foi confirmada por busca sistemática.

**Por quê importa:** Define se a contribuição é realmente inédita ou reinvenção.

**Ação necessária:** Em F1, antes de avançar para crítica, realizar busca em:
- IEEE Xplore (compression, Hilbert curve, context modeling)
- ACM Digital Library (data compression, space-filling curves)
- arXiv (cs.IT, cs.MM)
- Google Scholar (Hilbert curve compression, probabilistic modeling)

**Queries sugeridas:**
- "Hilbert curve" + "context model" + compression
- "space-filling curve" + "entropy coding" + context
- "Hilbert" + "Markov" + compression
- "multidimensional" + "compression" + probability

### Resultado parcial da S1 (triagem inicial)

**Critério aplicado nesta rodada:** identificar trabalhos com Hilbert/space-filling curves aplicados a compressão, separando uso como reordenação (scan/ordering) de uso como modelagem probabilística de contexto.

**Shortlist de alta relevância (preliminar):**
- 2021 — *Modified Hilbert Curve for Rectangles and Cuboids and Its Application in Entropy Coding for Image and Video Compression* — DOI: 10.3390/e23070836
- 2011 — *Image Coder Based on Hilbert Scanning of Embedded QuadTrees* — DOI: 10.1109/dcc.2011.74
- 2000 — *Hilbert scan and image compression* — DOI: 10.1109/icpr.2000.903522
- 1998 — *Color image compression using a Hilbert scan* — DOI: 10.1109/icpr.1998.712012
- 1996 — *A gray image compression using a Hilbert scan* — DOI: 10.1109/icpr.1996.547299
- 2007 — *Lossless compression of medical images using Hilbert scan* — DOI: 10.1117/12.747119
- 2015 — *Genome Compression based on Hilbert Space Filling Curve* — DOI: 10.2991/meici-15.2015.294
- 2016 — *Region of Interest Based MRI Brain Image Compression Using Peano Space Filling Curve* — DOI: 10.2174/1574362411666160616124516

**Sinal técnico observado:** predominam abordagens com Hilbert como estratégia de varredura/reordenação para favorecer etapas posteriores (entropia, VQ, etc.). Nesta rodada inicial, não foi identificado trabalho claramente centrado em Hilbert como modelo probabilístico de contexto generalista.

**Limitação da rodada:** cobertura ainda parcial (sem varredura completa em IEEE Xplore/ACM DL/Scopus com protocolo fechado de exclusão por texto completo).

**Implicação para desenvolvimento imediato:** seguir para protótipo comparativo sem esperar fechamento total da revisão, mantendo a Q1 como lacuna crítica aberta até S1 completa.

### 🟡 Lacuna 2: Categoria indefinida
**Problema:** Tipo do artigo ainda não foi explicitamente registrado.

**Candidatos:**
- Proposta de método (framework novo)
- Híbrido (proposta + validação empírica)

**Ação necessária:** Antes do Gate, usuário confirma categoria.

### 🟡 Lacuna 3: Venue não definido
**Problema:** Periódico ou conferência alvo ainda não escolhidos.

**Por quê importa:** Afeta critérios de aceitação em F2 (dimensões de adequação editorial).

**Ação necessária:** Em F1, durante planejamento.

---

## Próximas Fases

### Imediatamente (antes de Gate de Entendimento)
- [ ] Usuário confirma categoria do artigo
- [ ] Gate: "Esse mapa representa o trabalho? O que fica de fora?"

### F1 — Planejamento
- [ ] Definir venue (periódico ou conferência)
- [ ] Registrar output desejado: (a) rascunho completo, (b) esqueleto + lacunas, (c) roteiro de escrita, ou (d) lista cirúrgica de revisões
- [~] **Busca sistemática de literatura** (lacuna Q1/Q5) — triagem inicial concluída; falta fechamento por protocolo completo
- [ ] Confirmar critérios de aceite

### Sprint de desenvolvimento (paralelo à S1)
- [x] Implementar baseline A: raster + backend entrópico
- [x] Implementar baseline B: Morton + mesmo backend
- [x] Implementar baseline C: Hilbert + mesmo backend
- [x] Implementar proposta D: Hilbert + modelo de contexto probabilístico (protótipo simplificado)
- [x] Rodar benchmark mínimo: taxa, bps, tempo de encode/decode e memória

### Resultado inicial da sprint (protótipo)

**Artefato:** `prototype/compare_orders.py`

**Cenário 1 — texto do workspace (sequencial):**
- A_raster superou B_morton e C_hilbert em `zlib_ratio` e `model_bps`.
- Interpretação: em dados originalmente sequenciais (texto markdown), impor vizinhança 2D por SFC tende a degradar contexto útil.

**Cenário 2 — sintético espacial 2D (correlação local):**
- B_morton e C_hilbert superaram A_raster.
- Interpretação: quando há estrutura espacial local, ordem por curva melhora compressibilidade relativa.

**Leitura para a hipótese:**
- A vantagem de Hilbert/Morton é condicional ao tipo de dado e à topologia subjacente.
- O próximo ciclo deve focar na seleção automática de topologia/dimensão por classe de dado, não em uma única ordem fixa.

**Extensão implementada no protótipo (E):**
- Busca automática entre topologias {raster, Morton, Hilbert} e tamanhos de malha por menor `model_bps`.
- Resultado observado:
	- Texto do workspace: melhor topologia = raster.
	- Dataset sintético espacial 2D: melhor topologia = Morton.
- Implicação metodológica: a hipótese de generalização para outras topologias é suportada no nível de prova de conceito inicial.

### F2 — Crítica Adversarial
- [ ] Aplicar dimensões universais: validade interna, novidade verificável, coerência, consistência, limitações, cobertura de estado da arte, premissas silenciosas, viés de confirmação, força de evidências, integridade documental, ética, estilo
- [ ] Aplicar dimensões condicionais (baseado em categoria confirmada)
- [ ] Classificar achados: 🔴 bloqueante, 🟡 degradante, 🟢 opcional

### F3 — Revisão do Plano
- [ ] Integrar achados de F2
- [ ] Dispor cada achado: resolvido, declarável aceito, incorporado, postergado, ou descartado
- [ ] Atualizar SIAC-log
- [ ] Decidir: mais uma rodada F2–F3 ou avançar para execução?

### F4 — Execução
- [ ] Produzir output conforme definido em F1
- [ ] Para Modo A: rascunho respeitando hierarquia 🔴 primeiro
- [ ] Marcar lacunas que permanecem abertas
- [ ] Encerrar sem adicionar escopo

---

## Decisões Tomadas

| Decisão | Justificativa | Data |
|---------|---------------|------|
| Modo A (escrita do zero) | Pesquisa existe mas não há rascunho de artigo | 2026-03-29 |
| Piloto 2D/texto | Prova de conceito antes de dimensões maiores | 2026-03-29 |
| Corpus consagrado | Comparabilidade com trabalhos existentes | 2026-03-29 |
| Arquitetura modular Python→Rust | Performance progressiva, não bloqueio de conceito | 2026-03-29 |

---

## Notas de Contexto

**Expertise do usuário:**
- Compressão de dados (vários anos)
- Matemática multidimensional (áudio/vídeo)
- Implementação de sistemas (Python, Rust, GPU)

**Insight central:**
Hilbert curves já são conhecidas para reordenação espacial. A novidade proposta é usá-las como **modelo de contexto dinâmico** (análogo a cadeias de Markov) para estimação de probabilidades, permitindo seleção automática de dimensão e controle unificado lossy/lossless.

**Risco principal:**
Se a busca de literatura em F1 encontrar trabalho anterior cobrindo essa exata ideia, a 🔴 Q1 muda de "novidade inédita" para "refinamento de abordagem existente" — ajuste de escopo necessário.

---

## Controle de Avaliações (evaluations/)

O diretório `evaluations/` centraliza hipóteses e conclusões em formato Q&A científico:

```
evaluations/
├── open/      ← perguntas em aberto (hipóteses, planos de teste)
└── answered/  ← conclusões com evidência documentada
```

| ID | Título | Status |
|----|--------|--------|
| [Q-001](../../evaluations/open/Q-001_novidade-hilbert-modelo-contexto.md) | Novidade: Hilbert como modelo de contexto probabilístico | 🔴 Aberta |
| [Q-002](../../evaluations/open/Q-002_datasets-canonicos-benchmark.md) | Seleção de datasets canônicos para benchmark | 🟡 Aberta |
| [Q-003](../../evaluations/open/Q-003_hilbert-vs-raster-dados-2d-reais.md) | Hilbert reduz entropia em dados 2D espaciais reais? | 🔴 Aberta |
| [Q-004](../../evaluations/open/Q-004_selecao-adaptativa-topologia-dimensao.md) | Seleção adaptativa de topologia × dimensão é efetiva? | 🟡 Aberta |
| [Q-005](../../evaluations/open/Q-005_smoothing-alpha-otimizacao.md) | Parâmetro α de suavização afeta os resultados? | 🟢 Aberta |
| [Q-006](../../evaluations/open/Q-006_ordem-modelo-contexto.md) | Modelo de contexto de ordem >1 melhora discriminação? | 🟢 Aberta |
| [Q-007](../../evaluations/open/Q-007_pipeline-completo-vs-compressores.md) | Pipeline completo bate compressores de referência? | 🟡 Aberta |
| [A-001](../../evaluations/answered/A-001_texto-sequencial-raster-supera-espacial.md) | Texto sequencial favorece raster | ✅ Respondida |
| [A-002](../../evaluations/answered/A-002_dados-2d-sinteticos-favorecem-hilbert-morton.md) | Dados 2D sintéticos favorecem Hilbert/Morton | ✅ Respondida |
| [A-003](../../evaluations/answered/A-003_prototipo-5-pipelines-funcional.md) | Protótipo 5 pipelines está funcional | ✅ Respondida |

---

**Próximo passo:** Confirmar categoria e Gate de Entendimento.
