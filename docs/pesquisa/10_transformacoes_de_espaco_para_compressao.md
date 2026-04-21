# 10 — Transformações de Espaço de Features para Compressão

## Tese Central

Compressão de dados é, em essência, **descoberta de estrutura**. Toda técnica de
compressão opera encontrando regularidades e codificando-as de forma mais econômica.
O que diferencia as abordagens é **em que espaço** procuram essa estrutura.

A ideia fundamental deste documento é que **mudar o espaço de representação dos dados**
(o "feature space") pode revelar regularidades invisíveis no espaço original. Diferentes
transformações "veem" diferentes padrões — e a combinação de múltiplas perspectivas
pode superar qualquer perspectiva única.

---

## Taxonomia: 6 Perspectivas sobre Transformação de Espaço

### Perspectiva 1 — Remapear para Visualizar Estrutura

> *"Mudar o feature space para que os dados fiquem com visualização mais fácil para comprimir."*

**Ideia:** Os dados têm estrutura, mas ela está oculta pela representação original.
Ao mudar o espaço, a estrutura emerge como padrões locais exploráveis.

| Técnica | O que faz | Estrutura revelada |
|---------|-----------|-------------------|
| **Curvas de Hilbert/Morton** | Mapeia grade 2D→1D preservando vizinhança | Correlação espacial local vira correlação sequencial |
| **Recurrence plots** | Mapeia série temporal 1D→matriz 2D de recorrência | Padrões dinâmicos (periodicidade, caos, estacionaridade) |
| **UMAP/t-SNE** | Embedding de alta→baixa dimensão preservando topologia | Clusters e manifolds intrínsecos |
| **Embedding de Takens** | Série 1D→espaço de fase nD via atrasos | Geometria do atrator dinâmico |

**Princípio matemático:** Teorema de Takens (1981) — uma série temporal escalar contém
informação suficiente para reconstruir a geometria do sistema dinâmico subjacente,
desde que a dimensão de embedding seja ≥ 2d+1 (onde d é a dimensão fractal do atrator).

**Para compressão:** Se os dados vêm de um sistema com atrator de baixa dimensão (quase
todos os processos naturais), então existe um espaço de representação onde os dados
vivem num manifold de dimensão muito menor que o espaço ambiente. Encontrar esse
espaço é encontrar a compressão ótima.

**Conexão com HSC:** Hilbert é um caso específico — mapeia dados 2D para 1D preservando
localidade. Mas o princípio é mais geral: *qualquer* mapeamento que preserve a estrutura
relevante pode servir como pré-processamento para compressão.

---

### Perspectiva 2 — Mudar de Base para Concentrar Energia

> *"Mudar o feature space para que os dados mudem o formato para comprimir."*

**Ideia:** Trocar a base de representação para que a informação se concentre em
poucos coeficientes — o resto pode ser descartado (lossy) ou codificado economicamente.

| Técnica | Base alvo | Concentração |
|---------|-----------|-------------|
| **DCT** (Discrete Cosine Transform) | Cossenos de frequência crescente | Energia em baixas frequências (poucos coeficientes grandes) |
| **DWT** (Discrete Wavelet Transform) | Wavelets multi-resolução | Energia em poucos coeficientes por escala |
| **KLT/PCA** (Karhunen-Loève) | Autovetores da covariância dos dados | Variância máxima nos primeiros componentes (ótimo linear) |
| **SVD** | Vetores singulares | Equivalente empírico do KLT |
| **BWT** (Burrows-Wheeler) | Permutação lexicográfica | Símbolos com contexto similar agrupados |

**Hierarquia de otimalidade:**
```
KLT (ótimo para dados Gaussianos)
 └─ DCT (boa aproximação universal, O(n log n))
     └─ DWT (boa + multirresolução, localização tempo-frequência)
         └─ Autoencoders (ótimo não-linear, aprendido dos dados)
```

