"""compare_orders.py — Orquestrador de benchmark comparativo.

O QUE ESTÁ SENDO TESTADO
=========================

Hipótese central:  a ordem de leitura dos bytes de um dataset influencia
a compressibilidade.  Curvas de preenchimento de espaço (Hilbert, Morton)
podem criar sequências 1-D com mais dependências locais exploráveis por
um codificador entrópico ou compressor real.

Pipelines avaliados
-------------------
A  raster     — leitura linha-a-linha (baseline ingênuo).
B  morton     — reordenação por curva Z/Morton (baseline competitivo).
C  hilbert    — reordenação por curva de Hilbert (hipótese principal).
D  hilbert+ctx — Hilbert com busca automática do lado de malha que
                 minimiza bits por símbolo no modelo de contexto ordem-1.
E  auto       — busca exaustiva de (topologia × lado) que minimiza bps.

Métricas coletadas
------------------
- zlib_bytes / zlib_ratio  — compressor real (deflate nível 9).
- model_bps                — bits por símbolo estimados por um modelo
                             adaptativo de contexto ordem-1 (proxy teórico).
- tempos de execução de ambos.

Uso
---
  python prototype/compare_orders.py datasets/pt-br.tsv
  python prototype/compare_orders.py datasets/pt-br.tsv --side 2048
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Sequence

# Garante saída UTF-8 no Windows (terminal cp1252 não suporta ━ e ─)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")

from data import load_file, pad_to_square, reorder_bytes, choose_side
from metrics import adaptive_order1_bits, zlib_size
from orders import raster_order, morton_order, hilbert_order

# ── Helpers de diagnóstico ─────────────────────────────────────────────


def _evaluate(name: str, seq: bytes) -> dict:
    """Roda as duas métricas e devolve um dict com resultados."""
    t0 = time.perf_counter()
    zsize = zlib_size(seq)
    t_zlib = time.perf_counter() - t0

    t0 = time.perf_counter()
    bits = adaptive_order1_bits(seq)
    t_model = time.perf_counter() - t0

    return {
        "name": name,
        "nbytes": len(seq),
        "zlib_bytes": zsize,
        "zlib_ratio": len(seq) / zsize if zsize else float("inf"),
        "model_bits": bits,
        "model_bps": bits / len(seq) if seq else 0.0,
        "time_zlib_s": t_zlib,
        "time_model_s": t_model,
    }


def _print_table(results: Sequence[dict]) -> None:
    headers = [
        "pipeline", "bytes", "zlib_bytes", "zlib_ratio",
        "model_bps", "t_zlib(s)", "t_model(s)",
    ]
    header_line = " | ".join(f"{h:>14}" for h in headers)
    print(header_line)
    print("─" * len(header_line))
    for r in results:
        print(" | ".join([
            f"{r['name']:>14}",
            f"{r['nbytes']:>14}",
            f"{r['zlib_bytes']:>14}",
            f"{r['zlib_ratio']:>14.4f}",
            f"{r['model_bps']:>14.4f}",
            f"{r['time_zlib_s']:>14.4f}",
            f"{r['time_model_s']:>14.4f}",
        ]))


# ── Testes ─────────────────────────────────────────────────────────────


def test_abc(raw: bytes, side: int) -> list[dict]:
    """Teste A/B/C: compara as três topologias com o mesmo lado de malha.

    O que se espera ver:
    - Dado com correlação espacial → Hilbert ≥ Morton > raster.
    - Dado sequencial puro (texto) → raster pode vencer (já é a ordem
      natural de escrita).
    """
    padded = pad_to_square(raw, side)
    valid = len(raw)

    results = []
    for label, order_fn in [
        ("A_raster", raster_order),
        ("B_morton", morton_order),
        ("C_hilbert", hilbert_order),
    ]:
        seq = reorder_bytes(padded, order_fn(side), valid)
        results.append(_evaluate(label, seq))
    return results


def test_d_hilbert_ctx(raw: bytes, sides: Sequence[int]) -> dict | None:
    """Teste D: Hilbert + busca de dimensão ótima.

    Varia o lado da malha entre *sides* e escolhe aquele que minimiza
    bits por símbolo no modelo de contexto ordem-1.  Isso simula a
    ideia de "seleção automática de dimensão" do framework proposto.
    """
    valid = len(raw)
    best = None
    for s in sides:
        if s * s < valid:
            continue
        padded = pad_to_square(raw, s)
        seq = reorder_bytes(padded, hilbert_order(s), valid)
        r = _evaluate(f"D_hilbert_{s}", seq)
        if best is None or r["model_bps"] < best["model_bps"]:
            best = r
    return best


def test_e_auto(raw: bytes, sides: Sequence[int]) -> dict | None:
    """Teste E: busca exaustiva (topologia × lado).

    Testa todas as combinações de topologia e lado de malha.
    Se a topologia ótima muda conforme o dado, isso sustenta a hipótese
    de que a escolha deve ser adaptativa — e abre caminho para expansão
    a outras topologias além de Hilbert.
    """
    valid = len(raw)
    best = None
    for s in sides:
        if s * s < valid:
            continue
        padded = pad_to_square(raw, s)
        for topo_name, order_fn in [
            ("raster", raster_order),
            ("morton", morton_order),
            ("hilbert", hilbert_order),
        ]:
            seq = reorder_bytes(padded, order_fn(s), valid)
            r = _evaluate(f"E_{topo_name}_{s}", seq)
            if best is None or r["model_bps"] < best["model_bps"]:
                best = r
    return best


# ── Orquestração ───────────────────────────────────────────────────────


def run(dataset_path: Path, side: int | None, csv_path: Path | None = None) -> list[dict]:
    raw = load_file(dataset_path)
    print(f"Dataset : {dataset_path.name}")
    print(f"Tamanho : {len(raw):,} bytes")

    # Limite prático: lado 4096 = 16M posições, lento demais em Python puro.
    # Para lados maiores, migrar geração de ordens para Rust/numpy.
    side_candidates = [512, 1024, 2048]
    main_side = side if side is not None else choose_side(len(raw), side_candidates)
    print(f"Lado    : {main_side}  (malha {main_side}×{main_side} = {main_side*main_side:,} posições)")
    print()

    # ── Teste A/B/C ──
    print("━" * 60)
    print("TESTE A/B/C — Três topologias, mesmo lado de malha")
    print("Pergunta: qual ordenação produz menor entropia condicional e")
    print("          melhor taxa zlib para este dataset?")
    print("━" * 60)
    abc = test_abc(raw, main_side)
    _print_table(abc)
    print()

    # ── Teste D ──
    print("━" * 60)
    print("TESTE D — Hilbert + busca de dimensão ótima")
    print("Pergunta: existe um lado de malha diferente do default que")
    print("          faz Hilbert comprimir melhor este dataset?")
    print("━" * 60)
    d = test_d_hilbert_ctx(raw, side_candidates)
    if d:
        _print_table([d])
        print(f"  → melhor: {d['name']}  ({d['model_bps']:.4f} bps)")
    print()

    # ── Teste E ──
    print("━" * 60)
    print("TESTE E — Busca exaustiva (topologia × lado)")
    print("Pergunta: se pudéssemos escolher livremente a topologia e o")
    print("          lado, qual combinação seria ótima?  Se a resposta")
    print("          mudar conforme o dataset, isso sustenta seleção")
    print("          adaptativa de topologia.")
    print("━" * 60)
    e = test_e_auto(raw, side_candidates)
    if e:
        _print_table([e])
        print(f"  → melhor: {e['name']}  ({e['model_bps']:.4f} bps)")
    print()

    # ── Diagnóstico ──
    print("━" * 60)
    print("DIAGNÓSTICO")
    print("━" * 60)
    best_abc = min(abc, key=lambda r: r["model_bps"])
    print(f"  Melhor A/B/C : {best_abc['name']}  ({best_abc['model_bps']:.4f} bps)")
    if d:
        print(f"  Melhor D     : {d['name']}  ({d['model_bps']:.4f} bps)")
    if e:
        print(f"  Melhor E     : {e['name']}  ({e['model_bps']:.4f} bps)")

    if d and e:
        delta = best_abc["model_bps"] - e["model_bps"]
        if delta > 0.01:
            print(f"\n  ⮕  Busca automática (E) economizou {delta:.4f} bps sobre o melhor fixo (A/B/C).")
            print("     Isso sugere que a escolha de topologia/dimensão importa para este dataset.")
        else:
            print(f"\n  ⮕  Diferença marginal ({delta:.4f} bps).  Para este dataset a topologia")
            print("     fixa já é quase ótima.")

    # ── Coleta de resultados para CSV ──
    all_results = abc + ([d] if d else []) + ([e] if e else [])

    # ── Salvar CSV se solicitado ──
    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "dataset",
            "pipeline",
            "nbytes",
            "zlib_bytes",
            "zlib_ratio",
            "model_bits",
            "model_bps",
            "time_zlib_s",
            "time_model_s",
        ]
        # Verificar se precisa escrever header
        write_header = not csv_path.exists() or csv_path.stat().st_size == 0
        with open(csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            for result in all_results:
                # Renomear 'name' → 'pipeline' para compatibilidade com CSV
                row = {
                    "dataset": dataset_path.stem,
                    "pipeline": result["name"],
                    **{k: v for k, v in result.items() if k != "name"},
                }
                writer.writerow(row)
        print(f"\n✓ Resultados salvos em: {csv_path}")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark comparativo de topologias de reordenação para compressão.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "dataset",
        type=Path,
        help="Caminho para o arquivo de dados (ex: datasets/pt-br.tsv).",
    )
    parser.add_argument(
        "--side",
        type=int,
        default=None,
        help="Lado da malha quadrada (potência de 2).  Se omitido, escolhe automaticamente.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Salvar resultados em arquivo CSV (append mode).",
    )
    args = parser.parse_args()
    run(args.dataset, args.side, args.csv)
