---
id: Q-009
titulo: Índice invertido por bitmask (valor→posições) + Hilbert clustering é efetivo?
categoria: empirico
prioridade: alta
criado: 2026-04-02
relacionado: [Q-003, Q-004, Q-007]
---

## Pergunta

O esquema de compressão por **índice invertido com bitmask** (representar cada símbolo
como a lista das posições onde ele ocorre, em vez da sequência posição→símbolo), combinado
com pré-ordenação por curva de Hilbert para criar clustering espacial, produz compressão
mensurável em dados 2D reais?

---

## Descrição do Método

### Transformação Base

Em vez de representar:
```
posição: 0  1  2  3
valor:   11 00 01 01
```

Representar como índice invertido:
```
valor 01 → bitmask 0011   (posições 2 e 3)
valor 00 → bitmask 0100   (posição 1)
valor 11 → bitmask 1000   (posição 0)
valor 10 → (ausente)
```

### Otimização 1 — Complemento implícito

Para N posições e k símbolos possíveis, apenas k-1 bitmasks precisam ser transmitidas.
A última é deduzida como:

```
bitmask_k = ~(bitmask_1 | bitmask_2 | ... | bitmask_{k-1})
```

**Ganho:** Economia de exatamente 1 bitmask de N bits.

### Otimização 2 — Serialização Sudoku (enumerative coding)

Transmitir os bitmasks de forma entrelaçada, posição a posição. À medida que posições
são atribuídas, as restantes diminuem. Quando apenas 1 posição resta não atribuída para
um dado símbolo, o bit correspondente está **forçado** → custo 0 bits.

**Resultado:** O custo total do esquema converge para o limite de entropia
H(distribuição dos símbolos), idêntico ao custo do codificador aritmético ótimo.

Isso é equivalente ao **enumerative coding** (Cover, 1973).

### Otimização 3 — Compressão dos bitmasks

Os bitmasks, antes de transmissão, podem ser comprimidos com:
- **RLE (Run-Length Encoding):** Efetivo quando as posições de cada símbolo formam
  blocos contíguos.
- **Golomb/Rice coding:** Efetivo para listas esparsas de posições.
- **Elias-delta coding:** Universal, funciona para qualquer distribuição.

---

## A Conexão com Hilbert — Hipótese Central

```
Dados 2D com correlação espacial local
        ↓
Reordenar com curva de Hilbert
        ↓
Posições com o mesmo valor ficam ADJACENTES na sequência 1D
        ↓
Bitmask("onde está valor 0x3F?") → bloco contíguo de 1s
        ↓
RLE do bitmask: (offset, comprimento) → muito poucos bits
```

**Sem Hilbert:** bitmask de cada valor tem 1s espalhados → RLE ineficiente (pior caso:
N bits para descrever N/2 posições aleatórias).

**Com Hilbert:** bitmask de cada valor tem 1s em bloco → RLE produz (offset, comprimento)
com poucos bits → compressão real.

**Implicação:** Este método é fundamentalmente diferente do modelo de contexto ordem-1
atual. O modelo de contexto explora correlação *entre posições consecutivas*.
O índice invertido explora a *distribuição espacial global* de cada símbolo.
São perspectivas ortogonais e potencialmente complementares.

---

## Análise Teórica

### Custo sem bitmask compression (pessimista)

```
(k - 1) bitmasks × N bits/bitmask = (k-1) × N bits

Para 2-bit symbols (k=4), N pares:
  Custo = 3N bits  (vs. original 2N bits)  → PIOR
```

**Conclusão:** O esquema base sem compressão dos bitmasks é sempre pior. O ganho vem
inteiramente da compressibilidade dos bitmasks.

### Custo com RLE perfeito nos bitmasks (otimista)

Se cada símbolo ocorre em M blocos contíguos de tamanho médio L = N/(k·M):
```
Custo por bitmask ≈ M × (log2(N) + log2(L)) bits
Custo total ≈ (k-1) × M × (log2(N) + log2(L)) bits

Para M=1 (um bloco contíguo por símbolo — caso Hilbert ideal):
  Custo ≈ (k-1) × 2 × log2(N) bits  → sublinear em N!
```

**Para N=1024, k=4:**  
- Original: 2048 bits  
- Com bitmask RLE (M=1): ≈ 3 × 2 × 10 = 60 bits  
- Ganho teórico: 34× !

**Mas isso é o caso ideal.** Dados reais têm M > 1.

### Crossover point

O esquema supera o raster quando:
```
(k-1) × M × (log2(N) + log2(L)) < N × H(p)
```

Onde H(p) é a entropia do símbolo. Para dados uniformes H(p) = log2(k).

