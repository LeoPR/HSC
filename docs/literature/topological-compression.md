# 11 — Compressão Funcional Topológica

## Tese Central (Reformulação)

> **Compressão não é reduzir dados. É encontrar o espaço onde os dados são simples,
> descrever esse espaço e a função que o mapeia de volta ao original.**

O que guardamos não é o dado — é a **função homeomórfica** φ que transforma
um espaço compacto no espaço original dos dados. Decompressão é avaliar φ.

```
Compressão:    dados D  ──→  encontrar φ tal que φ(C) ≅ D
                             C = espaço compacto (feature space)
               guardar:  (descrição de C) + (descrição de φ)

Descompressão: φ(C)  ──→  D
               avaliar a função — sem armazenar D explicitamente
```

Isso transforma compressão em um problema de **análise funcional** e
**topologia diferencial**, não de codificação de símbolos. E torna o
resultado **independente do substrato computacional** — binário, analógico,
quântico, ou qualquer outro.

---

## Mapa de Conceitos

```
                    DADO ORIGINAL D
                         │
                         │  Análise topológica
                         ▼
              ┌─────────────────────┐
              │  Feature Space F    │  ← dimensão alta, não compacto
              │  (espaço original)  │
              └──────────┬──────────┘
                         │  Homeomorfismo φ⁻¹ (compressão)
                         ▼
              ┌─────────────────────┐
              │  Compact Space C    │  ← dimensão baixa, compacto
              │  (representação)    │
              └──────────┬──────────┘
                         │  Homeomorfismo φ (descompressão)
                         ▼
                    DADO ORIGINAL D

  O arquivo comprimido = descrição de C + descrição de φ
```

---

## Pilar 1 — Topologia como Linguagem de Compressão

### Por que Topologia?

Topologia é o estudo do que permanece invariante sob deformações contínuas.
Para compressão, isso é exatamente o que queremos: encontrar o que é
**essencial** nos dados (invariante) vs. o que é **acidental** (deformação).

**Homologia Persistente** mede features topológicas em múltiplas escalas:
- Componentes conectados (H₀) — "onde há blocos de dados similares?"
- Loops (H₁) — "onde há estrutura cíclica?"
- Cavidades (H₂) — "onde há vazios estruturais?"

O diagrama de persistência é uma representação compacta da topologia dos dados.
Features de alta persistência = estrutura real. Features de baixa persistência = ruído.

```
Diagrama de persistência como compressão:
  dados N-dimensionais  →  {(nascimento_i, morte_i)}  →  poucos pares
  compressão = descartar features de baixa persistência
  reconstrução = usar features remanescentes para guiar φ
```

### Hipótese do Manifold

Dados de alta dimensão não ocupam o espaço todo — vivem em manifolds de
dimensão muito menor. Esta é a **hipótese do manifold**, empiricamente
confirmada em imagens, texto, áudio, código genômico.

```
Imagem 256×256 = 65.536 dimensões (espaço ambiente)
Imagem natural vive em manifold d << 65.536
d é a "dimensão intrínseca" dos dados

Compressão ótima ≈ encontrar o manifold + φ: ℝ^d → ℝ^{65536}
```

A hipótese do manifold é a razão pela qual toda compressão funciona.
O projeto HSC está, implicitamente, explorando esta hipótese ao
perguntar: "qual topologia/dimensão é ótima para estes dados?"

### Autoencoders Topológicos

Autoencoders treinados com perda topológica (Hofer et al., 2019):

```
L_total = L_reconstrução + λ · L_topológica
L_topológica = distância entre diagramas de persistência
               de (espaço de entrada) e (espaço latente)
```

O encoder aprende φ⁻¹ (compressão) preservando a topologia.
O arquivo = pesos da rede = descrição de φ.

---

## Pilar 2 — Álgebra Fuzzy para Resíduos e Aproximações

### Por que Fuzzy?

Muitos dados têm **origem contínua**. Um sinal de áudio é uma onda contínua
amostrada; uma imagem é uma cena 3D projetada; dados tabulares são medições
de fenômenos analógicos. A quantização introduz uma perda irreversível —
mas essa perda tem **estrutura**: ela é suave, gradual, orientada pela
topologia do sinal original.

**Álgebra fuzzy** trabalha com graus de pertencimento ∈ [0,1] em vez de
crisp {0, 1}. Para compressão, isso significa:

