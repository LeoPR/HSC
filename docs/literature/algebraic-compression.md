# Compressão Algébrica — Mapa da Literatura

Famílias de compressão cujo motor principal é **álgebra** (linear, abstrata, geométrica, teoria de grupos), distintas de:

- estatística / codificação entrópica ([entropy-coding.md](entropy-coding.md))
- dicionário / reordenação simbólica ([symbol-reordering.md](symbol-reordering.md))
- transformadas de frequência ([frequency-transforms.md](frequency-transforms.md))
- compressão fractal ([fractal-compression.md](fractal-compression.md))
- topologia / fuzzy / INR ([topological-compression.md](topological-compression.md))

O traço comum às famílias deste documento: comprimem identificando **redundância estrutural/algébrica** (posto, simetria, pertencimento a ideal, estrutura de coset) em vez de redundância estatística.

---

## 1. Álgebra linear: decomposição tensorial e matricial

| Técnica | Ideia | Referência | Tipo | Dados alvo | Maturidade |
|---------|-------|-----------|------|-----------|------------|
| **Tucker** | Tensor N-way fatorado em core + matrizes modais ortogonais | Tucker (1966); De Lathauwer et al. (HOSVD, 2000), *SIMAX* | Lossy | Dados científicos multidim, hiperspectral, vídeo | Madura (TuckerMPI, TensorLy) |
| **CP / PARAFAC** | Soma de R produtos externos rank-1 | Harshman (1970); Kolda & Bader (2009), *SIAM Review* | Lossy | Quimiometria, neuroimagem, tensores de recomendação | Madura academicamente |
| **Tensor Train (TT)** | Cadeia de cores 3-way — quebra maldição da dimensionalidade | Oseledets (2011), *SIAM J. Sci. Comput.* | Lossy | Soluções de PDE, estados quânticos, parâmetros de NN | Madura em análise numérica |
| **Hierarchical Tucker** | Árvore binária de Tuckers — partição recursiva de dimensões | Hackbusch & Kühn (2009) | Lossy | Similar a TT, dados com estrutura em árvore | Acadêmica |
| **HOSVD** | Generalização N-dimensional de SVD | De Lathauwer et al. (2000) | Lossy | Imagens, dados tensoriais | Madura |
| **NMF** | V ≈ WH com W,H ≥ 0 — partes interpretáveis | Lee & Seung (1999), *Nature* | Lossy | Imagens (faces), texto (tópicos), espectrogramas | Madura |
| **CUR / skeleton** | Usa colunas e linhas reais da matriz, não base abstrata | Mahoney & Drineas (2009), *PNAS* | Lossy | Matrizes esparsas grandes, genômica, redes | Madura academicamente |
| **SVD aleatório / sketching** | Projeções aleatórias para aproximação de baixo posto | Halko, Martinsson, Tropp (2011), *SIAM Review* | Lossy | Matrizes em streaming | Madura |

---

## 2. Teoria algébrica de códigos aplicada a compressão

| Técnica | Ideia | Referência | Tipo | Dados alvo | Maturidade |
|---------|-------|-----------|------|-----------|------------|
| **Slepian–Wolf (syndrome)** | Comprime fontes correlacionadas via síndromes de código linear | Slepian & Wolf (1973), *IEEE TIT*; Pradhan & Ramchandran (DISCUS, 2003) | Lossless | Fontes distribuídas correlacionadas, sensores | Madura em distributed source coding |
| **Wyner–Ziv** | Extensão lossy do Slepian–Wolf com quantização lattice | Wyner & Ziv (1976) | Lossy | Vídeo distribuído (PRISM, DISCOVER) | Pesquisa |
| **LDPC para fonte** | Códigos paridade esparsa reutilizados como syndrome-former | Liveris, Xiong, Georghiades (2002), *IEEE CL* | Lossless | Fontes binárias correlacionadas | Acadêmica |
| **Reed–Solomon / BCH** | Avaliação polinomial em GF(q) para dados esparsos / estruturados | MacWilliams & Sloane (1977) | Lossless | Dados numéricos estruturados, vetores esparsos | Códigos: maduros; compressão: nicho |
| **Códigos AG** | Códigos em corpos de funções de curvas algébricas (Hermitian, etc) | Goppa (1981); Tsfasman, Vlăduţ, Zink (1982) | Lossless | Blocos longos estruturados | Acadêmica |
| **Goppa clássico (quantização)** | Quantização via cosets aninhados em códigos Goppa | Zamir, Shamai, Erez (2002), *IEEE TIT* | Lossy | Fontes gaussianas | Acadêmica |

