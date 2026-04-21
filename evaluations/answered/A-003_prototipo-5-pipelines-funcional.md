---
id: A-003
titulo: Protótipo implementa corretamente os 5 pipelines de benchmark
categoria: design
prioridade: media
criado: 2026-03-29
concluido: 2026-03-29
---

## Pergunta Original

A implementação Python dos pipelines A–E do protótipo está funcionalmente correta
e pode ser usada como base para expansão do benchmark?

---

## Resposta

**Sim.** O protótipo em `prototype/` implementa os 5 pipelines com separação clara
de responsabilidades. A lógica de cada módulo está correta para os fins do experimento
atual, com ressalvas documentadas abaixo.

---

## Estrutura Verificada

| Módulo | Função | Status |
|--------|--------|--------|
| `orders/raster.py` | Índices 0..N² sequencialmente | ✅ Correto |
| `orders/morton.py` | Bit-interleaving Z-order | ✅ Correto |
| `orders/hilbert.py` | Algoritmo recursivo d2xy | ✅ Correto |
| `data/loader.py` | Load, pad, reorder | ✅ Correto (ver ressalva 1) |
| `metrics/entropy.py` | Modelo contexto ordem-1, Laplace | ✅ Correto (ver ressalva 2) |
| `metrics/compression.py` | zlib nível 9 | ✅ Correto |
| `compare_orders.py` | Orquestrador A/B/C/D/E | ✅ Correto |

### Pipelines

| Pipeline | Descrição | Implementado |
|----------|-----------|-------------|
| A | Raster + modelo entropia + zlib | ✅ |
| B | Morton + modelo entropia + zlib | ✅ |
| C | Hilbert + modelo entropia + zlib | ✅ |
| D | Hilbert + busca de side ótimo | ✅ |
| E | Exaustivo: todas topologias × todos sides | ✅ |

---

## Ressalvas Técnicas

### Ressalva 1 — `reorder_bytes` descarta índices silenciosamente

```python
# data/loader.py — reorder_bytes
# Índices ≥ valid_len são silenciosamente ignorados
```

**Impacto:** Quando `side²` > `len(data)`, alguns índices do percurso caem no
padding de zeros. `reorder_bytes` descarta esses, resultando em sequência menor
que `side²`. Isso é comportamento correto para evitar lixo no final, mas o
chamador deve saber que a sequência de saída pode ter tamanho diferente do esperado.

**Recomendação:** Adicionar docstring explicando comportamento; não é bug, é design.

### Ressalva 2 — `hilbert_order` exige potência de 2

```python
# orders/hilbert.py — hilbert_order
if side & (side - 1) != 0:
    raise ValueError(f"side must be a power of 2, got {side}")
```

**Impacto:** Limita sides a {512, 1024, 2048, ...}. Não é problema para o benchmark,
mas deve ser documentado nos métodos do paper.

### Ressalva 3 — Performance Python pura

`hilbert_order(side=2048)` gera 4M índices em Python puro — pode ser lento para
benchmark em lote. Para testes rápidos, usar side=512 (262K) ou side=1024 (1M).

**Estimativas aproximadas (CPython):**
- side=512: ~0.3s por call
- side=1024: ~1.2s por call
- side=2048: ~5s por call

Para benchmark completo Silesia (~12 arquivos × 3 topologias × 3 sides), estimar
~15 minutos em Python puro. Aceitável para fase de protótipo.

---

## Conclusão Científica

O protótipo está pronto para expansão de benchmark com os datasets canônicos definidos
em Q-002. A base de código tem separação de responsabilidades adequada para adicionar:
- Novos datasets sem alterar lógica de pipeline
- Novas topologias (ex: Z-curve 3D, Peano) sem alterar métricas
- Novas métricas (ordem-2, PPMd score) sem alterar pipelines

---

## Próximos Passos de Desenvolvimento (derivados)

1. Adicionar `prototype/data/synthetic.py` — gerador de dados sintéticos controlados
2. Adicionar script de download de corpora canônicos em `scripts/download_corpora.sh`
3. Implementar `prototype/transforms/` (BWT, MTF, RLE) para Q-007
4. Adicionar logging de resultados em CSV para análise posterior

---

## Referências

- Código: `prototype/compare_orders.py`
- Módulos: `prototype/data/`, `prototype/metrics/`, `prototype/orders/`
