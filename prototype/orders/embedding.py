"""Delay Embedding: projeta uma sequência 1D em espaço R^D.

Ideia central: ao invés de assumir que os dados *são* 2D (imagens),
projetamos os bytes numa grade D-dimensional via janela deslizante.
A posição i no dado vira o ponto (data[i], data[i+1], ..., data[i+D-1]).

Isso revela estrutura latente: se data[i] e data[i+1] são correlacionados,
pontos vizinhos na série temporal ficam próximos no espaço D-dimensional.
O percurso SFC nesse espaço agrupa posições com contexto similar.

Conexão com Takens (1981): uma série 1D contém informação suficiente para
reconstruir a geometria do sistema dinâmico subjacente em dimensão D >= 2d+1.
Para dados compressíveis (baixa dimensão intrínseca), existe D pequeno
onde a estrutura emerge.

Diferença de Hilbert 2D fixo:
- Hilbert 2D fixo: assume layout espacial (pixel[x,y]) e varre em ordem
- Delay embedding: usa os próprios valores como coordenadas, sem presupor layout
"""

from __future__ import annotations

from .hilbert_nd import _coords_to_hilbert, morton_order_nd


def _hilbert_key_2d(x: int, y: int, bits: int = 8) -> int:
    """Índice de Hilbert para (x, y) em grid 2^bits × 2^bits."""
    return _coords_to_hilbert([x, y], bits)


def _morton_key_nd(coords: tuple[int, ...]) -> int:
    """Índice Morton para ponto n-dimensional (cada coord em [0,255])."""
    key = 0
    for b in range(8):
        for d, c in enumerate(coords):
            key |= ((c >> b) & 1) << (len(coords) * b + d)
    return key


def delay_embedding_order(
    data: bytes,
    D: int,
    curve: str = "hilbert",
) -> list[int]:
    """Gera ordem de traversal via delay embedding em R^D.

    Para cada posição i em [0, N-D], cria o ponto:
        p_i = (data[i], data[i+1], ..., data[i+D-1])

    Ordena as posições pelo índice da SFC nesse espaço D-dimensional.
    O resultado: posições com contexto local similar ficam adjacentes.

    Args:
        data: bytes a ordenar.
        D: dimensão do embedding (1=sem mudança, 2=pares, 3=trios, ...).
        curve: 'hilbert' (D=2 exato, D>2 usa Morton) ou 'morton'.

    Returns:
        Lista de índices de posição em data, na nova ordem.
        Tamanho = N-D+1 (posições completas) + D-1 (tail literal).

    Notes:
        Posições sem D vizinhos completos (tail) são anexadas no final
        em ordem original.
    """
    N = len(data)
    if D <= 1 or N < D:
        return list(range(N))

    # Gerar pares (índice, chave_sfc)
    # Apenas posições i em [0, N-D] têm janela completa de D bytes
    pairs = []
    for i in range(N - D + 1):
        coords = tuple(data[i: i + D])
        if curve == "hilbert" and D == 2:
            key = _hilbert_key_2d(coords[0], coords[1], bits=8)
        else:
            key = _morton_key_nd(coords)
        pairs.append((key, i))

    pairs.sort()

    # Posições completas (ordenadas) + D-1 posições finais (tail) em ordem original
    ordered = [i for _, i in pairs]
    # Tail: as D-1 posições finais (N-D+1 a N-1) que não têm janela completa
    tail = list(range(N - D + 1, N))
    return ordered + tail


def measure_embedding_dims(
    data: bytes,
    dims: tuple[int, ...] = (1, 2, 3, 4),
    curve: str = "hilbert",
) -> dict[int, list[int]]:
    """Gera ordens para múltiplas dimensões de embedding.

    Conveniente para comparação D=1 (raster), D=2, D=3, D=4.

    Returns:
        {D: lista_de_índices}
    """
    result = {}
    for D in dims:
        if D == 1:
            result[1] = list(range(len(data)))
        else:
            result[D] = delay_embedding_order(data, D, curve)
    return result
