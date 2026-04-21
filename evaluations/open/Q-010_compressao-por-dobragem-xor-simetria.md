---
id: Q-010
titulo: Compressão por alinhamento aproximado elástico (fold-XOR generalizado) supera LZ?
categoria: novidade
prioridade: critica
criado: 2026-04-02
relacionado: [Q-001, Q-009, Q-008]
---

## Pergunta

O framework de "compressão por dobragem" — buscar permutações σ sobre a sequência
binária que minimizam o custo de representar os resíduos XOR das metades dobradas —
é uma generalização unificada de técnicas existentes (LZ, BWT, Hilbert, compressão
fractal) e constitui uma contribuição original?

---

## Descrição do Framework

### Operação de Dobragem

Dado um bloco binário S de comprimento 2k e uma permutação σ:

```
fold(S, k, σ):
  A = S[σ[0:k]]     # primeira metade após permutação
  B = S[σ[k:2k]]    # segunda metade
  diff = A XOR B    # resíduo: 0 = iguais, 1 = opostos
  retorna (A, diff)  # A é a base; diff codifica as diferenças
```

**Decodificação:**
```
unfold(A, diff, σ⁻¹):
  B = A XOR diff
  S[σ] = concat(A, B)
  retorna S
```

### Propriedade Binária Fundamental

No domínio binário, há apenas dois estados de alinhamento:
- `XOR[i] = 0` → posição i é **cópia exata** (custo: 0 bits adicionais)
- `XOR[i] = 1` → posição i é **cópia invertida** (também totalmente previsível)

O custo real de representar `diff` é proporcional ao número de **transições** em `diff`
(runs de 0s e 1s), não ao número de 1s. Isso porque transições = run-length encoding.

```
diff = 00000001   →  1 run de zeros (7) + 1 run de um (1)  →  ~4 bits
diff = 01010101   →  8 alternâncias  →  ~8 bits (incompressível)
diff = 00000000   →  1 run de zeros (8)  →  ~1 bit (dobra perfeita)
```

### Árvore de Dobras Recursiva

```
FoldTree(S):
  se entropia(S) == 0 ou |S| == 1:
    retorna S  # base case irredutível
  
  (k*, σ*) = busca_ótima(S)
  
  diff = fold(S, k*, σ*)
  retorna (k*, σ*, FoldTree(S[0:k*]), encode_runs(diff))
```

**MDL (Minimum Description Length) do nó:**
```
custo(nó) = log2(N) + custo_codificar(σ*) + custo_runs(diff) + custo(subárvore)
```

---

## Como Este Framework Generaliza Técnicas Existentes

| Técnica | Equivalência como dobragem | Restrição implícita |
|---------|---------------------------|---------------------|
| **RLE** | σ = identidade, k = comprimento do run | k fixo (1 símbolo repetido) |
| **LZ77** | σ = offset d, A = janela anterior | Greedy, 1 direção, sem XOR |
| **BWT** | σ = permutação lexicográfica de rotações | σ fixo, não busca ótimo |
| **Compressão fractal (PIFS)** | σ = transformação afim em blocos 2D | Só blocos 2D, similaridade aproximada |
| **Hilbert scan** | σ = curva de Hilbert em grade 2D | σ fixo, não adapta aos dados |
| **Sequitur/Re-Pair** | Dobragem hierárquica por dígrafos frequentes | Apenas matches exatos, sem XOR |
| **Autocorrelação** | Mede alinhamento para cada k com σ=deslocamento | Análise, não codec |
| **Gray code** | Minimiza XOR entre elementos consecutivos | Só para ordenação, não para compressão |

**O framework de dobragem generaliza todos** ao tornar σ e k variáveis de busca.

---

## O Papel do Hilbert neste Framework

O Hilbert curve é uma **permutação específica σ_H** que satisfaz:

```
σ_H: ℤ_N → ℤ²_{√N}   (mapeia posição linear em coordenadas 2D)
```

tal que posições próximas na grade 2D ficam próximas em σ_H.

**No contexto da dobragem:** Usar σ_H equivale a dobrar a sequência na grade 2D antes
de comparar metades. Para dados com correlação espacial 2D:

```
S[σ_H[0:N/2]]  ≈  S[σ_H[N/2:N]]   (as duas metades da curva de Hilbert)
diff = XOR(A, B)  →  esparso para dados 2D correlacionados
```

Mas σ_H é **fixo** — não adapta aos dados. O framework proposto busca σ* ótimo para
cada bloco, potencialmente superando Hilbert quando a estrutura não é 2D.

---

## Espaço de Busca

### Restrições Práticas

Busca exaustiva sobre todas as permutações de N elementos é O(N!) — intratável.
Restrições práticas que tornam a busca viável:

**Classe 1 — Dobras por potência de 2:**
```
k ∈ {1, 2, 4, 8, ..., N/2}
σ = identidade (ordem original)
O(log N) dobras candidatas — eficiente
```

**Classe 2 — Dobras com offset (generaliza LZ):**
```
k fixo, σ = deslocamento d ∈ {1, 2, ..., N-k}
O(N) candidatos — suffix array resolve em O(N log N)
```

