---
id: Q-002
titulo: Seleção de datasets canônicos para benchmark estratificado
categoria: dataset
prioridade: alta
criado: 2026-04-01
relacionado: [Q-003, Q-004, Q-007]
---

## Pergunta

Quais datasets canônicos, usados nos principais benchmarks mundiais de compressão,
devem compor a suíte de testes do HSC para que os resultados sejam comparáveis
com a literatura publicada?

---

## Contexto

O único dataset real testado até agora (`datasets/pt-br.tsv`) é um dicionário fonético
português-IPA (3.7 MB, 95.937 linhas). Ele:

- **Não pertence a nenhum corpus canônico** — resultados não são comparáveis com literatura
- **É dados 1D sequenciais** — exatamente o caso desfavorável para Hilbert/Morton
- **Tem codificação mista** (ASCII + IPA UTF-8) não representativa de benchmarks padrão
- **Serve como controle negativo**, mas não testa a hipótese central do projeto

Para publicação, os resultados precisam ser reproduzíveis sobre datasets que outros
pesquisadores conhecem e usam.

---

## Hipótese de Trabalho

Uma suíte estratificada cobrindo **5 categorias** de dados permite:
1. Confirmar que Hilbert não degrada dados 1D (controle negativo)
2. Demonstrar ganho em dados 2D espaciais (hipótese primária)
3. Caracterizar o comportamento em tipos intermediários
4. Estabelecer resultados diretamente comparáveis com literatura pós-2003

---

## Corpora Canônicos — Visão Geral

### Calgary Corpus (1987)
- 14 arquivos, ~3.14 MB total
- Referência clássica, ainda citada para comparabilidade histórica
- Limitação: arquivos pequenos, dados dos anos 1980

### Canterbury Corpus (1997)
- 11 arquivos padrão + 3 grandes (~8.5 MB total)
- Sucessor do Calgary, mais representativo
- Inclui `e.coli` (DNA) e `bible.txt` (texto longo)

### Silesia Corpus (2003) — **padrão atual da literatura**
- 12 arquivos, ~211.9 MB total
- Cobre dados modernos: médico, banco de dados, código-fonte, executável
- Usado na maioria dos papers de compressão pós-2003

### Large Text Compression Benchmark (Matt Mahoney)
- `enwik8` (100 MB) e `enwik9` (1 GB) — Wikipedia em XML/UTF-8
- Essencial para comparação com trabalhos que citam Hutter Prize
- `enwik8` é o mínimo para publicação em NLP/compressão de texto

---

## Estratificação por Tipo de Dado

### Estrato 1 — Texto Natural (controle negativo esperado: raster ≥ Hilbert)

| Arquivo | Corpus | Tamanho | Conteúdo |
|---------|--------|---------|----------|
| `book1` | Calgary | 769 KB | Romance inglês (Hardy), ASCII |
| `alice29.txt` | Canterbury | 152 KB | Alice no País das Maravilhas |
| `lcet10.txt` | Canterbury | 427 KB | Paper técnico longo (ACM) |
| `dickens` | Silesia | 10.2 MB | Obras de Dickens, ASCII |
| `reymont` | Silesia | 6.6 MB | Romance polonês (PDF descomprimido) |
| `enwik8` | LTCB | 100 MB | Wikipedia 100M bytes (XML+UTF-8) |

**Por que incluir:** Confirma que o método não degrada texto 1D. Resultados comparáveis
com qualquer paper de compressão de texto.

---

### Estrato 2 — Código-Fonte (comportamento intermediário esperado)

| Arquivo | Corpus | Tamanho | Conteúdo |
|---------|--------|---------|----------|
| `progc` | Calgary | 39 KB | Código C |
| `fields.c` | Canterbury | 11 KB | Código C (arquivo único) |
| `samba` | Silesia | 21.6 MB | Código Samba 2.2.3a (tar) |

**Por que incluir:** Código tem estrutura 2D implícita (indentação, blocos), mas é
serializado linearmente. Caso intermediário que testa robustez.

---

### Estrato 3 — Dados Estruturados / Binários (hipótese secundária)

| Arquivo | Corpus | Tamanho | Conteúdo |
|---------|--------|---------|----------|
| `kennedy.xls` | Canterbury | 1.03 MB | Planilha Excel (binário) |
| `osdb` | Silesia | 10.1 MB | Dump MySQL sintético |
| `xml` | Silesia | 5.3 MB | XML do OpenOffice |
| `nci` | Silesia | 33.6 MB | Base química (texto estruturado) |
| `sao` | Silesia | 7.3 MB | Catálogo estelar SAO (binário) |
| `geo` | Calgary | 102 KB | Dados sísmicos (binário) |

