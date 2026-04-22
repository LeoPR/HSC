# Fatoração Numérica como Compressão

Família de técnicas que **interpretam uma sequência binária como um objeto matemático** (polinômio, inteiro, sequência linear-recorrente) e a comprimem via decomposição algébrica — tipicamente fatoração.

A tese subjacente: **se uma sequência tem estrutura interna (periodicidade, auto-similaridade, geração por recorrência), essa estrutura aparece como uma fatoração simples em algum anel apropriado**. O arquivo comprimido guarda os fatores, não a sequência.

Esta é uma especialização de [algebraic-compression.md](algebraic-compression.md) com foco em "como mapear bits para um ambiente algébrico fatorável".

---

## Três interpretações

### (a) Sequência como polinômio em GF(2)\[x\]

A interpretação mais direta: bits `b_0 b_1 … b_{N-1}` viram coeficientes de um polinômio `f(x) = b_0 + b_1 x + b_2 x² + … + b_{N-1} x^{N-1}` sobre o corpo finito **GF(2)** (aritmética módulo 2).

- Soma: XOR.
- Multiplicação: AND + XOR de deslocamentos.
- Fatoração em GF(2)\[x\] é **polinomial no tempo** (Berlekamp, Cantor-Zassenhaus).

Se `f(x) = p(x) · q(x)` e `deg(p) + deg(q) < deg(f)` (contando representação), temos compressão. Mas o custo real do header (lista de fatores + expoentes) tem que caber no ganho.

### (b) Sequência como saída de um LFSR mínimo

Dada uma sequência `s`, existe um polinômio de feedback `C(x)` de menor grau L tal que um LFSR com `C(x)` e um estado inicial de L bits produz exatamente `s`. O par `(C(x), estado)` tem `2L` bits. Se `L ≪ N`, compressão massiva.

O **algoritmo de Berlekamp–Massey** encontra `C(x)` e L em tempo O(N²). Ele é o "fatorador de sequências" por excelência.

### (c) Sequência como inteiro a fatorar

`b_0 b_1 … b_{N-1}` interpretado como inteiro `n = Σ b_i · 2^i`. Fatoração em primos `n = p_1^{a_1} · … · p_k^{a_k}`.

Pouco prático para compressão genérica:
- Fatoração de inteiros é **presumidamente fora de P** (base de RSA).
- Fatoração típica de N bits produz fatores ainda grandes.
- Número com muitos fatores pequenos é **raro**.

Fica como curiosidade conceitual, não linha de ataque.

---

## Conceitos-chave

### Complexidade linear de uma sequência

Definição: `L(s)` = grau do menor LFSR que gera `s`. Equivalentemente, grau do **polinômio mínimo** `C(x)` de `s` sobre GF(2).

Propriedades:

- `L(s) ≤ N/2` pelo teorema da iteração de Berlekamp–Massey (acima disso, BM tem evidência de que nada mais reduz).
- Sequências aleatórias independentes têm `L(s) ≈ N/2`: incompressíveis neste sentido.
- Sequências periódicas com período p dividindo 2^k − 1 têm `L(s) = k`: compressíveis a `~2k` bits.
- Sequências constantes têm `L(s) = 1`.

### Berlekamp–Massey: o "fatorador de sequências"

Dado `s` de comprimento `N`, retorna:
1. Complexidade linear `L(s)`.
2. Polinômio de conexão `C(x) = 1 + c_1 x + … + c_L x^L` sobre GF(2).
3. Estado inicial de `L` bits.

Pseudocódigo informal:

```
inicializa C(x) = 1, B(x) = 1, L = 0, m = -1, b = 1
para n = 0 até N-1:
    d = s_n + Σ_{i=1..L} c_i · s_{n-i}   (em GF(2))
    se d == 0:
        continue
    T(x) = C(x)
    C(x) = C(x) + (d/b) · x^{n-m} · B(x)
    se 2L <= n:
        L = n + 1 - L
        m = n
        B(x) = T(x)
        b = d
retorna C(x), L
```