**Insight chave:** A KLT é a transformação linear ótima para concentração de energia,
mas é **dependente dos dados** (precisa da matriz de covariância). A DCT é uma
aproximação fixa que funciona surpreendentemente bem para dados naturais — por isso
é usada em JPEG há 30 anos. A DWT adiciona localização (sabe *onde* a frequência muda),
o que evita artefatos de bloco.

**Para o HSC:** A contribuição do Hilbert não é concentração de energia (como DCT/DWT),
mas **concentração de contexto** — fazer com que símbolos adjacentes no percurso 1D
sejam mais previsíveis a partir de seus vizinhos. São propriedades ortogonais e
potencialmente complementares.

---

### Perspectiva 3 — Transformação Adaptativa / Iterativa

> *"Mexer no feature space enquanto os padrões vão se alinhando."*

**Ideia:** Em vez de aplicar uma transformação fixa, ajustar o espaço dinamicamente
conforme a estrutura dos dados vai sendo descoberta.

| Técnica | Mecanismo de adaptação | Velocidade |
|---------|----------------------|-----------|
| **Context mixing (PAQ/CMIX)** | Pesos de modelos ajustados símbolo-a-símbolo | Online (streaming) |
| **Autoencoders aprendidos** | Gradiente descendente sobre corpus de treino | Offline (batch) |
| **Neural SFC** | GNN aprende ordem de percurso adaptada ao tipo de dado | Offline + inferência |
| **Codificação aritmética adaptativa** | Probabilidades atualizadas a cada símbolo | Online |
| **MTF (Move-to-Front)** | Lista de vocabulário reordenada dinamicamente | Online |
| **PPM (Prediction by Partial Match)** | Modelos de contexto de ordem variável | Online |

**Context mixing — a abordagem mais poderosa conhecida:**

O PAQ/CMIX usa dezenas a milhares de modelos simultaneamente, cada um "vendo" os dados
de uma perspectiva diferente:
- Modelo de ordem 0: frequência global de símbolos
- Modelo de ordem 1-8: contextos de N símbolos anteriores
- Modelo de dicionário: correspondência com padrões longos
- Modelos especializados: tipo de arquivo, região do arquivo

Um **mixer** (rede neural simples ou logística) combina as previsões de todos os modelos
com pesos adaptativos. Os pesos são atualizados a cada símbolo — os modelos que acertam
mais ganham mais peso.

**Resultado:** Os melhores compressores do mundo (cmix, paq8px) usam context mixing e
atingem compressão próxima do limite teórico em benchmarks como enwik8/enwik9.

**Implicação para HSC:** Se a curva de Hilbert é vista como *um modelo de contexto*
(provê P(s_t|s_{t-1}) baseado na vizinhança espacial), ela pode ser integrada como
**mais um modelo** num sistema de context mixing — não como a única perspectiva,
mas como uma perspectiva que os outros modelos não têm.

---

### Perspectiva 4 — Remapear Vocabulário / Reduzir Alfabeto

> *"Remapear instruções e padrões de uso para diminuir o vocabulário."*

**Ideia:** Se os dados usam um subconjunto dos símbolos possíveis, ou se grupos de
símbolos sempre aparecem juntos, podemos criar um vocabulário menor e mais eficiente.

| Técnica | Mecanismo | Aplicação principal |
|---------|-----------|-------------------|
| **BPE** (Byte Pair Encoding) | Merge iterativo dos pares mais frequentes | Tokenização NLP, compressão |
| **Sequitur** | Inferência de gramática livre de contexto | Dados estruturados, DNA |
| **Re-Pair** | Substituição do digrama mais frequente (offline) | Compressão gramatical |
| **LZW/LZ78** | Dicionário crescente de sequências | Compressão universal |
| **LZ77** | Janela deslizante (dicionário implícito) | DEFLATE, gzip, ZIP |
| **Filtros de instrução (EXE)** | Conversão endereço relativo→absoluto | Executáveis (UPX, kkrunchy) |

