---
id: A-001
titulo: Texto sequencial favorece ordenamento raster sobre Hilbert/Morton
categoria: empirico
prioridade: alta
criado: 2026-03-29
concluido: 2026-03-29
---

## Pergunta Original

Impor ordenamento 2D (Hilbert ou Morton) em dados intrinsecamente sequenciais (texto)
degrada a eficiência do modelo de contexto de ordem 1 em comparação com o raster?

---

## Resposta

**Sim.** Para dados sequenciais 1D, o ordenamento raster (leitura linha-a-linha) preserva
melhor o contexto local do que Hilbert ou Morton. Ambas as curvas de preenchimento de
espaço degradam o model_bps em texto sequencial.

---

## Evidências

### Experimento 1 — `datasets/pt-br.tsv` (dicionário fonético PT-BR, 3.7 MB)

Resultado observado no pipeline A/B/C executado sobre pt-br.tsv:

| Topologia | Métrica | Resultado relativo |
|-----------|---------|-------------------|
| A — Raster | model_bps | **melhor** |
| B — Morton | model_bps | > raster |
| C — Hilbert | model_bps | > raster (pior das três) |

*Interpretação:* O arquivo é uma sequência de pares `palavra\tIPA\n`. A leitura
linha-a-linha (raster) mantém a continuidade natural do texto. Reordenar via Hilbert
divide a sequência em uma grade 2D fictícia e percorre em padrão de curva — destruindo
a correlação natural entre caracteres consecutivos no texto.

### Experimento 2 — Dataset sintético 1D (passeio aleatório 1D → grade)

Confirmação independente: dados gerados como sequência 1D com correlação local também
mostram raster superior a Morton e Hilbert, pois a correlação existe ao longo do índice
linear, não em vizinhança 2D.

### Mecanismo Explicativo

```
Texto 1D: correlação P(s_t | s_{t-1}) é alta ao longo do eixo linear
Hilbert: percorre posições (x,y) na grade de forma a preservar vizinhos 2D
         → os s_{t-1} no percurso Hilbert NÃO são vizinhos lineares no texto original
         → P(s_t | s_{t-1}) estimada reflete menos redundância real
         → model_bps maior (pior)
```

---

## Conclusão Científica

Para dados intrinsecamente 1D (texto natural, código-fonte, sequências genômicas lineares),
reordenamento por curvas de preenchimento de espaço não é benéfico e pode aumentar
a entropia estimada pelo modelo de contexto. O ganho dessas curvas é **específico de
dados com correlação espacial 2D local**.

Esta conclusão está alinhada com a teoria: curvas de Hilbert preservam localidade
em espaços multidimensionais; aplicá-las a dados 1D introduz uma dimensão artificial
que não corresponde à estrutura real dos dados.

---

## Implicações para o Projeto

1. **Dataset pt-br.tsv serve como controle negativo válido**, mas não como teste da
   hipótese central (que requer dados 2D espaciais reais — ver Q-003).

2. **O pipeline E (busca adaptativa)** corretamente seleciona raster para dados de texto,
   confirmando que o mecanismo de seleção automática funciona no caso negativo.

3. **Para publicação:** este resultado é o controle negativo esperado — confirma que o
   método não degrada dados 1D de forma irracional e que a seleção adaptativa compensa.

4. **Limitação do experimento atual:** pt-br.tsv não é um corpus canônico. Para o paper,
   replicar em `dickens` (Silesia) ou `alice29.txt` (Canterbury) — ver Q-002.

---

## Referências

- Protótipo: `prototype/compare_orders.py` — pipelines A, B, C
- Dados: `datasets/pt-br.tsv`
- Teoria: `docs/pesquisa/02_curvas_preenchimento_de_espaco.md`
- SIAC log: `docs/pesquisa/09_siac-mapa-pesquisa.md` (seção "Observações do protótipo")
