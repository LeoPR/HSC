"""
Maquina M1 — VM linear com RLE.

ISA (opcodes de 2 bits):
    00 LIT  (simbolo k bits)                       — emite 1 simbolo
    01 REP  (simbolo k bits, n Elias-gamma >=2)    — emite simbolo n vezes
    10 RAW  (len Elias-gamma >=2, len*k bits)      — emite len simbolos literais
    11 END                                         — termina

Formato do arquivo (bits):
    header  k (3 bits), N_symbols (32 bits)
    body    sequencia de instrucoes ate encontrar END

Ver machines.md para taxonomia completa.
"""

from __future__ import annotations

from dataclasses import dataclass


# ── Primitivas de bitstream ────────────────────────────────────────────


class BitWriter:
    """Escritor de stream de bits. Acumula bits MSB-first em bytearray."""

    __slots__ = ("bits",)

    def __init__(self) -> None:
        self.bits: list[int] = []

    def write(self, value: int, n: int) -> None:
        for i in range(n - 1, -1, -1):
            self.bits.append((value >> i) & 1)

    def write_gamma(self, value: int) -> None:
        """Elias-gamma: v >= 1. Emite floor(log2(v)) zeros + binario(v)."""
        if value < 1:
            raise ValueError(f"Elias-gamma requer v >= 1, recebeu {value}")
        bits = value.bit_length()
        # (bits-1) zeros + binario completo (que comeca com 1)
        for _ in range(bits - 1):
            self.bits.append(0)
        for i in range(bits - 1, -1, -1):
            self.bits.append((value >> i) & 1)

    def to_bytes(self) -> bytes:
        # Padding a direita com zeros ate multiplo de 8
        pad = (-len(self.bits)) % 8
        out = bytearray()
        cur = 0
        count = 0
        for b in self.bits + [0] * pad:
            cur = (cur << 1) | b
            count += 1
            if count == 8:
                out.append(cur)
                cur = 0
                count = 0
        return bytes(out)

    def nbits(self) -> int:
        return len(self.bits)


class BitReader:
    """Leitor de stream de bits. Consome do bytearray MSB-first."""

    __slots__ = ("data", "pos", "nbits")

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0
        self.nbits = len(data) * 8

    def read(self, n: int) -> int:
        if self.pos + n > self.nbits:
            raise EOFError(f"leitura alem do fim: pos={self.pos}, n={n}, total={self.nbits}")
        value = 0
        for _ in range(n):
            byte_idx = self.pos >> 3
            bit_idx = 7 - (self.pos & 7)
            value = (value << 1) | ((self.data[byte_idx] >> bit_idx) & 1)
            self.pos += 1
        return value

    def read_gamma(self) -> int:
        # Conta zeros ate achar o primeiro 1
        zeros = 0
        while self.read(1) == 0:
            zeros += 1
            if zeros > 64:
                raise ValueError("Elias-gamma: valor grande demais")
        # Ja consumimos o primeiro 1; ler mais 'zeros' bits para completar
        value = 1
        for _ in range(zeros):
            value = (value << 1) | self.read(1)
        return value


# ── Opcodes ────────────────────────────────────────────────────────────


OP_LIT = 0b00
OP_REP = 0b01
OP_RAW = 0b10
OP_END = 0b11


# ── Estrutura ──────────────────────────────────────────────────────────


@dataclass
class M1Payload:
    """Representacao do programa compilado para a maquina M1.

    Atributos:
        k: bits por simbolo.
        N: numero de simbolos no output.
        compressed: bytes do programa codificado (header + body).
        n_ops: contagem de instrucoes emitidas (diagnostico).
    """

    k: int
    N: int
    compressed: bytes
    n_ops: dict[str, int]

    def size_bytes(self) -> int:
        return len(self.compressed)


# ── Encoder (politica gulosa) ──────────────────────────────────────────


def _bytes_to_symbols(data: bytes, k: int) -> tuple[list[int], int]:
    """Converte bytes em lista de simbolos de k bits. Retorna (symbols, leftover_bits)."""
    if k == 8:
        return list(data), 0
    # Extrair bits MSB-first por byte, agrupar em k
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    usable = len(bits) - (len(bits) % k)
    symbols = []
    for i in range(0, usable, k):
        v = 0
        for j in range(k):
            v = (v << 1) | bits[i + j]
        symbols.append(v)
    leftover = len(bits) - usable  # bits de cauda nao formando simbolo completo
    return symbols, leftover


