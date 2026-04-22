# Literatura — Base Bibliográfica

Notas técnicas sobre famílias consolidadas de compressão. Não contém contribuições originais do HSC — apenas síntese de material existente para fundamentar decisões e posicionar o trabalho.

---

## Documentos (índice)

| Documento | Tema |
|-----------|------|
| [space-filling-curves.md](space-filling-curves.md) | Hilbert, Morton/Z-order, Peano — curvas e propriedades de localidade |
| [frequency-transforms.md](frequency-transforms.md) | DCT, DWT, KLT/PCA — concentração de energia em bases ortogonais |
| [symbol-reordering.md](symbol-reordering.md) | BWT, MTF, RLE — reorganização simbólica |
| [entropy-coding.md](entropy-coding.md) | Huffman, aritmética, ANS — codificação final |
| [fractal-compression.md](fractal-compression.md) | IFS/PIFS — auto-similaridade |
| [feature-space.md](feature-space.md) | Taxonomia das 6 perspectivas sobre transformação de espaço de features |
| [topological-compression.md](topological-compression.md) | Homeomorfismo, topologia persistente, fuzzy, INR, AIT |
| [algebraic-compression.md](algebraic-compression.md) | Tensor decomposition, syndrome coding, CS, grupos, reticulados |
| [numerical-factorization.md](numerical-factorization.md) | GF(2)\[x\], Berlekamp–Massey, complexidade linear, LFSR mínimo |
| [top-performers-strategies.md](top-performers-strategies.md) | Rankings (LTCB, Silesia) e as 5 estratégias dominantes |

---

## Leitura mínima por perfil

**Orientação geral do projeto (3 docs):**
1. `space-filling-curves.md` — ponto de partida histórico do HSC
2. `feature-space.md` — por que SFC é instância de algo mais geral
3. `topological-compression.md` — enquadramento abstrato unificador

**Para posicionar em relação ao estado da arte:**
1. `top-performers-strategies.md` — o que efetivamente ganha
2. `entropy-coding.md` — base comum a todos os codecs
3. `feature-space.md` — onde o HSC se diferencia

**Para território algébrico / numérico:**
1. `numerical-factorization.md` — mais próximo de "compressão via fatoração"
2. `algebraic-compression.md` — mapa amplo
3. `topological-compression.md` — conexão algebra-topologia

---

## Vista transversal 1 — Por estratégia de operação

Como o compressor trabalha internamente.

| Estratégia | Documento(s) | Técnicas representativas |
|------------|--------------|--------------------------|
| **Predição de símbolo** | top-performers, entropy-coding | PPM, Context Mixing, Neural LM, NNCP, cmix |
| **Dicionário / referência** | top-performers | LZ77, LZ78, LZMA, LZ4, zstd, brotli |
| **Reordenação simbólica** | symbol-reordering, space-filling-curves | BWT, MTF, Hilbert, Morton, Peano |
| **Transformada de base** | frequency-transforms, algebraic-compression | DCT, DWT, KLT/PCA, SVD, HOSVD, Tucker, TT |
| **Codificação entrópica final** | entropy-coding | Huffman, aritmética, range coding, ANS, rANS |
| **Auto-similaridade / funcional** | fractal-compression, topological-compression | IFS, PIFS, SIREN, autoencoders, INR |
| **Fatoração algébrica** | numerical-factorization, algebraic-compression | Berlekamp–Massey, tensor decomposition, Gröbner, AG-codes |
| **Quantização estruturada** | algebraic-compression | Lattice VQ (E₈, Leech), nested lattices |
| **Sparse recovery** | algebraic-compression | Compressed sensing, L1, OMP |
| **Quociente por simetria** | algebraic-compression | Equivariantes, grupo de automorfismos, Lehmer |

---

## Vista transversal 2 — Por razão de compressão típica

Ordens de grandeza aproximadas em texto natural (enwik9, 1 GB). Para outros domínios os valores mudam, mas a ordenação relativa é estável.

| Faixa | Razão típica | Exemplos | Custo computacional |
|-------|--------------|----------|---------------------|
| **Teto teórico** | ~14x (Shannon bound para texto) | — | — |
| **LLM-based** | 9–11x (ainda requer modelo externo) | NNCP v3.2, ts_zip RWKV | Dias CPU / horas GPU |
| **Context mixing neural** | 9–10x | cmix v21, fx2-cmix, starlit | Dias CPU |
| **Context mixing clássico** | 7–8x | paq8px, lpaq9m, zpaq | Horas a dias |
| **PPM avançado** | 6–7x | durilca, PPMII | Minutos |
| **LZMA / XZ** | 4–5x | xz -9, LZMA2 | Minutos |
| **Brotli / LZ modernos** | 3.5–4.5x | brotli -11, zstd -22 | Segundos |
| **LZ77 rápido** | 3–3.5x | gzip -9, deflate | Segundos |
| **Huffman puro** | 1.8–2x | (sem dicionário) | Sub-segundo |
| **SFC / BWT sozinhos** | 1.0x ou pior | raster, Hilbert, Morton, BWT cru | Sub-segundo |
| **RLE puro** | 1.0x em texto, 10–100x em runs | — | Trivial |

