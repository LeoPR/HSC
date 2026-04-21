---
id: Q-014
titulo: Arquivo comprimido como sistema auto-descritivo — a função φ descreve a si mesma
categoria: design
prioridade: alta
criado: 2026-04-03
relacionado: [Q-011, Q-013]
---

## Pergunta

Como projetar o formato de arquivo do framework de compressão funcional topológica
de forma que ele seja **auto-descritivo** — contenha todas as informações necessárias
para sua própria decompressão, sem dependência de software externo?

---

## Motivação

Se o arquivo comprimido é a função φ, surge o problema prático:
> "Como o decoder sabe o que fazer com os bytes do arquivo?"

Em compressão clássica, o decoder é um programa separado (zip, gzip, bzip2).
No framework proposto, φ pode ter forma qualquer — curva de Hilbert, rede neural,
gramática, F-transform. O decoder precisa saber:
1. Qual família de φ foi usada
2. Quais parâmetros de φ
3. Qual estrutura tem C
4. Como reconstruir D a partir de φ(C)

**Solução:** O arquivo carrega φ + o interpretador de φ + a descrição de C.
O arquivo é, ele mesmo, o programa de decompressão.

---

## Conceitos Fundantes

### Autopoiese (Maturana-Varela, 1972)

Um sistema autopoiético **produz os componentes necessários para sua própria
manutenção**. Uma célula sintetiza as proteínas que a compõem.

**Aplicação:** Um arquivo autopoiético contém:
- Os dados (ou φ que os gera)
- O interpretador necessário para ler os dados
- Os metadados que descrevem a estrutura
- Tudo isso se referencia mutuamente

O arquivo "sabe" como ser decomprimido — sem dependência externa.

### Códigos Auto-Delimitantes (Levin-Gács, 1974)

Programas que carregam a informação de onde terminam:
```
<comprimento em unário> <programa>
```

Propriedade: o decoder pode ler o programa sem saber seu tamanho a priori.
Custo adicional: O(log n) bits para o prefixo de comprimento.

**Importância para o framework:** A descrição de φ precisa ser auto-delimitante
para que o arquivo possa conter múltiplos componentes sem delimitadores externos.

### MDL como Critério de Design

O arquivo ótimo segundo MDL:
```
arquivo* = argmin |φ| + |C | φ| + |residual | φ, C|
```

Cada componente condicionado nos anteriores — φ define o vocabulário para
descrever C, e (φ, C) definem o vocabulário para descrever o residual.

---

## Estrutura Proposta do Formato

```
┌────────────────────────────────────────────────────┐
│  MAGIC + VERSION  (4 bytes)                        │
│    Identifica o framework, versão do formato       │
├────────────────────────────────────────────────────┤
│  TOPOLOGY HEADER  (auto-delimitante)               │
│    Tipo de φ: {hilbert, siren, ifs, grammar, ...}  │
│    Dimensão de C: d                                │
│    Dimensão de D: n                                │
│    Parâmetros de tolerância: ε (lossy/lossless)   │
│    Hash de verificação                             │
├────────────────────────────────────────────────────┤
│  COMPACT SPACE C  (auto-delimitante)               │
│    Descrição topológica de C                       │
│    Diagrama de persistência (se calculado)         │
│    Parâmetros da partição fuzzy (se aplicável)     │
├────────────────────────────────────────────────────┤
│  FUNCTION φ  (auto-delimitante)                    │
│    Parâmetros de φ no formato da família escolhida │
│    Ex (Hilbert): {side, dimensões, curva_variant}  │
│    Ex (SIREN):   {arquitetura, pesos θ comprimidos}│
│    Ex (IFS):     {transformações afins w₁...wₖ}   │
│    Ex (grammar): {regras R, símbolo inicial S}     │
├────────────────────────────────────────────────────┤
│  SPARSE RESIDUAL  (auto-delimitante)               │
│    O que φ(C) não capturou: r = D - φ(C)          │
│    Codificado com Golomb/Elias-delta               │
│    Hierárquico: resíduo do resíduo (se necessário) │
├────────────────────────────────────────────────────┤
│  DECODER  (opcional, para portabilidade máxima)    │
│    Bytecode mínimo que avalia φ                    │
│    Ex: WASM (~kilobytes para implementação simples)│
│    Garante decompressão sem software externo       │
└────────────────────────────────────────────────────┘
```

---

## Análise de Overhead

### Custo de Cada Componente

