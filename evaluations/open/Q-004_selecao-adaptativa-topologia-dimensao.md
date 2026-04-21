---
id: Q-004
titulo: Seleção adaptativa de topologia × dimensão é estatisticamente efetiva?
categoria: empirico
prioridade: alta
criado: 2026-04-01
relacionado: [Q-002, Q-003, Q-006]
---

## Pergunta

O pipeline E (busca exaustiva de topologia × dimensão por mínimo de model_bps)
seleciona consistentemente a topologia correta para cada tipo de dado, e a melhoria
sobre a topologia fixa é estatisticamente significativa?

---

## Contexto

O protótipo já implementa dois níveis de seleção adaptativa:

- **Pipeline D:** Hilbert fixo + busca de side ótimo (minimiza model_bps)
- **Pipeline E:** Busca exaustiva de topologia {raster, Morton, Hilbert} × side → mínimo global

Os primeiros testes mostraram:
- Texto (`pt-br.tsv`): E seleciona raster — correto
- Sintético 2D: E seleciona Morton ou Hilbert — correto

**Pergunta em aberto:** Essa seleção é *estatisticamente confiável* quando aplicada
a dados reais variados? O ganho de E sobre ABC-melhor justifica o custo computacional?

---

## Hipótese

**H1:** Para dados com tipo bem definido (puro texto vs. pura imagem), E seleciona
a topologia correta em >90% dos casos.

**H2:** O delta entre E e ABC-melhor (gap de adaptação) é ≥ 3% em model_bps para
dados com correlação espacial 2D.

**H3:** O custo computacional de E (O(topologias × sides)) é aceitável para protótipo
mas impraticável para produção — justificando a necessidade de heurística de seleção rápida.

---

## Desenho Experimental

### Variáveis

| Variável | Valores |
|----------|---------|
| Topologias | {raster, Morton, Hilbert} |
| Side candidates | {512, 1024, 2048} |
| Métrica de seleção | min(model_bps) |
| Métrica de validação | zlib_ratio, model_bps, Δ% vs ABC-melhor |

### Datasets de Validação

Para cada estrato definido em Q-002:

| Estrato | Dataset | Topologia esperada pelo E |
|---------|---------|--------------------------|
| Texto 1D | `dickens`, `alice29.txt` | raster |
| Imagem 2D | `mr`, `x-ray`, `pic` | Hilbert ou Morton |
| Código | `progc`, `samba` | raster ou Morton |
| Estruturado | `osdb`, `xml` | incerto |
| Genômico | `e.coli` | incerto |

### Protocolo

1. Executar pipeline E em cada dataset
2. Registrar: topologia selecionada, side selecionado, model_bps do E, model_bps do melhor A/B/C
3. Calcular gap = (model_bps_ABC_melhor - model_bps_E) / model_bps_ABC_melhor × 100
4. Verificar se a topologia selecionada coincide com a expectativa por tipo

### Análise Adicional

- Plotar model_bps × side para cada topologia em cada dataset (visualizar landscape)
- Identificar se o mínimo é bem definido ou flat (indica insensibilidade)
- Verificar se Morton e Hilbert se comportam similarmente (caso de troca sem custo)

---

## Questão de Custo Computacional

Para cada dataset, medir:
- Tempo de cálculo da ordem Hilbert (side=1024: 1M pontos)
- Tempo de cálculo da ordem Morton (mesmo)
- Tempo de cálculo da entropia de modelo
- Tempo total do pipeline E vs pipeline A (overhead %)

**Threshold de aceitabilidade:** E não deve levar >10× o tempo de A para protótipo.
Para produção (Rust/GPU), o custo pode ser amortizado ou paralelizado.

---

## Critério de Conclusão

- **Confirmação de H1:** E seleciona topologia correta em ≥ 5 dos 6 datasets esperados
- **Confirmação de H2:** Gap ≥ 3% em pelo menos 2 datasets do estrato 2D
- **Evidência para H3:** Tempo E / Tempo A medido e documentado

Migrar para A-004 após completar testes em Silesia completo + sintéticos.