**O caso dos executáveis — exemplo concreto:**

Um binário x86 contém:
```
Instrução CALL 0x00401234    →    E8 30 12 40 00
Instrução CALL 0x00401234    →    E8 30 12 40 00  (mesma, em outro lugar)
```

Mas se os dois CALLs estão em endereços diferentes, os offsets relativos diferem:
```
Posição 0x100: CALL +0x1134   →    E8 34 11 00 00
Posição 0x200: CALL +0x1034   →    E8 34 10 00 00
```

**Filtro de instrução:** Converte offsets relativos em endereços absolutos → agora os
dois CALLs para 0x00401234 produzem bytes idênticos → melhor compressão por dicionário.

**Princípio geral:** Qualquer dado estruturado tem um "vocabulário" implícito.
Descobrir e remapear esse vocabulário é uma forma de compressão:
- Proteínas: 20 aminoácidos → alfabeto de 20, não 256
- DNA: 4 bases → 2 bits por base, não 8
- Código-fonte: keywords, identificadores, literais → tokenização
- Dados tabulares: colunas com domínio restrito → codificação por coluna

**Implicação para HSC:** A curva de Hilbert opera no nível de bytes individuais.
Mas se primeiro remapearmos o vocabulário (BPE, tokenização, filtro de instrução)
e *depois* aplicarmos Hilbert sobre os tokens remapeados, o modelo de contexto
P(token_t | token_{t-1}) pode ser muito mais informativo.

---

### Perspectiva 5 — Dobrar o Espaço para Buscar em Múltiplas Direções

> *"Dobrando o espaço, fica mais rápido achar padrões não apenas buscando em stream,
> mas com qualquer perspectiva, já que está num espaço diferente e direções diferentes
> podem ser usadas."*

**Ideia:** Um compressor de stream vê os dados em uma única direção (posição 0, 1, 2, ...).
Ao embedar os dados numa grade 2D (ou 3D, nD), ganha-se **múltiplas direções de busca**.

```
Stream 1D:      → → → → → → →   (1 direção)
Grade 2D:       → → → →         (4+ direções: ↑ ↓ ← → ↗ ↘ ↙ ↖)
                → → → →
Cubo 3D:                         (13+ direções de vizinhança)
```

**Fundamentação teórica:**

1. **Curvas de preenchimento de espaço** são exatamente isso: "dobram" uma sequência 1D
   num espaço 2D/3D e então percorrem de forma a explorar vizinhança multidirecional.

2. **Análise direcional em wavelets:** Curvelets e shearlets são extensões de wavelets
   que capturam informação direcional (boa para bordas em ângulos arbitrários).

3. **Recurrence plots:** Fazem exatamente isso — convertem 1D→2D para que padrões de
   recorrência temporal se tornem padrões geométricos 2D (diagonais = determinismo,
   horizontais = estacionaridade).

4. **Embedding de Takens:** "Dobra" série temporal num espaço de dimensão superior
   onde o atrator dinâmico se torna geometricamente visível.

**Exemplo concreto — dados binários em grade 2D:**

```
Stream: 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10

Grade 4×4:
  01 02 03 04
  05 06 07 08
  09 0A 0B 0C
  0D 0E 0F 10

Agora posso buscar padrões:
- Horizontal: 01→02→03→04 (incremento de 1)
- Vertical:   01→05→09→0D (incremento de 4)
- Diagonal:   01→06→0B→10 (incremento de 5)
```

Em dados reais (não sequenciais triviais), diferentes direções revelam diferentes
correlações. Uma imagem tem gradientes em múltiplas direções; código tem estrutura
de indentação (vertical) e keywords (horizontal).

**O que Hilbert adiciona:** Ao percorrer a grade via curva de Hilbert, o percurso
1D resultante captura correlações de *todas* essas direções simultaneamente (porque
a curva muda de direção recursivamente). Um percurso raster captura apenas horizontal.

