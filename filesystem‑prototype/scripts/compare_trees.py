#!/usr/bin/env python3
"""
compare_trees.py

Compare insertion & lookup performance + memory usage for:
  • fs.btree.BTree       (order=64)
  • bintrees.RBTree      (red-black tree)

Usage:
    pip install bintrees pandas matplotlib tqdm
    chmod +x compare_trees.py
    ./compare_trees.py
"""

import random
import string
import time
import tracemalloc
import statistics as stat

import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from fs.index.btree  import BTree
from fs.index.rbtree import RBTree

# -- CONFIGURATION ----------------------------------------------------------
SCALES = [10_000, 50_000, 100_000]   # number of keys to insert
LOOKUPS = 5_000                      # number of random lookups per tree
KEY_LEN = 8                          # length of each random key
# ----------------------------------------------------------------------------

def make_keys(n):
    """Generate n distinct random string keys."""
    rnd = random.Random(42)
    chars = string.ascii_lowercase + string.digits
    keys = set()
    while len(keys) < n:
        keys.add("".join(rnd.choices(chars, k=KEY_LEN)))
    return list(keys)

def bench_tree(TreeClass, keys, lookups):
    """
    Inserts all keys into TreeClass, measures:
      • insert_time (median & p95 in µs)
      • insert_mem_peak (MB)
    Then:
      • lookup_time (median & p95 in µs) over only successfully inserted keys
      • lookup_mem_peak (MB)
    """
    # ------- insertion -------
    insert_times = []
    tracemalloc.start()
    tree = TreeClass()
    for k in keys:
        t0 = time.perf_counter()
        if isinstance(tree, BTree):
            tree.insert(k, 0)
        else:
            tree[k] = 0
        insert_times.append((time.perf_counter() - t0)*1e6)
    _, peak_ins = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # ------- determine which keys actually got stored -------
    available = []
    for k in keys:
        try:
            # BTree.get / RBTree.__getitem__
            _ = tree.get(k) if isinstance(tree, BTree) else tree[k]
            available.append(k)
        except KeyError:
            pass
    dropped = len(keys) - len(available)
    if dropped:
        print(f"    ⚠️  {TreeClass.__name__} dropped {dropped} keys during splits")

    # ------- lookup -------
    lookup_times = []
    tracemalloc.start()
    for _ in range(lookups):
        k = random.choice(available)
        t0 = time.perf_counter()
        _ = tree.get(k) if isinstance(tree, BTree) else tree[k]
        lookup_times.append((time.perf_counter() - t0)*1e6)
    _, peak_lu = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "impl": TreeClass.__name__,
        "n_keys": len(keys),
        "insert_p50_µs": stat.median(insert_times),
        "insert_p95_µs": stat.quantiles(insert_times, n=20)[18],
        "insert_peak_MB": peak_ins / 1024**2,
        "lookup_p50_µs": stat.median(lookup_times),
        "lookup_p95_µs": stat.quantiles(lookup_times, n=20)[18],
        "lookup_peak_MB": peak_lu / 1024**2,
    }

def main():
    random.seed(0)
    results = []

    for n in SCALES:
        print(f"\n>>> Benchmarking with {n:,} keys …")
        keys = make_keys(n)
        for TreeClass in (BTree, RBTree):
            print(f"  • {TreeClass.__name__} …", end="", flush=True)
            res = bench_tree(TreeClass, keys, LOOKUPS)
            results.append(res)
            print(" done")

    # --- tabulate ---
    df = pd.DataFrame(results)
    print("\n" + df.to_string(index=False, float_format="{:0.2f}".format))

    # --- plotting insert times ---
    plt.figure(figsize=(6,4))
    for impl in df['impl'].unique():
        sub = df[df['impl'] == impl]
        plt.plot(sub['n_keys'], sub['insert_p50_µs'], marker="o", label=f"{impl} insert")

    plt.xscale("log"); plt.yscale("log")
    plt.xlabel("number of keys"); plt.ylabel("median insert latency (µs)")
    plt.title("Insert latency: BTree vs. RBTree")
    plt.legend(); plt.tight_layout()
    plt.savefig("compare_insert_latency.png")

    # --- plotting lookup times ---
    plt.figure(figsize=(6,4))
    for impl in df['impl'].unique():
        sub = df[df['impl'] == impl]
        plt.plot(sub['n_keys'], sub['lookup_p50_µs'], marker="s", label=f"{impl} lookup")
    plt.xscale("log"); plt.yscale("log")
    plt.xlabel("number of keys"); plt.ylabel("median lookup latency (µs)")
    plt.title("Lookup latency: BTree vs. RBTree")
    plt.legend(); plt.tight_layout()
    plt.savefig("compare_lookup_latency.png")

    print("\nPlots saved → compare_insert_latency.png, compare_lookup_latency.png")

if __name__ == "__main__":
    main()

