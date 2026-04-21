---
id: Q-008
titulo: O framework HSC explora todas as perspectivas de transformação de feature space?
categoria: metodologia
prioridade: alta
criado: 2026-04-02
relacionado: [Q-001, Q-003, Q-007]
---

## Pergunta

Das 6 perspectivas identificadas para transformação de feature space aplicada
à compressão, quais o HSC já cobre, quais pode incorporar, e quais são
fundamentalmente fora do escopo?

---

## Contexto

O documento `docs/pesquisa/10_transformacoes_de_espaco_para_compressao.md` identifica
6 perspectivas teóricas sobre como mudar o espaço de representação revela estrutura
compressível:

| # | Perspectiva | Descrição |
|---|-------------|-----------|
| P1 | Remapear para visualizar | SFC, recurrence plots, manifold learning |
| P2 | Mudar de base | DCT, DWT, PCA/KLT, BWT |
| P3 | Adaptação iterativa | Context mixing, codificação adaptativa, PPM |
| P4 | Remapear vocabulário | BPE, gramática, filtro de instrução, LZ |
| P5 | Dobrar o espaço | Embedding nD, Takens, busca multidirecional |
| P6 | Composição multi-perspectiva | Ensembles, context mixing, pipelines híbridos |

---

## Análise de Cobertura Atual do HSC

| Perspectiva | Cobertura | O que existe | O que falta |
|-------------|-----------|-------------|-------------|
| P1 | ✅ Parcial | Hilbert/Morton como SFC; raster como baseline | Peano, Moore, Gosper não testados; sem manifold learning |
| P2 | ❌ Ausente | Nenhuma transformada implementada | BWT planejado (Q-007) mas não implementado; DCT/DWT fora do escopo imediato |
| P3 | ✅ Parcial | Modelo contexto ordem-1 adaptativo; busca adaptativa de topologia (pipeline E) | Sem context mixing; sem PPM; ordem fixa 1 |
| P4 | ❌ Ausente | — | Sem tokenização pré-Hilbert; sem filtro de instrução; sem BPE |
| P5 | ✅ Parcial | Embedding 1D→2D via grade quadrada; busca de dimensão ótima | Sem embedding nD>2; sem Takens; sem análise direcional |
| P6 | ❌ Ausente | — | Sem composição de modelos; sem ensemble; sem context mixer |

**Diagnóstico:** O HSC cobre P1 e P5 parcialmente (curvas de Hilbert são simultaneamente
remapeamento espacial e "dobra" do espaço), e toca P3 (modelo adaptativo). As perspectivas
P2, P4, P6 estão ausentes — e P6 é potencialmente a mais impactante para a contribuição
do projeto.

---

## Hipótese

**H1:** A contribuição mais forte do HSC não é usar Hilbert isoladamente (P1+P5),
mas posicioná-lo como **um modelo de contexto espacial** dentro de um sistema
multi-perspectiva (P6).

**H2:** A integração de perspectivas P2 (BWT como pré-processamento simbólico)
com P1 (Hilbert como pré-processamento espacial) em cascata produz ganho aditivo.

**H3:** A perspectiva P4 (tokenização/vocabulário) antes de P1 (Hilbert) é
uma extensão natural que amplifica o modelo de contexto para dados simbólicos.

---

## Plano de Investigação

### Fase Imediata (dentro do escopo do paper)

1. **P1 expandido:** Testar Peano e Moore (além de Hilbert e Morton) para verificar se
   a família de curva importa ou se a propriedade genérica de localidade é suficiente.

2. **P2 básico (BWT):** Implementar pipeline B (Hilbert→BWT→MTF→RLE→Entropia) conforme
   Q-007. Isso adiciona a perspectiva de mudança de base simbólica.

3. **P3 expandido:** Implementar modelo de contexto de ordem 2 (Q-006) para medir
   se adaptação mais profunda amplifica o efeito do Hilbert.

### Fase Exploratória (trabalho futuro candidato)

4. **P4 (vocabulário):** Aplicar BPE sobre os bytes antes do Hilbert scan. Medir se
   tokens de vocabulário reduzido melhoram model_bps.

5. **P5 expandido:** Testar embedding 3D (Hilbert 3D) em dados volumétricos (MRI 3D).

6. **P6 (multi-perspectiva):** Prototipar um context mixer simples com 3 modelos:
   - Modelo 1: ordem-1 sobre percurso Hilbert (contexto espacial)
   - Modelo 2: ordem-1 sobre sequência original (contexto linear)
   - Modelo 3: ordem-1 sobre percurso BWT (contexto lexicográfico)
   - Mixer: média ponderada adaptativa

---

## O que Cada Perspectiva Contribui para o Paper

| Perspectiva | Contribuição para publicação | Prioridade |
|-------------|------------------------------|-----------|
| P1 | Resultado central: Hilbert melhora compressão em dados 2D | **Essencial** |
| P2 | Pipeline completo: Hilbert+BWT supera BWT sozinho? | Alta |
| P3 | Modelo adaptativo: seleção de topologia × dimensão | Alta |
| P4 | Extensão: vocabulário + Hilbert | Trabalho futuro |
| P5 | Generalização: nD Hilbert | Trabalho futuro |
| P6 | Extensão teórica: Hilbert em context mixer | Trabalho futuro (mas fortalece Q1) |

---

## Critério de Conclusão

- **Escopo do paper definido:** Quais perspectivas entram na publicação atual (P1+P2+P3)
  e quais ficam como contribuição futura (P4+P5+P6).
- **Q-009, Q-010, Q-011 criadas** para as extensões identificadas (se aprovado).
- **doc 10 revisado** com mapeamento explícito HSC→perspectivas.

Migrar para A-008 quando o escopo for decidido com o autor.