Complexidade: O(N²) em operações de GF(2). Existem variantes O(N log² N) via FFT sobre GF(2).

### Polinômios ciclotômicos sobre GF(2)

A fatoração de `x^n − 1` sobre GF(2) é o esqueleto de toda repetição cíclica:

```
x^n − 1 = ∏_{d | n} Φ_d(x)   (sobre ℚ)
```

Sobre GF(2), cada `Φ_d(x)` fatora em polinômios irredutíveis de grau igual à **ordem multiplicativa de 2 módulo d**. Tabelas para `n ≤ 31` são clássicas na literatura de códigos cíclicos.

Implicação para compressão: uma sequência estritamente periódica com período `p` divisor de `n` é gerada por um fator de `x^n − 1`. O polinômio mínimo é sempre divisor de `x^p − 1`.

### m-sequências e polinômios primitivos

Um polinômio `C(x)` de grau `k` é **primitivo** se for o polinômio mínimo de um elemento gerador de GF(2^k). Um LFSR com polinômio primitivo de grau `k` e estado inicial não-zero produz sequência de período máximo `2^k − 1`.

Exemplo: `C(x) = 1 + x + x⁴` é primitivo de grau 4 → período 15. Os 15 bits da m-sequência são representados por `(1+x+x⁴, estado inicial)` = 4 bits de polinômio + 4 bits de estado = **8 bits comprimem 15 bits** (razão ~1.9x).

Para k=16: período 65535. Compressão para 32 bits = **razão ~2048x** nesse caso específico.

Mas cuidado: isto só vale se a sequência **for** uma m-sequência. Sequências arbitrárias em geral não têm estrutura LFSR compacta.

---

## Exemplo trabalhado

### Sequência periódica simples

`s = 1 0 1 0 1 0 1 0 1 0` (10 bits, período 2)

Como polinômio: `f(x) = 1 + x² + x⁴ + x⁶ + x⁸`

Fatoração sobre GF(2):

```
f(x) = 1 + x² + x⁴ + x⁶ + x⁸
     = (1 + x)⁸   em GF(2) (pois característica 2 — lifting)
```

Hmm, verificando: `(1 + x)² = 1 + x²` em GF(2). Então `(1+x)⁸ = 1 + x⁸`, que não é f(x). Recontando.

Na verdade: `1 + x² + x⁴ + x⁶ + x⁸ = (x^{10} − 1)/(x² − 1)` sobre ℚ. Em GF(2) fica `(x^{10} + 1)/(x² + 1)`.

`x^{10} + 1 = (x+1)^2 · (x⁴ + x³ + x² + x + 1)² ` em GF(2).

`x² + 1 = (x+1)²`.

Logo `f(x) = (x⁴ + x³ + x² + x + 1)²` — um quadrado perfeito.

Representação comprimida (conceitual): armazenar `(x⁴ + x³ + x² + x + 1)² ` como `(polinômio de grau 4, expoente 2)` — 5 bits do polinômio + algum bit do expoente = ~7 bits comprimindo 10 bits. Ganho modesto, mas o exemplo é microscópico.

### O mesmo pela lente de Berlekamp–Massey

BM aplicado a `s = 1010101010` produz:

```
C(x) = 1 + x²,  L = 2,  estado inicial = "10"
```

Representação comprimida: 2 bits do polinômio (além do termo constante, que é sempre 1) + 2 bits de estado = 4 bits.

**4 bits comprimindo 10 bits — razão 2.5x.**

A versão BM é mais econômica porque não armazena a fatoração completa — armazena apenas a recorrência mínima.

### Sequência aleatória

`s = 1 0 1 1 0 0 1 0 1 1` (10 bits aparentemente aleatórios)

BM neste caso pode retornar `L = 5` (metade do comprimento). Representação comprimida: `~10 bits`. Sem ganho.

Isto é o comportamento honesto: **sequências com estrutura → compressão algébrica alta; sequências sem estrutura → nenhum ganho**.

---

## Algoritmos de fatoração em GF(2)\[x\]

