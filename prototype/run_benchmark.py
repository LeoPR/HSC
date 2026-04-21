#!/usr/bin/env python3
"""
run_benchmark.py — Batch runner para todos os datasets do projeto HSC.

Roda pipelines A/B/C (raster, morton, hilbert) em todos os datasets
disponíveis, incluindo sintéticos como controles, e salva tudo em CSV.

Sempre persiste resultados em disco. Sem --csv, usa results/benchmark_YYYYMMDD_HHMMSS.csv.

Uso:
    python prototype/run_benchmark.py
    python prototype/run_benchmark.py --csv results/meu_teste.csv
    python prototype/run_benchmark.py --only-priority
    python prototype/run_benchmark.py --sides 256 512 1024
"""

from __future__ import annotations

import csv
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Sequence

# Garante UTF-8 no Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")

# Adicionar prototype ao path
sys.path.insert(0, str(Path(__file__).parent))

from data import load_file, pad_to_square, reorder_bytes, choose_side
from data.synthetic import (
    generate_2d_gaussian_blobs,
    generate_2d_gradient,
    generate_2d_noise,
    generate_1d_walk,
    generate_composite_2d,
)
from metrics import adaptive_order1_bits, zlib_size
from orders import raster_order, morton_order, hilbert_order
from orders.embedding import delay_embedding_order

# ── Diretórios ─────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "results"

# ── Catálogo de datasets ───────────────────────────────────────────────

# tipo: "2D_Image" (hipótese), "1D_Text" (controle negativo),
#       "Synthetic_2D" (controle positivo), "Other" (exploratório)

REAL_DATASETS = {
    # Silesia — prioridade para imagens 2D
    "mr":          {"path": "silesia/mr",        "tipo": "2D_Image",    "priority": True},
    "x-ray":       {"path": "silesia/x-ray",     "tipo": "2D_Image",    "priority": True},
    "dickens":     {"path": "silesia/dickens",    "tipo": "1D_Text",     "priority": True},
    "mozilla":     {"path": "silesia/mozilla",    "tipo": "Binary_Exec", "priority": False},
    "nci":         {"path": "silesia/nci",        "tipo": "Structured",  "priority": False},
    "osdb":        {"path": "silesia/osdb",       "tipo": "Structured",  "priority": False},
    # Calgary — nomes em maiúsculas no filesystem
    "pic":         {"path": "calgary/PIC",        "tipo": "2D_Image",    "priority": True},
    "book1":       {"path": "calgary/BOOK1",      "tipo": "1D_Text",     "priority": False},
    "book2":       {"path": "calgary/BOOK2",      "tipo": "1D_Text",     "priority": False},
    "geo":         {"path": "calgary/GEO",        "tipo": "Other",       "priority": False},
    "news":        {"path": "calgary/NEWS",       "tipo": "1D_Text",     "priority": False},
    "obj1":        {"path": "calgary/OBJ1",       "tipo": "Binary_Exec", "priority": False},
    "obj2":        {"path": "calgary/OBJ2",       "tipo": "Binary_Exec", "priority": False},
    "paper1":      {"path": "calgary/PAPER1",     "tipo": "1D_Text",     "priority": False},
    "paper2":      {"path": "calgary/PAPER2",     "tipo": "1D_Text",     "priority": False},
    "progc":       {"path": "calgary/PROGC",      "tipo": "SourceCode",  "priority": False},
    "progl":       {"path": "calgary/PROGL",      "tipo": "SourceCode",  "priority": False},
    "progp":       {"path": "calgary/PROGP",      "tipo": "SourceCode",  "priority": False},
    "trans":       {"path": "calgary/TRANS",      "tipo": "1D_Text",     "priority": False},
    "bib":         {"path": "calgary/BIB",        "tipo": "1D_Text",     "priority": False},
    # Canterbury
    "alice29":     {"path": "canterbury/alice29.txt",  "tipo": "1D_Text",    "priority": True},
    "ptt5":        {"path": "canterbury/ptt5",         "tipo": "2D_Image",   "priority": True},
    "lcet10":      {"path": "canterbury/lcet10.txt",   "tipo": "1D_Text",    "priority": False},
    "plrabn12":    {"path": "canterbury/plrabn12.txt", "tipo": "1D_Text",    "priority": False},
    "asyoulik":    {"path": "canterbury/asyoulik.txt", "tipo": "1D_Text",    "priority": False},
    "kennedy":     {"path": "canterbury/kennedy.xls",  "tipo": "Structured", "priority": False},
    "sum":         {"path": "canterbury/sum",           "tipo": "Binary_Exec","priority": False},
}