---

## 3. Compressed sensing e recuperação esparsa

| Técnica | Ideia | Referência | Tipo | Dados alvo | Maturidade |
|---------|-------|-----------|------|-----------|------------|
| **Basis pursuit (L1)** | Recupera solução mais esparsa de y = Ax via min‖x‖₁ | Chen, Donoho, Saunders (2001); Candès & Tao (2005) | Lossy (reconstrução) | MRI, radar, sísmica, hiperspectral | Produção (MRI vendors) |
| **RIP** | Condição sobre matrizes aleatórias que garante recuperação exata | Candès, Romberg, Tao (2006), *IEEE TIT* | Teoria | — | Fundacional |
| **OMP / CoSaMP / IHT** | Algoritmos greedy / thresholding iterativo | Tropp & Gilbert (2007); Needell & Tropp (2009) | Lossy | Sinais esparsos | Madura |
| **Structured CS** | Grupo-esparso, baixo posto, árvore-esparso | Baraniuk et al. (2010), *IEEE TIT* | Lossy | Imagens, vídeo, matrix completion | Pesquisa madura |

---

## 4. Teoria de grupos e representações

| Técnica | Ideia | Referência | Tipo | Dados alvo | Maturidade |
|---------|-------|-----------|------|-----------|------------|
| **Equivariância / invariância** | Guarda apenas um representante canônico por órbita do grupo G | Cohen & Welling (2016), *ICML* (G-CNNs); Kondor & Trivedi (2018) | Lossy/Lossless | Moléculas, cristais, grafos, formas 3D | Pesquisa ativa |
| **Fourier em grupos** | Generaliza DFT para grupos não-abelianos (Sₙ, SO(3)) | Diaconis (1988); Rockmore (2004) | Lossy | Dados de ranking, sinais esféricos, rotacionais | Acadêmica |
| **Harmônicos esféricos / Wigner D** | Base de representação irredutível de SO(3) | Driscoll & Healy (1994), *Adv. Appl. Math.* | Lossy | Mapas ambiente, BRDFs, cryo-EM, dados climáticos | Madura em gráficos / sci-comp |
| **Grafos via automorfismos** | Codifica grafo módulo grupo de automorfismos | McKay (1981) nauty; Choi & Szpankowski (2012) | Lossless | Grafos, redes | Acadêmica |
| **Lehmer / permutações** | Sequências codificadas via estrutura do grupo simétrico | Lehmer (1960) | Lossless | Permutações, rankings | Nicho |

---

## 5. Polinomial e geometria algébrica

| Técnica | Ideia | Referência | Tipo | Dados alvo | Maturidade |
|---------|-------|-----------|------|-----------|------------|
| **Interpolação (Lagrange/Newton)** | N amostras de polinômio grau N → N+1 coeficientes | Clássico; Shamir secret sharing (1979) | Lossless no modelo | Dados científicos suaves, corpos finitos | Ferramenta matemática |
| **Prony / soma de exponenciais** | Sinal modelado como soma de K exponenciais complexas | Prony (1795); Potts & Tasche (2013) | Lossy | Séries temporais, NMR, radar | Madura |
| **Curvas/superfícies algébricas** | Ajusta f(x,y,z)=0 implícita a nuvem de pontos | Taubin (1991), *PAMI*; Tasdizen et al. (2000) | Lossy | Point clouds 3D, formas, contornos | Acadêmica / CAD |
| **Multigrid / bases polinomiais hierárquicas** | Hierarquia Chebyshev / Legendre para campos de PDE | Xu (1992); métodos spectral-element | Lossy | Dados de simulação | Madura em sci-comp |
| **Finite Rate of Innovation** | Sinais com K graus de liberdade recuperáveis de 2K amostras | Vetterli, Marziliano, Blu (2002), *IEEE TSP* | Lossy | Streams de pulsos, biossinais | Pesquisa |

