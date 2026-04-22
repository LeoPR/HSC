"""
TBC v1 — demo didatico do processo, passo a passo.

Objetivo: ver o processo de compressao/descompressao em qualquer escala,
ignorando custo de header (fingindo que cabecalho e metadados sao gratis).

So medimos bits-dos-planos. Nao tiramos conclusoes sobre compressao real.

Uso:
    python v1_demo.py                   # exemplo canonico 14 dibits
    python v1_demo.py --bits 1001100110010101010101010111
    python v1_demo.py --scale            # teste de escala em varios tamanhos
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import Counter
from pathlib import Path


# ── Primitivas v1 (explicitas, sem depender de tbc.py para ser didatico) ──


def bits_to_dibits(bits: str) -> list[str]:
    """Agrupa string de bits em dibits. Ignora bit sobrando no final."""
    usable = len(bits) - (len(bits) % 2)
    return [bits[i:i + 2] for i in range(0, usable, 2)]


def rank_dibits(dibits: list[str]) -> list[tuple[str, int]]:
    """Ordena por frequencia desc, desempate lex asc. Inclui todos os 4 simbolos."""
    all_syms = ["00", "01", "10", "11"]
    freq = Counter(dibits)
    return sorted([(s, freq.get(s, 0)) for s in all_syms],
                  key=lambda kv: (-kv[1], kv[0]))


def build_planes(dibits: list[str], ranking: list[tuple[str, int]]) -> list[list[int]]:
    """Constroi os planos indicadores na ordem do ranking.

    Retorna lista de planos, cada um sendo lista de 0/1.
    O ultimo simbolo do ranking nao recebe plano (residuo implicito).
    """
    positions = list(range(len(dibits)))
    planes = []
    for sigma, _freq in ranking[:-1]:  # ate o penultimo
        plane = []
        next_positions = []
        for pos in positions:
            if dibits[pos] == sigma:
                plane.append(1)
            else:
                plane.append(0)
                next_positions.append(pos)
        planes.append(plane)
        positions = next_positions
        if not positions:
            break  # nada mais a cobrir
    return planes


def reconstruct(planes: list[list[int]], ranking: list[tuple[str, int]], N: int) -> list[str]:
    """Reconstroi a sequencia de dibits a partir dos planos e do ranking."""
    result: list[str | None] = [None] * N
    positions = list(range(N))
    for i, plane in enumerate(planes):
        sigma, _ = ranking[i]
        next_positions = []
        for j, pos in enumerate(positions):
            if plane[j] == 1:
                result[pos] = sigma
            else:
                next_positions.append(pos)
        positions = next_positions
    # Posicoes remanescentes: σ da posicao len(planes) no ranking (residuo implicito).
    if positions:
        residual_sigma = ranking[len(planes)][0]
        for pos in positions:
            result[pos] = residual_sigma
    return result  # type: ignore[return-value]


# ── Metricas PURAS (sem header) ──


def plane_sizes(planes: list[list[int]]) -> list[int]:
    return [len(p) for p in planes]


def total_plane_bits(planes: list[list[int]]) -> int:
    return sum(plane_sizes(planes))


# ── Demo passo a passo ──


def demo(bits: str, title: str = "") -> None:
    if title:
        print(f"\n=== {title} ===")
    print(f"input (bits)   : {bits}  ({len(bits)} bits)")

    dibits = bits_to_dibits(bits)
    N = len(dibits)
    print(f"dibits (N={N}) : {' '.join(dibits)}")

    ranking = rank_dibits(dibits)
    print(f"ranking        : " + "  ".join(f"{s}={f}" for s, f in ranking))

    planes = build_planes(dibits, ranking)

    print("\nconstrucao dos planos:")
    positions = list(range(N))
    for i, plane in enumerate(planes):
        sigma, freq = ranking[i]
        print(f"  P{i+1} sobre {sigma} (freq={freq}, {len(positions)} posicoes candidatas)")
        print(f"     {'  '.join(str(b) for b in plane)}     (|P{i+1}| = {len(plane)} bits)")
        # atualiza positions so para o log (nao reusamos aqui)
        next_positions = [positions[j] for j, b in enumerate(plane) if b == 0]
        positions = next_positions
    residual_sigma = ranking[len(planes)][0]
    print(f"  residuo implicito: {residual_sigma} em {len(positions)} posicoes restantes")

    total = total_plane_bits(planes)
    print(f"\nmetricas PURAS (sem header):")
    print(f"  tamanhos dos planos : {plane_sizes(planes)}")
    print(f"  total bits planos   : {total}")
    print(f"  input bits usaveis  : {N * 2}")
    print(f"  delta (plano - orig): {total - N * 2:+d} bits")

    # Round-trip
    reconstructed = reconstruct(planes, ranking, N)
    original = dibits
    ok = reconstructed == original
    print(f"  round-trip          : {'OK' if ok else 'FAIL'}")
    if not ok:
        for j, (a, b) in enumerate(zip(original, reconstructed)):
            if a != b:
                print(f"    posicao {j}: orig={a} reconst={b}")


# ── Teste de escala ──


def synth_input(N_dibits: int, distribution: dict[str, float], seed: int = 42) -> str:
    """Gera input sintetico de N_dibits com distribuicao especificada.

    distribution: dict {dibit: probabilidade}, devem somar 1.0
    """
    rng = random.Random(seed)
    syms = list(distribution.keys())
    weights = list(distribution.values())
    dibits = rng.choices(syms, weights=weights, k=N_dibits)
    return "".join(dibits)


def scale_test(
    sizes: list[int],
    distributions: list[tuple[str, dict[str, float]]],
) -> None:
    """Roda v1 em varios tamanhos e distribuicoes. Reporta tamanho bruto dos planos."""
    print(f"\n{'dist':<25s}  {'N_dibits':>10s}  {'input_bits':>11s}  "
          f"{'planos':>8s}  {'delta':>8s}  {'rt':>3s}")
    print("-" * 75)
    for dist_name, dist in distributions:
        for N in sizes:
            bits = synth_input(N, dist)
            dibits = bits_to_dibits(bits)
            ranking = rank_dibits(dibits)
            planes = build_planes(dibits, ranking)
            total = total_plane_bits(planes)
            rt_ok = reconstruct(planes, ranking, N) == dibits
            delta = total - 2 * N
            print(f"{dist_name:<25s}  {N:>10d}  {2*N:>11d}  "
                  f"{total:>8d}  {delta:>+8d}  {'OK' if rt_ok else 'X':>3s}")


# ── CLI ──


def main() -> None:
    parser = argparse.ArgumentParser(description="TBC v1 — demo didatico.")
    parser.add_argument("--bits", default=None,
                        help="string binaria de input (default: exemplo canonico)")
    parser.add_argument("--scale", action="store_true",
                        help="roda teste de escala em varios tamanhos")
    args = parser.parse_args()

    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.scale:
        print("Teste de escala — aplicando v1 em distribuicoes e tamanhos variados.")
        print("(medidas puras em bits de plano, header fingido como gratis)")

        distributions = [
            ("desbalanceado 75-8-8-8",  {"01": 0.75, "00": 0.08, "10": 0.08, "11": 0.09}),
            ("homogeneo 25-25-25-25",   {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}),
            ("um ausente (00=0%)",      {"01": 0.50, "10": 0.30, "11": 0.20, "00": 0.0}),
            ("bimodal 40-40-10-10",     {"01": 0.40, "10": 0.40, "00": 0.10, "11": 0.10}),
            ("extremo (1 dominante)",   {"01": 0.95, "10": 0.02, "11": 0.02, "00": 0.01}),
        ]
        sizes = [7, 50, 500, 5000]
        scale_test(sizes, distributions)
        return

    # Demo single
    bits = args.bits or "1001100110010101010101010111"  # 28 bits = 14 dibits
    demo(bits, title="exemplo canonico (logic_03)" if args.bits is None else "input custom")


if __name__ == "__main__":
    main()
