# Datasets Manifest

Documentação centralizada dos datasets usados no projeto HSC.
Cada dataset é categor izando por origem, tamanho, tipo e fonte.

---

## Datasets Canônicos (Competições Top 10 Compressores)

Estes são os datasets usados nos principais benchmarks mundiais de compressão.
Referência: [Maximum Compression Benchmark](https://www.maximumcompression.com/),
[Squash Benchmark](http://quixdb.github.io/squash-benchmark/),
[Large Text Compression Benchmark](https://mattmahoney.net/dc/text.html)

### Silesia Corpus (2003) — Padrão Ouro

**Versão:** Completa (12 arquivos, ~211.9 MB)  
**URL de download:** https://sun.aei.polsl.pl/~sdeor/index.php?page=silesia  
**Status:** Ativo desde 2003, último update Jan 2026

| Arquivo | Tamanho | Tipo | Categoria HSC | Notas |
|---------|---------|------|---------------|-------|
| dickens | 10.2 MB | Texto (ASCII) | 1D_Text | Obras de Charles Dickens |
| mozilla | 51.2 MB | Binário/Executável | Binary_Exec | Mozilla executable + libs |
| mr | 9.97 MB | Médico (3D MRI) | **2D_Image** | DICOM 16-bit, MRI scan — **PRIORITÁRIO** |
| nci | 33.6 MB | Estruturado (BD) | Structured | Banco químico em texto |
| ooffice | 6.15 MB | Binário (DLL) | Binary_Exec | Windows DLL |
| osdb | 10.1 MB | Binário (BD) | Structured | Banco MySQL sintético |
| reymont | 6.63 MB | Texto/PDF | 1D_Text | Romance polonês (PDF descomprimido) |
| samba | 21.6 MB | Código-fonte (tar) | SourceCode | Código Samba 2.2.3a |
| sao | 7.25 MB | Estruturado (BD) | Structured | Catálogo estelar (binário) |
| webster | 41.5 MB | Estruturado/Texto | 1D_Text | Dicionário Webster 1913 em HTML |
| x-ray | 8.47 MB | Médico (Raio-X) | **2D_Image** | DICOM 16-bit, raio-X — **PRIORITÁRIO** |
| xml | 5.35 MB | Estruturado (XML) | Structured | Arquivo XML do OpenOffice |

### Calgary Corpus (1987) — Referência Histórica

**Versão:** Completa (14 arquivos, ~3.14 MB)  
**URL de download:** https://mattmahoney.net/dc/calgary.html  
**Status:** Histórico, ainda usado para comparabilidade

| Arquivo | Tamanho | Tipo | Categoria HSC |
|---------|---------|------|---------------|
| bib | 111 KB | Texto (refer) | 1D_Text |
| book1 | 769 KB | Texto (ASCII) | 1D_Text |
| book2 | 611 KB | Texto (troff) | 1D_Text |
| geo | 102 KB | Binário (sísmico) | Structured |
| news | 377 KB | Texto | 1D_Text |
| obj1 | 21 KB | Binário | Binary_Exec |
| obj2 | 247 KB | Binário | Binary_Exec |
| paper1 | 53 KB | Texto | 1D_Text |
| paper2 | 82 KB | Texto | 1D_Text |
| **pic** | **513 KB** | **Fax bitmap 1-bit** | **2D_Image** |
| progc | 39 KB | Código C | SourceCode |
| progl | 71 KB | Código Lisp | SourceCode |
| progp | 49 KB | Código Pascal | SourceCode |
| trans | 93 KB | Binário (transdata) | Structured |

### Canterbury Corpus (1997) — Referência Moderna

**Versão:** Padrão (11 arquivos, ~2.81 MB)  
**URL de download:** https://corpus.canterbury.ac.nz/  
**Status:** Bem mantido, ainda em uso

| Arquivo | Tamanho | Tipo | Categoria HSC |
|---------|---------|------|---------------|
| alice29.txt | 152 KB | Texto (ASCII) | 1D_Text |
| asyoulik.txt | 125 KB | Texto (Shakespeare) | 1D_Text |
| cp.html | 24 KB | HTML/Markup | 1D_Text |
| fields.c | 11 KB | Código C | SourceCode |
| grammar.lsp | 3.7 KB | Código Lisp | SourceCode |
| kennedy.xls | 1.03 MB | Binário (Excel) | Structured |
| lcet10.txt | 427 KB | Texto técnico | 1D_Text |
| plrabn12.txt | 482 KB | Texto (poesia) | 1D_Text |
| **ptt5** | **513 KB** | **Fax bitmap 1-bit** | **2D_Image** |
| sum | 38 KB | Executável SPARC | Binary_Exec |
| xargs.1 | 4.2 KB | Man page | 1D_Text |

---

## Datasets Complementares

Datasets adicionais para cobertura experimental além do cânone.

### Large Text Compression Benchmark (Matt Mahoney)

**enwik8 (Wikipedia 100MB)**  
URL: https://mattmahoney.net/dc/text.html  
Tamanho: 100 MB  
Tipo: UTF-8 XML (Wikipedia dump)  
Categoria HSC: 1D_Text  
Uso: Benchmark de compressão de texto de referência global

**enwik9 (Wikipedia 1GB)**  
URL: https://mattmahoney.net/dc/text.html  
Tamanho: 1 GB  
Tipo: UTF-8 XML (Wikipedia dump)  
Categoria HSC: 1D_Text  
Uso: Teste de escalabilidade, Hutter Prize

### Dados Sintéticos Controlados (Gerador Local)

Não há download — gerados dinamicamente por `prototype/data/synthetic.py`

| Tipo | Dimensão | Função | Uso |
|------|----------|--------|-----|
| gaussian_blobs_2d | 2D | Blobs Gaussianos correlacionados | Teste ideal para Hilbert |
| gradient_2d | 2D | Gradiente linear | Teste de suavidade |
| noise_2d | 2D | Ruído branco | Teste negativo |
| walk_1d | 1D | Passeio aleatório → grade 2D | Teste de degradação |

---

## Estratificação para Experimentos

### Estrato 1: Texto Sequencial 1D (Controle Negativo)

Dados onde raster deve ganhar.

- `alice29.txt` (Canterbury) — 152 KB, teste rápido
- `dickens` (Silesia) — 10.2 MB, teste completo
- `enwik8` (LTCB) — 100 MB, teste escalável

**Propósito:** Confirmar que Hilbert não degrada dados 1D naturais.

### Estrato 2: Imagens 2D (Hipótese Central)

Dados onde Hilbert deve ganhar.

- `pic` (Calgary) — 513 KB, fax bitmap
- `ptt5` (Canterbury) — 513 KB, fax bitmap
- `mr` (Silesia) — 9.97 MB, MRI 3D
- `x-ray` (Silesia) — 8.47 MB, raio-X

**Propósito:** Testar hipótese central — Hilbert reduz entropia em dados 2D reais.

### Estrato 3: Código-Fonte

Dados intermediários.

- `progc` (Calgary) — 39 KB
- `fields.c` (Canterbury) — 11 KB
- `samba` (Silesia) — 21.6 MB (tar archive)

**Propósito:** Testar comportamento em dados semi-estruturados.

### Estrato 4: Dados Estruturados/Binários

Comportamento a ser caracterizado.

- `nci` (Silesia) — 33.6 MB, base química
- `osdb` (Silesia) — 10.1 MB, BD sintética
- `sao` (Silesia) — 7.25 MB, catálogo estelar

### Estrato 5: Sintéticos (Controle)

- `gaussian_blobs_2d` — ideal para Hilbert
- `noise_2d` — sem correlação
- `walk_1d` — degradação esperada

---

## Plano de Download

### Fase 1: Mínima (Rápida)

**Tamanho total:** ~2 GB  
**Tempo:** 10-30 min

Canônicos essenciais:
- Silesia: `mr`, `x-ray`, `dickens`
- Calgary: `pic`
- Canterbury: `alice29.txt`, `ptt5`

### Fase 2: Completa Canônica (Padrão)

**Tamanho total:** ~218 MB (Silesia) + 3.1 MB (Calgary) + 2.8 MB (Canterbury) = ~224 MB  
**Tempo:** 30-60 min

Todos os datasets canônicos para comparação justa.

### Fase 3: Escalabilidade (Opcional)

**Tamanho adicional:** 100 MB (enwik8) ou 1 GB (enwik9)  
**Tempo:** 1-10 min (enwik8) ou 10-30 min (enwik9)

Para testes de escalabilidade.

---

## Atualizações e Manutenção

**Frequência:** Dados não mudam (benchmarks estabelecidos)  
**Política de limpeza:** Script de download permite `--cleanup` para remover arquivos e recuperar espaço  
**Verificação de integridade:** MD5/SHA256 checksums disponíveis nas fontes

---

## Referências Externas

- Maximum Compression: https://www.maximumcompression.com/
- Squash Benchmark: http://quixdb.github.io/squash-benchmark/
- Large Text Benchmark: https://mattmahoney.net/dc/text.html
- Hutter Prize: http://prize.hutter1.net/
