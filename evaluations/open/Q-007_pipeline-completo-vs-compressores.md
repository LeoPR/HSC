---
id: Q-007
titulo: Pipeline completo Hilbert→BWT→MTF→RLE→Entropia bate compressores de referência?
categoria: empirico
prioridade: alta
criado: 2026-04-01
relacionado: [Q-003, Q-004]
---

## Pergunta

Um pipeline completo de compressão usando curvas de Hilbert como reordenação espacial,
seguido de BWT→MTF→RLE→codificação entrópica, produz razão de compressão competitiva
com compressores de referência (bzip2, LZMA, PPMd, zstd) nos datasets canônicos?

---

## Contexto

O protótipo atual mede dois proxies:
1. **model_bps:** estimativa teórica de entropia via modelo de contexto de ordem 1
2. **zlib_ratio:** compressão prática com deflate nível 9 aplicado à sequência reordenada

Nenhum desses é um compressor completo. O zlib sobre sequência reordenada por Hilbert
é um teste parcial — o reordenamento pode ajudar o zlib, mas não é o pipeline proposto.

**O pipeline proposto em `docs/pesquisa/08_ideias_de_pipeline_hibrido.md`:**
```
Pipeline B: bloco → Hilbert → BWT → MTF → RLE → Entropia
```

Esse pipeline **não está implementado** — é a próxima fase de desenvolvimento.

**Por que importa:** A publicação precisa mostrar resultados de compressão *real*, não
apenas entropia teórica. Compressores como bzip2 já usam BWT+MTF+RLE+Huffman; a
questão é se o pré-processamento com Hilbert *antes* do BWT adiciona ganho líquido.

---

## Hipótese

**H1:** Para dados com correlação 2D (imagens, dados médicos), Hilbert+BWT+MTF+RLE+Entropia
supera bzip2 (BWT+MTF+RLE+Huffman sem reordenação 2D) em razão de compressão.

**H2:** Para texto 1D, o ganho é nulo ou negativo (overhead sem benefício).

**H3:** O pipeline é competitivo com LZMA e PPMd para dados 2D, mas inferior para texto.

---

## Desenho Experimental

### Compressores de Referência

| Compressor | Tipo | Backend | Uso no benchmark |
|------------|------|---------|-----------------|
| `bzip2 -9` | BWT+MTF+RLE+Huffman | block-sorting | Baseline principal (mais próximo do pipeline proposto) |
| `gzip -9` | LZ77+Huffman | sliding window | Referência popular |
| `xz -9` (LZMA) | LZMA2 | chain | Melhor compressão geral |
| `zstd -19` | LZ+Huffman/ANS | hybrid | Referência moderna |
| `ppmd` / `7z ppmd` | PPM | prediction by partial match | Melhor em texto |

### Datasets Prioritários

Os mesmos do estrato 2D em Q-002 (hipótese primária) + estrato texto (controle negativo):

```
2D:   mr, x-ray, pic, ptt5
Text: dickens, alice29.txt, enwik8
Code: progc, samba
```

### Protocolo de Comparação

Para cada dataset e cada compressor de referência:
```
razão_ref = tamanho_original / tamanho_comprimido_pelo_ref
razão_pipeline = tamanho_original / tamanho_pipeline_HSC
ganho_líquido = razão_pipeline - razão_ref
```

### Implementação Necessária

Esta pergunta requer implementação que ainda não existe:

- [ ] `prototype/transforms/bwt.py` — Burrows-Wheeler Transform (encode/decode)
- [ ] `prototype/transforms/mtf.py` — Move-To-Front (encode/decode)
- [ ] `prototype/transforms/rle.py` — Run-Length Encoding (encode/decode)
- [ ] `prototype/pipeline.py` — orquestrador do pipeline completo
- [ ] `prototype/compare_full.py` — benchmark contra compressores de referência

**Nota:** Para o paper, a implementação em Python puro é aceitável para proof-of-concept,
mas os resultados de velocidade devem ser apresentados com ressalva. Razão de compressão
(não velocidade) é a métrica primária.

---

## Análise de Ganho Líquido vs. Custo

A comparação justa com bzip2 deve considerar:

```
bzip2:           BWT → MTF → RLE → Huffman
Pipeline HSC:    Hilbert → BWT → MTF → RLE → Entropia

Overhead do HSC: custo de reordenar bytes via curva Hilbert
Benefício:       BWT opera sobre sequência com menor entropia pós-Hilbert
                 → potencialmente menos runs, melhor MTF, melhor RLE
```

Se Hilbert reduz a entropia de entrada do BWT, o BWT produz runs mais longos,
o MTF produz mais zeros, e o RLE comprime mais — ganho cascateado.

---

## Critério de Conclusão

- **H1 confirmada:** Pipeline HSC supera bzip2 em ≥ 2 datasets do estrato 2D com
  margem ≥ 1% em razão de compressão. Este é o resultado de publicação.
- **H1 refutada:** Pipeline HSC não supera bzip2 nem em dados 2D. Revisitar design
  do pipeline (talvez Hilbert deva ser aplicado em blocos, não no arquivo inteiro).
- **H2 e H3 informam** a narrativa do paper: "melhor para dados 2D, comparável para texto".

---

## Notas de Dependência

Esta questão depende de:
- Q-002 (datasets canônicos disponíveis)
- Q-003 (confirmação que Hilbert reduz entropia em 2D real)
- Implementação do pipeline completo (fase F3/F4 do SIAC)

Não bloqueia Q-001, Q-003, Q-004, Q-005, Q-006 — pode ser desenvolvida em paralelo
após confirmação experimental de Q-003.