---

## 6. Reticulados (lattices), módulos e anéis

| Técnica | Ideia | Referência | Tipo | Dados alvo | Maturidade |
|---------|-------|-----------|------|-----------|------------|
| **Quantização em reticulados (E₈, Leech, Dₙ)** | Quantizador é um grupo/reticulado, cobertura ótima | Conway & Sloane (1988); Gersho & Gray (1992) | Lossy | Áudio, fala, vetores genéricos | Produção (MPEG-4 ALS, G.719) |
| **Reticulados aninhados (Voronoi)** | Coarse lattice dentro de fine lattice para source-channel | Zamir, Shamai, Erez (2002) | Lossy | Fontes gaussianas, MIMO | Acadêmico → aplicado |
| **Códigos de grupo em anéis (Z₄, Z_pᵏ)** | Códigos como subgrupos de módulos sobre anéis finitos | Hammons et al. (1994) (Z₄-linearity) | Lossless | Sequências estruturadas | Acadêmica |
| **Module-LWE (cripto)** | Compressão de ciphertexts via modulus switching | Regev (2005); Kyber (Bos et al. 2018) | Lossy | Dados valorados em lattice (pós-quântico) | Padronizada |

---

## 7. Frentes menos óbvias

| Técnica | Ideia | Referência | Tipo | Dados alvo | Maturidade |
|---------|-------|-----------|------|-----------|------------|
| **Grassmanniano / Stiefel** | Representa subespaços como pontos em manifolds, quantiza com métrica chordal | Barg & Nogin (2002); Dai, Liu, Rider (2008) | Lossy | Subespaços, beamforming, dicionários CS | Acadêmica |
| **Gröbner / ideais polinomiais** | Conjunto gerador mínimo de ideal = variedade algébrica comprimida | Buchberger (1965); Cox, Little, O'Shea (1992) | Lossless no variety | Dados simbólicos, sistemas de restrições | Acadêmica (CAS) |
| **Momentos / Christoffel** | Medidas/formas via sequência finita de momentos; reconstrução Hankel/Toeplitz | Lasserre (2001); Schmüdgen (2017) | Lossy | Distribuições, formas | Acadêmica |
| **Feixes / módulos de persistência** | Apresentação mínima de módulos graduados k[t] | Carlsson & Zomorodian (2005); Bubenik (2015) | Lossless no módulo | TDA, sensores | Pesquisa ativa |
| **Quiver / representações de grafos** | Decomposição canônica (Gabriel) de representações | Gabriel (1972); Derksen & Weyman (2017) | Lossless | Redes com nós/arestas tipados | Fronteira acadêmica |
| **Tropical / semianéis idempotentes** | Álgebra (min,+)/(max,+) para estruturas piecewise-linear | Maclagan & Sturmfels (2015) | Lossy/lossless | Funções PL, ReLU nets, scheduling | Emergente |

---

## Posicionamento em relação ao HSC

### O que já é coberto por outros docs do projeto

| Tema | Doc do projeto |
|------|----------------|
| SVD / KLT / PCA como mudança de base | [feature-space.md §P2](feature-space.md) |
| Álgebra fuzzy | [topological-compression.md Pilar 2](topological-compression.md) |
| Kernel trick (Hilbert space no sentido analítico) | [Q-015](../../evaluations/open/Q-015_kernel-trick-feature-space-compressao.md) |
| Homeomorfismos como compressão | [Q-011](../../evaluations/open/Q-011_homeomorfismo-topologico-como-compressao.md) |
| Compressão por fold-XOR (generalização de LZ/BWT/Hilbert como σ) | [Q-010](../../evaluations/open/Q-010_compressao-por-dobragem-xor-simetria.md) |

