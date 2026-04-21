"""Ordem de Hilbert: curva de preenchimento de espaço que maximiza a
preservação de localidade espacial ao custo de cálculo de índice mais
caro que Morton.  É a topologia central da hipótese deste projeto."""

from __future__ import annotations


def _rot(n: int, x: int, y: int, rx: int, ry: int) -> tuple[int, int]:
    if ry == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        x, y = y, x
    return x, y


def _d2xy(n: int, d: int) -> tuple[int, int]:
    x = y = 0
    t = d
    s = 1
    while s < n:
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        x, y = _rot(s, x, y, rx, ry)
        x += s * rx
        y += s * ry
        t //= 4
        s *= 2
    return x, y


def hilbert_order(side: int) -> list[int]:
    """Retorna índices lineares na ordem de Hilbert para uma malha side×side.

    Requer side potência de 2.
    """
    if side & (side - 1) != 0:
        raise ValueError(f"Hilbert requer lado potência de 2, recebeu {side}.")
    order = []
    for d in range(side * side):
        x, y = _d2xy(side, d)
        order.append(y * side + x)
    return order