| Algoritmo | Complexidade | Função |
|-----------|--------------|--------|
| **Berlekamp (1967)** | O(n³) clássico | Primeiro algoritmo em tempo polinomial para fatoração em GF(q) |
| **Cantor–Zassenhaus (1981)** | O(n²·⁵·⁶) probabilístico | Algoritmo padrão moderno; baseado em distinct-degree + equal-degree factorization |
| **Kaltofen–Shoup (1998)** | O(n^{1.815}) probabilístico | Estado da arte em expoente |
| **Berlekamp–Massey (1968/69)** | O(n²) | Encontra **polinômio mínimo** de uma sequência — não o mesmo que fatoração geral, mas resolve o problema de compressão via LFSR |
| **Massey–Schaub (1988)** | O(n²) | Extensão do BM para corpos maiores |

Para fins de compressão, **Berlekamp–Massey é o algoritmo que importa**. Os outros (Cantor-Zassenhaus etc.) são para quando queremos fatorar um polinômio dado, não para extrair o polinômio mínimo de uma sequência.

---

## Quando vence, quando perde

**Vence:**

- Sequências periódicas (período curto)
- Sequências linear-recorrentes (como saídas de LFSR ou geradores congruenciais)
- Sequências com estrutura cíclica ou auto-similar
- Sinais amostrados de sistemas dinâmicos lineares

**Empata ou perde:**

- Sequências i.i.d. de alta entropia (linear complexity ≈ N/2)
- Sequências com estrutura **não-linear** (ex: saída de filtros não-lineares, texto natural)
- Sequências curtas onde o custo do header domina

**Observação importante:** BM produz um polinômio mínimo **exato** para a sequência dada. Se a sequência tem um "erro" (1 bit diferente do padrão esperado), a complexidade linear pode explodir. Extensões robustas:

- **k-error linear complexity** (Stamp & Martin 1993): menor complexidade linear alcançável trocando até k bits. Compressão lossy.
- **Modified Berlekamp-Massey** (Lauder & Paterson 2003): aproxima k-error LC.

---

## Conexões

### Com códigos cíclicos

Códigos cíclicos (BCH, Reed-Solomon) são **projetados** em torno da fatoração de `x^n − 1`. O gerador do código é um divisor dessa fatoração. A teoria é a mesma: compressão e correção de erros são duais neste anel polinomial.

### Com criptografia de fluxo

A complexidade linear é uma **medida de segurança**: um bom gerador pseudo-aleatório deve ter complexidade linear alta. BM é a ferramenta clássica de análise.

Para compressão esta relação diz o contrário: sequências "seguras" são **incompressíveis** por este método. O compressor trabalha bem exatamente onde o criptógrafo falhou.

### Com complexidade de Kolmogorov

A complexidade linear é uma **aproximação linear** da complexidade de Kolmogorov. Se a sequência tem um programa curto que **é** um LFSR, BM encontra. Se o programa não é linear, BM superestima.

Isso coloca a fatoração numérica como **caso particular** da compressão funcional topológica ([topological-compression.md](topological-compression.md) Pilar 3): a função `φ` aqui é o LFSR — um sistema dinâmico linear.

### Com o TBC

O TBC v1 (planos indicadores por frequência) não opera em GF(2)\[x\] — opera sobre contagens estatísticas. São ortogonais.

Mas há uma conexão interessante: **os planos do TBC são eles mesmos sequências binárias**, e podem ser alimentados em BM para checar se têm estrutura linear-recorrente. Isso é recursão algébrica (não a recursão estatística que testamos em [v1_recursive.md](../../techniques/TBC/v1_recursive.md)).

---

## Posicionamento em relação ao HSC

A pergunta "existe um ambiente numérico fatorável em que a sequência se represente por repetição?" tem uma resposta concreta e clássica: **GF(2)\[x\] com Berlekamp–Massey**.

Isto é território novo para o projeto:

- Não coberto por `frequency-transforms.md` (DCT/DWT não envolvem fatoração)
- Não coberto por `space-filling-curves.md` (reordenação sem fatoração)
- Não coberto por `symbol-reordering.md` (BWT é permutação, não fatoração)
- Mencionado tangencialmente em `algebraic-compression.md` §2 (Reed-Solomon, códigos AG) mas sem foco em compressão pura

