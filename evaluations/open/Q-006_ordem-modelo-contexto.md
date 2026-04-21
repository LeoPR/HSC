---
id: Q-006
titulo: Modelo de contexto de ordem >1 melhora a discriminação entre topologias?
categoria: empirico
prioridade: media
criado: 2026-04-01
relacionado: [Q-003, Q-005]
---

## Pergunta

Um modelo de contexto de ordem 2 (P(s_t | s_{t-1}, s_{t-2})) ou superior amplia
a diferença de model_bps entre Hilbert e raster em dados 2D, ou o ganho já é
capturado completamente pela ordem 1?

---

## Contexto

O modelo atual (`entropy.py`) estima P(s_t | s_{t-1}):
- Tabela de transição 256×256 (ordem 1)
- Captura dependência entre símbolos consecutivos no percurso

**Limitação conhecida:** Correlação 2D local pode se manifestar mais fortemente
entre posições mais distantes no percurso 1D — especialmente em bordas e texturas
que não se alinham com a granularidade do percurso de ordem 1.

**Questão:** Modelo de ordem 2 (256×256×256 = 16M entradas) capturaria correlações
de 3 símbolos consecutivos. Para percurso Hilbert em imagem, isso equivale a modelar
transições de 3 vizinhos no espaço 2D — potencialmente capturando mais estrutura.

**Custo:** Ordem 2 requer 256^3 ≈ 16M tabela de transição (16 MB para contagens int32).
Viável para protótipo, borderline para produção sem compressão da tabela.

---

## Hipótese

**H1:** Para dados 2D (imagens), ordem 2 aumenta o gap Hilbert vs. raster em model_bps
em ≥ 20% relativo ao gap de ordem 1.

**H2:** Para dados 1D (texto), ordem 2 não altera o ranking (raster ainda ganha).

**H3:** Existe um ponto de saturação: além de ordem 2, ganhos adicionais são mínimos
devido a esparsidade da tabela (dados insuficientes para estimar P de ordem alta).

---

## Desenho Experimental

### Implementação

```python
def adaptive_order2_bits(seq: bytes, alpha: float = 1.0) -> float:
    """Modelo de contexto de ordem 2: P(s_t | s_{t-2}, s_{t-1})"""
    # counts[ctx1][ctx2][sym] com suavização Laplace
    # Total de estados: 256 * 256 * 256 = 16M
    # Inicializar com alpha (sparse representation recomendada)
```

**Atenção:** Tabela 256^3 com int32 = 64 MB. Usar defaultdict ou sparse array para
evitar uso excessivo de memória em protótipo.

### Comparação

Para cada dataset em Q-002 (estratos 1 e 4):

| Ordem | Dataset | Topologia | model_bps |
|-------|---------|-----------|-----------|
| 1 | `alice29.txt` | raster | ? |
| 1 | `alice29.txt` | hilbert | ? |
| 2 | `alice29.txt` | raster | ? |
| 2 | `alice29.txt` | hilbert | ? |
| 1 | `mr` | raster | ? |
| 1 | `mr` | hilbert | ? |
| 2 | `mr` | raster | ? |
| 2 | `mr` | hilbert | ? |

### Métrica de Avaliação

```
gap_N = (model_bps_raster_ordemN - model_bps_hilbert_ordemN) / model_bps_raster_ordemN
amplificação = gap_2 / gap_1  # H1: amplificação ≥ 1.20 para dados 2D
```

---

## Notas Técnicas

- Implementar ordem N como parâmetro: `adaptive_orderN_bits(seq, order=1, alpha=1.0)`
- Para ordem ≥ 3 em protótipo Python puro: considerar limite de memória (ordem 3 = 4 GB para int32)
- Alternativa: usar dicionário esparsono lugar de array denso para N ≥ 3
- Ordem 1.5 (efetiva): usar contexto misto — exemplo: (símbolo anterior, posição na grade)

---

## Critério de Conclusão

- **H1 confirmada:** Gap aumenta ≥ 20% para ≥ 2 datasets de imagem. Incorporar
  ordem 2 ao pipeline principal e reportar como hyperparâmetro na metodologia.
- **H1 refutada:** Gap não aumenta significativamente. Manter ordem 1, adicionar
  nota na metodologia: "ordem superior não adiciona poder discriminativo".
- **H3 evidenciada:** Curva de gap vs ordem mostra plateau após N=2. Reportar N_ótimo.
