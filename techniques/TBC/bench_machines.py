"""Benchmark consolidado: roda todas as maquinas TBC + baselines num dado.

Uso:
    python bench_machines.py                   # default: xargs.1
    python bench_machines.py <arquivo>         # em qualquer arquivo
    python bench_machines.py --all             # varre varios canonicos
"""

from __future__ import annotations

import sys
import zlib
import bz2
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import tbc as m0
import m1
import m2

HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parent.parent


def _m0_size_bytes(data: bytes, k: int) -> tuple[int, bool]:
    """Estimativa do tamanho M0 em bytes + flag de round-trip OK."""
    payload = m0.encode(data, k=k)
    ok = m0.decode(payload) == data
    s = m0.summary(payload)
    total_bits = s["total_plane_bits"] + s["header_bits"]
    return (total_bits + 7) // 8, ok


def _m1_size_bytes(data: bytes, k: int) -> tuple[int, bool]:
    payload = m1.encode(data, k=k)
    ok = m1.decode(payload) == data
    return payload.size_bytes(), ok


def _m2_size_bytes(data: bytes, k: int) -> tuple[int, bool]:
    payload = m2.encode(data, k=k)
    ok = m2.decode(payload) == data
    return payload.size_bytes(), ok


def bench_file(path: Path) -> None:
    if not path.exists():
        print(f"[SKIP] {path} nao encontrado")
        return
    data = path.read_bytes()
    print(f"\n=== {path.name}  ({len(data):,} bytes) ===")
    print(f"{'method':<16s}  {'bytes':>10s}  {'ratio':>7s}  {'ok':>3s}")
    print("-" * 42)

    # M0 em varios k
    for k in [1, 2, 4, 8]:
        size, ok = _m0_size_bytes(data, k)
        ratio = len(data) / size if size else float("inf")
        print(f"M0  k={k:<11d}  {size:>10,}  {ratio:>6.2f}x  {'OK' if ok else 'X'}")

    # M1 em varios k
    for k in [1, 2, 4, 8]:
        size, ok = _m1_size_bytes(data, k)
        ratio = len(data) / size if size else float("inf")
        print(f"M1  k={k:<11d}  {size:>10,}  {ratio:>6.2f}x  {'OK' if ok else 'X'}")

    # M2 so em k=4 e k=8 (k<4 fica muito lento no scan linear)
    for k in [4, 8]:
        size, ok = _m2_size_bytes(data, k)
        ratio = len(data) / size if size else float("inf")
        print(f"M2  k={k:<11d}  {size:>10,}  {ratio:>6.2f}x  {'OK' if ok else 'X'}")

    # Baselines classicos
    for name, fn in [("zlib -9", lambda d: zlib.compress(d, 9)),
                     ("bz2 -9",  lambda d: bz2.compress(d, 9))]:
        compressed = fn(data)
        ratio = len(data) / len(compressed)
        print(f"{name:<14s}  {len(compressed):>10,}  {ratio:>6.2f}x   OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark maquinas TBC.")
    parser.add_argument("files", nargs="*", type=Path,
                        help="arquivos a testar (default: xargs.1)")
    parser.add_argument("--all", action="store_true",
                        help="varrer varios canonicos pequenos")
    args = parser.parse_args()

    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.all:
        targets = [
            PROJECT_ROOT / "datasets/canterbury/xargs.1",
            PROJECT_ROOT / "datasets/canterbury/grammar.lsp",
            PROJECT_ROOT / "datasets/canterbury/fields.c",
            PROJECT_ROOT / "datasets/canterbury/cp.html",
            PROJECT_ROOT / "datasets/calgary/PROGC",
            PROJECT_ROOT / "datasets/calgary/PAPER1",
        ]
    elif args.files:
        targets = args.files
    else:
        targets = [PROJECT_ROOT / "datasets/canterbury/xargs.1"]

    for t in targets:
        bench_file(t)


if __name__ == "__main__":
    main()