SYNTHETIC_SIDE = 256  # 256x256 = 65536 bytes

SYNTHETIC_DATASETS = {
    "synth_blobs":     {"tipo": "Synthetic_2D", "priority": True,
                        "gen": lambda: generate_2d_gaussian_blobs(SYNTHETIC_SIDE, n_blobs=5)},
    "synth_gradient":  {"tipo": "Synthetic_2D", "priority": True,
                        "gen": lambda: generate_2d_gradient(SYNTHETIC_SIDE)},
    "synth_noise":     {"tipo": "Synthetic_2D", "priority": True,
                        "gen": lambda: generate_2d_noise(SYNTHETIC_SIDE)},
    "synth_walk":      {"tipo": "Synthetic_1D", "priority": True,
                        "gen": lambda: generate_1d_walk(SYNTHETIC_SIDE * SYNTHETIC_SIDE)},
    "synth_composite": {"tipo": "Synthetic_2D", "priority": True,
                        "gen": lambda: generate_composite_2d(SYNTHETIC_SIDE)},
}


# ── Métricas ───────────────────────────────────────────────────────────


def evaluate_pipeline(name: str, seq: bytes) -> dict:
    """Roda zlib e modelo ordem-1, retorna dict de métricas."""
    t0 = time.perf_counter()
    zsize = zlib_size(seq)
    t_zlib = time.perf_counter() - t0

    t0 = time.perf_counter()
    bits = adaptive_order1_bits(seq)
    t_model = time.perf_counter() - t0

    return {
        "pipeline": name,
        "nbytes": len(seq),
        "zlib_bytes": zsize,
        "zlib_ratio": round(len(seq) / zsize, 4) if zsize else float("inf"),
        "model_bits": round(bits, 2),
        "model_bps": round(bits / len(seq), 6) if seq else 0.0,
        "time_zlib_s": round(t_zlib, 4),
        "time_model_s": round(t_model, 4),
    }


GRID_PIPELINES = [
    ("A_raster",  raster_order),
    ("B_morton",  morton_order),
    ("C_hilbert", hilbert_order),
]


def run_abc(raw: bytes, side: int) -> list[dict]:
    """Roda A/B/C (grid 2D fixo) no mesmo side."""
    padded = pad_to_square(raw, side)
    valid = len(raw)
    results = []
    for label, order_fn in GRID_PIPELINES:
        seq = reorder_bytes(padded, order_fn(side), valid)
        results.append(evaluate_pipeline(label, seq))
    return results


EMBED_SIZE_LIMIT = 2 * 1024 * 1024  # 2 MB — acima disso, muito lento em Python puro


def run_embedding(raw: bytes) -> list[dict]:
    """Roda pipelines de delay embedding D=2,3,4.

    Cada posição i é tratada como ponto (data[i], data[i+1], ...) no R^D.
    Posições com contexto local similar ficam adjacentes após ordenação SFC.
    Não pressupõe layout espacial — usa os próprios valores como coordenadas.

    Limitado a EMBED_SIZE_LIMIT bytes (Python puro é O(N log N) por D).
    Datasets maiores recebem resultado vazio com nota.
    """
    if len(raw) > EMBED_SIZE_LIMIT:
        label_prefix = "E_embed"
        return [evaluate_pipeline(f"E{D}_embed_SKIP", b"\x00") for D in [2, 3, 4]]

    results = []
    for D in [2, 3, 4]:
        label = f"E{D}_embed"
        order = delay_embedding_order(raw, D, curve="hilbert")
        seq = bytes(raw[i] for i in order)
        results.append(evaluate_pipeline(label, seq))
    return results


# ── CSV ────────────────────────────────────────────────────────────────

CSV_FIELDS = [
    "timestamp",
    "dataset",
    "tipo",
    "raw_bytes",
    "side",
    "padding_pct",
    "pipeline",
    "nbytes",
    "zlib_bytes",
    "zlib_ratio",
    "model_bits",
    "model_bps",
    "time_zlib_s",
    "time_model_s",
]


