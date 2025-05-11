"""
fs.bench
========

Synthetic load‑generator & micro‑benchmarks for the virtual file‑system.

python -m fs.bench --dirs 200 --files 500 \
            --ops   100_000 \
            --state .bench_state.pkl.gz

That command will:

1. Create 200 top‑level directories `/dir_000 … /dir_199`.
2. Inside each, create up to 500 files `file_<n>.bin` with random 256‑B payloads.
3. Time *ops* random look‑ups / reads.
4. Print summary statistics.

The default parameters stay small so it finishes fast; tweak them on the CLI.
"""

from __future__ import annotations

import argparse
import os
import random
import statistics as stats
import string
import time
from pathlib import PurePosixPath

from rich.console import Console
from rich.table import Table

from . import persist
from .vfs import VFS

RND = random.Random(42)
console = Console()


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _rand_name(prefix: str, length: int = 6) -> str:
    body = "".join(RND.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}_{body}"


def populate(vfs: VFS, n_dirs: int, n_files: int):
    """Create n_dirs top‑level dirs, each with up to n_files random files."""
    for d in range(n_dirs):
        dir_path = PurePosixPath("/") / f"dir_{d:03d}"
        vfs.mkdir(str(dir_path))
        for f in range(n_files):
            name = _rand_name("file")
            full = dir_path / f"{name}.bin"
            data = os.urandom(256)
            vfs.write(str(full), data)


def time_random_reads(vfs: VFS, ops: int) -> list[float]:
    """Pick random files and measure read latency in µs."""
    paths = []
    for dir_name, dir_inode_id in vfs.table.get(vfs.root_id).children.items():
        dir_node = vfs.table.get(dir_inode_id)
        for fname in dir_node.children:
            paths.append(f"/{dir_name}/{fname}")

    t_samples: list[float] = []
    for _ in range(ops):
        p = RND.choice(paths)
        t0 = time.perf_counter()
        vfs.read(p)
        t_samples.append((time.perf_counter() - t0) * 1e6)  # µs
    return t_samples


# --------------------------------------------------------------------------
# main entry
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="VFS benchmark")
    ap.add_argument("--dirs", type=int, default=50, help="# top‑level dirs")
    ap.add_argument("--files", type=int, default=200, help="# files per dir")
    ap.add_argument("--ops", type=int, default=20_000, help="# random read ops")
    ap.add_argument("--state", default=".bench_state.pkl.gz", help="snapshot path")
    ap.add_argument("--reuse", action="store_true", help="reuse existing snapshot")
    args = ap.parse_args()

    vfs: VFS
    if args.reuse and os.path.exists(args.state):
        console.print(f"[cyan]Loading snapshot from {args.state}[/cyan]")
        vfs = persist.load(args.state)
    else:
        console.print(f"[cyan]Creating new VFS[/cyan]")
        vfs = VFS()
        console.print(
            f"[yellow]Populating {args.dirs} dirs × {args.files} files…[/yellow]"
        )
        populate(vfs, args.dirs, args.files)
        persist.save(vfs, args.state)
        console.print(f"[green]Snapshot saved → {args.state}[/green]")

    console.print(
        f"[yellow]Timing {args.ops:_} random reads (µs)…[/yellow]", highlight=False
    )
    samples = time_random_reads(vfs, args.ops)

    tbl = Table(title="Random read latency (µs)")
    tbl.add_column("metric", justify="right")
    tbl.add_column("value", justify="right")
    tbl.add_row("p50", f"{stats.median(samples):,.1f}")
    tbl.add_row("p95", f"{stats.quantiles(samples, n=20)[18]:,.1f}")
    tbl.add_row("max", f"{max(samples):,.1f}")
    tbl.add_row("min", f"{min(samples):,.1f}")
    tbl.add_row("mean", f"{stats.mean(samples):,.1f}")
    console.print(tbl)


if __name__ == "__main__":
    main()

