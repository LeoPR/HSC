"""Métricas baseadas em compressores reais (zlib/deflate).

zlib serve como referência prática: se uma reordenação melhora a taxa
do zlib, é evidência de que a estrutura local ficou mais explorável."""

from __future__ import annotations

import zlib


def zlib_size(seq: bytes, level: int = 9) -> int:
    """Retorna o tamanho em bytes após compressão zlib nível *level*."""
    return len(zlib.compress(seq, level=level))
