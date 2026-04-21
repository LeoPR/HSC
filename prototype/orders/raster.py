"""Ordem raster (row-major): percorre a malha linha a linha, sem nenhuma
tentativa de preservar localidade espacial.  Serve como baseline ingênuo."""

from __future__ import annotations


def raster_order(side: int) -> list[int]:
    """Retorna índices lineares na ordem raster para uma malha side×side."""
    return list(range(side * side))