Observação importante: as últimas três linhas são **preprocessadores**, não compressores finais. Fazem sentido apenas compostos com codificador entrópico posterior.

---

## Vista transversal 3 — Linha do tempo evolutiva

| Período | Marco | Documento relevante |
|---------|-------|---------------------|
| 1948 | Shannon formaliza entropia e limite de compressão | entropy-coding |
| 1952 | Huffman publica código de prefixo ótimo | entropy-coding |
| 1966 | Tucker — decomposição tensorial | algebraic-compression |
| 1966 | Morton / Z-order | space-filling-curves |
| 1968–69 | Berlekamp–Massey (complexidade linear de sequências) | numerical-factorization |
| 1974 | DCT (Ahmed) | frequency-transforms |
| 1976 | Wyner–Ziv (lossy source coding com side info) | algebraic-compression |
| 1977 | LZ77 (Ziv & Lempel) | top-performers (LZ) |
| 1978 | LZ78 (Ziv & Lempel) | top-performers (LZ) |
| 1981 | Cantor–Zassenhaus (fatoração em GF(q)) | numerical-factorization |
| 1984 | Arithmetic coding prático (Witten, Neal, Cleary) | entropy-coding |
| 1984 | Lattice VQ (Conway & Sloane) | algebraic-compression |
| 1984 | Huffman adaptativo | entropy-coding |
| 1988 | Compressão fractal (Barnsley) | fractal-compression |
| 1988 | PPM (Cleary & Witten) | top-performers (PPM) |
| 1991 | DWT e JPEG baseado em DCT | frequency-transforms |
| 1994 | BWT (Burrows–Wheeler) | symbol-reordering |
| 1999 | NMF (Lee & Seung) | algebraic-compression |
| 2000 | HOSVD (De Lathauwer et al.) | algebraic-compression |
| 2002 | PAQ1 (Mahoney) — context mixing moderno | top-performers (CM) |
| 2004 | PPMd / durilca otimizados | top-performers (PPM) |
| 2005 | Compressed sensing (Candès, Donoho, Tao) | algebraic-compression |
| 2005 | Homologia persistente algorítmica (Carlsson–Zomorodian) | topological-compression |
| 2006 | F-transform (Perfilieva) — álgebra fuzzy | topological-compression |
| 2009 | LZ4 — LZ77 otimizado para velocidade | (baseline) |
| 2011 | Tensor Train (Oseledets) | algebraic-compression |
| 2013 | Brotli (Google) — LZ + ordem-2 + dicionário static | top-performers |
| 2014 | ANS / rANS (Duda) — entropia rápida | entropy-coding |
| 2015 | Zstandard (Facebook) | top-performers |
| 2016 | Group-equivariant CNNs (Cohen & Welling) | algebraic-compression |
| 2019 | NNCP v1 (Bellard) — RNN neural coding | top-performers |
| 2020 | SIREN (Sitzmann et al.) — INR neural | topological-compression |
| 2021 | NNCP v2 com Transformer-XL | top-performers |
| 2023 | ts_zip (Bellard) — RWKV para texto | top-performers |
| 2023 | cmix v21 | top-performers |
| 2024 | "Language Modeling Is Compression" (DeepMind, ICLR) | top-performers |
| 2024 | fx2-cmix | top-performers |

Observação estrutural: cada família nasce de um **salto teórico** (Shannon 1948, LZ 1977, BWT 1994, PAQ 2002, neural 2019) e sofre **refinamento incremental** por décadas. O projeto HSC propõe explorar um salto de tipo diferente — transformação de espaço antes do preditor, em vez de novos preditores.

---

## Vista transversal 4 — Por domínio de dados

