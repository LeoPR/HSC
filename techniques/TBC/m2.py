"""
Maquina M2 — M1 + referencia retroativa (LZ77-style).

ISA (opcodes de 3 bits — opcao A do machines.md):

    000 LIT  (simbolo k bits)                      — emite 1 simbolo
    001 REP  (simbolo k bits, n Elias-gamma >=2)   — emite simbolo n vezes
    010 RAW  (len Elias-gamma >=2, len*k bits)     — emite len simbolos literais
    011 REF  (offset Elias-gamma, len Elias-gamma) — copia len simbolos a partir
                                                     de (posicao_atual - offset)
    100 END                                        — termina
    101..111 reservados para M3

Formato do arquivo (bits):
    header  k (3 bits), N_symbols (32 bits), leftover_bits (4 bits), leftover content
    body    sequencia de instrucoes ate END

Encoder: greedy com janela deslizante + hash de trigramas.
- Para cada posicao: consulta hash do trigrama corrente, tenta estender matches
  entre candidatos na janela. Se len_match >= MIN_MATCH, emite REF. Senao, cai
  para a politica do M1 (REP/RAW/LIT).

Ver machines.md para a taxonomia.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from m1 import (
    BitReader,
    BitWriter,
    _bytes_to_symbols,
    _symbols_to_bytes,
    symbols_tail_bits,
)


# ── Opcodes (3 bits) ───────────────────────────────────────────────────

OP_LIT = 0b000
OP_REP = 0b001
OP_RAW = 0b010
OP_REF = 0b011
OP_END = 0b100

OPCODE_BITS = 3

# Parametros da busca
DEFAULT_WINDOW = 4096      # janela deslizante em simbolos
DEFAULT_MAX_ATTEMPTS = 32  # maximo de candidatos consultados por posicao
MIN_MATCH = 3              # comprimento minimo para REF valer a pena


# ── Estrutura ──────────────────────────────────────────────────────────


@dataclass
class M2Payload:
    k: int
    N: int
    compressed: bytes
    n_ops: dict[str, int]

    def size_bytes(self) -> int:
        return len(self.compressed)


# ── Busca de matches ───────────────────────────────────────────────────


def _find_match(
    symbols: list[int],
    i: int,
    hashmap: dict[tuple[int, int, int], list[int]],
    window: int,
    max_attempts: int,
) -> tuple[int, int]:
    """Retorna (offset, length) do melhor match, ou (0, 0) se nao ha.

    Usa hash de trigramas. Sem overlap (match inteiro antes de i).
    """
    N = len(symbols)
    if i + 2 >= N:
        return 0, 0
    tri = (symbols[i], symbols[i + 1], symbols[i + 2])
    candidates = hashmap.get(tri)
    if not candidates:
        return 0, 0

    start = i - window
    best_offset = 0
    best_len = 0
    attempts = 0
    # Percorre candidatos do mais recente ao mais antigo
    for idx in range(len(candidates) - 1, -1, -1):
        j = candidates[idx]
        if j < start:
            break  # fora da janela
        if j >= i:
            continue  # posicao atual ou futura (nao deveria acontecer)
        # Limite de match sem overlap
        max_k = min(N - i, i - j)
        # Confere os 3 primeiros (ja sabemos que trigrama bate — mas por seguranca)
        k = 0
        while k < max_k and symbols[j + k] == symbols[i + k]:
            k += 1
        if k > best_len:
            best_len = k
            best_offset = i - j
        attempts += 1
        if attempts >= max_attempts:
            break
    return best_offset, best_len


def _update_hash(
    hashmap: dict[tuple[int, int, int], list[int]],
    symbols: list[int],
    from_pos: int,
    to_pos: int,
) -> None:
    """Registra trigramas começando em [from_pos, to_pos) no hashmap."""
    N = len(symbols)
    for p in range(from_pos, to_pos):
        if p + 2 >= N:
            break
        tri = (symbols[p], symbols[p + 1], symbols[p + 2])
        hashmap[tri].append(p)


# ── Encoder ────────────────────────────────────────────────────────────


def encode(
    data: bytes,
    k: int = 2,
    window: int = DEFAULT_WINDOW,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    min_match: int = MIN_MATCH,
) -> M2Payload:
    """Compila dados para programa M2 (M1 + REF).

    Estrategia:
        1. Busca match via hash de trigramas. Se len >= min_match, emite REF.
        2. Senao, tenta REP (run do simbolo atual >= 2).
        3. Senao, tenta RAW (sequencia sem run >= 2 de comprimento >= 2).
        4. Senao, LIT.
    """
    if not (1 <= k <= 8):
        raise ValueError(f"k deve estar em [1,8], recebeu {k}")

    symbols, leftover = _bytes_to_symbols(data, k)
    N = len(symbols)

    w = BitWriter()
    w.write(k - 1, 3)
    w.write(N, 32)
    w.write(leftover, 4)
    for b in symbols_tail_bits(data, leftover):
        w.write(b, 1)

    n_ops = {"LIT": 0, "REP": 0, "RAW": 0, "REF": 0, "END": 0}
    hashmap: dict[tuple[int, int, int], list[int]] = defaultdict(list)

    i = 0
    while i < N:
        # 1) Tenta REF
        offset, match_len = _find_match(symbols, i, hashmap, window, max_attempts)
        if match_len >= min_match:
            w.write(OP_REF, OPCODE_BITS)
            w.write_gamma(offset)
            w.write_gamma(match_len)
            _update_hash(hashmap, symbols, i, i + match_len)
            i += match_len
            n_ops["REF"] += 1
            continue

        # 2) Tenta REP
        run = 1
        while i + run < N and symbols[i + run] == symbols[i]:
            run += 1
        if run >= 2:
            w.write(OP_REP, OPCODE_BITS)
            w.write(symbols[i], k)
            w.write_gamma(run)
            _update_hash(hashmap, symbols, i, i + run)
            i += run
            n_ops["REP"] += 1
            continue

        # 3) Tenta RAW: olhar a frente por sequencia sem run
        j = i + 1
        while j < N:
            if j + 1 < N and symbols[j + 1] == symbols[j]:
                break
            j += 1
        raw_len_limit = j - i
        if raw_len_limit >= 2:
            # Durante a varredura, atualizamos o hash incrementalmente
            # para que futuras consultas REF vejam trigramas ja registrados.
            # Se em alguma posicao scan > i encontrarmos um REF bom, truncamos.
            scan = i
            while scan < i + raw_len_limit:
                if scan > i:
                    off2, len2 = _find_match(symbols, scan, hashmap, window, max_attempts)
                    if len2 >= min_match:
                        break
                # Registra trigrama iniciando em scan
                if scan + 2 < N:
                    tri = (symbols[scan], symbols[scan + 1], symbols[scan + 2])
                    hashmap[tri].append(scan)
                scan += 1
            best_raw = scan - i
            if best_raw >= 2:
                w.write(OP_RAW, OPCODE_BITS)
                w.write_gamma(best_raw)
                for s in symbols[i:i + best_raw]:
                    w.write(s, k)
                # Trigramas ja foram registrados no loop acima
                i += best_raw
                n_ops["RAW"] += 1
                continue

        # 4) LIT
        w.write(OP_LIT, OPCODE_BITS)
        w.write(symbols[i], k)
        _update_hash(hashmap, symbols, i, i + 1)
        i += 1
        n_ops["LIT"] += 1

    w.write(OP_END, OPCODE_BITS)
    n_ops["END"] = 1

    return M2Payload(k=k, N=N, compressed=w.to_bytes(), n_ops=n_ops)


# ── Decoder ────────────────────────────────────────────────────────────


def decode(payload: M2Payload) -> bytes:
    r = BitReader(payload.compressed)

    k_minus_1 = r.read(3)
    k = k_minus_1 + 1
    N = r.read(32)
    leftover = r.read(4)
    tail_bits = [r.read(1) for _ in range(leftover)]

    if k != payload.k or N != payload.N:
        raise ValueError(
            f"header divergente: esperava k={payload.k}, N={payload.N} "
            f"mas leu k={k}, N={N}"
        )

    out: list[int] = []
    while True:
        op = r.read(OPCODE_BITS)
        if op == OP_END:
            break
        elif op == OP_LIT:
            out.append(r.read(k))
        elif op == OP_REP:
            s = r.read(k)
            n = r.read_gamma()
            out.extend([s] * n)
        elif op == OP_RAW:
            n = r.read_gamma()
            out.extend([r.read(k) for _ in range(n)])
        elif op == OP_REF:
            offset = r.read_gamma()
            length = r.read_gamma()
            if offset > len(out):
                raise ValueError(f"REF offset fora de alcance: {offset} > {len(out)}")
            start = len(out) - offset
            # Copia sem overlap (encoder garante offset >= length)
            for j in range(length):
                out.append(out[start + j])
        else:
            raise ValueError(f"opcode desconhecido: {op}")

        if len(out) > N:
            raise ValueError(f"output excedeu N: {len(out)} > {N}")

    if len(out) != N:
        raise ValueError(f"output incompleto: {len(out)} != {N}")

    return _symbols_to_bytes(out, k, tail_bits)


# ── Diagnostico ────────────────────────────────────────────────────────


def summary(payload: M2Payload, original_size: int) -> dict:
    total = payload.size_bytes()
    return {
        "k": payload.k,
        "N_symbols": payload.N,
        "original_bytes": original_size,
        "compressed_bytes": total,
        "ratio": original_size / total if total else float("inf"),
        "ops": dict(payload.n_ops),
    }
