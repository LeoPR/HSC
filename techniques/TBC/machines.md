# Máquinas TBC — Taxonomia Progressiva

> **Premissa de leitura.** Cada máquina é um **ISA** (Instruction Set Architecture). O arquivo comprimido é um programa para essa ISA. Decompressão é execução. Qualquer máquina maior contém a anterior como caso particular. Qualidade de compressão é subproduto; a prioridade é que cada máquina tenha semântica decidível, round-trip exato e grau crescente de expressividade.

---

## M0 — Planos fixos, sem programa

**ISA:** nenhuma. O arquivo é puramente declarativo.

**Estrutura:**
```
header    k, N, ranking_permutation
planes    P₁, P₂, …, P_{m−1}        (ver compression_logic_03.md §3)
```

**Decoder:** percorre os planos na ordem do ranking e preenche posições. Todas as posições não cobertas recebem σ_m. É equivalente a uma máquina de estados finitos.

**Limite:** sem compressão por si só. Planos são máscaras; sua entropia é herdada do dado original. M0 **apenas rearranja**. Qualquer ganho exige entropia posterior nos planos ou recursão.

**Status no protótipo:** implementado em [`tbc.py`](tbc.py), round-trip verificado em [`test_tbc.py`](test_tbc.py).

---

## M1 — VM linear com RLE

**ISA (opcodes de 2 bits):**

| Opcode | Bits | Operandos | Semântica |
|--------|------|-----------|-----------|
| `LIT`  | `00` | símbolo (`k` bits) | Emite 1 símbolo |
| `REP`  | `01` | símbolo (`k` bits), n (Elias-γ ≥ 2) | Emite símbolo n vezes |
| `RAW`  | `10` | len (Elias-γ ≥ 2), len×k bits | Emite len símbolos literais |
| `END`  | `11` | —         | Termina o programa |

**Estrutura do arquivo:**
```
header    k (3 bits), N (32 bits)
program   sequência de (opcode, operandos) até encontrar END
```

**Decoder (pseudocódigo):**
```
out = []
loop:
  op = read(2)
  if op == 00: out.append(read(k))
  if op == 01: s = read(k); n = read_gamma(); out.extend([s]*n)
  if op == 10: n = read_gamma(); out.extend([read(k) for _ in range(n)])
  if op == 11: break
return out
```

**Encoder (guloso):** varre os dados com ponteiro. Se o símbolo atual se repete ≥ 2 vezes, emite `REP`. Se há uma sequência de ≥ 2 símbolos não-repetidos, emite `RAW`. Caso contrário, emite `LIT`.

**Expressividade em relação a M0:** incomparável direto. M1 não usa planos; os símbolos são emitidos linearmente. M1 captura runs (RLE) que M0 expressa apenas implicitamente via padrão de bits nos planos.

**O que falta em M1:** qualquer coisa que dependa de referência a posições anteriores (cópia, gramática). M1 é strictly run-length.

---

## M2 — M1 + referência retroativa

**ISA adicional:**

| Opcode | Bits  | Operandos | Semântica |
|--------|-------|-----------|-----------|
| `REF`  | `110` | offset (Elias-γ), length (Elias-γ) | Copia `length` símbolos começando `offset` posições atrás da posição atual |

Para caber em 2 bits, `REF` precisaria deslocar algum opcode. Opções:

- **Opção A — 3 bits para todos os opcodes.** Opcodes ficam em `000..111` (8 entradas), com folga.
- **Opção B — escape.** Manter 2 bits; `11` deixa de ser `END` e passa a ser prefixo para um sub-opcode de 2 bits: `1100=END`, `1101=REF`, `1110=?`, `1111=?`.

A opção B privilegia o caso comum (opcodes frequentes em 2 bits) mas introduz variabilidade. A opção A é mais simples e provavelmente ganha em arquivos grandes.

**Recomendação para o protótipo:** começar com **opção A (3 bits)** até termos dados empíricos que justifiquem otimizar.

**Encoder:** busca em janela deslizante por matches de `length ≥ 3` (abaixo disso RAW é mais barato). Implementação de referência: suffix array ou hash de trigramas.

**Expressividade sobre M1:** adiciona a classe LZ77 inteira. Supera M1 em qualquer dado com repetições não-adjacentes.

---

## M3 — M2 + definição e chamada de subprograma

**ISA adicional:**