```
Pertencimento crisp:   byte 0x3F pertence ao cluster A? Sim/Não
Pertencimento fuzzy:   byte 0x3F pertence ao cluster A com grau 0.87,
                       e ao cluster B com grau 0.12

O resíduo = (0.87, 0.12, ...)  ←  muito mais comprimível que o byte original
             └─ distribuição de pertencimento esparsa
```

### F-Transform (Transformada Fuzzy)

Proposta por Perfilieva (2006):

```
F-transform de f em relação a partição fuzzy {A₁, ..., Aₙ}:
  Fₖ = Σᵢ f(xᵢ) · Aₖ(xᵢ) / Σᵢ Aₖ(xᵢ)

Reconstrução (inversa):
  f̃(x) = Σₖ Fₖ · Aₖ(x)
```

Onde:
- `Aₖ` são funções de pertencimento (triângulos, gaussianas, etc.)
- `Fₖ` são os coeficientes F-transform — muito menos que os dados originais
- `f̃` é a reconstrução — exata no limite de partição densa

**Para compressão:** A F-transform guarda `{Fₖ}` (coeficientes) + `{Aₖ}` (base).
Se `n << N`, a compressão é real. A qualidade é controlada pela densidade da partição.

**Conexão com HSC:** A curva de Hilbert define uma partição implícita sobre o
espaço 2D — os blocos da curva são regiões de alta coerência local. A F-transform
pode ser aplicada sobre esses blocos, com `Aₖ` definindo a suavidade da transição.

### Conjuntos Rough (Rough Sets — Pawlak, 1982)

Para dados com imprecisão inherente, rough sets fornecem:

```
Aproximação inferior:  o que definitivamente pertence ao cluster
Aproximação superior:  o que possivelmente pertence ao cluster
Região de fronteira:   incerteza = superior - inferior

Compressão =   guardar {inferior, superior} em vez dos dados exatos
               fronteira = resíduo a comprimir separadamente
```

**Combinação Rough-Fuzzy:** A região de fronteira pode ter graus de pertencimento
fuzzy → rough-fuzzy clustering → compressão com dois níveis de precisão.

### Lógica Fuzzy como Ponte Contínuo-Discreto

A ideia central: dados discretos (binários) podem ser **levantados** para o
domínio fuzzy [0,1]ⁿ onde a estrutura contínua se torna visível, e depois
**rebaixados** de volta com residual esparso.

```
Dado binário:    0x3F = 0011 1111
                    ↓  (lifting)
Representação:   pertencimento fuzzy em bases contínuas
                    ↓  (análise no espaço contínuo)
Estrutura:       cluster, transições suaves, correlações
                    ↓  (lowering com residual)
Comprimido:      (id_cluster, residual_esparso)
```

O residual esparso captura o que a estrutura fuzzy não explica —
análogo ao `diff` no framework de dobragem (Q-010).

---

## Pilar 3 — Representações Implícitas Neurais (INR)

### A Ideia

Em vez de armazenar os valores de um sinal, armazenar a **função** que
mapeia coordenadas em valores:

```
Tradicional:    arquivo = {(x, y): valor(x,y)}   para cada pixel
INR:            arquivo = rede neural f_θ tal que f_θ(x,y) ≈ valor(x,y)
```

Os pesos θ da rede são o arquivo comprimido. Decompressão = inferência.

### SIREN (Sinusoidal Representation Networks — Sitzmann et al., 2020)

Arquitetura especial com ativações senoidais:

```
f_θ(x) = W_n · (sin(W_{n-1} · ... sin(W_1 · x + b_1) ... + b_{n-1})) + b_n
```

**Por que senos?** Derivadas de senos são senos — o mesmo tipo de função.
Isso significa que SIREN pode representar imagem, gradiente da imagem,
e Laplaciano da imagem com a mesma rede. Apropriado para sinais com estrutura
de frequência (quase tudo que existe na natureza).

**Resultados empíricos:**
- Imagens: 200× compressão com qualidade visual alta
- Volumes médicos (MRI): 2-3 ordens de magnitude
- Vídeo: competitivo com HEVC para baixas taxas de bits
- Simulações científicas: 200× em dados aeroespaciais

**A relação com homeomorfismo:** Os pesos θ são uma codificação do homeomorfismo
φ: ℝ² → ℝ (coordenadas → valores). O espaço compacto C é a variedade de
funções representáveis pela arquitetura SIREN. A compressão é encontrar φ ∈ C.

