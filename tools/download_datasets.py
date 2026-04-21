#!/usr/bin/env python3
"""
Dataset Download Manager for HSC Compression Research

Downloads canonical compression benchmarks and supports cleanup.

Tested working sources (2026-04-03):
  - Calgary:    https://mattmahoney.net/dc/calgary.zip        (~3 MB)
  - Canterbury: https://corpus.canterbury.ac.nz/resources/cantrbry.zip  (~3 MB)
  - enwik8:     https://mattmahoney.net/dc/enwik8.zip         (~36 MB compressed)
  - Silesia:    manual download from https://sun.aei.polsl.pl/~sdeor/index.php?page=silesia

Usage:
    python tools/download_datasets.py download          # Calgary + Canterbury
    python tools/download_datasets.py download --ltcb   # also enwik8
    python tools/download_datasets.py status
    python tools/download_datasets.py cleanup --corpus all --no-dry-run
"""

import argparse
import logging
import shutil
import ssl
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional
from urllib.error import URLError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"

# SSL context that ignores self-signed certs (needed for some mirrors)
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


def download_file(url: str, dest: Path, force: bool = False) -> bool:
    """Download *url* to *dest* with basic progress output."""
    if dest.exists() and not force:
        logger.info(f"  skip (exists): {dest.name}")
        return True

    logger.info(f"  => {dest.name}")
    temp = dest.with_suffix(".tmp")
    try:
        with urllib.request.urlopen(url, timeout=60, context=_SSL_CTX) as r:
            total = int(r.headers.get("content-length", 0))
            done = 0
            with open(temp, "wb") as f:
                while chunk := r.read(65536):
                    f.write(chunk)
                    done += len(chunk)
                    if total and done % (4 * 1024 * 1024) < 65536:
                        logger.info(f"     {done / 1e6:.1f}/{total / 1e6:.1f} MB")
        temp.replace(dest)
        logger.info(f"  ok: {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
        return True
    except URLError as e:
        logger.error(f"  FAIL: {dest.name} — {e}")
        if temp.exists():
            temp.unlink()
        return False


def extract_zip(archive: Path, dest_dir: Path) -> int:
    """Extract a .zip archive to *dest_dir*. Returns number of files extracted."""
    logger.info(f"  extracting {archive.name} ...")
    with zipfile.ZipFile(archive) as zf:
        members = [m for m in zf.infolist() if not m.filename.endswith("/")]
        for m in members:
            # Flatten paths: write everything directly to dest_dir
            target = dest_dir / Path(m.filename).name
            if not target.exists():
                target.write_bytes(zf.read(m))
    logger.info(f"  extracted {len(members)} files to {dest_dir.name}/")
    return len(members)


def extract_tar(archive: Path, dest_dir: Path) -> int:
    """Extract a .tar.gz or .tar.bz2 archive. Returns number of files extracted."""
    logger.info(f"  extracting {archive.name} ...")
    count = 0
    with tarfile.open(archive, "r:*") as tf:
        for m in tf.getmembers():
            if m.isfile():
                target = dest_dir / Path(m.name).name
                if not target.exists():
                    src = tf.extractfile(m)
                    if src:
                        target.write_bytes(src.read())
                        count += 1
    logger.info(f"  extracted {count} files to {dest_dir.name}/")
    return count


# ── Corpus downloads ───────────────────────────────────────────────────


def download_calgary(force: bool = False) -> bool:
    """Calgary corpus (~3.1 MB) — all 14 files from Matt Mahoney's zip."""
    logger.info("\n[Calgary Corpus]")
    dest_dir = DATASETS_DIR / "calgary"
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive = DATASETS_DIR / "calgary.zip"
    ok = download_file("https://mattmahoney.net/dc/calgary.zip", archive, force)
    if ok:
        extract_zip(archive, dest_dir)
        archive.unlink()  # remove zip after extraction
    return ok


def download_canterbury(force: bool = False) -> bool:
    """Canterbury corpus (~2.8 MB) — all 11 files from official site."""
    logger.info("\n[Canterbury Corpus]")
    dest_dir = DATASETS_DIR / "canterbury"
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive = DATASETS_DIR / "cantrbry.zip"
    ok = download_file(
        "https://corpus.canterbury.ac.nz/resources/cantrbry.zip", archive, force
    )
    if ok:
        extract_zip(archive, dest_dir)
        archive.unlink()
    return ok


def download_enwik8(force: bool = False) -> bool:
    """enwik8 (Wikipedia 100 MB) — zipped (~36 MB download)."""
    logger.info("\n[enwik8 — Large Text Benchmark]")
    dest_dir = DATASETS_DIR / "ltcb"
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / "enwik8"
    if target.exists() and not force:
        logger.info(f"  skip (exists): enwik8")
        return True
    archive = dest_dir / "enwik8.zip"
    ok = download_file("https://mattmahoney.net/dc/enwik8.zip", archive, force)
    if ok:
        extract_zip(archive, dest_dir)
        archive.unlink()
    return ok


def print_silesia_instructions() -> None:
    """Print manual download instructions for Silesia (SSL issues prevent automation)."""
    logger.info("\n[Silesia Corpus — Manual Download Required]")
    logger.info(
        """
  The Silesia server uses a self-signed certificate that blocks automated
  downloads. Download manually at:

    https://sun.aei.polsl.pl/~sdeor/index.php?page=silesia

  Priority files (place in datasets/silesia/):
    mr      (~10 MB) — MRI scan         [2D_Image, PRIORITÁRIO]
    x-ray   (~8.5 MB) — X-ray           [2D_Image, PRIORITÁRIO]
    dickens (~10 MB) — Charles Dickens  [1D_Text, controle negativo]
"""
    )


# ── CLI ────────────────────────────────────────────────────────────────


def status() -> None:
    corpora = {
        "Silesia": DATASETS_DIR / "silesia",
        "Calgary": DATASETS_DIR / "calgary",
        "Canterbury": DATASETS_DIR / "canterbury",
        "LTCB": DATASETS_DIR / "ltcb",
    }
    logger.info("\n" + "="*60)
    logger.info("DATASET STATUS")
    logger.info("="*60)
    total_files, total_bytes = 0, 0
    for name, d in corpora.items():
        if not d.exists():
            logger.info(f"  {name:15} (not found)")
            continue
        files = [f for f in d.glob("*") if f.is_file()]
        size = sum(f.stat().st_size for f in files)
        total_files += len(files)
        total_bytes += size
        if files:
            logger.info(f"  {name:15} {len(files):3d} files   {size/1e6:8.1f} MB")
        else:
            logger.info(f"  {name:15} (empty)")
    logger.info("-"*60)
    logger.info(f"  {'TOTAL':15} {total_files:3d} files   {total_bytes/1e6:8.1f} MB")


def cleanup(corpus_name: str, dry_run: bool) -> None:
    dirs = {
        "silesia": DATASETS_DIR / "silesia",
        "calgary": DATASETS_DIR / "calgary",
        "canterbury": DATASETS_DIR / "canterbury",
        "ltcb": DATASETS_DIR / "ltcb",
    }
    targets = list(dirs.values()) if corpus_name == "all" else [dirs[corpus_name]]
    total_freed = 0
    for d in targets:
        if not d.exists():
            continue
        files = [f for f in d.glob("*") if f.is_file()]
        size = sum(f.stat().st_size for f in files)
        if files:
            logger.info(f"  {'[DELETE]' if not dry_run else '[would delete]'} {d.name}/ ({len(files)} files, {size/1e6:.1f} MB)")
            if not dry_run:
                shutil.rmtree(d)
            total_freed += size
    freed_mb = total_freed / 1e6
    if dry_run:
        logger.info(f"\n  Would free {freed_mb:.1f} MB  (use --no-dry-run to execute)")
    else:
        logger.info(f"\n  Freed {freed_mb:.1f} MB")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download canonical compression benchmark datasets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd")

    dl = sub.add_parser("download", help="Download Calgary + Canterbury (+ optional enwik8)")
    dl.add_argument("--ltcb", action="store_true", help="Also download enwik8 (~36 MB)")
    dl.add_argument("--force", action="store_true", help="Re-download even if files exist")

    cl = sub.add_parser("cleanup", help="Remove datasets to recover disk space")
    cl.add_argument(
        "--corpus",
        choices=["silesia", "calgary", "canterbury", "ltcb", "all"],
        default="all",
    )
    cl.add_argument("--no-dry-run", action="store_true")

    sub.add_parser("status", help="Show current dataset status")

    args = parser.parse_args()

    try:
        if args.cmd == "download":
            download_calgary(args.force)
            download_canterbury(args.force)
            if args.ltcb:
                download_enwik8(args.force)
            print_silesia_instructions()
            status()
        elif args.cmd == "cleanup":
            cleanup(args.corpus, dry_run=not args.no_dry_run)
        else:
            status()
    except KeyboardInterrupt:
        logger.warning("\nInterrupted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