# ── Orquestração ───────────────────────────────────────────────────────


def run_benchmark(
    csv_path: Path,
    sides: Sequence[int],
    only_priority: bool = False,
    skip_synthetic: bool = False,
) -> None:
    """Roda o benchmark completo e salva em CSV."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    csvfile = open(csv_path, "a", newline="")
    writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
    if write_header:
        writer.writeheader()

    total_datasets = 0
    total_rows = 0

    # ── Datasets Reais ──
    print("=" * 70)
    print("BENCHMARK -- Datasets Reais")
    print("=" * 70)

    for name, info in sorted(REAL_DATASETS.items()):
        if only_priority and not info["priority"]:
            continue

        fpath = DATASETS_DIR / info["path"]
        if not fpath.exists():
            print(f"  SKIP {name:20s} (nao encontrado)")
            continue

        raw = load_file(fpath)
        raw_bytes = len(raw)
        side = choose_side(raw_bytes, sides)
        padding_pct = round((side * side - raw_bytes) / (side * side) * 100, 1)

        print(f"\n  {name:20s}  {info['tipo']:15s}  {raw_bytes:>10,} bytes  side={side}  pad={padding_pct}%")

        results = run_abc(raw, side) + run_embedding(raw)
        bps_values = []
        for r in results:
            row = {
                "timestamp": timestamp,
                "dataset": name,
                "tipo": info["tipo"],
                "raw_bytes": raw_bytes,
                "side": side,
                "padding_pct": padding_pct,
                **r,
            }
            writer.writerow(row)
            total_rows += 1
            bps_values.append(f"{r['pipeline']}={r['model_bps']:.4f}")

        print(f"    {' | '.join(bps_values)}")
        total_datasets += 1
        csvfile.flush()  # persistir após cada dataset

    # ── Datasets Sintéticos ──
    if not skip_synthetic:
        print("\n" + "=" * 70)
        print("BENCHMARK -- Datasets Sinteticos (controles)")
        print("=" * 70)

        for name, info in sorted(SYNTHETIC_DATASETS.items()):
            if only_priority and not info["priority"]:
                continue

            raw = info["gen"]()
            raw_bytes = len(raw)
            side = SYNTHETIC_SIDE
            padding_pct = 0.0

            print(f"\n  {name:20s}  {info['tipo']:15s}  {raw_bytes:>10,} bytes  side={side}")

            results = run_abc(raw, side) + run_embedding(raw)
            bps_values = []
            for r in results:
                row = {
                    "timestamp": timestamp,
                    "dataset": name,
                    "tipo": info["tipo"],
                    "raw_bytes": raw_bytes,
                    "side": side,
                    "padding_pct": padding_pct,
                    **r,
                }
                writer.writerow(row)
                total_rows += 1
                bps_values.append(f"{r['pipeline']}={r['model_bps']:.4f}")

            print(f"    {' | '.join(bps_values)}")
            total_datasets += 1
            csvfile.flush()

    csvfile.close()

    # ── Resumo ──
    print("\n" + "=" * 70)
    print(f"CONCLUIDO: {total_datasets} datasets, {total_rows} linhas")
    print(f"Resultados salvos em: {csv_path}")
    print("=" * 70)


# ── CLI ────────────────────────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Benchmark batch: roda A/B/C em todos os datasets e salva CSV.",
    )
    parser.add_argument(
        "--csv", type=Path, default=None,
        help="CSV de saida (default: results/benchmark_YYYYMMDD_HHMMSS.csv)",
    )
    parser.add_argument(
        "--sides", type=int, nargs="+", default=[256, 512, 1024, 2048, 4096],
        help="Candidatos de side (potencias de 2). Default: 256 512 1024 2048 4096",
    )
    parser.add_argument(
        "--only-priority", action="store_true",
        help="Rodar apenas datasets prioritarios (Sprint 1 minimo)",
    )
    parser.add_argument(
        "--skip-synthetic", action="store_true",
        help="Pular datasets sinteticos",
    )

    args = parser.parse_args()

    if args.csv is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.csv = RESULTS_DIR / f"benchmark_{ts}.csv"

    run_benchmark(
        csv_path=args.csv,
        sides=args.sides,
        only_priority=args.only_priority,
        skip_synthetic=args.skip_synthetic,
    )


if __name__ == "__main__":
    main()