### Conexão com IFS (Compressão Fractal)

IFS (Iterated Function Systems — Barnsley, 1988) armazena transformações afins:

```
f(S) = ∪ᵢ wᵢ(S)    onde wᵢ são transformações afins contrácteis

Atrator A = lim_{n→∞} fⁿ(qualquer S inicial)
```

O arquivo = {w₁, w₂, ..., wₖ} — um punhado de transformações, não os dados.
Decompressão = iterar as transformações até convergir.

**Problema:** Codificação é cara (busca de transformações similares).
**Conexão com HSC:** A curva de Hilbert pode acelerar a busca de blocos similares
(os blocos adjacentes na curva são candidatos naturais para wᵢ → wⱼ).

### Hierarquia de Representações Funcionais

```
Menos expressivo ←──────────────────────────→ Mais expressivo

IFS (afim)  →  Gramática  →  SIREN (neural)  →  Turing-completo (K-complexity)

Cada nível consegue comprimir mais estrutura, mas requer mais para descrever φ.
O trade-off: complexidade de φ vs. compacidade de C.
```

---

## Pilar 4 — Independência de Substrato

### O Problema com Compressão Binária Clássica

Compressão binária clássica assume:
- Dado: sequência de bits (discreta, enumerável, finita)
- Cálculo: aritmética binária em CPU
- Saída: sequência de bits mais curta

Isso prende a compressão ao substrato computacional binário. Mas a estrutura
dos dados não é binária — ela é topológica, funcional, contínua.

### Entropia de Shannon vs. Entropia de Von Neumann

| | Shannon (clássico) | Von Neumann (quântico) |
|---|---|---|
| Estado | Distribuição de probabilidade | Matriz de densidade ρ |
| Entropia | H = -Σ pᵢ log pᵢ | S = -Tr(ρ log ρ) |
| Compressão | Até H bits/símbolo | Até S qubits/símbolo |
| Substrato | Bits clássicos | Qubits |

O **Teorema de Schumacher** (1995) é o análogo quântico do teorema de Shannon:
qubits de uma fonte quântica podem ser comprimidos até S qubits/símbolo
sem perda de informação quântica.

**Insight:** A compressão é um fenômeno mais fundamental que o substrato.
A estrutura matemática é a mesma — muda apenas o espaço em que opera.

### Teoria da Informação Algorítmica (AIT)

Kolmogorov-Solomonoff-Chaitin:

```
K(x) = comprimento do menor programa p tal que U(p) = x
       onde U = máquina de Turing universal

Compressão ótima (teórica) = K(x)
```

**AIT é independente de substrato** porque:
- "Programa" pode ser qualquer modelo computacional (Turing, lambda calculus,
  circuito analógico, sistema quântico)
- O teorema de invariância garante que K(x) difere em no máximo uma constante
  entre quaisquer dois modelos computacionais equivalentes

**Implicação:** O limite de compressão de um dado é uma propriedade do dado
em si, não do computador. Mudar para hardware analógico ou quântico não
muda K(x) — mas pode tornar o cálculo de φ mais eficiente.

### Entropia Diferencial (Fontes Contínuas)

Para dados de origem contínua:

```
h(X) = -∫ f(x) log₂ f(x) dx    (entropia diferencial)
```

**Diferença crítica:** h(X) não é invariante sob transformações de coordenadas
(ao contrário de H para fontes discretas). Isso significa:

```
Mudar o feature space muda a entropia diferencial →
Se φ: X → Y é uma transformação, h(Y) = h(X) + E[log|φ'(X)|]
O termo adicional é o log do jacobiano de φ
```

**Implicação para HSC:** A escolha da transformação φ (qual curva, qual espaço)
não é neutra para dados de origem contínua — ela afeta a entropia. Existe
uma φ* que minimiza h(φ(X)) para os dados. Encontrar φ* é a tarefa do compressor.

---

## Pilar 5 — Auto-Descrição e Autopoiese

### O Problema da Descompressão

Se o arquivo é uma função φ, como o decoder sabe:
- Que arquitetura neural usar?
- Que espaço C pressupor?
- Como avaliar φ?

**Solução:** O arquivo deve ser **auto-descritivo** — conter todas as informações
necessárias para sua própria decompressão.

### Abordagens Existentes

**MDL (Minimum Description Length — Rissanen, 1978):**
```
Comprimento total = L(modelo) + L(dados | modelo)
Melhor modelo = minimiza o total
```

