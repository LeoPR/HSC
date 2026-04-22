# Top Performers em Benchmarks de Compressão — Estratégias

Análise dos compressores no topo dos benchmarks reconhecidos (Large Text Compression Benchmark, Silesia, Hutter Prize), com foco nas **estratégias** que os colocam ali.

A informação aqui é complementar a [algebraic-compression.md](algebraic-compression.md) e [feature-space.md](feature-space.md): aqueles documentos mapeiam o terreno teórico; este reporta o que está **efetivamente ganhando** competições em 2024–2026.

---

## Rankings

### Large Text Compression Benchmark — enwik9 (top 20)

Ranqueado por `compressed + decompressor size`.

| # | Compressor | Tamanho | Família | Custo tempo |
|---|------------|--------:|---------|--------|
| 1  | nncp v3.2             | 107,261,318 | Transformer neural      | Alto |
| 2  | cmix v21 -t           | 108,244,767 | Context Mixing + LSTM   | Muito alto |
| 3  | fx2-cmix              | 110,351,665 | Context Mixing          | Alto |
| 4  | jax-compress          | 113,393,442 | LSTM neural             | Alto |
| 5  | tensorflow-compress v4| 113,597,696 | LSTM neural             | Alto |
| 6  | cmix-hp v1            | 113,712,798 | Context Mixing          | Alto |
| 7  | fast-cmix             | 113,746,218 | Context Mixing          | Médio |
| 8  | starlit (2021)        | 114,951,433 | Context Mixing + preproc| Alto |
| 9  | phda9 v1.8            | 116,587,793 | Context Mixing          | Médio |
| 10 | gmix v1               | 122,518,098 | Context Mixing          | Médio |
| 11 | paq8px_v206fix1 -12L  | 125,099,359 | Context Mixing          | Alto |
| 12 | durilca'kingsize      | 127,784,888 | PPM                     | **Baixo** |
| 13 | fxv v1                | 129,299,169 | Context Mixing          | Médio |
| 14 | cmve v0.2.0           | 130,184,645 | Context Mixing          | Muito alto |
| 15 | paq8hp12any -8        | 132,375,726 | Context Mixing (Hutter) | Médio |
| 16 | drt\|emma v1.23       | 135,522,772 | Context Mixing          | Médio |
| 17 | zpaq v6.42            | 142,257,365 | Context Mixing          | Baixo |
| 18 | drt\|lpaq9m           | 144,054,338 | Context Mixing          | Baixo |
| 19 | mcm v0.83             | 144,934,149 | Context Mixing          | Baixo |
| 20 | nanozip v0.09a        | 149,328,821 | Context Mixing          | Baixo |

Observações:

- **Context Mixing domina a lista:** 16 de 20 entradas.
- **Neural (transformer + LSTM):** 4 de 20, mas inclui o #1 e dois do top 5.
- **PPM ainda compete:** durilca'kingsize em #12 com tempo **muito menor** que qualquer outro no top 15.
- **LZ puro não aparece:** gzip, zstd, xz, brotli não chegam ao top 20 em compressão máxima de texto. Ficam com ~20% pior que o nanozip em troca de 1000× mais velocidade.

### Silesia corpus (top 15, geral)

Ranqueado por tamanho comprimido total dos 12 arquivos.

| # | Compressor | Tamanho | Família |
|---|------------|--------:|---------|
| 1  | paq8px v210 -12L             | 27,987,907 | Context Mixing |
| 2  | paq8px v209 -12L             | 28,025,541 | Context Mixing |
| 3  | paq8px v206 -12TL            | 28,241,197 | Context Mixing |
| 4  | precomp + cmix v21           | 28,261,094 | Preproc + CM   |
| 5  | paq8px v206 -12TR            | 28,280,021 | Context Mixing |
| …  | (mais variantes paq8px/cmix) | …          | …              |

Em compressão geral (não só texto), **paq8px** domina. Não há neural puro no top 15 do Silesia — o overhead de um transformer não compensa para dados heterogêneos (executáveis, XML, DNA, etc.).

### Nota sobre LLM-based emergentes

