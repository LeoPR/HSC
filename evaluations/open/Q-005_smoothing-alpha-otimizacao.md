---
id: Q-005
titulo: O parâmetro α de suavização de Laplace afeta significativamente os resultados?
categoria: empirico
prioridade: media
criado: 2026-04-01
relacionado: [Q-006]
---

## Pergunta

O valor `α=1.0` de suavização aditiva (Laplace) usado no modelo de contexto de ordem 1
é ótimo para a métrica de discriminação entre topologias, ou outros valores de α
alteram as conclusões qualitativas do benchmark?

---

## Contexto

O modelo de entropia atual (`adaptive_order1_bits` em `metrics/entropy.py:16`) usa:

```python
p = (count + alpha) / (total + alpha * 256)  # alpha=1.0 hardcoded
```

A suavização de Laplace com α=1 assume um prior uniforme com peso de 1 contagem
por símbolo. Para sequências longas (>256 bytes por contexto), isso é negligenciável.
Para sequências curtas ou esparsas, α=1 pode dominar e achatar as probabilidades.

**Implicação:** Se α muito alto → todas as topologias convergem para a mesma entropia
(modelo "cego"). Se α muito baixo → overfitting a contextos raros, instabilidade.

**Questão prática:** α afeta *absolutamente* os valores de model_bps, mas o que importa
é se afeta as *diferenças relativas* entre topologias — porque é essa diferença que
define qual topologia "ganha".

---

## Hipótese

**H1:** Para α ∈ [0.01, 5.0], as conclusões qualitativas (qual topologia tem menor
model_bps) são estáveis — α afeta a magnitude absoluta mas não o ranking.

**H2 (alternativa):** Para dados esparsos (arquivos pequenos, alfabeto grande por
contexto), α alto pode mascarar ganhos reais de Hilbert → valores menores revelam
diferenças reais.

---

## Desenho Experimental

### Ablação de α

```
α_candidates = [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
```

Para cada α:
1. Executar pipeline A/B/C em `alice29.txt` (texto) e `mr` (imagem MRI)
2. Registrar model_bps de cada topologia
3. Calcular delta (raster_bps - hilbert_bps) para cada α
4. Verificar se o sinal do delta muda com α

### Análise de Sensibilidade

Plotar: delta(raster, hilbert) em função de α para cada dataset.
- Curva flat → resultados insensíveis a α (H1 confirmada)
- Curva com cruzamento de zero → α muda o ranking (H2 relevante)

---

## Critério de Conclusão

- **H1 confirmada:** Para todos os datasets testados, o ranking de topologias não
  muda em α ∈ [0.01, 5.0]. Conclusão: α=1.0 é razoável, mencionar na metodologia.
- **H2 relevante:** Cruzamento de zero encontrado → reportar o valor de α crítico e
  implementar busca de α ótimo como parâmetro do pipeline.
- **Decisão de implementação:** Se H1 confirmada e α não é crítico, remover do scope
  de otimização. Se H2 relevante, adicionar α ao espaço de busca do pipeline E.
