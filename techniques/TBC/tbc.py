"""
TuringBitCompression (TBC) — indicator-plane coding by frequency ranking.

Algoritmo (nao-recursivo, nivel 1):
    1. Agrupa bits em simbolos de k bits (default k=2, alfabeto = 2^k).
    2. Ordena simbolos por frequencia descendente (desempata por lex).
    3. Para cada simbolo sigma_i (exceto o ultimo do ranking):
         emite plano P_i = bitmask sobre as posicoes ainda nao preenchidas
         indicando onde sigma_i ocorre.
    4. O ultimo simbolo e implicito (residuo em posicoes remanescentes).

Propriedades:
    - Lossless (round-trip exato).
    - |P_1| = N, |P_i| = N - sum(f_1 .. f_{i-1}).
    - Total bits dos planos = (m-1)*N - sum_{i=1..m-2} (m-1-i) * f_i
      onde m = 2^k e f_i = frequencia do simbolo rank-i.
    - Ganha quando a distribuicao de simbolos e desbalanceada.

Ver README.md para detalhes e exemplo trabalhado.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class TBCPayload:
    """Representacao intermediaria do TBC (nivel 1)."""

    k: int                        # bits por simbolo
    N: int                        # numero de simbolos
    tail_bits: str                # bits sobressalentes (len(bits) % k)
    ranking: list[str]            # permutacao completa dos 2^k simbolos
    planes: list[list[int]]       # lista de planos (0s e 1s)

    def total_plane_bits(self) -> int:
        return sum(len(p) for p in self.planes)

    def header_bits_estimate(self) -> int:
        """Estimativa de overhead do cabecalho.

        Componentes:
        - log2(N_max) para o comprimento (fixo em 32 bits para simplicidade)
        - (2^k) * k bits para a permutacao de ranking (pior caso explicito)
        - 3 bits para k em si (k in 1..8)
        - 3 bits para len(tail_bits)
        - len(tail_bits) bits para os bits de cauda
        """
        alphabet = 2 ** self.k
        return 32 + alphabet * self.k + 3 + 3 + len(self.tail_bits)

    def total_bits_estimate(self) -> int:
        return self.total_plane_bits() + self.header_bits_estimate()


def _bytes_to_bits(data: bytes) -> str:
    """Converte bytes para string binaria MSB-first por byte."""
    return "".join(format(b, "08b") for b in data)


def _bits_to_bytes(bits: str) -> bytes:
    """Converte string binaria de volta para bytes. Requer len(bits) % 8 == 0."""
    if len(bits) % 8 != 0:
        raise ValueError(f"bits length must be multiple of 8, got {len(bits)}")
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


def _rank_symbols(symbols: list[str], k: int) -> list[str]:
    """Ranking completo de todos os 2^k simbolos possiveis.

    Inclui simbolos com frequencia zero no final para que o ranking seja
    uma permutacao fixa do alfabeto — isso simplifica a codificacao do header.
    Desempate: lexicografico ascendente.
    """
    freq = Counter(symbols)
    all_syms = [format(i, f"0{k}b") for i in range(2 ** k)]
    all_syms.sort(key=lambda s: (-freq.get(s, 0), s))
    return all_syms


def _build_planes(symbols: list[str], ranking: list[str]) -> list[list[int]]:
    """Constroi os planos indicadores na ordem do ranking.

    Para cada simbolo sigma_i (exceto o ultimo), constroi bitmask sobre as
    posicoes ainda nao marcadas. A posicao e 1 se symbol[pos] == sigma_i,
    0 caso contrario (e vai para o proximo plano).
    """
    positions = list(range(len(symbols)))
    planes: list[list[int]] = []
    # O ultimo simbolo do ranking e implicito (residuo): nao emite plano.
    for sigma in ranking[:-1]:
        if not positions:
            # Todos as posicoes ja cobertas; planos restantes seriam vazios.
            break
        plane = []
        next_positions = []
        for pos in positions:
            if symbols[pos] == sigma:
                plane.append(1)
            else:
                plane.append(0)
                next_positions.append(pos)
        planes.append(plane)
        positions = next_positions
    return planes


def _apply_planes(planes: list[list[int]], ranking: list[str], N: int) -> list[str]:
    """Reconstroi simbolos a partir dos planos e do ranking."""
    result: list[str | None] = [None] * N
    positions = list(range(N))
    for i, plane in enumerate(planes):
        sigma = ranking[i]
        next_positions = []
        for j, pos in enumerate(positions):
            if plane[j] == 1:
                result[pos] = sigma
            else:
                next_positions.append(pos)
        positions = next_positions
    # Residuo: as posicoes ainda nao preenchidas recebem o simbolo seguinte.
    if positions:
        residual = ranking[len(planes)]
        for pos in positions:
            result[pos] = residual
    # Sanity
    if any(r is None for r in result):
        raise RuntimeError("decode: posicao nao preenchida (bug)")
    return result  # type: ignore[return-value]


def encode(data: bytes, k: int = 2) -> TBCPayload:
    """Codifica bytes usando TBC nivel 1 (sem recursao).

    Args:
        data: bytes a comprimir.
        k: bits por simbolo (1 <= k <= 8). Default 2.

    Returns:
        TBCPayload com ranking, planos e cauda.
    """
    if not (1 <= k <= 8):
        raise ValueError(f"k deve estar em [1, 8], recebeu {k}")

    bits = _bytes_to_bits(data)
    usable = len(bits) - (len(bits) % k)
    tail_bits = bits[usable:]

    symbols = [bits[i:i + k] for i in range(0, usable, k)]
    ranking = _rank_symbols(symbols, k)
    planes = _build_planes(symbols, ranking)

    return TBCPayload(
        k=k,
        N=len(symbols),
        tail_bits=tail_bits,
        ranking=ranking,
        planes=planes,
    )


def decode(payload: TBCPayload) -> bytes:
    """Decodifica um TBCPayload de volta para os bytes originais."""
    symbols = _apply_planes(payload.planes, payload.ranking, payload.N)
    bits = "".join(symbols) + payload.tail_bits
    return _bits_to_bytes(bits)


# ── Utilitarios de diagnostico ─────────────────────────────────────────


def frequencies(data: bytes, k: int = 2) -> list[tuple[str, int]]:
    """Retorna (simbolo, contagem) ordenado por freq descendente."""
    bits = _bytes_to_bits(data)
    usable = len(bits) - (len(bits) % k)
    symbols = [bits[i:i + k] for i in range(0, usable, k)]
    freq = Counter(symbols)
    return sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))


def summary(payload: TBCPayload) -> dict:
    """Resumo numerico do payload (para logging/CSV)."""
    plane_sizes = [len(p) for p in payload.planes]
    return {
        "k": payload.k,
        "N_symbols": payload.N,
        "n_planes": len(payload.planes),
        "plane_sizes": plane_sizes,
        "total_plane_bits": sum(plane_sizes),
        "tail_bits": len(payload.tail_bits),
        "header_bits": payload.header_bits_estimate(),
        "total_bits": payload.total_bits_estimate(),
        "original_bits": payload.N * payload.k + len(payload.tail_bits),
    }
