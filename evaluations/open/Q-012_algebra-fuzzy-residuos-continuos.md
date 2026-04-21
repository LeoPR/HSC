---
id: Q-012
titulo: Álgebra fuzzy melhora qualificação e compressão de resíduos de dados de origem contínua?
categoria: empirico
prioridade: alta
criado: 2026-04-03
relacionado: [Q-010, Q-011, Q-003]
---

## Pergunta

Para dados que têm origem em fenômenos contínuos (sinais de áudio/vídeo, imagens,
medições científicas), o uso de álgebra fuzzy para modelar resíduos de compressão
(o que φ não capturou exatamente) produz representação mais compacta do que
codificação crisp (binária) dos mesmos resíduos?

---

## Contexto e Motivação

### O Problema dos Resíduos Crisp

No framework de dobragem (Q-010) e no framework homeomórfico (Q-011), o residual
é o que a função φ não capturou:

```
residual = D - φ(C)    (diferença ponto-a-ponto)
```

Em compressão clássica, esse residual é armazenado como bits — crisp, binário,
sem estrutura presumida. Mas para dados de origem contínua, o residual não é
aleatório — ele tem estrutura derivada da continuidade do sinal original.

**Exemplo:** imagem MRI (origem: campo magnético contínuo → amostrado em DICOM 16-bit)
- Residual de compressão = diferença entre pixel reconstruído e pixel original
- Essa diferença não é ruído branco — é suave, localmente correlacionada
- A estrutura do residual pode ser modelada com funções de pertencimento fuzzy

### A Ponte Contínuo-Discreto

```
Fenômeno físico contínuo
        ↓  (amostragem + quantização)
Dado discreto (binário)
        ↓  (compressão com φ)
Espaço compacto C
        ↓  (residual = o que φ perdeu)
Resíduo esparso r

Se r vem de origem contínua:
  r não é aleatório — tem topologia própria
  r pode ser modelado em [0,1]ⁿ (domínio fuzzy)
  → representação mais compacta do que bits crus
```

---

## Ferramentas Fuzzy Relevantes

### F-Transform (Perfilieva, 2006)

```
Dado: f: X → ℝ  (sinal discreto de origem contínua)
Partição fuzzy: {A₁, ..., Aₙ} sobre X, com Σₖ Aₖ(x) = 1 para todo x

Coeficientes F-transform:
  Fₖ = Σᵢ f(xᵢ) · Aₖ(xᵢ) / Σᵢ Aₖ(xᵢ)

Reconstrução:
  f̃(x) = Σₖ Fₖ · Aₖ(x)

Resíduo: r(x) = f(x) - f̃(x)
```

Se n << N: {F₁, ..., Fₙ} são muito menos que {f(x₁), ..., f(x_N)}.
O resíduo r é tipicamente menor que f para dados suaves.

**Cascata natural:** Aplicar F-transform sobre resíduo de φ_Hilbert.
O resíduo do Hilbert ainda tem estrutura contínua → F-transform comprime mais.

### Rough-Fuzzy Clustering para Residuais

Para cada ponto do residual r(x):
```
Aproximação inferior:   r(x) definitivamente pertence a cluster Cₖ
Aproximação superior:   r(x) possivelmente pertence a cluster Cₖ
Região de borda:        incerteza = precisa de bits adicionais
```

Codificação:
```
(id_cluster_inferior, id_cluster_superior, bits_borda)
```

Se a região de borda é pequena (resíduo estruturado), poucos bits extras são necessários.
Se a região de borda é grande (resíduo ruidoso), sem ganho — detetar e usar codificação crisp.

### Graus de Pertencimento como Probabilidades

```
μₖ(r) ∈ [0,1] = grau de pertencimento de r ao cluster Cₖ

Interpretação probabilística:
  μₖ(r) ≈ P(r | cluster Cₖ)

Codificação:
  código(r) = log₂(1/μ_{argmax_k}(r)) + custo(precisão)
```

