"""Modelo adaptativo de entropia condicional de ordem 1.

Calcula bits teóricos estimados usando P(s_t | s_{t-1}) com suavização
aditiva (Laplace).  Serve como proxy rápido para medir quão bem uma
reordenação cria dependências locais exploráveis por um codificador."""

from __future__ import annotations

import math


def adaptive_order1_bits(seq: bytes, alpha: float = 1.0) -> float:
    """Retorna o total de bits estimados por um modelo de contexto ordem-1.

    Parameters
    ----------
    seq : bytes
        Sequência de símbolos (0–255).
    alpha : float
        Parâmetro de suavização aditiva (Laplace).  Default=1.0.
    """
    symbols = 256
    table = [[0] * symbols for _ in range(symbols)]
    totals = [0] * symbols
    bits = 0.0
    prev = 0

    for b in seq:
        count = table[prev][b]
        total = totals[prev]
        p = (count + alpha) / (total + alpha * symbols)
        bits += -math.log2(p)
        table[prev][b] += 1
        totals[prev] += 1
        prev = b

    return bits