O "modelo" é φ. Os "dados dado o modelo" são os resíduos.
MDL é exatamente o critério de compressão funcional.

**Formato F3 (Zeng et al., SIGMOD 2025):**
Cada arquivo contém:
- Os dados
- Metadados descrevendo o formato
- Binário WebAssembly (WASM) do decoder

O decoder está *dentro* do arquivo — nenhum software externo necessário.

**Códigos Auto-Delimitantes (Levin-Gács, 1974):**
Programas que carregam consigo a informação de onde terminam.
Eliminam a necessidade de saber o comprimento do código antes de decodificar.

### Autopoiese Aplicada a Compressão

Autopoiese (Maturana-Varela, 1972): sistemas que se auto-produzem e se
auto-mantêm — a célula gera os componentes necessários para continuar existindo.

**Compressão autopoiética (conceito):**

```
Arquivo autopoiético:
  - Contém φ (a função de reconstrução)
  - Contém a descrição de C (o espaço compacto)
  - Contém o decoder de φ
  - Contém metadados sobre o tipo de dado
  - Todos os componentes se descrevem mutuamente
```

O arquivo é um sistema fechado que se auto-explica. Dado qualquer sistema
computacional suficientemente geral (Turing-completo), o arquivo pode ser
decomprimido sem software externo.

### Estrutura do Arquivo Auto-Descritivo

```
┌──────────────────────────────────────────┐
│  HEADER (auto-delimitante)               │
│    versão do framework                   │
│    tipo de φ (SIREN, IFS, gramática, ...) │
│    dimensão de C                         │
│    métricas de qualidade                 │
├──────────────────────────────────────────┤
│  DESCRIÇÃO DE C                          │
│    topologia (diagrama de persistência)  │
│    dimensão intrínseca                   │
│    parâmetros fuzzy (se aplicável)       │
├──────────────────────────────────────────┤
│  PARÂMETROS DE φ                         │
│    pesos (se neural), regras (se gramát.)│
│    coeficientes (se F-transform)         │
│    transformações afins (se IFS)         │
├──────────────────────────────────────────┤
│  RESÍDUO ESPARSO                         │
│    o que φ(C) não captou exatamente      │
│    codificado com Golomb/Elias-delta     │
├──────────────────────────────────────────┤
│  DECODER (opcional, para portabilidade)  │
│    WASM ou bytecode mínimo para φ        │
└──────────────────────────────────────────┘
```

---

## Pilar 6 — Teoria das Categorias como Linguagem Unificadora

### Compressão como Funtor

Um esquema de compressão é um funtor F: **Data** → **Compact** que:
- Preserva estrutura essencial (morfismos relevantes)
- Descarta estrutura acidental

Descompressão é o funtor adjunto F⁻¹ (ou uma aproximação).

**Adjeção:** F ⊣ G significa que comprimir com F e descomprimir com G é
o melhor trade-off possível dado o espaço de compressores F.

### Entropia como Transformação Natural

Baez et al. (2011, 2023) mostram que a entropia de Shannon é uma
**transformação natural** entre funtores:

```
η: Prob ⟹ ℝ≥0
```

Onde Prob é a categoria de distribuições de probabilidade.
As propriedades da entropia (monotonicidade, aditividade, subaditividade)
seguem dos axiomas das transformações naturais.

**Implicação:** Diferentes tipos de entropia (Shannon, Rényi, Von Neumann)
são transformações naturais em diferentes categorias. A compressão ótima
é dependente de qual categoria o dado "pertence".

### Morfismos de Compressão

Compressores diferentes são morfismos entre esquemas:

```
φ_Huffman: Dados → CodigosHuffman
φ_Hilbert: Dados2D → DadosReordenados
φ_SIREN:  DadosCoordenadas → PesosRede

Natural transformation η: φ_Hilbert ⟹ φ_SIREN
    "Hilbert e SIREN são formas diferentes de explorar a mesma estrutura topológica"
```

---

## Síntese: O Framework HSC Ampliado

### Visão Original (antes deste documento)

```
HSC = curva de Hilbert como modelo de contexto Markov em dados 2D
```

### Visão Ampliada (após este documento)