**Generalização nD:** Cada dimensão adicional de embedding dobra o número de direções
de vizinhança disponíveis. Mas há rendimento decrescente — para dados 1D embedados
em 2D, ganha-se ~4 direções extras; de 2D para 3D, ~9 extras; mas o custo computacional
cresce exponencialmente.

---

### Perspectiva 6 — Composição de Técnicas (Multi-Perspectiva)

> *"Misturar técnicas para ver o que uma pode ver na outra."*

**Ideia:** Nenhuma técnica vê tudo. A composição de perspectivas complementares
captura mais estrutura do que qualquer uma isoladamente.

**Princípio formal:** Dado um conjunto de modelos {M₁, M₂, ..., Mₖ}, onde cada
modelo captura um tipo de redundância, o modelo composto captura a *união* das
redundâncias — desde que os modelos sejam suficientemente diversos.

**O que cada técnica "vê" vs. "não vê":**

| Técnica | Vê | Não vê |
|---------|-----|--------|
| **Hilbert/Morton** | Localidade espacial, clustering 2D | Estrutura de frequência |
| **DCT** | Concentração de energia em frequência | Localização temporal de detalhes |
| **DWT** | Multirresolução + localização | Equilíbrio global de frequência |
| **BWT** | Agrupamento por contexto lexicográfico | Adjacência espacial original |
| **LZ77/78** | Repetições exatas de sequências | Repetições aproximadas |
| **PCA/KLT** | Direção de máxima variância | Estrutura não-linear |
| **Context mixing** | Tudo (por composição) | Nada (mas custo computacional extremo) |

**Pipelines compostos propostos (do doc 08):**

```
Pipeline A (lossless simples):
  Hilbert → Delta → RLE → Entropia
  (localidade + suavidade + runs + estatística)

Pipeline B (lossless simbólico):
  Hilbert → BWT → MTF → RLE → Entropia
  (localidade + contexto + vocabulário + runs + estatística)

Pipeline C (lossy):
  Hilbert por blocos → DWT/DCT → Quantização → Entropia
  (localidade + frequência + precisão + estatística)
```

**Pipeline D (proposta nova — multi-perspectiva):**
```
  Dados → [Hilbert ctx, BWT ctx, LZ ctx, ordem-N ctx] → Context Mixer → Aritmético
  (cada modelo provê P(s_t) de perspectiva diferente; mixer pondera adaptativamente)
```

Este Pipeline D é onde a contribuição do HSC pode ser mais forte: Hilbert não como
*a* transformação, mas como *uma perspectiva* num sistema multi-modelo.

---

## Tabela Síntese: Técnica × Estágio do Pipeline × Tipo de Padrão

| Técnica | Estágio | Tipo de padrão | Reversível | Custo |
|---------|---------|---------------|-----------|-------|
| Hilbert/Morton | Pré-processamento | Localidade espacial | ✅ | O(N log N) |
| BWT | Pré-processamento | Contexto lexicográfico | ✅ | O(N) a O(N log N) |
| MTF | Pós-BWT | Frequência → índice | ✅ | O(N·σ) |
| Delta | Pós-reordenação | Suavidade local | ✅ | O(N) |
| RLE | Pós-MTF/Delta | Runs de valor repetido | ✅ | O(N) |
| DCT | Transformada | Concentração de frequência | ✅ (lossy com quant.) | O(N log N) |
| DWT | Transformada | Multirresolução | ✅ | O(N) |
| PCA/KLT | Transformada | Direção de variância | ✅ (lossy com truncamento) | O(N·d²) |
| BPE/Gramática | Vocabulário | Repetições hierárquicas | ✅ | O(N) a O(N²) |
| LZ77/78 | Dicionário | Repetições exatas | ✅ | O(N) |
| Filtro EXE | Pré-proc. especializado | Padrões de instrução | ✅ | O(N) |
| Huffman | Codificação final | Distribuição de frequência | ✅ | O(N log σ) |
| Aritmético | Codificação final | Distribuição de probabilidade | ✅ | O(N) |
| ANS | Codificação final | Distribuição de probabilidade | ✅ | O(N) |
| Context mixing | Todo o pipeline | Múltiplos padrões | ✅ | O(N·k) (k modelos) |
| Autoencoder | Todo o pipeline (aprendido) | Padrões específicos dos dados | ✅ | Treino: alto; Inferência: médio |
| Takens embed | Análise | Dinâmica de atrator | ✅ | O(N·m) |
| UMAP | Análise | Manifold intrínseco | ~reversível | O(N^1.14) |

