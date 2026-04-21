"""Curva de Hilbert em dimensão arbitrária (nD).

Usa o algoritmo de Skilling (2004): "Programming the Hilbert Curve".
AIP Conference Proceedings 707, 381-387.

Suporta n=1,2,3,4,... dimensões com p bits por dimensão.
Side = 2^p posições por eixo. Total = 2^(n*p) posições.

Exemplos:
  n=2, p=8 → grid 256×256 (como bytes)
  n=3, p=8 → grid 256×256×256
  n=2, p=4 → grid 16×16 (compacto para testes)
"""

from __future__ import annotations


def _coords_to_hilbert(X: list[int], p: int) -> int:
    """Skilling (2004): coordenadas nD → índice de Hilbert.

    Args:
        X: lista de n inteiros, cada um em [0, 2^p - 1]. MODIFICADA in-place.
        p: bits por dimensão.

    Returns:
        Índice inteiro da curva de Hilbert.
    """
    n = len(X)
    if n == 1:
        return X[0]

    M = 1 << (p - 1)

    # Passo 1: "work" — inverter/trocar coordenadas
    Q = M
    while Q > 1:
        P = Q - 1
        for i in range(n):
            if X[i] & Q:
                X[0] ^= P           # inverte
            else:
                t = (X[0] ^ X[i]) & P
                X[0] ^= t
                X[i] ^= t           # troca
        Q >>= 1

    # Passo 2: Gray encode + propagação
    for i in range(1, n):
        X[i] ^= X[i - 1]
    Z = 0
    Q = M
    while Q > 1:
        if X[n - 1] & Q:
            Z ^= Q - 1
        Q >>= 1
    for i in range(n):
        X[i] ^= Z

    # Passo 3: intercalar bits → índice escalar
    h = 0
    for i in range(n):
        for b in range(p):
            if X[i] & (1 << b):
                h |= 1 << (n * b + i)
    return h


def _hilbert_to_coords(h: int, n: int, p: int) -> list[int]:
    """Skilling (2004): índice de Hilbert → coordenadas nD.

    Args:
        h: índice escalar.
        n: número de dimensões.
        p: bits por dimensão.

    Returns:
        Lista de n inteiros em [0, 2^p - 1].
    """
    if n == 1:
        return [h]

    # Desempacotar bits intercalados
    X = [0] * n
    for i in range(n):
        for b in range(p):
            if h & (1 << (n * b + i)):
                X[i] |= 1 << b

    # Desfazer Gray encode
    Z = X[n - 1] >> 1
    for i in range(n - 1, 0, -1):
        X[i] ^= X[i - 1]
    X[0] ^= Z

    # Desfazer "work"
    Q = 2
    while Q != (1 << p):
        P = Q - 1
        for i in range(n - 1, -1, -1):
            if X[i] & Q:
                X[0] ^= P
            else:
                t = (X[0] ^ X[i]) & P
                X[0] ^= t
                X[i] ^= t
        Q <<= 1

    return X


def hilbert_order_nd(side: int, ndim: int) -> list[int]:
    """Gera a ordem de traversal de Hilbert numa grade side^ndim.

    Retorna lista de índices lineares na ordem da curva de Hilbert nD.

    Args:
        side: lado da grade (deve ser potência de 2, side = 2^p).
        ndim: número de dimensões.

    Returns:
        Lista de side^ndim inteiros, representando os índices lineares
        na ordem de percurso Hilbert.
    """
    if side <= 0 or (side & (side - 1)) != 0:
        raise ValueError(f"side deve ser potência de 2, recebeu {side}")

    p = side.bit_length() - 1  # side = 2^p
    total = side ** ndim
    order = []

    for h in range(total):
        coords = _hilbert_to_coords(h, ndim, p)
        # Converter coordenadas para índice linear (row-major)
        idx = 0
        stride = 1
        for c in reversed(coords):
            idx += c * stride
            stride *= side
        order.append(idx)

    return order


def morton_order_nd(side: int, ndim: int) -> list[int]:
    """Gera a ordem Z (Morton) numa grade side^ndim.

    Mais rápida de calcular que Hilbert, localidade quase tão boa.
    Útil como fallback para dimensões altas.

    Args:
        side: lado da grade (potência de 2).
        ndim: número de dimensões.

    Returns:
        Lista de índices lineares na ordem Z-order.
    """
    total = side ** ndim

    def morton_key(linear_idx: int) -> int:
        # Recuperar coordenadas
        coords = []
        tmp = linear_idx
        for _ in range(ndim):
            coords.append(tmp % side)
            tmp //= side
        # Intercalar bits
        key = 0
        bits = side.bit_length() - 1
        for b in range(bits):
            for d, c in enumerate(coords):
                key |= ((c >> b) & 1) << (ndim * b + d)
        return key

    indices = list(range(total))
    indices.sort(key=morton_key)
    return indices
