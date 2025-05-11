#!/usr/bin/env python3
"""
Full benchmark: measure write/delete latency and Python memory usage
across different directory scales. Uses tracemalloc for peak allocations.
"""

import time
import random
import statistics as stat
import tracemalloc
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from fs.vfs import VFS

# reproducible sampling
random.seed(42)

def populate(vfs: VFS, n_dirs: int, n_files: int):
    for d in range(n_dirs):
        dpath = f"/dir_{d:04d}"
        vfs.mkdir(dpath)
        for f in range(n_files):
            vfs.touch(f"{dpath}/file_{f:05d}.bin")

def benchmark(config, n_ops=5_000):
    n_dirs, n_files = config

    # ---------- population + memory ----------
    tracemalloc.start()
    vfs = VFS()
    populate(vfs, n_dirs, n_files)
    _, peak_pop = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # gather all existing file paths
    paths = []
    root = vfs.table.get(vfs.root_id)
    for dname in root.iter_names():
        dnode = vfs.table.get(root.get_child(dname))
        for fname in dnode.iter_names():
            paths.append(f"/{dname}/{fname}")

    # ---------- write latency ----------
    write_times = []
    tracemalloc.start()
    for _ in range(n_ops):
        p = random.choice(paths)
        t0 = time.perf_counter()
        vfs.write(p, b"x" * 128)
        write_times.append((time.perf_counter() - t0) * 1e6)
    _, peak_write = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # ---------- delete latency ----------
    # rebuild fresh VFS to avoid deleting from the already-mutated one
    tracemalloc.start()
    vfs2 = VFS()
    populate(vfs2, n_dirs, n_files)
    delete_times = []
    # delete up to as many files as exist
    delete_count = min(n_ops, len(paths))
    # one-by-one random deletes
    for _ in range(delete_count):
        idx = random.randrange(len(paths))
        p = paths.pop(idx)
        t0 = time.perf_counter()
        vfs2.rm(p)
        delete_times.append((time.perf_counter() - t0) * 1e6)
    _, peak_delete = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "dirs": n_dirs,
        "files/dir": n_files,
        "objects": n_dirs * n_files,
        "pop_peak_MB": peak_pop / 1024**2,
        "p50_write_µs": stat.median(write_times),
        "p95_write_µs": stat.quantiles(write_times, n=20)[18],
        "write_peak_MB": peak_write / 1024**2,
        "p50_del_µs": stat.median(delete_times),
        "p95_del_µs": stat.quantiles(delete_times, n=20)[18],
        "del_peak_MB": peak_delete / 1024**2,
    }

if __name__ == "__main__":
    configs = [(20, 200), (100, 1000), (300, 2000)]
    results = []
    for cfg in tqdm(configs, desc="Scaling configs"):
        results.append(benchmark(cfg))
    df = pd.DataFrame(results)

    # print table
    print(df.to_string(index=False, float_format="{:0.2f}".format))

    # plot latencies
    plt.figure(figsize=(6,4))
    plt.plot(df["objects"], df["p50_write_µs"], marker="o", label="p50 write")
    plt.plot(df["objects"], df["p95_write_µs"], marker="o", label="p95 write")
    plt.plot(df["objects"], df["p50_del_µs"],  marker="s", label="p50 delete")
    plt.plot(df["objects"], df["p95_del_µs"],  marker="s", label="p95 delete")
    plt.xscale("log")
    plt.xlabel("Total files")
    plt.ylabel("Latency (µs)")
    plt.title("Write & Delete latency vs directory size")
    plt.legend()
    plt.tight_layout()
    out_png = "write_delete_latency.png"
    plt.savefig(out_png, dpi=150)
    print(f"\nPlot saved → {out_png}")