**Por que incluir:** Dados estruturados têm correlação local irregular — testa se
Hilbert encontra estrutura onde não é óbvia.

---

### Estrato 4 — Imagens 2D / Dados Médicos (**hipótese primária**)

| Arquivo | Corpus | Tamanho | Conteúdo |
|---------|--------|---------|----------|
| `pic` | Calgary | 513 KB | Bitmap fax CCITT (1-bit, 2D) |
| `ptt5` | Canterbury | 513 KB | Bitmap fax CCITT (1-bit, 2D) |
| `mr` | Silesia | 9.97 MB | Imagem MRI 3D, DICOM 16-bit |
| `x-ray` | Silesia | 8.47 MB | Raio-X mão infantil, DICOM 16-bit |

**Por que incluir:** Este é o estrato central para a hipótese. Imagens médicas e
fax têm forte correlação espacial 2D local — exatamente onde Hilbert deve ganhar.
Resultados aqui são a prova-de-conceito do projeto.

**Nota sobre DICOM:** `mr` e `x-ray` são arquivos DICOM com header — extração dos
pixels raw pode ser necessária para teste limpo. Considerar usar apenas o payload
de pixel data.

---

### Estrato 5 — Dados Genômicos (caso especial: 1D com estrutura periódica)

| Arquivo | Corpus | Tamanho | Conteúdo |
|---------|--------|---------|----------|
| `e.coli` | Canterbury Large | 4.6 MB | Sequência DNA de E. coli (FASTA) |

**Por que incluir:** DNA é alfabeto de 4 símbolos (ACGT) com repetições longas.
Hipótese: Morton/Hilbert podem capturar estrutura de repetições melhor que raster
se mapeadas em grade 2D com tamanho calibrado. Caso exploratório.

---

### Estrato 6 — Sintético (controle experimental)

Gerar programaticamente para experimentos controlados:

| Dataset | Descrição | Hipótese |
|---------|-----------|----------|
| `synth_2d_gauss` | Grade de blobs Gaussianos (σ=8–32) | Hilbert >> raster |
| `synth_2d_noise` | Ruído branco 2D puro | Todos empatam |
| `synth_1d_walk` | Passeio aleatório 1D → grade quadrada | Raster >> Hilbert |
| `synth_2d_gradient` | Gradiente linear 2D | Morton ≈ Hilbert >> raster |
| `synth_2d_blocks` | Blocos uniformes 8×8 (tipo JPEG) | Hilbert ≥ Morton >> raster |

**Por que incluir:** Isola exatamente as condições que favorecem cada topologia.
Permite validação controlada antes de afirmar resultados em dados reais.

---

## Suíte Mínima Recomendada (para primeira publicação)

Prioridade de aquisição:

```
FASE 1 — Validação de hipótese (urgente):
  mr, x-ray (Silesia)           → hipótese primária 2D
  pic, ptt5 (Calgary/Canterbury) → hipótese primária 2D (pequenos, rápidos)
  dickens, alice29.txt           → controle negativo texto
  datasets sintéticos (gerar)    → validação controlada

FASE 2 — Completude para publicação:
  Todos os 12 arquivos Silesia
  enwik8
  e.coli (Canterbury Large)

FASE 3 — Cobertura histórica (comparabilidade):
  Calgary completo (14 arquivos)
  Canterbury completo (11 arquivos)
```

---

## Downloads

| Corpus | URL |
|--------|-----|
| Calgary | https://mattmahoney.net/dc/calgary.html |
| Canterbury | https://corpus.canterbury.ac.nz/ |
| Silesia | https://sun.aei.polsl.pl/~sdeor/index.php?page=silesia |
| enwik8/9 | https://mattmahoney.net/dc/text.html |

---

## Critério de Conclusão

Esta pergunta estará respondida quando:
- [ ] Todos os arquivos da Suíte Mínima (Fase 1) estiverem no diretório `datasets/`
- [ ] Geradores sintéticos implementados em `prototype/data/synthetic.py`
- [ ] Pipeline de testes executado com sucesso em pelo menos 2 estratos
- [ ] Resultados documentados em Q-003 e Q-004

---

## Notas de Progresso

- 2026-04-01: Questão criada. pt-br.tsv mantido como dado auxiliar (controle negativo
  informal), mas não fará parte da suíte canônica de publicação.