- **ts_zip** (Bellard, 2023) — usa RWKV 169M/430M. No enwik8 atinge 0.948 bpb com rwkv_430M. Não costuma entrar no LTCB oficial porque requer GPU, mas mostra que LLMs quantizados são competitivos.
- **llama.cpp-based** (2023–24) — experimentos independentes com LLaMA 7B atingem ~0.6 bpb em texto natural, mas com tamanho de modelo inviável para o benchmark padrão.
- **L3TC** (AAAI 2024) — RWKV otimizado para "learned lossless low-complexity text compression".

Essas abordagens colocam LLMs como a próxima fronteira, mas têm um **problema metodológico grave**: o modelo é parte da compressão? Se sim, o arquivo "comprimido" é enorme. Se não, o compressor precisa do modelo presente. O LTCB resolve isso incluindo o decodificador no total — por isso NNCP é o #1 honesto, não um LLM qualquer.

---

## As cinco estratégias dominantes

### 1. Context Mixing (CM)

**Como funciona:**

```
        input bit stream
              │
              ▼
    ┌─────────────────────┐
    │  ensemble de N      │   N tipicamente 50-2000
    │  modelos preditivos │   cada um "vê" o contexto de um ângulo
    └──────────┬──────────┘
               │  prob_1(bit), prob_2(bit), ..., prob_N(bit)
               ▼
    ┌─────────────────────┐
    │  mixer (regressão   │   pesos adaptativos via gradiente online
    │  logística + NN)    │   muitas vezes uma camada LSTM
    └──────────┬──────────┘
               │  prob_mista(bit)
               ▼
    ┌─────────────────────┐
    │  SSE (Secondary     │   pós-correção pela probabilidade já vista
    │  Symbol Estimation) │
    └──────────┬──────────┘
               │  prob_final(bit)
               ▼
    ┌─────────────────────┐
    │  arithmetic coding  │
    └──────────┬──────────┘
               ▼
          output bit
```

**Modelos típicos do ensemble (ex: cmix):**

- Ordem-0 a ordem-8 (Markov tradicional)
- Match model (LZ-like)
- Word model (tokenização implícita)
- Record model (texto tabular)
- JPEG/image/executable-specific models
- Sparse models (bits não-adjacentes)
- LSTM contextual

Total no cmix v21: **2122 modelos**.

**Forças:**
- Adaptativo em tempo real (online learning).
- Combina muitas perspectivas — cobre qualquer tipo de estrutura vista por qualquer submodelo.
- Dominante em ranking há ~20 anos.

**Fraquezas:**
- Tempo: cmix comprime enwik9 em dias, decomprime em dias. Inviável para uso prático.
- Não é paralelizável trivialmente (dependência serial pelo mixer).
- Cada modelo adicional tem retorno decrescente.

### 2. Neural (Transformer / LSTM)

**Como funciona:**

```
        input bit stream (ou byte/token)
              │
              ▼
    ┌─────────────────────┐
    │  transformer / LSTM │   context window: últimos K tokens
    │  (modelo de lingua) │   parâmetros: milhões a bilhões
    └──────────┬──────────┘
               │  distribuicao completa sobre proximo token
               ▼
    ┌─────────────────────┐
    │  arithmetic coding  │
    └──────────┬──────────┘
               ▼
          output bits
```

**NNCP (Bellard):** Transformer-XL customizado, treinado online durante a compressão. Sem pré-treinamento externo — o modelo aprende os dados enquanto comprime. Decoder usa o mesmo processo.

**ts_zip (Bellard):** RWKV pré-treinado. Mais rápido que NNCP, menos competitivo no benchmark oficial (modelo não conta no tamanho), mas melhor razão prática.

**Forças:**
- Predição mais precisa que CM clássico para texto natural.
- Aproveita estrutura de longa distância (context window).
- Treina e comprime simultaneamente (NNCP).

**Fraquezas:**
- Tempo e memória: NNCP v3.2 em enwik9 leva **dias** e consome **GBs** de RAM.
- Dependência de GPU para versões práticas.
- Não-determinismo numérico entre hardwares é um risco.