| Domínio | Melhores hoje | Referências |
|---------|---------------|-------------|
| Texto natural | NNCP, cmix, ts_zip, LLM-based | top-performers |
| Código fonte | cmix, paq8px | top-performers |
| Executáveis | paq8px + filtro BCJ | top-performers, feature-space |
| Imagens raster | JPEG (lossy), JPEG-XL, PNG, WebP | frequency-transforms, fractal-compression |
| Volumes médicos (3D) | SIREN, tensor train, wavelets 3D | topological-compression, algebraic-compression |
| Áudio | FLAC, MP3, Opus; lattice VQ (G.719) | algebraic-compression |
| Vídeo | H.264/H.265/AV1 (motion+DCT+entropy) | frequency-transforms |
| Genômico | specialized (FASTQ-specific), cmix | top-performers, symbol-reordering |
| Séries temporais | Prony, FRI, LFSR mínimo | numerical-factorization, algebraic-compression |
| Grafos / redes | nauty (automorfismos), grammar compression | algebraic-compression |
| Dados tabulares | column-wise + entropy (Parquet, ORC) | entropy-coding, feature-space |
| Pontos 3D | polinômios implícitos, INR | algebraic-compression, topological-compression |

---

## Vista transversal 5 — Lossless vs lossy

| Tipo | Família predominante | Teto prático |
|------|----------------------|--------------|
| **Lossless** | LZ+entropy, PPM, CM, neural, BWT+entropy | limitado pela entropia do dado |
| **Lossy** (quantização) | DCT/DWT+quant, lattice VQ, k-means, NMF truncado | controlado por distorção |
| **Lossy estrutural** (perda com invariantes) | Fractal (IFS), INR (SIREN), PCA truncado | depende da métrica |
| **Lossless aproximado** (quasi-lossless) | k-error linear complexity, fuzzy residuals | perto de lossless + fallback |

O HSC até aqui trabalha **lossless**. A linha de compressão funcional topológica ([topological-compression.md](topological-compression.md)) abre caminho para lossy controlado por preservação de invariantes topológicos.

---

## Vista transversal 6 — Maturidade

| Nível | Famílias | Onde encontrar |
|-------|----------|----------------|
| **Produção industrial** | gzip, xz, zstd, brotli, LZMA2, bzip2 | Presente em qualquer SO |
| **Competições / maximização** | cmix, NNCP, paq8px, ts_zip | Benchmarks LTCB, Hutter |
| **Comercial nichado** | JPEG-XL, AV1, FLAC, Opus, lattice VQ áudio | Codecs de mídia |
| **Pesquisa aplicada** | Tensor decomposition (TT), INR (SIREN), CS | Papers, bibliotecas científicas |
| **Pesquisa básica** | AG-codes, módulos de persistência, Gröbner | Artigos em revistas de matemática |
| **Especulativo / fronteira** | quiver compression, tropical, LLM-compression honesta | Publicações recentes |

Posicionamento do HSC: **pesquisa básica com protótipo aplicado**. O framework abstrato ([topological-compression.md](topological-compression.md)) está no nível 5. O TBC está entre 4 e 5.

---

## Vista transversal 7 — O que o HSC cobre versus não cobre

Cada tema abaixo aparece em algum documento; o HSC pode usar como ferramenta ou como alvo de comparação.

| Tema | Cobertura no projeto | Onde |
|------|----------------------|------|
| Curvas de preenchimento | **Foco principal** | space-filling-curves, prototype/orders |
| Transformadas de frequência | Referência, não foco | frequency-transforms |
| Reordenação simbólica (BWT) | Referência + experimento marcado | symbol-reordering, evaluations/Q-007 |
| Codificação entrópica | Baseline (zlib) | entropy-coding, prototype/metrics |
| Compressão fractal | Referência | fractal-compression |
| Feature space 6-perspectivas | **Contribuição original** | feature-space |
| Topologia / homeomorfismo | **Contribuição original** | topological-compression |
| Fuzzy / INR / AIT | Conexão teórica | topological-compression |
| Tensor decomposition | Território novo a explorar | algebraic-compression |
| Syndrome coding (Slepian–Wolf) | Território novo a explorar | algebraic-compression |
| Lattice quantization | Território novo a explorar | algebraic-compression |
| Berlekamp–Massey / LFSR mínimo | Território novo a explorar | numerical-factorization |
| Context mixing / neural / PPM | Referência externa, não alvo | top-performers |
| TBC (indicator-plane coding) | **Técnica experimental** | techniques/TBC |

---

## Notas sobre uso

Os documentos desta pasta são **material de referência** para decidir escopo, posicionar contribuições e guiar experimentos. Cada um tem:

- Descrição técnica breve da família
- Histórico e marcos
- Conexões com o projeto HSC (quando relevantes)
- Referências bibliográficas essenciais

Para contribuições **originais** do projeto (o que o HSC propõe), ver [`../framework/`](../framework/). Para a metodologia (como a pesquisa é conduzida), ver [`../methodology/`](../methodology/).