Se μ é alta e concentrada (resíduo bem pertencente a um cluster): poucos bits.
Se μ é flat (resíduo imprevisível): muitos bits — sem ganho.

---

## Hipóteses

**H1:** Para dados de origem contínua (imagens MRI, raio-X), o residual de
φ_Hilbert tem grau de pertencimento fuzzy alto em poucos clusters → compressível
com F-transform ou rough-fuzzy.

**H2:** A combinação (φ_Hilbert + F-transform sobre resíduo) supera φ_Hilbert
isolado em ≥ 3% de compressão para datasets do estrato 2D (mr, x-ray).

**H3:** O ganho fuzzy é proporcional à "continuidade" do dado de origem —
mensurável pela variação total do residual. Para dados com alta variação
total (ruído, binário puro), o ganho é nulo ou negativo.

**H4:** Para dados de texto (origem discreta), o ganho fuzzy é nulo ou
negativo — confirmando que a técnica é específica de dados de origem contínua.

---

## Protocolo Experimental

### Experimento 1 — Medir estrutura do residual

Para cada dataset do benchmark (estrato 2D e texto):
1. Aplicar φ_Hilbert (pipeline C)
2. Computar r = dados_originais XOR dados_reconstruídos (lossless: r = 0)
   ou r = dados_originais - φ(C) (lossy: r ≠ 0)
3. Medir variação total de r: TV(r) = Σ |r(i+1) - r(i)|
4. Plotar autocorrelação de r

**Métrica de estrutura:** se autocorrelação de r decai lentamente → r tem estrutura
contínua → fuzzy pode ajudar.

### Experimento 2 — F-Transform sobre resíduo

Para datasets com TV(r) baixa (estruturado):
1. Aplicar F-transform com partição Gaussiana de n coeficientes
2. Variar n: {8, 16, 32, 64, 128} — trade-off compressão/qualidade
3. Medir: |F-coeficientes| + |resíduo-de-resíduo| vs. |r|

### Experimento 3 — Comparação final

```
Pipeline A: φ_raster + Huffman(r)           (baseline)
Pipeline C: φ_Hilbert + Huffman(r)          (HSC atual)
Pipeline F: φ_Hilbert + F-transform(r)      (nova proposta)
Pipeline G: φ_Hilbert + rough-fuzzy(r)      (variante rough)
```

---

## Implementação Necessária

```python
def f_transform(signal: np.ndarray, n_components: int,
                basis: str = "gaussian") -> np.ndarray:
    """
    Aplica F-transform com n_components coeficientes.
    basis: "gaussian", "triangular", "sigmoid"
    Retorna array de n_components coeficientes Fₖ.
    """

def f_transform_inverse(coeffs: np.ndarray, n_points: int,
                        basis: str = "gaussian") -> np.ndarray:
    """
    Reconstrói sinal de n_points a partir de coeficientes F-transform.
    """

def residual_fuzzy_encode(residual: bytes, n_clusters: int = 16) -> bytes:
    """
    Codifica resíduo via rough-fuzzy clustering.
    Retorna (cluster_ids, borda_bits) comprimido.
    """
```

---

## Dependências

- Q-002: datasets canônicos (mr, x-ray necessários para H1)
- Q-003: confirmação que φ_Hilbert funciona em 2D real (pré-condição para H2)
- Implementação de numpy/scipy para F-transform

---

## Critério de Conclusão

- **H1+H2 confirmadas:** Ganho ≥ 3% em ≥ 2 datasets 2D. Incorporar F-transform
  ao pipeline principal. Reportar como extensão natural para dados de origem contínua.
- **H3+H4 confirmadas mas H1 refutada:** Fuzzy não ajuda após Hilbert — o Hilbert
  já "capturou" a estrutura contínua suficientemente. Reportar como análise negativa
  com explicação mecanística.
- **Todos refutados:** Residual de Hilbert é incompressível com fuzzy para todos
  os tipos de dado. Conclusão: estrutura de origem contínua já está na decisão de φ,
  não no residual.