**Classe 3 — Dobras em grades nD (generaliza Hilbert):**
```
k = N/2, σ ∈ {curvas de Hilbert, Morton, Peano em dimensão 1, 2, 3, ...}
O(D) candidatos onde D = número de dimensões testadas
```

**Classe 4 — Dobras por gramática (generaliza Re-Pair):**
```
σ definida por padrões frequentes na sequência
Encontrar via suffix array ou BWT
```

**Busca hierárquica proposta:**
1. Testar Classe 1 (barato, O(N log N) total)
2. Para blocos que não comprimiram bem, testar Classe 2
3. Para blocos com estrutura 2D detectada, testar Classe 3
4. Parar quando ganho marginal < custo de codificar σ

---

## Análise Teórica

### Limite Inferior

O framework não pode superar o limite de Shannon:
```
custo_mínimo = N × H(p)   bits
```

Mas pode atingi-lo para qualquer distribuição se σ* for ótimo (ergue ao nível do
codificador aritmético com modelo perfeito).

### Condição de Ganho

A dobragem com σ produz ganho quando:
```
custo(σ) + custo_runs(XOR(A, B)) < N/2 × H(p_original)
```

Para dobra perfeita (XOR = 0):
```
custo = log2(N)   (para codificar k)
```
vs. original: `N/2 × H(p)` bits — ganho quase máximo.

### Análise para dados uniformes vs. estruturados

| Dado | XOR esperado | Runs no XOR | Compressão |
|------|-------------|-------------|-----------|
| Aleatório (i.i.d.) | ~50% uns | N/2 runs | Sem ganho |
| Periódico (período k) | 00...0 | 1 run | Ganho máximo |
| Suave 1D (texto) | Esparso com LZ/BWT | Poucos runs | Ganho moderado |
| Correlacionado 2D (imagem) | Esparso com σ_H | Blocos contíguos | Ganho alto |
| Executável (instruções) | Esparso com σ_ISA | Padrões de instrução | Ganho moderado |

---

## Conexão com Teoria de Informação

### Kolmogorov Complexity

A árvore de dobras ótima é uma aproximação prática da **complexidade de Kolmogorov**:
```
K(S) = comprimento do menor programa que gera S
```

A busca de dobragem encontra a estrutura recursiva de S — o programa mais curto que
o reproduz via dobragens + resíduos. Isso é:
- Decisível (ao contrário de K)
- Computável em tempo polinomial com as restrições da Classe 1-3
- Um limite superior prático de K(S)

### Minimum Description Length (MDL)

O critério de seleção de σ* é exatamente MDL:
```
σ* = argmin  [L(σ) + L(S | σ)]
```
onde `L(σ)` é o custo de codificar a permutação e `L(S | σ)` o custo do resíduo.

---

## Hipóteses a Testar

**H1 (teórica):** O framework de dobragem com restrição à Classe 1 (potências de 2)
captura toda a estrutura explorada por RLE + LZ77 de forma mais eficiente ou igual.

**H2 (experimental):** Para dados 2D reais, adicionar Classe 3 (Hilbert) à busca
produz ganho adicional de ≥ 5% sobre Classe 1 em razão de compressão.

**H3 (implementação):** Um codec baseado em árvore de dobras com busca restrita a
Classes 1+2+3 produz compressão comparável a bzip2 em ≥ 3 tipos de dados.

**H4 (novidade):** A combinação de busca sobre σ + resíduo XOR + codificação de runs
não está descrita como framework unificado na literatura de compressão.

---

## Prioridade para o Paper

Esta pergunta tem duas dimensões:

1. **Teórica (H1, H4):** Formalizar o framework e posicionar na literatura.
   Pode ser feito agora, sem implementação. Potencialmente o núcleo de Q1.

2. **Empírica (H2, H3):** Implementar e testar.
   Depende de: Q-002 (datasets) + implementação do codec básico.

**Implicação para Q-001 (novidade):** Se H4 se confirmar, o framework de dobragem
é uma contribuição mais ampla que "Hilbert como modelo de contexto" — possivelmente
reformulando a contribuição central do projeto.

---

## Relação com as Perspectivas de Feature Space (doc 10)

| Perspectiva | Como o framework de dobragem se encaixa |
|-------------|----------------------------------------|
| P1 (visualizar) | σ define como "ver" os dados |
| P2 (mudar base) | Dobra é uma mudança de base binária |
| P3 (adaptação) | σ* é adaptado a cada bloco |
| P4 (vocabulário) | Resíduos esparsos reduzem o vocabulário efetivo |
| P5 (múltiplas direções) | Classes 1-4 exploram diferentes "direções de dobragem" |
| P6 (composição) | Árvore de dobras é composição hierárquica |

**O framework de dobragem é uma instância concreta de P1+P3+P5 combinados.**

---

## Generalização Elástica: Alinhamento Aproximado com Fronteiras Variáveis

*Adicionado após refinamento da intuição original.*

A versão fixa (k = N/2, fronteiras exatas) é uma simplificação. A ideia completa é
**elástica**: o match pode ter qualquer comprimento, começar em qualquer posição, e
ser **aproximado** (não exato).