### O que é território novo

1. **Tensor Train / Hierarchical Tucker** — generaliza a ambição multidimensional do HSC. Compressão por baixo posto multilinear é ortogonal a SFC: SFC reordena, TT fatora.
2. **Syndrome coding (Slepian–Wolf / Wyner–Ziv)** — compressão via cosets de código linear. Diferente de qualquer coisa no TBC.
3. **Compressão equivariante** — quociente por grupo de simetria. Natural para dados com simetrias (moléculas, grafos, imagens com invariância rotacional).
4. **Quantização em reticulados (E₈, Leech)** — compressão geométrica pura, produção em codecs de áudio.
5. **Apresentação mínima de módulos de persistência** — algébrico-topológico, espelha o Pilar 1 do topological-compression.md mas pelo lado algébrico.
6. **Fronteiras**: quiver, Gröbner, tropical — abstrato, pouco explorado em compressão de dados genéricos.

### Onde pode pegar para o HSC

Três candidatos naturais, cada um com motivação distinta:

**(a) Tensor Train como evolução direta do HSC.**
HSC olha para dados N-D através de SFC (reordenação 1D preservando localidade). TT olha para dados N-D através de fatorização multilinear (baixo posto por dimensão). São técnicas **complementares**: SFC reordena, TT fatora. A combinação "TT sobre coordenadas reordenadas por Hilbert" é, até onde este levantamento foi, território pouco explorado.

**(b) Syndrome coding como formalização do "banco complementar" (Q-016).**
A ideia do Q-016 — "representantes canônicos + resíduos esparsos" — tem uma formulação algébrica natural via cosets: escolha de um código linear define os representantes (cosets) e os resíduos (elementos do coset). Slepian–Wolf é exatamente isso, mas para fontes distribuídas. Pode ser adaptado para single-source.

**(c) Módulos de persistência como ponte com topologia.**
O Pilar 1 de `topological-compression.md` menciona homologia persistente. Módulos de persistência são a visão **algébrica** do mesmo objeto. Comprimir via apresentação mínima do módulo é uma instanciação concreta do framework homeomorphism φ: C → D.

---

## O que **não** é compressão algébrica, embora pareça

- DCT / DWT / FFT são transformadas com suporte algébrico mas sua função primária é energia-concentração via ortogonalidade, já cobertas em [frequency-transforms.md](frequency-transforms.md).
- Huffman / aritmética são codificadoras estatísticas — a "base" usada não é algébrica.
- Compressão fractal usa transformações afins (álgebra de matrizes 2×2) mas o motor é auto-similaridade, não álgebra estrutural. Cobertas em [fractal-compression.md](fractal-compression.md).

---

## Referências essenciais para leitura inicial

- **Kolda & Bader (2009).** Tensor decompositions and applications. *SIAM Review* 51(3). → survey canônico de tensor decomposition.
- **Conway & Sloane (1988).** *Sphere Packings, Lattices and Groups*. Springer. → compêndio de quantização em reticulado.
- **Candès & Tao (2005).** Decoding by linear programming. *IEEE TIT*. → base de compressed sensing.
- **MacWilliams & Sloane (1977).** *The Theory of Error-Correcting Codes*. North-Holland. → álgebra de códigos lineares, base para Slepian–Wolf.
- **Cox, Little, O'Shea (1992).** *Ideals, Varieties, and Algorithms*. Springer. → álgebra computacional (Gröbner).
- **Carlsson & Zomorodian (2005).** Computing persistent homology. *Discrete Comput. Geom.* → módulos de persistência.
- **Rockmore (2004).** Recent progress and applications in group FFTs. *Comput. Sci. Eng.* → Fourier em grupos.
