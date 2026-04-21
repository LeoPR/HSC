"""Testes do TBC: correcao (round-trip) e exemplo do logic_03."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tbc import encode, decode, frequencies, summary, _bytes_to_bits


def test_roundtrip_example() -> None:
    """Exemplo do compression_logic_03.md: 28 bits, 14 simbolos de 2 bits."""
    # 1001100110010101010101010111
    bits = "1001100110010101010101010111"
    # Converter para bytes (28 bits = 3 bytes + 4 bits de cauda)
    # Pad ate multiplo de 8 com zeros a direita, e armazenar quantos bits reais
    padded = bits + "0" * (8 - len(bits) % 8) if len(bits) % 8 else bits
    data = bytes(int(padded[i:i + 8], 2) for i in range(0, len(padded), 8))

    # Encode
    payload = encode(data, k=2)

    # Verifica frequencias esperadas
    freqs = frequencies(data, k=2)
    freq_dict = dict(freqs)
    # Os primeiros 28 bits tem: 10 01 10 01 10 01 01 01 01 01 01 01 01 11
    # Mas o padding adiciona mais simbolos "00" — vamos testar sobre os 28 bits reais
    # atraves de um teste mais controlado abaixo.
    print(f"Frequencias (com padding): {freq_dict}")
    print(f"Summary: {summary(payload)}")

    # Round-trip
    decoded = decode(payload)
    assert decoded == data, f"roundtrip falhou: {decoded.hex()} != {data.hex()}"
    print(f"Roundtrip (dados + padding): OK")


def test_roundtrip_controlled() -> None:
    """Teste controlado sobre bits exatos do exemplo (sem padding extra).

    Usa k=2 e bits que caem exatamente em byte-boundary.
    """
    # 32 bits = 4 bytes, 16 simbolos de 2 bits
    # Distribuicao desbalanceada: 01 x10, 10 x3, 11 x1, 00 x2
    bits = "01" * 10 + "10" * 3 + "11" + "00" * 2  # 20+6+2+4 = 32 bits
    assert len(bits) == 32
    data = bytes(int(bits[i:i + 8], 2) for i in range(0, 32, 8))

    payload = encode(data, k=2)
    decoded = decode(payload)
    assert decoded == data, "roundtrip controlado falhou"

    s = summary(payload)
    print(f"\nTeste controlado (32 bits, k=2):")
    print(f"  Simbolos: N={s['N_symbols']}, {s['plane_sizes']=}")
    print(f"  Bits planos: {s['total_plane_bits']}, original: {s['original_bits']}")
    print(f"  Header estimado: {s['header_bits']} bits")
    print(f"  Total estimado: {s['total_bits']} bits (vs original {s['original_bits']})")


def test_roundtrip_random() -> None:
    """Round-trip em dados aleatorios de varios tamanhos e k."""
    import random

    random.seed(42)
    for size in [1, 7, 8, 16, 100, 1000]:
        data = bytes(random.randint(0, 255) for _ in range(size))
        for k in [1, 2, 4, 8]:
            payload = encode(data, k=k)
            decoded = decode(payload)
            assert decoded == data, f"falha: size={size}, k={k}"
    print(f"\nRoundtrip aleatorio: OK (varios tamanhos e k=1,2,4,8)")


def test_all_same_byte() -> None:
    """Caso degenerado: todos os bytes iguais — deve comprimir muito."""
    data = bytes([0xAA] * 1000)  # 10101010 repetido
    payload = encode(data, k=2)
    s = summary(payload)
    assert decode(payload) == data

    # Com k=2 e todos 0xAA = 10101010, cada byte vira "10 10 10 10"
    # Entao temos 4000 simbolos "10", 0 dos outros.
    # sigma_1 = "10" (4000×), P_1 = 4000 bits todos 1s. Proximo simbolo nao tem plano
    # pois nao sobraram posicoes — break no _build_planes.
    print(f"\nTodos 0xAA (k=2): {s['total_plane_bits']} bits planos / {s['original_bits']} originais")
    print(f"  (P_1 com todos 1s nao comprime sozinho — precisa de entropia/recursao)")


def test_frequencies_example() -> None:
    """Verifica que as frequencias do exemplo batem com o esperado."""
    # Dados exatos do logic_03 (28 bits) — mas precisamos nao incluir padding
    # na contagem. Testamos por multiplo de 16 bits (8 simbolos de 2).
    bits = "10011001100101010101010101"  # 26 bits — multiplo de 2, nao de 8
    # Precisamos alinhar em byte: 24 bits usaveis = 12 simbolos
    bits24 = bits[:24]
    # 10 01 10 01 10 01 01 01 01 01 01 01 — freq: 01 x8, 10 x3, 11 x0, 00 x0
    data = bytes(int(bits24[i:i + 8], 2) for i in range(0, 24, 8))

    freqs = dict(frequencies(data, k=2))
    print(f"\nFrequencias de {bits24!r}: {freqs}")
    # bits24 = "10 01 10 01 10 01 01 01 01 01 01 01" → 01 x9, 10 x3
    assert freqs.get("01", 0) == 9, f"esperava 01=9, tem {freqs.get('01')}"
    assert freqs.get("10", 0) == 3, f"esperava 10=3, tem {freqs.get('10')}"
    print(f"  OK: 01=9, 10=3")


if __name__ == "__main__":
    # Garantir UTF-8 no Windows
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    test_frequencies_example()
    test_roundtrip_controlled()
    test_roundtrip_example()
    test_roundtrip_random()
    test_all_same_byte()
    print("\nTodos os testes passaram.")