### 3. PPM (Prediction by Partial Match)

**Como funciona:**

Mantém modelos de Markov de ordem decrescente. Para prever o próximo símbolo:

1. Tenta contexto de ordem máxima (ex: últimos 8 bytes).
2. Se o símbolo já foi visto nesse contexto, usa sua frequência.
3. Se não, emite um "escape" para ordem inferior e tenta novamente.
4. Cascateia até ordem-0 ou ordem--1 (uniforme).

**durilca (Shkarin):** otimização clássica do PPMII. Ainda no top 12 do LTCB com tempo ~500× menor que cmix.

**Forças:**
- Simples conceitualmente.
- Rápido comparado a CM/neural.
- Boa razão em texto estruturado.

**Fraquezas:**
- Plateau de performance — não chega perto de CM/neural.
- Sensível a memória: contextos longos são caros.
- Pobre em dados heterogêneos sem pré-processamento.

### 4. Preprocessing + CM (hybrid)

**Como funciona:**

Antes do compressor principal, um pré-processador **detecta formatos conhecidos embutidos no stream** e os descomprime ou normaliza:

- `precomp` detecta e descomprime: gzip/zlib/deflate/bzip2/jpeg/png interno, PDF streams
- Reexpande para que o CM principal veja a versão "crua" e capture sua estrutura real.
- Na descompressão, o processo é invertido (recomprime para o formato original).

**starlit, precomp|cmix:** variantes hybrid que dominam o Silesia.

**Forças:**
- Ganha quando o input contém dados já comprimidos por outros métodos.
- É a única estratégia que supera CM puro em dados heterogêneos.

**Fraquezas:**
- Depende de reconhecer formatos. Fora do catálogo, não ajuda.
- Overhead de engenharia: cada formato novo exige novo módulo.

### 5. LZ+Entropy (prático, não top em ratio)

**Como funciona:**

- **LZ77 / LZ78** parsing — encontra matches em janela deslizante.
- Emite `(literal)` ou `(offset, length)` tokens.
- Entropy coding final (Huffman, Range, ANS).

**zstd, brotli, xz/LZMA, deflate.**

**Forças:**
- Velocidade: zstd comprime ~500 MB/s em um core moderno.
- Escala trivialmente com paralelismo (zstd multi-thread).
- Formato estabilizado, decoders em toda linguagem.

**Fraquezas:**
- Razão limitada. Em enwik9:
  - gzip -9: ~314 MB (3.18x)
  - brotli -11: ~237 MB (4.22x)
  - xz -9: ~198 MB (5.05x)
  - zstd --long --ultra -22: ~198 MB (5.05x)
- vs. NNCP: ~107 MB (9.34x). **~2× mais comprimido, mas 10000× mais tempo.**

---

## Padrão unificador

Todas as estratégias no topo podem ser descritas pelo mesmo template:

```
[preprocessing opcional] → [predizer prob do próximo símbolo] → [arithmetic coding]
                                         ▲
                    a família se distingue aqui
```

| Família | Como predizem prob(próximo) |
|---------|-----------------------------|
| PPM | Markov ordem variável, fallback de escape |
| CM clássico | Ensemble de modelos + mixer logístico |
| CM + neural | Ensemble + LSTM mixer + SSE |
| Neural puro | Transformer/LSTM calcula distribuição |
| LZ+Entropy | Frequência global (Huffman/ANS) — não condicional |

A qualidade do compressor é essencialmente a qualidade do **preditor de próximo símbolo**. Arithmetic coding é universal — perto do limite teórico dado um preditor.

Isso tem uma implicação forte: **a pesquisa em compressão contemporânea é, na prática, pesquisa em predição sequencial**. Compressão e modelagem de linguagem são duais, formalizado pelo *Language Modeling Is Compression* (DeepMind, ICLR 2024).

---

## Onde as famílias deste documento se encaixam em relação ao HSC