| Componente | Tamanho típico | Quando vale |
|---|---|---|
| Magic + Version | 4 bytes | Sempre |
| Topology Header | 20-100 bytes | Sempre |
| Compact Space C | 10-1000 bytes | Sempre (varia com d) |
| Function φ (Hilbert) | ~50 bytes | Arquivos > 1 KB |
| Function φ (SIREN) | KB-MB (pesos) | Arquivos > 1 MB |
| Sparse Residual | varia | Depende de φ |
| Decoder (WASM) | ~10 KB | Quando portabilidade > eficiência |

**Break-even point:** O overhead fixo (header + φ) precisa ser menor que
o dado original para a compressão ser positiva.

Para φ_Hilbert: overhead ≈ 200 bytes → break-even ≈ 1 KB de dado.
Para φ_SIREN: overhead ≈ pesos da rede → break-even ≈ tamanho dos pesos.

### Custo do Decoder Embutido

O decoder WASM para φ_Hilbert:
- Implementação Python atual: ~200 linhas
- Compilado para WASM: ~5-10 KB
- Overhead relativo: 5-10 KB / tamanho_dado

Para dados < 10 KB, o decoder representa overhead significativo.
Para dados > 100 KB, o overhead é < 10% — aceitável para portabilidade.

---

## Variantes por Caso de Uso

### Variant A — Mínima (sem decoder)

```
Header + C + φ + residual
```
Assume que o decoder está instalado separadamente.
Menor overhead. Equivalente a ZIP/gzip em termos de dependência.

### Variant B — Auto-contido (com decoder WASM)

```
Header + C + φ + residual + decoder
```
Arquivo decomprime-se em qualquer ambiente com runtime WASM.
Overhead: +5-50 KB.

### Variant C — Quine (completamente auto-explicativo)

```
Header + C + φ + residual + decoder + especificação do formato
```
Arquivo contém a especificação completa para ser implementado do zero.
Overhead maior, mas garantia de preservação a longo prazo.

---

## Conexão com Formatos Existentes

| Formato | Auto-descritivo? | O que carrega | Limitação |
|---------|-----------------|---------------|-----------|
| ZIP | ❌ (precisa de unzip) | dados + tabela de diretório | decoder externo |
| HDF5 | ✅ parcial | dados + metadados | decoder externo |
| F3 (SIGMOD 2025) | ✅ | dados + metadados + WASM decoder | novo, pouco adotado |
| **Proposta** | ✅ | φ + C + residual + decoder | a definir |

---

## Autodescrição Fuzzy: Metadados com Incerteza

Para dados de origem contínua, os metadados do arquivo podem carregar
graus de pertencimento fuzzy:

```
"Este arquivo é 87% imagem natural, 12% gradiente, 1% ruído"
"A partição ótima tem entre 64 e 128 componentes (grau 0.7 para 96)"
```

Isso permite ao decoder tomar decisões mais informadas sobre como reconstruir.

---

## Propriedade Quine do Arquivo

Um arquivo que contém sua própria especificação satisfaz:
```
decode(arquivo) = D
especificação(arquivo) = "como construir arquivo a partir de D"
```

Isso é análogo a um **quine** em programação — um programa que imprime seu
próprio código. Aqui: um arquivo que contém a receita para recriar a si mesmo.

**Implicação para preservação:** Um arquivo quine-like pode ser recriado do zero
a partir da especificação contida nele + dados originais. Útil para arquivamento
de longo prazo onde formatos de arquivo podem se tornar obsoletos.

---

## Plano de Implementação

### Fase 1 — Variant A (sem decoder)

```python
# prototype/format/writer.py
def write_archive(D: bytes, phi_family: str, phi_params: dict,
                  C_params: dict, residual: bytes) -> bytes:
    """Serializa (φ, C, residual) em formato auto-delimitante."""

# prototype/format/reader.py
def read_archive(archive: bytes) -> tuple[str, dict, dict, bytes]:
    """Deserializa e retorna (phi_family, phi_params, C_params, residual)."""

# prototype/format/decoder.py
def decompress(archive: bytes) -> bytes:
    """Decomprime arquivo usando φ e residual."""
```

### Fase 2 — Variant B (com WASM)

Compilar implementação Python de φ_Hilbert para WASM e embutir no formato.
Usar ferramentas: emscripten, wasm-pack, ou compilação manual em C.

---

## Critério de Conclusão

- [ ] Formato Variant A especificado e implementado para φ_Hilbert
- [ ] Codec completo: compress(D) → arquivo, decompress(arquivo) → D com verificação
- [ ] Overhead documentado por tamanho de arquivo (tabela)
- [ ] Comparação com gzip/bzip2 em arquivos pequenos (< 1 KB) e grandes (> 1 MB)
- [ ] Decisão sobre Variant B (decoder embutido) para o paper final
