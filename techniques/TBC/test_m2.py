"""Round-trip e benchmark da maquina M2 (M1 + REF)."""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from m2 import encode, decode, summary


def test_roundtrip_empty() -> None:
    data = b""
    for k in [1, 2, 4, 8]:
        p = encode(data, k=k)
        assert decode(p) == data, f"empty k={k}"
    print("M2 empty OK")


def test_roundtrip_tiny() -> None:
    for data in [b"\x00", b"\xff", b"\xaa" * 4, b"abc", b"abcabcabc"]:
        for k in [1, 2, 4, 8]:
            p = encode(data, k=k)
            d = decode(p)
            assert d == data, f"tiny data={data!r} k={k}: {d!r} != {data!r}"
    print("M2 tiny OK")


def test_roundtrip_random() -> None:
    random.seed(42)
    for size in [1, 7, 8, 16, 100, 1000]:
        data = bytes(random.randint(0, 255) for _ in range(size))
        for k in [1, 2, 4, 8]:
            p = encode(data, k=k)
            d = decode(p)
            assert d == data, f"random size={size} k={k}"
    print("M2 random OK")


def test_repetitivo_longo() -> None:
    # Dados com padroes macro repetidos (mira LZ/M2)
    padrao = b"The quick brown fox jumps over the lazy dog. "
    data = padrao * 50
    for k in [1, 2, 4, 8]:
        p = encode(data, k=k)
        d = decode(p)
        assert d == data, f"padrao k={k}"
        s = summary(p, len(data))
        print(f"  padrao*50 k={k}: {s['ratio']:.2f}x  {s['compressed_bytes']}B  ops={s['ops']}")


def test_texto_canonico() -> None:
    path = Path("../../datasets/canterbury/xargs.1")
    if not path.exists():
        print(f"  SKIP: {path}")
        return
    data = path.read_bytes()
    print(f"\nxargs.1 ({len(data)} bytes):")
    for k in [4, 8]:  # k pequeno e muito lento com O(N*W)
        p = encode(data, k=k)
        d = decode(p)
        assert d == data, f"xargs.1 k={k}"
        s = summary(p, len(data))
        print(f"  k={k}: {s['ratio']:.2f}x  {s['compressed_bytes']}B  ops={s['ops']}")


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    test_roundtrip_empty()
    test_roundtrip_tiny()
    test_roundtrip_random()
    print("\nRepetitivo macro:")
    test_repetitivo_longo()
    print("\nTexto canonico:")
    test_texto_canonico()
    print("\nTodos os testes de M2 passaram.")
