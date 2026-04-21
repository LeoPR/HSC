"""Carregamento e preparação de dados para benchmark.

Responsável por ler datasets de disco, ajustar para malhas N-dimensionais
e aplicar reordenações. Suporta embedding em espaços de dimensão arbitrária
(1D, 2D, 3D, ...) — não assume que os dados são imagens.

Filosofia: os bytes raw não "são" 2D — nós *escolhemos* projetá-los num
espaço R^n para explorar estrutura. O loader fornece as ferramentas para
essa projeção de forma agnóstica à dimensão."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence
from functools import reduce
import operator


def _next_power_of_two(x: int) -> int:
    if x <= 1:
        return 1
    return 1 << (x - 1).bit_length()


def load_file(path: str | Path) -> bytes:
    """Lê um arquivo inteiro como bytes."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {p}")
    return p.read_bytes()


# ── Dimensionamento de malha ──────────────────────────────────────────


def choose_side(n: int, candidates: Sequence[int] | None = None) -> int:
    """Escolhe o menor lado (potência de 2) cuja malha quadrada comporta *n* bytes.

    Se *candidates* for fornecido, escolhe entre eles; senão calcula
    automaticamente.

    Para retrocompatibilidade com pipeline A/B/C 2D.
    """
    if candidates:
        valid = [s for s in candidates if s * s >= n and s & (s - 1) == 0]
        if valid:
            return min(valid)
    return _next_power_of_two(math.ceil(math.sqrt(n)))


def choose_side_nd(n: int, ndim: int = 2, candidates: Sequence[int] | None = None) -> int:
    """Escolhe o menor lado cuja malha n-dimensional comporta *n* bytes.

    Para ndim=2: side^2 >= n (malha quadrada, como antes)
    Para ndim=3: side^3 >= n (malha cúbica)
    Para ndim=1: side >= n (trivial, sequência linear)

    O lado é sempre potência de 2 (requerido por Hilbert nD).
    """
    if candidates:
        valid = [s for s in candidates if s ** ndim >= n and s & (s - 1) == 0]
        if valid:
            return min(valid)
    # Calcular automaticamente
    raw_side = math.ceil(n ** (1.0 / ndim))
    return _next_power_of_two(raw_side)


def grid_volume(side: int, ndim: int = 2) -> int:
    """Total de posições numa malha side^ndim."""
    return side ** ndim


def padding_ratio(n: int, side: int, ndim: int = 2) -> float:
    """Fração da malha ocupada por padding (0.0 = sem padding, 1.0 = tudo padding)."""
    vol = grid_volume(side, ndim)
    return (vol - n) / vol if vol > n else 0.0


# ── Padding ───────────────────────────────────────────────────────────


def pad_to_square(data: bytes, side: int) -> bytes:
    """Ajusta *data* para exatamente side×side bytes, truncando ou paddando.

    Mantido para retrocompatibilidade com pipeline A/B/C.
    """
    return pad_to_grid(data, side, ndim=2)


def pad_to_grid(data: bytes, side: int, ndim: int = 2) -> bytes:
    """Ajusta *data* para exatamente side^ndim bytes.

    Se len(data) > side^ndim: trunca.
    Se len(data) < side^ndim: preenche com zeros (padding).
    """
    total = side ** ndim
    if len(data) >= total:
        return data[:total]
    return data + bytes(total - len(data))


# ── Reordenação ───────────────────────────────────────────────────────


def reorder_bytes(data: bytes, order: Sequence[int], valid_len: int) -> bytes:
    """Reordena *data* segundo *order*, descartando posições >= valid_len."""
    return bytes(data[i] for i in order if i < valid_len)
