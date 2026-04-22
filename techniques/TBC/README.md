# TBC — TuringBitCompression

Técnica experimental de compressão lossless baseada em **codificação por planos de indicadores** ordenados por frequência decrescente de símbolo.

Parte do projeto-guarda-chuva [HSC](../../README.md) mas autônoma — tem código, testes e documentação próprios.

---

## Ideia central

Dado um fluxo binário, em vez de codificar símbolo a símbolo, codifica-se **onde cada símbolo ocorre**:

1. Agrupa os bits em símbolos de `k` bits (alfabeto de tamanho `2^k`, default `k=2`).
2. Ordena os símbolos por frequência descendente: `σ₁ ≥ σ₂ ≥ … ≥ σ_m`.
3. Para cada `σ_i` (exceto o último), emite um **plano indicador** `P_i`: um bitmask sobre as posições ainda não preenchidas, com `1` onde `σ_i` ocorre.
4. O último símbolo é implícito — ocupa o resíduo de todas as posições remanescentes, sem gastar plano.
5. (Planejado) Recursão sobre os planos até não haver mais ganho.

### Exemplo trabalhado

```
dados: 10 01 10 01 10 01 01 01 01 01 01 01 01 11        (14 símbolos, 28 bits)

Frequências:  01 ×10   10 ×3   11 ×1   00 ×0

P₁ (onde σ₁=01 ocorre, 14 posições):   0 1 0 1 0 1 1 1 1 1 1 1 1 0       14 bits
P₂ (onde σ₂=10 ocorre, restam 4):      1 1 1 0                            4 bits
P₃ (onde σ₃=11 ocorre, resta 1):       1                                   1 bit
σ₄=00 é resíduo implícito (zero ocorrências, nada a armazenar)

Total bruto: 19 bits vs. 28 originais (sem header, sem recursão)
```

---

## Taxonomia de máquinas

O TBC é uma família de ISAs de complexidade crescente. Cada máquina é um programa executado pelo decodificador. Ver [`machines.md`](machines.md) para a definição completa.

| Máquina | ISA | Expressividade | Artefato |
|---------|-----|----------------|----------|
| **M0** | planos puros (sem opcodes) | bitplane coding | [`tbc.py`](tbc.py) |
| **M1** | `LIT` / `REP` / `RAW` / `END` | RLE | [`m1.py`](m1.py) |
| **M2** | M1 + `REF(offset, length)` | LZ77 | planejado |
| **M3** | M2 + `DEF` / `CALL` / `LOOP` | grammar-based | planejado |

## Estado da implementação

| Artefato | Status |
|---|---|
| Descrição conceitual do método | [`compression_logic_03.md`](compression_logic_03.md) |
| Taxonomia formal das máquinas | [`machines.md`](machines.md) |
| M0 — encoder/decoder + round-trip | [`tbc.py`](tbc.py) + [`test_tbc.py`](test_tbc.py) |
| M1 — encoder/decoder + round-trip | [`m1.py`](m1.py) + [`test_m1.py`](test_m1.py) |
| Benchmark consolidado | [`bench_machines.py`](bench_machines.py) |
| M2 — back-reference (REF) | Planejado |
| M3 — subprogramas (DEF/CALL/LOOP) | Planejado |
| Serialização binária final padronizada | Planejado |
| Recursão TBC sobre planos | Planejado |

## Resultados iniciais (canterbury/xargs.1, 4227 bytes)

| Método | Bytes | Razão |
|--------|-------|-------|
| M0 (k=1) | 4232 | 1.00x |
| M0 (k=2) | 4378 | 0.97x |
| M1 (k=2) | 7081 | 0.60x |
| M1 (k=8) | 4324 | 0.98x |
| zlib -9  | 1736 | 2.43x |
| bz2 -9   | 1762 | 2.40x |

**Leitura:** M0 puro é neutro (rearranjo sem entropia). M1 (RLE) não comprime texto estruturado — domina o caso com runs (3.88x em 1000 'A' com k=8). Para superar texto será necessário M2 (back-reference, classe LZ).

Reproduzir: `python bench_machines.py --all`.

---

## Uso

### Rodar testes

```bash
cd techniques/TBC
python test_tbc.py
```

Sai com `Todos os testes passaram.` quando o round-trip está correto em todos os cenários de teste.

### API (nível 1)

```python
from tbc import encode, decode, summary

data = b"exemplo de bytes a comprimir"
payload = encode(data, k=2)          # TBCPayload
decoded = decode(payload)            # bytes
assert decoded == data

print(summary(payload))
# {'k': 2, 'N_symbols': ..., 'total_plane_bits': ..., 'header_bits': ..., ...}
```

O `TBCPayload` é uma `dataclass` com os campos `k`, `N`, `tail_bits`, `ranking`, `planes`. Ainda **não** há serialização binária final — o objetivo atual é validar a lógica, não produzir um formato de arquivo.

---

## Quando TBC deve ganhar ou perder

O total de bits dos planos é:

```
Σ Lᵢ = (m-1)·N − Σⱼ=1..m-2 (m-1-j)·fⱼ
```

onde `m = 2^k`, `N` é número de símbolos e `fⱼ` a frequência do símbolo rank-j.

- **Ganho esperado**: distribuição desbalanceada (algum `f_j` grande em relação a `N`).
- **Perda esperada**: distribuição uniforme — aí a soma dos planos supera `k·N` bits originais.
- **Caso degenerado útil**: um único símbolo domina — os planos subsequentes ficam todos vazios (curto-circuito).

A análise de ganho real depende também do header e da futura recursão/entropia nos planos.

---

## Conexão com literatura

Técnicas relacionadas, mas distintas:

| Técnica | Relação |
|---|---|
| Bitplane coding (JBIG/JBIG2) | Decomposição por plano de bits — TBC usa planos por símbolo ordenados por frequência |
| Symbol ranking (Bentley et al. 1986; Ryabko 1987) | Rank dinâmico do vocabulário — TBC usa ranking estático por frequência global |
| Move-to-Front (MTF) | Reordena vocabulário por recência; análogo mas adaptativo |
| BWT + MTF | Produz bitmasks de posições, estrutura similar ao Passo 3 do TBC |
| PPM / PAQ | Modelos de contexto adaptativos — abordagem ortogonal |

**Diferencial específico do TBC**: planos por símbolo em ranking de frequência global, com o último símbolo implícito como resíduo, destinados à recursão. Até o levantamento atual, não foi identificado equivalente direto na literatura.

## Referências

- Bentley, J.L. et al. (1986). A locally adaptive data compression scheme. *CACM* 29(4).
- Ryabko, B.Y. (1987). Data compression by means of a book stack. *Problems of Information Transmission*.
- Witten, I., Neal, R., Cleary, J. (1987). Arithmetic coding for data compression. *CACM* 30(6).
- Seong, S.W., Mishra, P. (2008). Bitmask-based code compression for embedded systems. *ICCAD*.
