---
id: Q-003
titulo: Hilbert reduz entropia de modelo em dados 2D espaciais reais?
categoria: empirico
prioridade: critica
criado: 2026-04-01
relacionado: [Q-002, Q-004, A-002]
---

## Pergunta

Curvas de Hilbert (e Morton) produzem menor entropia de modelo (model_bps)
do que ordenamento raster em **dados reais com correlação espacial 2D**
(imagens médicas, fax, imagens de satélite)?

---

## Contexto

A hipótese central do projeto está fundamentada em dois experimentos anteriores:

1. **Teste com pt-br.tsv** (texto sequencial): raster ganhou — resultado esperado e negativo
2. **Teste sintético 2D** (blobs Gaussianos artificiais): Hilbert/Morton ganharam — confirmação
   de princípio, mas em dados *gerados pelo próprio experimento*

O que **ainda não foi testado** é se a vantagem se mantém em **dados reais** —
imagens com sua estrutura natural, ruído, bordas e variação não-controlada.

**Por que isso importa:** Dados sintéticos com correlação perfeita são trivialmente
favoráveis a Hilbert. Dados reais têm estrutura mista, bordas, texturas e ruído que
podem anular o ganho. Só resultados em dados reais têm validade para publicação.

---

## Hipótese

**H-primária:** Para imagens médicas e de fax dos corpora canônicos (Silesia `mr`, `x-ray`,
Calgary/Canterbury `pic`/`ptt5`), o modelo de contexto de ordem 1 baseado em
percurso Hilbert produz **model_bps < model_bps do percurso raster**.

**H-secundária:** A vantagem se mantém mesmo considerando o overhead de alinhamento
em grade 2D (padding para potência de 2).

**H-nula:** Dados reais têm correlação espacial 2D insuficiente ou irregular para que
o percurso Hilbert supere o raster no modelo de contexto de ordem 1.

---

## Desenho Experimental

### Datasets (por ordem de prioridade)

| Prioridade | Arquivo | Tamanho | Tipo | Expectativa |
|-----------|---------|---------|------|-------------|
| 1 | `pic` (Calgary) | 513 KB | Fax bitmap 1-bit | Hilbert < raster bps |
| 1 | `ptt5` (Canterbury) | 513 KB | Fax bitmap 1-bit | Hilbert < raster bps |
| 2 | `x-ray` (Silesia) | 8.47 MB | Raio-X DICOM 16-bit | Hilbert < raster bps |
| 2 | `mr` (Silesia) | 9.97 MB | MRI DICOM 16-bit | Hilbert < raster bps |
| 3 | `sao` (Silesia) | 7.25 MB | Catálogo estelar (binário) | Incerto |

### Protocolo

1. Carregar arquivo como bytes raw (para DICOM: extrair apenas pixel data, ignorar header)
2. Executar pipeline A (raster), B (Morton), C (Hilbert) sobre os mesmos bytes
3. Registrar: `zlib_ratio`, `model_bps`, tempo de encode, side usado
4. Repetir com múltiplos `side` candidates: [512, 1024, 2048]
5. Comparar model_bps: Hilbert vs Raster (delta absoluto e percentual)

### Métricas de Aceitação

| Critério | Threshold |
|----------|-----------|
| Hilbert supera Raster em model_bps | ≥ 2% redução |
| Hilbert supera Raster em zlib_ratio | ≥ 0.5% melhoria |
| Resultado consistente em ≥ 3 arquivos do estrato 2D | — |

### Análise de Confundidor

Antes de concluir, verificar:
- O padding (zeros adicionados) está distorcendo o resultado?
  → Testar com e sem padding, comparar deltas
- O side escolhido afeta o resultado?
  → Testar todos os sides candidatos, verificar estabilidade

---

## Hipótese sobre Mecanismo

Se Hilbert vencer em imagens reais, o mecanismo provável é:

```
Imagem 2D tem correlação local: pixel(x,y) ≈ pixel(x±1, y±1)
↓
Percurso Hilbert mantém vizinhos 2D próximos no percurso 1D
↓
P(s_t | s_{t-1}) captura mais redundância via transições locais
↓
Model_bps menor → entropia estimada menor → compressor final mais eficiente
```

Se Hilbert **não** vencer, hipóteses alternativas:
1. A correlação em dados reais é muito local (sub-pixel) para ser capturada por ordem-1
2. Ruído e bordas quebram a correlação antes que o percurso ajude
3. É necessário modelo de contexto de ordem superior (ver Q-006)

---

## Preparação Necessária

- [ ] Download dos arquivos canônicos (ver Q-002)
- [ ] Para DICOM: implementar `loader.py` com extração de pixel data raw
- [ ] Executar `compare_orders.py` com os novos arquivos
- [ ] Tabela comparativa raster vs Morton vs Hilbert por arquivo

---

## Critério de Conclusão

- **Conclusão positiva:** ≥ 3 arquivos do estrato 2D mostram Hilbert < raster em model_bps
  com margem ≥ 2%. Migrar para A-003.
- **Conclusão negativa:** Ganho consistentemente < 1% ou inexistente. Revisitar hipótese
  de mecanismo, possivelmente elevar para ordem de contexto maior (Q-006).
- **Inconclusivo:** Resultados mistos — abrir Q adicional sobre papel do tipo específico
  de dado 2D.