---

## Curvas de Preenchimento de Espaço — Catálogo Completo

### Propriedades de Localidade

| Curva | Ano | Localidade 2D | Custo de índice | Generalização nD | Caso de uso |
|-------|-----|--------------|----------------|-----------------|------------|
| **Hilbert** | 1891 | Excelente | O(log² N) | Sim (via Gray code) | Referência para localidade ótima |
| **Morton (Z-order)** | 1966 | Muito boa | O(1) (bit interleaving) | Sim | Alta performance, uso industrial |
| **Peano** | 1890 | Boa | O(log² N) | Sim | Referência histórica, base-3 |
| **Moore** | 1900 | Excelente (variante Hilbert) | O(log² N) | Sim | Loops fechados, bordas |
| **Sierpinski** | 1915 | Boa | Médio | Limitada | Dados com estrutura fractal |
| **Gosper (Flowsnake)** | 1970s | Boa-Excelente | Médio | Hexagonal | Grades hexagonais |
| **Lebesgue** | 1904 | Moderada | Rápido | Sim | Baseline teórico |
| **Gray-code** | 1953 | Muito boa (diferença mínima) | O(1) | Sim | Busca com mínima mudança |

### Localidade Formal

**Definição:** Uma curva f: [0,1]→[0,1]² tem boa localidade se:
para |t₁ - t₂| < ε, então ||f(t₁) - f(t₂)||₂ < δ(ε) com δ pequeno.

**Ranking empírico** (por número médio de clusters em range query):
```
Hilbert ≈ Moore > Gray-code > Morton/Z-order > Peano > Lebesgue > Raster
```

Hilbert ganha na maioria dos cenários, mas Morton é **ordens de magnitude mais rápido**
para calcular (operação bitwise vs. recursão). Na prática, a decisão é:
- Se localidade é crítica e custo de índice é tolerável → Hilbert
- Se throughput importa mais que localidade marginal → Morton
- Se os dados são hexagonais → Gosper
- Se precisa de loop fechado → Moore

---

## Compressão de Executáveis — Caso Detalhado

Um caso concreto da perspectiva 4 (remapear vocabulário):

### Estrutura de um binário x86

```
Opcode (1-3 bytes) | ModR/M (0-1) | SIB (0-1) | Displacement (0-4) | Immediate (0-4)
```

**Padrões exploráveis:**
1. **Opcodes frequentes:** MOV, PUSH, CALL, JMP dominam (~60% das instruções)
2. **Endereços de CALL:** Apontam para poucos targets (funções) → altamente repetitivos
3. **Registradores:** ESP, EBP em funções → padrão de prólogo/epílogo
4. **Zeros:** Padding de alinhamento, campos não usados

**Filtro BCJ (Branch/Call/Jump):** Converte offsets relativos em absolutos antes de comprimir.
Resultado: bytes de endereço ficam idênticos para mesmos targets → LZ/deflate captura melhor.

**Compressores especializados (kkrunchy, Crinkler):**
1. Disassembly parcial do binário
2. Separação de streams: opcodes, operandos, imediatos, dados
3. Cada stream comprimida com modelo próprio
4. Resultado: 50-70% redução vs. binário original

**Analogia com HSC:** O "vocabulário" de um executável são as instruções e seus padrões.
Remapear esse vocabulário (filtro BCJ) é análogo a remapear bytes via curva de Hilbert —
ambos buscam criar uma representação onde a redundância é mais visível.