### Match Aproximado (Elastic Approximate Match)

```
Match(i, j, l, e):
  i   = posição alvo (onde o padrão está sendo descrito)
  j   = posição fonte (de onde vem a cópia)
  l   = comprimento (variável, definido pelo match ótimo)
  e   = número de bits diferentes (erros)
  
  diff = XOR(S[i:i+l], S[j:j+l])    ← e bits = 1, resto = 0
  
  Custo = bits_para_codificar(j) + bits_para_codificar(l) +
          bits_para_codificar(posições dos e erros no diff)
```

**Condição de ganho:** `log₂(N) + e·log₂(l) << l`
— match longo com poucos erros supera armazenar os `l` bits diretamente.

### Exemplo do raciocínio original

```
S = 111100011111001111000   (21 bits)

Encontrar match aproximado com d=4:
  S[0:7]  = 1001111
  S[4:11] = 0001111   →   XOR = 1000000   (1 erro, posição 0)

Codificação:
  Armazenar base:    1001111          (7 bits)
  Match para alvo:   (fonte=0, l=7, e=1, pos_erro=0)   (≈5 bits)
  vs. armazenar alvo diretamente:     7 bits

  Ganho por match ≈ 2 bits — modesto aqui, mas cascateia.
```

### Notação compacta

```
1 _ 0001111
│   └──────── base (armazenada uma vez)
└──────────── residual (1 bit diff na posição 0)

O "_" significa: "derivado da base — não precisa ser guardado"
```

### Diferença Fundamental para LZ77

| Aspecto | LZ77 | Match Aproximado |
|---------|------|-----------------|
| Tipo de match | Exato (XOR = 0 obrigatório) | Aproximado (XOR esparso) |
| Comprimento | Variável | Variável |
| Residual | 1 literal (próximo char) | e bits diff comprimidos |
| Busca | Janela deslizante | Qualquer posição anterior |
| Custo de miss | 1 literal (8 bits) | Match aproximado (< 8 bits se e < l/8) |

**LZ77 deixa como literais** sequências que diferem em 1-2 bits de algo já visto.
O match aproximado as codifica como `(ref, 1-2 bits diff)` — ganho real em dados
com variação suave (texto com typos, código com variações, dados comprimidos lossy).

### Cascata de Resíduos

A propriedade mais poderosa: os resíduos `diff` são **auto-similares**.

```
S → match M₁ + diff₁
         diff₁ → match M₂ + diff₂   ← diff₁ tem estrutura própria
                      diff₂ → match M₃ + diff₃
                                   ...
                                        → literal irredutível (pequeno)
```

Se os erros de aproximação têm estrutura (clustering, periodicidade), cada nível
de residual comprime melhor que o anterior. O processo termina quando o residual
é incompressível (ruído puro).

### Conexão com Literatura Existente

| Campo | Técnica equivalente | Limitação vs. framework |
|-------|--------------------|-----------------------|
| Compressão de genomas | Approximate LZ (GorillaC, MFCompress) | Fixo no domínio DNA (4 bases) |
| Controle de versão | Git pack (delta encoding) | Só entre versões, não interno |
| Compressão de vídeo | Compensação de movimento | Só blocos 2D, custo de busca |
| Compressão de texto | LZed, approximate LZ | Sem cascata de resíduos |
| Teoria | Edit-distance based coding | Teorias existem, codecs eficientes não |

**O que parece não existir:** Um codec geral que:
1. Usa alinhamento aproximado elástico (fronteiras variáveis)
2. Codifica resíduos esparsos eficientemente
3. Cascateia resíduos recursivamente
4. Busca sobre classes de permutação (incluindo curvas espaciais)

### Hipóteses Adicionais

**H5:** Para qualquer string S com complexidade de Kolmogorov K(S), o framework
de alinhamento aproximado elástico atinge comprimento de código ≤ K(S) + O(log N)
em tempo polinomial (com oracle de busca eficiente).

**H6:** A taxa de compressão do framework elástico supera LZ77 em dados com
variação suave (Δ_hamming ≤ δ entre segmentos similares), para δ/l < 0.1.

### Implementação Mínima para Validação

```python
def find_best_approx_match(S: bytes, pos: int, max_errors: int,
                           min_len: int = 8) -> tuple[int, int, bytes]:
    """
    Para posição `pos`, encontra o melhor match aproximado em S[0:pos].
    Retorna (fonte_pos, comprimento, diff_bytes).
    Usa suffix array + Hamming distance bounded search.
    """
    best_gain = 0
    best = (0, 0, b'')
    # Para cada candidato j em S[0:pos]:
    #   Para cada comprimento l de min_len a pos-j:
    #     diff = XOR(S[pos:pos+l], S[j:j+l])
    #     erros = popcount(diff)
    #     if erros <= max_errors:
    #       ganho = l - (log2(pos) + erros * log2(l) / 8)
    #       if ganho > best_gain: melhor candidato
    return best
```

Custo O(N²) ingênuo — otimizar com suffix array para O(N log N).

