"""Ordem Z (Morton): intercala bits de x e y para produzir um índice que
preserva localidade espacial de forma razoável com custo computacional
muito baixo.  Serve como baseline competitivo contra Hilbert."""

from __future__ import annotations


def _interleave_bits(x: int, y: int) -> int:
    key = 0
    bit = 0
    while x > 0 or y > 0:
        key |= (x & 1) << (2 * bit)
        key |= (y & 1) << (2 * bit + 1)
        x >>= 1
        y >>= 1
        bit += 1
    return key


def morton_order(side: int) -> list[int]:
    """Retorna índices lineares na ordem Z/Morton para uma malha side×side."""
    coords = []
    for y in range(side):
        for x in range(side):
            coords.append((_interleave_bits(x, y), x, y))
    coords.sort(key=lambda t: t[0])
    return [y * side + x for _, x, y in coords]