| Opcode | Bits  | Operandos | Semântica |
|--------|-------|-----------|-----------|
| `DEF`  | —     | id (6 bits), tamanho em instruções (γ) | Abre um bloco; as próximas instruções pertencem ao subprograma `id` e **não são executadas** |
| `CALL` | —     | id (6 bits) | Executa o subprograma `id` |
| `LOOP` | —     | count (γ), body_len (γ) | Executa as próximas `body_len` instruções `count` vezes |

`DEF` / `CALL` generalizam `REF`: em vez de copiar bytes, executam código. Permite fatorar padrões em subprogramas nomeados.

**Expressividade sobre M2:** adiciona a classe de **grammar-based compression** (Re-Pair, Sequitur). Programa pode ter profundidade arbitrária.

**Custo:** id de subprograma gasta bits fixos; só compensa em fluxos longos com padrões hierárquicos. Para M3 ser útil, o encoder precisa descobrir os padrões frequentes — problema de inferência de gramática.

---

## M∞ — Máquina completa

Se levarmos M3 ao limite (labels arbitrários, saltos condicionais, aritmética simples) chegamos a uma máquina Turing-completa. Nesse regime, o comprimento ótimo do programa é a **complexidade de Kolmogorov** do dado — incomputável em geral, mas aproximável na prática.

M∞ é o horizonte teórico. Nenhum codec real o atinge, mas o enquadramento explica por que máquinas maiores ganham em média: carregam menos dado redundante no programa.

---

## Princípios gerais da família

**1. Opcode curto, operandos longos.**
O opcode é o único "custo inevitável" de cada instrução. Em M1/M2/M3 mantemos 2–3 bits. Operandos usam codificação variável (Elias-γ) para não penalizar valores pequenos.

**2. Hibridismo fixo/serial.**
O header é **fixo** — tem campos em posições conhecidas, decodificáveis sem ambiguidade. O programa é **serial** — cada instrução só faz sentido no contexto da posição do ponteiro. A fronteira entre os dois deve ser explícita e pequena.

**3. Inferência máxima.**
Qualquer campo que o decodificador possa **deduzir** não precisa ser armazenado. Exemplos:
- Se `N` (tamanho do output) for conhecido, o programa pode omitir `END`.
- Se o alfabeto é conhecido e exaustivo, `ranking` é uma permutação de um conjunto fixo — dá para codificar como índice de permutação em `log₂(m!)` bits.
- Em `REP(s, n)`, se `s` é o símbolo mais frequente, talvez o opcode próprio possa escondê-lo.

**4. Política de codificação explícita.**
O encoder precisa de uma regra determinística para escolher entre instruções concorrentes (emitir `REP` vs `RAW` vs `LIT`). A política pode ser gulosa (miopic), ótima via programação dinâmica, ou aprendida. Para o protótipo: gulosa.

**5. Round-trip antes de tudo.**
Toda máquina nova entra no protótipo com `encode(decode(x)) == x` como pré-condição. Taxa de compressão é medida só depois.

---

## Roteiro de implementação

| Etapa | Máquina | Artefato                    | Critério                          |
|-------|---------|-----------------------------|-----------------------------------|
| 1 (pronta) | M0 | [`tbc.py`](tbc.py)          | Round-trip OK                     |
| 2 (hoje)   | M1 | `m1.py`                     | Round-trip OK + bench em xargs.1  |
| 3          | M2 | `m2.py`                     | Round-trip OK + bench em xargs.1  |
| 4          | M3 | `m3.py`                     | Round-trip OK + bench em xargs.1  |
| 5          | —  | `bench_machines.py`         | Tabela comparativa                |

Cada etapa é independente: M1 não depende de M2, e a comparação é feita no final sobre o mesmo dado.

---

## Dataset de referência para bring-up

[`datasets/canterbury/xargs.1`](../../datasets/canterbury/xargs.1) (4227 bytes, manpage em nroff).

Escolhas:
- **Pequeno** (testes em segundos) mas não trivial.
- **Texto real** com estrutura repetida (`\-`, `.SH`, comandos) e ruído (parâmetros, exemplos).
- **Canônico** do Canterbury Corpus — resultados comparáveis com a literatura.

Baselines reportados no benchmark:
- `zlib -9`: 1736 bytes (2.43x)
- `bz2 -9`: 1762 bytes (2.40x)
- `M0 (k=1)`: 4232 bytes (1.00x) — confirma que M0 puro não comprime