### Caminhos possíveis

1. **Experimento mínimo TBC-adjacente:** implementar BM em Python e aplicá-lo aos planos do v1 recursivo para checar se os planos têm estrutura linear-recorrente escondida. Hipótese: se tivessem, a recursão estatística teria convergido antes. Testar confirma ou refuta.

2. **BM como baseline experimental:** aplicar BM a `xargs.1` (4227 bytes = 33816 bits) e ver qual é `L(s)` para texto natural. Conjectura: `L ≈ N/2`, ou seja, texto natural é "não-linear" no sentido de BM.

3. **Ideia combinatória:** fatorar a sequência localmente (janelas de N bits), obter `L_local` para cada janela, codificar apenas a sequência de `L_local`s — que pode ser muito menor. Isto é um "perfil de linearidade" como feature.

4. **Conexão com fold-XOR (Q-010):** a operação XOR de dobragem é exatamente a operação de GF(2). O framework fold-XOR pode ser reinterpretado como busca de fatores em GF(2)\[x\] — se duas metades são iguais sob σ, seu XOR é zero, e isso significa que o polinômio da sequência completa é divisível por um fator específico.

---

## Referências essenciais

- **Berlekamp, E.R. (1968).** *Algebraic Coding Theory*. McGraw-Hill. → o livro-base; capítulo sobre decodificação de BCH introduziu BM implicitamente.
- **Massey, J.L. (1969).** Shift-register synthesis and BCH decoding. *IEEE Trans. Inf. Theory* 15(1). → artigo canônico que deu o nome ao algoritmo.
- **Cantor, D.G. & Zassenhaus, H. (1981).** A new algorithm for factoring polynomials over finite fields. *Math. Comp.* 36(154). → fatoração rápida em GF(q).
- **Kaltofen, E. & Shoup, V. (1998).** Subquadratic-time factoring of polynomials over finite fields. *Math. Comp.* 67(223). → estado da arte teórico.
- **Stamp, M. & Martin, C.F. (1993).** An algorithm for the k-error linear complexity of binary sequences. *IEEE Trans. Inf. Theory* 39(4). → extensão robusta do BM.
- **MacWilliams, F.J. & Sloane, N.J.A. (1977).** *The Theory of Error-Correcting Codes*. North-Holland. → polinômios ciclotômicos, códigos cíclicos, contexto amplo.
- **Golomb, S.W. (1967/1982).** *Shift Register Sequences*. Aegean Park Press. → m-sequências, polinômios primitivos.
- **Shoup, V. (2008).** *A Computational Introduction to Number Theory and Algebra*. Cambridge UP. → livro aberto e moderno cobrindo toda a máquina.

Sites úteis:

- Wikipedia: [Berlekamp–Massey algorithm](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm)
- Wikipedia: [Factorization of polynomials over finite fields](https://en.wikipedia.org/wiki/Factorization_of_polynomials_over_finite_fields)
- Calculadora online: [BM online](https://berlekamp-massey-algorithm.appspot.com/)

Sources:
- [Berlekamp–Massey algorithm - Wikipedia](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm)
- [Factorization of polynomials over finite fields - Wikipedia](https://en.wikipedia.org/wiki/Factorization_of_polynomials_over_finite_fields)
- [Berlekamp–Massey algorithm (SpringerLink)](https://link.springer.com/referenceworkentry/10.1007/978-1-4419-5906-5_335)
- [An Online Calculator of Berlekamp-Massey Algorithm](https://berlekamp-massey-algorithm.appspot.com/)
- [Chapter 8: Cyclic Codes - Caltech lecture notes](https://home.work.caltech.edu/~ling/webs/EE127/EE127A/handout/Ch8.pdf)
- [Galois Fields and Cyclic Codes - XMission](http://user.xmission.com/~rimrock/Documents/Galois%20Fields%20and%20Cyclic%20Codes.pdf)