---

## Conexão com Técnicas Existentes

| Técnica | Como se relaciona |
|---------|------------------|
| **Bit-plane coding (JPEG2000)** | Caso especial: decompõe por plano de bits (não por símbolo) |
| **Inverted index (busca de texto)** | Mesma estrutura; usa Golomb/Rice codes para posting lists esparsas |
| **Enumerative coding (Cover 1973)** | A serialização Sudoku é exatamente enumerative coding |
| **Symbol-ranked compression** | Compressão por ordenação dos símbolos por posições relativas |
| **Group testing theory** | Identificar posições de valores por queries estruturadas |

**Distinção:** Nenhuma dessas combina explicitamente índice invertido com Hilbert
como pré-ordenação para criar clustering. A combinação parece não estar descrita
como framework na literatura.

---

## Hipóteses a Testar

**H1:** Para dados 2D com alta correlação espacial (imagens médicas `mr`, `x-ray`),
a combinação Hilbert + bitmask-RLE produz compressão real mensurável.

**H2:** O número de blocos M por símbolo, após reordenação Hilbert, é significativamente
menor que após reordenação raster (para dados 2D).

**H3:** O índice invertido + Hilbert é complementar ao pipeline A/B/C (captura
estrutura diferente) e pode ser combinado em cascata.

---

## Protocolo Experimental

### Experimento 1 — Contar blocos M por topologia

Para cada dataset 2D (começar com `pic`, `mr`, `x-ray`):
1. Reordenar com raster, Morton, Hilbert
2. Para cada símbolo de 8 bits (ou k-bit agrupado), contar M = número de runs
3. Comparar M_raster vs M_morton vs M_hilbert
4. Plotar distribuição de M para cada topologia

**Métrica:** M menor → bitmask mais comprimível → índice invertido mais eficiente.

### Experimento 2 — Implementar o codec

```python
def encode_inverted_bitmap(seq: bytes, group_bits: int = 8) -> bytes:
    """
    Codifica sequência como índice invertido com bitmask RLE.
    
    group_bits: quantos bits por símbolo (2, 4, 8)
    """
    # 1. Agrupar bytes em símbolos de group_bits
    # 2. Para cada valor possível (exceto último), gerar bitmask
    # 3. RLE encode cada bitmask
    # 4. Serializar com header
    # 5. (Opcional) Otimização Sudoku: entrelaçar bitmasks e omitir bits forçados

def decode_inverted_bitmap(data: bytes) -> bytes:
    """Inverso: reconstruir sequência a partir dos bitmasks."""
    # 1. Parse header
    # 2. Decode RLE de cada bitmask
    # 3. Reconstruir bitmask do último valor = ~(OR de todos)
    # 4. Para cada posição, determinar valor pelo bitmask que a inclui
```

### Experimento 3 — Benchmark cruzado

Comparar no pipeline:
```
Raster + modelo ctx ordem-1  (pipeline A atual)
Hilbert + modelo ctx ordem-1 (pipeline C atual)
Raster + índice invertido bitmask
Hilbert + índice invertido bitmask     ← hipótese principal
```

---

## Implementação: Otimização do Group Size

O grupo de `group_bits` é um hiperparâmetro crítico:

- `group_bits = 1` (bits individuais): k=2, bitmasks são planos de bit → bit-plane coding
- `group_bits = 2`: k=4, bitmasks de N/2 bits — balanceado
- `group_bits = 8` (bytes individuais): k=256, 255 bitmasks de N bits — muita overhead

**Para k=256 (bytes individuais):** A maioria dos bitmasks é esparsa (cada byte value
aparece N/256 vezes em média) → Golomb coding é ideal, não RLE.

**Otimização proposta:** Adaptar o encoding de cada bitmask à sua densidade:
- Densa (> N/3): RLE
- Esparsa (< N/10): lista de posições com Golomb/Elias-delta
- Intermediária: aritmética adaptativa

---

## Critério de Conclusão

- **H1 confirmada:** Para ≥ 2 datasets 2D, Hilbert + bitmask-RLE produz compressão
  real superior a raster + bitmask-RLE com margem ≥ 5%.
- **H2 confirmada:** M_hilbert < M_raster × 0.5 em média para dados 2D.
- **H3 (combinação):** Pipeline A/C + índice invertido produz compressão adicional.

Migrar para A-009 após experimentos 1-2 completos.

---

## Prioridade de Implementação

Depende de:
- Q-002 (datasets canônicos disponíveis, para experimento real)
- Q-003 (confirmação que Hilbert clustura dados 2D — pré-condição para H1)

Pode ser desenvolvida em paralelo com Q-007 (pipeline BWT).