---

## Implicações para o Projeto HSC

### Posicionamento da Contribuição

O HSC propõe curvas de Hilbert como **modelo de contexto probabilístico**. No mapa
das 6 perspectivas, isso se posiciona na interseção de:

```
Perspectiva 1 (remapear para visualizar)
    ∩
Perspectiva 3 (adaptação iterativa)
    ∩
Perspectiva 5 (múltiplas direções)
```

A curva de Hilbert:
1. **Remapeia** os dados 2D para 1D preservando localidade (P1)
2. O modelo de contexto **adapta** probabilidades símbolo a símbolo (P3)
3. O percurso recurso explora **múltiplas direções** na grade (P5)

### Extensões Naturais

1. **Perspectiva 4:** Antes de aplicar Hilbert, tokenizar os dados (BPE/gramática)
   para reduzir o alfabeto → modelo de contexto opera sobre tokens, não bytes.

2. **Perspectiva 6:** Integrar Hilbert como **um modelo** num sistema de context mixing,
   junto com BWT-ctx, LZ-ctx, e ordem-N tradicional. O mixer decide quando
   a perspectiva espacial do Hilbert é útil.

3. **Perspectiva 2:** Combinar Hilbert (localidade) com DWT (frequência) —
   primeiro aplicar Hilbert scan, depois wavelet nos coeficientes linearizados.
   A wavelet vê a suavidade que o Hilbert criou.

### Perguntas de Pesquisa Derivadas

| ID sugerido | Pergunta | Perspectiva |
|-------------|----------|-------------|
| Q-008 | O framework HSC cobre qual subconjunto das 6 perspectivas? | Meta |
| Q-009 | Hilbert como modelo num context mixer (multi-perspectiva) é viável? | P6 |
| Q-010 | Tokenização pré-Hilbert (BPE/gramática) melhora o modelo? | P4 |
| Q-011 | Hilbert + DWT em cascata produz ganho aditivo? | P2+P5 |

---

## Referências Técnicas

### Curvas de Preenchimento de Espaço
- Sagan, H. (1994). *Space-Filling Curves*. Springer.
- Bader, M. (2013). *Space-Filling Curves: An Introduction with Applications in Scientific Computing*. Springer.
- Mokbel et al. (2003). Analysis of multi-dimensional space-filling curves. *GeoInformatica* 7(3).

### Transformadas (DCT, DWT, KLT)
- Ahmed, N. et al. (1974). Discrete cosine transform. *IEEE Trans. Computers* C-23(1).
- Daubechies, I. (1992). *Ten Lectures on Wavelets*. SIAM.
- Karhunen, K. (1947). Über lineare Methoden in der Wahrscheinlichkeitsrechnung.

### Compressão por Gramática
- Nevill-Manning, C. & Witten, I. (1997). Identifying hierarchical structure in sequences. *JAIR* 7.
- Larsson, N.J. & Moffat, A. (2000). Off-line dictionary-based compression. *Proc. IEEE* 88(11).

### Context Mixing
- Mahoney, M. (2005). Adaptive weighing of context models for lossless data compression. Florida Tech.
- Knoll, B. & de Freitas, N. (2012). A machine learning perspective on predictive coding with PAQ8.

### Embedding e Topologia
- Takens, F. (1981). Detecting strange attractors in turbulence. *Springer Lecture Notes in Mathematics* 898.
- McInnes, L. et al. (2018). UMAP: Uniform Manifold Approximation and Projection. *arXiv:1802.03426*.

### Compressão de Executáveis
- Giesen, F. (2006). x86 code compression in kkrunchy. *The ryg blog*.

### Compressão Neural
- Ballé, J. et al. (2020). Nonlinear transform coding. *IEEE JSTSP* 15(2).
- Minnen, D. & Singh, S. (2020). Channel-wise autoregressive entropy models for learned image compression.