| Família | Relação com o projeto HSC |
|---------|---------------------------|
| Context Mixing | Modelo de contexto que o HSC usa (adaptive_order1_bits) é o membro mais simples dessa família. CM completo seria uma extensão natural. |
| PPM | Não coberto explicitamente. Complementa o modelo ordem-1 atual com ordem variável. |
| Neural | Não coberto. Requer ecossistema que o protótipo atual não tem (PyTorch, GPU). |
| Preprocessing | Coberto implicitamente via `techniques/` — cada técnica é um preprocessador potencial. |
| LZ+Entropy | Não é foco: zlib aparece apenas como baseline externo. O TBC M2 está na classe LZ sem entropy coding final. |

Observação essencial: **o HSC está num eixo ortogonal ao ranking**. Ele explora transformação de espaço de features (SFC, embedding, fold-XOR) antes do preditor. Os top performers usam sempre a mesma sequência espacial (raster) e brigam no preditor. 

Isso sugere duas hipóteses distintas:

**H1:** se o HSC mostrar que uma transformação de espaço melhora a **previsibilidade** (baixa entropia condicional) para alguma classe de dados, essa transformação poderia ser **composta com qualquer preditor** — não precisa brigar com cmix/NNCP, pode ser um pré-processador deles.

**H2:** transformações de espaço já foram experimentadas (BWT é a mais famosa, e está dentro do CM). Qualquer ganho marginal do HSC tem que ser além do que CM já explora implicitamente.

Ambas são testáveis — a primeira foca em medir "a transformação X reduz H(dado|contexto)" para contexto fixo; a segunda em rodar HSC+preditor vs preditor sozinho.

---

## Tempos para contextualizar

| Compressor | Tempo enwik9 (s/MB) | Comentário |
|------------|---------------------|------------|
| zstd -22       | ~0.05  | sub-segundo por MB, multithread |
| brotli -11     | ~1     | segundos por MB |
| xz -9          | ~5     | segundos por MB |
| paq8px -12L    | ~300   | minutos por MB |
| cmix v21       | ~600   | ~10min por MB |
| NNCP v3.2      | ~240   | minutos por MB (CPU), mais rápido em GPU |

Um enwik9 inteiro:

- zstd: ~1 minuto
- NNCP/cmix: ~2–7 dias em CPU

Esse gap explica o mercado: zstd/xz em produção; CM/neural em competições.

---

## Referências principais

- Mahoney, M. **Large Text Compression Benchmark** — http://mattmahoney.net/dc/text.html
- Mahoney, M. **Silesia Open Source Compression Benchmark** — https://mattmahoney.net/dc/silesia.html
- Knoll, B. (2014). **cmix: A lossless data compression program.** https://www.byronknoll.com/cmix.html
- Bellard, F. (2021). **NNCP v2: Lossless Data Compression with Transformer.** https://bellard.org/nncp/nncp_v2.pdf
- Bellard, F. (2023). **ts_zip: Text Compression using LLMs.** https://bellard.org/ts_zip/
- Mahoney, M. (2005). **Adaptive Weighing of Context Models for Lossless Data Compression.** Florida Tech Tech. Report.
- Shkarin, D. (2002). **PPM: One Step to Practicality.** Data Compression Conference (DCC).
- DeepMind (2024). **Language Modeling Is Compression.** ICLR.
- Hutter Prize — http://prize.hutter1.net/

Sources:
- [Large Text Compression Benchmark - Matt Mahoney](https://www.mattmahoney.net/dc/text.html)
- [Silesia Open Source Compression Benchmark](https://mattmahoney.net/dc/silesia.html)
- [Byron Knoll - cmix](https://www.byronknoll.com/cmix.html)
- [NNCP: Lossless Data Compression with Neural Networks](https://www.bellard.org/nncp/)
- [NNCP v2: Lossless Data Compression with Transformer](https://bellard.org/nncp/nncp_v2.pdf)
- [Context mixing - Wikipedia](https://en.wikipedia.org/wiki/Context_mixing)
- [ts_zip: Text Compression using Large Language Models](https://bellard.org/ts_zip/)
- [Language Modeling Is Compression (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/file/3cbf627fa24fb6cb576e04e689b9428b-Paper-Conference.pdf)
- [cmix GitHub](https://github.com/byronknoll/cmix)