```
HSC = instância de um framework geral de compressão funcional topológica:

1. Encontrar φ: C → F  (homeomorfismo compacto→original)
2. Descrever C (espaço compacto) com topologia persistente
3. Descrever φ com representação funcional (curva, rede, gramática, IFS)
4. Qualificar resíduos com álgebra fuzzy
5. Empacotar (C, φ, resíduo) em arquivo auto-descritivo

Hilbert/Morton/Peano = classes específicas de φ para dados 2D
Generalização:       φ pode ser qualquer homeomorfismo adequado ao dado
```

### O que cada componente do HSC atual mapeia para este framework

| Componente atual | No framework ampliado |
|-----------------|----------------------|
| `hilbert_order(side)` | Instância de φ para dados 2D |
| `choose_side(n)` | Busca de C ótimo (dimensão do espaço compacto) |
| `adaptive_order1_bits` | Proxy para h(φ(X)) — entropia diferencial após φ |
| Pipeline E (busca exaustiva) | Busca de φ* = argmin h(φ(X)) |
| `pt-br.tsv` teste | Confirma que φ_Hilbert ≠ φ* para dados 1D |

### Extensões Diretas

| Extensão | Componente a adicionar | Pergunta |
|----------|----------------------|----------|
| Fuzzy residuals | F-transform sobre blocos Hilbert | Q-012 |
| Homeomorfismo neural | SIREN como φ genérico | nova Q |
| Espaço C topológico | Homologia persistente para escolher C | Q-011 |
| Auto-descrição | Formato de arquivo auto-delimitante | Q-014 |
| Substrate-independence | Formulação em AIT | Q-013 |
| Dobragem aproximada | Elastic fold-XOR como classe de φ | Q-010 |

---

## Referências Essenciais

### Topologia e TDA
- Edelsbrunner & Harer (2010). *Computational Topology: An Introduction*. AMS.
- Carlsson, G. (2009). Topology and data. *Bull. AMS* 46(2), 255-308.
- Hofer, C. et al. (2019). Topologically regularized autoencoders. arXiv:1906.00722.
- Mapper: Singh, G. et al. (2007). Topological methods for the analysis of high dimensional data sets.

### Fuzzy e Rough Sets
- Chang, C.L. (1968). Fuzzy topological spaces. *J. Math. Anal. Appl.* 24(1).
- Lowen, R. (1976). Fuzzy topological spaces and fuzzy compactness. *J. Math. Anal. Appl.* 56.
- Perfilieva, I. (2006). Fuzzy transforms: Theory and applications. *Fuzzy Sets and Systems* 157(8).
- Pawlak, Z. (1982). Rough sets. *Int. J. Comput. Inf. Sci.* 11(5).

### Representações Funcionais
- Barnsley, M. & Demko, S. (1985). Iterated function systems and the global construction of fractals.
- Sitzmann, V. et al. (2020). Implicit neural representations with periodic activation functions. NeurIPS. arXiv:2006.09661.
- Ballé, J. et al. (2020). Nonlinear transform coding. *IEEE JSTSP* 15(2).

### Teoria da Informação Abstrata
- Kolmogorov, A.N. (1965). Three approaches to the quantitative definition of information. *Prob. Inf. Transm.* 1.
- Rissanen, J. (1978). Modeling by shortest data description. *Automatica* 14(5).
- Schumacher, B. (1995). Quantum coding. *Phys. Rev. A* 51(4).
- Cover, T. & Thomas, J. (2006). *Elements of Information Theory*. 2nd ed. Wiley.

### Teoria das Categorias e Informação
- Baez, J. & Fritz, T. (2014). A Bayesian characterization of relative entropy. *TAC* 29(16).
- Fong, B. & Spivak, D. (2019). *An Invitation to Applied Category Theory*. Cambridge UP.
- Fritz, T. (2020). A synthetic approach to Markov kernels. arXiv:1908.07021.

### Auto-Descrição e MDL
- Rissanen, J. (1983). A universal prior for integers and estimation by minimum description length.
- Gács, P. (1974). On the symmetry of algorithmic information. *Soviet Math. Doklady* 15.
- Maturana, H. & Varela, F. (1980). *Autopoiesis and Cognition*. D. Reidel.

### Amostragem e Contínuo-Discreto
- Shannon, C. (1949). Communication in the presence of noise. *Proc. IRE* 37(1).
- Candès, E. et al. (2006). Robust uncertainty principles: Exact signal reconstruction. *IEEE TIT* 52(2).
- Vetterli, M. et al. (2014). *Foundations of Signal Processing*. Cambridge UP.
