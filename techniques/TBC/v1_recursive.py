"""
TBC v1 — aplicacao recursiva.

Aplica v1 sucessivamente, concatenando os planos de cada nivel como entrada
do proximo, ate que o tamanho pare de diminuir.

Premissa: header de graca. Mede so bits de plano.

Objetivo: observar como o ranking e os tamanhos evoluem ao longo dos niveis.

Uso:
    python v1_recursive.py                            # demo exemplo canonico
    python v1_recursive.py --bits 1001...             # input custom
    python v1_recursive.py --scale                    # varre distribuicoes x tamanhos
    python v1_recursive.py --max-levels 20
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

# reusa primitivas da v1_demo
sys.path.insert(0, str(Path(__file__).parent))
from v1_demo import (
    bits_to_dibits,
    rank_dibits,
    build_planes,
    reconstruct,
    synth_input,
)


@dataclass
class LevelInfo:
    level: int
    input_bits: int
    ranking: list[tuple[str, int]]
    plane_sizes: list[int]
    total_plane_bits: int
    tail_bit: str = ""   # bit solto do input que nao formou dibit (0 ou 1 bit)

    def delta(self) -> int:
        return self.total_plane_bits - self.input_bits

    def ranking_tuple(self) -> tuple[str, ...]:
        return tuple(s for s, _ in self.ranking)


def planes_to_bits(planes: list[list[int]]) -> str:
    return "".join("".join(str(b) for b in p) for p in planes)


def apply_recursive(
    bits: str,
    max_levels: int = 20,
) -> tuple[list[LevelInfo], str, list[list[list[int]]]]:
    """Aplica v1 recursivamente.

    Retorna:
        history: lista de LevelInfo por nivel
        final_bits: bits finais (da ultima iteracao bem-sucedida, ou originais se 0 iter)
        all_planes: planos de cada nivel (para round-trip)
    """
    history: list[LevelInfo] = []
    all_planes: list[list[list[int]]] = []

    current = bits
    for lvl in range(1, max_levels + 1):
        # Precisa ter pelo menos 2 bits para formar 1 dibit
        if len(current) < 2:
            break
        dibits = bits_to_dibits(current)
        # Bit solto (ao fim) que nao formou dibit
        usable = 2 * len(dibits)
        tail = current[usable:]
        ranking = rank_dibits(dibits)
        planes = build_planes(dibits, ranking)
        next_bits = planes_to_bits(planes)
        total = len(next_bits)

        info = LevelInfo(
            level=lvl,
            input_bits=len(current),
            ranking=ranking,
            plane_sizes=[len(p) for p in planes],
            total_plane_bits=total,
            tail_bit=tail,
        )

        # Criterio de parada: total >= entrada atual
        if total >= len(current):
            # Nao aceita esse nivel; para antes de aplicar
            break

        history.append(info)
        all_planes.append(planes)
        current = next_bits

    return history, current, all_planes


def decompress_recursive(
    final_bits: str,
    history: list[LevelInfo],
) -> str:
    """Reverte recursao. history em ordem de compressao (nivel 1, 2, ...)."""
    current_bits = final_bits
    for info in reversed(history):
        # current_bits do nivel atual deve ter exatamente total_plane_bits
        # (garantido pela propria cadeia de niveis).
        planes = []
        pos = 0
        for size in info.plane_sizes:
            plane = [int(b) for b in current_bits[pos:pos + size]]
            planes.append(plane)
            pos += size
        # Reconstroi os dibits do nivel anterior
        N_dibits = info.input_bits // 2
        dibits = reconstruct(planes, info.ranking, N_dibits)
        # Reanexa o bit solto (tail_bit) que ficou fora da pairing do nivel
        current_bits = "".join(dibits) + info.tail_bit
    return current_bits


def show_history(bits_in: str, history: list[LevelInfo]) -> None:
    print(f"input: {len(bits_in)} bits")
    print(f"{'lvl':>3s}  {'in_bits':>8s}  {'planos':>20s}  "
          f"{'total':>7s}  {'delta':>7s}  {'ranking':<20s}  {'eq_prev':>7s}")
    print("-" * 85)
    prev_rk = None
    for info in history:
        rk_str = ">".join(s for s, _ in info.ranking)
        eq = "yes" if prev_rk is not None and info.ranking_tuple() == prev_rk else ""
        sizes_str = str(info.plane_sizes)
        if len(sizes_str) > 18:
            sizes_str = sizes_str[:15] + "..."
        print(f"{info.level:>3d}  {info.input_bits:>8d}  {sizes_str:>20s}  "
              f"{info.total_plane_bits:>7d}  {info.delta():>+7d}  {rk_str:<20s}  {eq:>7s}")
        prev_rk = info.ranking_tuple()


def demo_single(bits: str, max_levels: int = 20) -> None:
    print(f"\n=== recursao em input de {len(bits)} bits ===\n")
    history, final_bits, all_planes = apply_recursive(bits, max_levels=max_levels)
    if not history:
        print("Nenhum nivel reduziu (estabilizou imediatamente).")
        return
    show_history(bits, history)
    print(f"\napos {len(history)} nivel(is): {len(bits)} -> {len(final_bits)} bits "
          f"(acumulado {len(final_bits)/len(bits):.4f}x)")

    # Round-trip
    decoded = decompress_recursive(final_bits, history)
    # Pode ter sobra de bits (de paridade nao-par) — comparar como prefixo
    ok = decoded[:len(bits)] == bits
    print(f"round-trip: {'OK' if ok else 'FAIL'}")
    if not ok:
        print(f"  esperado: {bits[:40]}...")
        print(f"  obtido:   {decoded[:40]}...")


def scale_test(max_levels: int = 20) -> None:
    distributions = [
        ("desbalanceado 75-8-8-8",  {"01": 0.75, "00": 0.08, "10": 0.08, "11": 0.09}),
        ("homogeneo 25-25-25-25",   {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}),
        ("um ausente (00=0%)",      {"01": 0.50, "10": 0.30, "11": 0.20, "00": 0.0}),
        ("bimodal 40-40-10-10",     {"01": 0.40, "10": 0.40, "00": 0.10, "11": 0.10}),
        ("extremo (1 dominante)",   {"01": 0.95, "10": 0.02, "11": 0.02, "00": 0.01}),
    ]
    sizes = [50, 500, 5000]

    print(f"\n{'dist':<25s} {'N':>6s}  {'niveis':>6s}  {'in':>6s} -> {'out':>6s}  "
          f"{'acum':>6s}  {'ranking_final':<20s}  {'pto_fixo':>8s}  rt")
    print("-" * 105)

    for dist_name, dist in distributions:
        for N in sizes:
            bits = synth_input(N, dist)
            history, final_bits, _ = apply_recursive(bits, max_levels=max_levels)
            decoded = decompress_recursive(final_bits, history)
            rt = "OK" if decoded[:len(bits)] == bits else "FAIL"

            if not history:
                print(f"{dist_name:<25s} {N:>6d}  {0:>6d}  {len(bits):>6d} -> "
                      f"{len(bits):>6d}  {1.0:>5.3f}x  {'(no reduction)':<20s}  "
                      f"{'yes':>8s}  {rt}")
                continue

            acum = len(final_bits) / len(bits)
            last_rk = ">".join(s for s, _ in history[-1].ranking)
            # Detecta ponto fixo: ultimos 2+ niveis com mesmo ranking
            fixed_streak = 1
            for i in range(len(history) - 1, 0, -1):
                if history[i].ranking_tuple() == history[i - 1].ranking_tuple():
                    fixed_streak += 1
                else:
                    break
            pto_fixo = f"{fixed_streak}/{len(history)}"

            print(f"{dist_name:<25s} {N:>6d}  {len(history):>6d}  "
                  f"{len(bits):>6d} -> {len(final_bits):>6d}  "
                  f"{acum:>5.3f}x  {last_rk:<20s}  {pto_fixo:>8s}  {rt}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TBC v1 recursivo — estudo do processo.")
    parser.add_argument("--bits", default=None, help="sequencia binaria de input")
    parser.add_argument("--scale", action="store_true", help="varre distribuicoes x tamanhos")
    parser.add_argument("--max-levels", type=int, default=20, help="maximo de niveis")
    args = parser.parse_args()

    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.scale:
        scale_test(max_levels=args.max_levels)
        return

    bits = args.bits or "1001100110010101010101010111"
    demo_single(bits, max_levels=args.max_levels)


if __name__ == "__main__":
    main()
