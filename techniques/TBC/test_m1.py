"""Round-trip e casos de borda da maquina M1."""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from m1 import encode, decode, summary, BitWriter, BitReader


def test_bitstream_basic() -> None:
    w = BitWriter()
    w.write(0b1010, 4)
    w.write(0b11, 2)
    w.write_gamma(1)      # 1 → "1"
    w.write_gamma(2)      # 2 → "010"
    w.write_gamma(5)      # 5 → "00101"
    buf = w.to_bytes()
    r = BitReader(buf)
    assert r.read(4) == 0b1010
    assert r.read(2) == 0b11
    assert r.read_gamma() == 1
    assert r.read_gamma() == 2
    assert r.read_gamma() == 5
    print("bitstream basico OK")


def test_roundtrip_empty() -> None:
    data = b""
    for k in [1, 2, 4, 8]:
        p = encode(data, k=k)
        assert decode(p) == data, f"empty falhou k={k}"
    print("roundtrip vazio OK")


def test_roundtrip_tiny() -> None:
    for data in [b"\x00", b"\xff", b"\xaa\xaa\xaa\xaa", b"abc"]:
        for k in [1, 2, 4, 8]:
            p = encode(data, k=k)
            d = decode(p)
            assert d == data, f"tiny falhou data={data!r} k={k}: {d!r} != {data!r}"
    print("roundtrip tiny OK")


def test_roundtrip_random() -> None:
    random.seed(42)
    sizes = [1, 7, 8, 16, 100, 1000, 4227]
    for size in sizes:
        data = bytes(random.randint(0, 255) for _ in range(size))
        for k in [1, 2, 4, 8]:
            p = encode(data, k=k)
            d = decode(p)
            assert d == data, f"random size={size} k={k}"
    print("roundtrip aleatorio OK")


def test_repetitivo() -> None:
    data = bytes([0x41]) * 1000 + bytes([0x42]) * 500 + b"ABCDEFGHIJ" * 50
    for k in [1, 2, 4, 8]:
        p = encode(data, k=k)
        d = decode(p)
        assert d == data, f"repetitivo k={k}"
        s = summary(p, len(data))
        print(f"  k={k}: ratio={s['ratio']:.2f}x  ops={s['ops']}")


def test_texto_canonico() -> None:
    path = Path("../../datasets/canterbury/xargs.1")
    if not path.exists():
        print(f"  SKIP: {path} nao encontrado")
        return
    data = path.read_bytes()
    print(f"\nxargs.1 ({len(data)} bytes):")
    for k in [1, 2, 4, 8]:
        p = encode(data, k=k)
        d = decode(p)
        assert d == data, f"xargs.1 k={k}"
        s = summary(p, len(data))
        print(f"  k={k}: ratio={s['ratio']:.2f}x  compressed={s['compressed_bytes']}B  ops={s['ops']}")


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    test_bitstream_basic()
    test_roundtrip_empty()
    test_roundtrip_tiny()
    test_roundtrip_random()
    print("\nTeste repetitivo:")
    test_repetitivo()
    print("\nTeste texto canonico:")
    test_texto_canonico()
    print("\nTodos os testes de M1 passaram.")