def _symbols_to_bytes(symbols: list[int], k: int, tail_bits: list[int]) -> bytes:
    """Converte simbolos de k bits de volta em bytes, reanexando tail_bits."""
    if k == 8:
        return bytes(symbols) + bytes([int("".join(map(str, tail_bits)), 2)]) if tail_bits else bytes(symbols)
    bits: list[int] = []
    for s in symbols:
        for i in range(k - 1, -1, -1):
            bits.append((s >> i) & 1)
    bits.extend(tail_bits)
    # Empacota em bytes (padding a direita com zero se faltar)
    pad = (-len(bits)) % 8
    bits.extend([0] * pad)
    out = bytearray()
    for i in range(0, len(bits), 8):
        v = 0
        for j in range(8):
            v = (v << 1) | bits[i + j]
        out.append(v)
    return bytes(out)


def encode(data: bytes, k: int = 2) -> M1Payload:
    """Compila dados para programa M1.

    Politica: varre os simbolos com ponteiro; decide inline entre LIT/REP/RAW.
    """
    if not (1 <= k <= 8):
        raise ValueError(f"k deve estar em [1,8], recebeu {k}")

    symbols, leftover = _bytes_to_symbols(data, k)
    N = len(symbols)

    w = BitWriter()
    # Header
    w.write(k - 1, 3)              # k-1 em 3 bits (k=1..8 → 0..7)
    w.write(N, 32)                 # N em 32 bits (cabe arquivos ate 2^32 simbolos)
    w.write(leftover, 4)           # bits de cauda (<= k-1 < 8)
    for b in _bits_from(symbols_tail_bits(data, leftover)):
        w.write(b, 1)

    n_ops = {"LIT": 0, "REP": 0, "RAW": 0, "END": 0}

    i = 0
    while i < N:
        # Conta run de simbolos iguais a symbols[i]
        run = 1
        while i + run < N and symbols[i + run] == symbols[i]:
            run += 1

        if run >= 2:
            # REP vale para runs de >= 2 (custo: 2 + k + gamma(run))
            # vs alternativas: run * LIT = run * (2 + k) bits
            # REP < LIT*run sempre que gamma(run) < (run-1)*(2+k) -- praticamente sempre.
            w.write(OP_REP, 2)
            w.write(symbols[i], k)
            w.write_gamma(run)
            n_ops["REP"] += 1
            i += run
            continue

        # Sem repeticao imediata: tentar RAW para sequencia variavel.
        # Olhar a frente enquanto nao houver run de >= 2 começando.
        j = i + 1
        while j < N:
            # Checar se em j comeca um run de >= 2
            if j + 1 < N and symbols[j + 1] == symbols[j]:
                break
            j += 1
        raw_len = j - i
        # Comparar RAW vs LITs: RAW custa 2 + gamma(raw_len) + raw_len*k
        #                      LITs custa raw_len * (2 + k)
        # RAW melhor quando gamma(raw_len) < (raw_len - 1) * 2 (ou seja, raw_len >= 2)
        if raw_len >= 2:
            w.write(OP_RAW, 2)
            w.write_gamma(raw_len)
            for s in symbols[i:i + raw_len]:
                w.write(s, k)
            n_ops["RAW"] += 1
            i += raw_len
        else:
            w.write(OP_LIT, 2)
            w.write(symbols[i], k)
            n_ops["LIT"] += 1
            i += 1

    w.write(OP_END, 2)
    n_ops["END"] = 1

    return M1Payload(k=k, N=N, compressed=w.to_bytes(), n_ops=n_ops)


def _bits_from(bits: list[int]) -> list[int]:
    return bits


def symbols_tail_bits(data: bytes, leftover: int) -> list[int]:
    """Retorna os `leftover` bits de cauda que nao formaram simbolo completo."""
    if leftover == 0:
        return []
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits[-leftover:] if leftover > 0 else []


# ── Decoder ────────────────────────────────────────────────────────────


def decode(payload: M1Payload) -> bytes:
    """Executa o programa M1 e retorna os bytes originais."""
    r = BitReader(payload.compressed)

    # Header
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
        op = r.read(2)
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
        else:
            raise ValueError(f"opcode desconhecido: {op}")

        if len(out) > N:
            raise ValueError(f"output excedeu N: {len(out)} > {N}")

    if len(out) != N:
        raise ValueError(f"output incompleto: {len(out)} != {N}")

    return _symbols_to_bytes(out, k, tail_bits)


# ── Diagnostico ────────────────────────────────────────────────────────


def summary(payload: M1Payload, original_size: int) -> dict:
    total = payload.size_bytes()
    return {
        "k": payload.k,
        "N_symbols": payload.N,
        "original_bytes": original_size,
        "compressed_bytes": total,
        "ratio": original_size / total if total else float("inf"),
        "ops": dict(payload.n_ops),
    }
