import time, random, statistics as stat, pandas as pd, matplotlib.pyplot as plt
from fs.vfs import VFS                      # uses your in‑repo package
from tqdm import tqdm                      # optional progress bar

random.seed(42)                            # reproducibility

def populate(vfs, n_dirs, n_files):
    """mkdir ‑p and touch a bunch of empty files"""
    for d in range(n_dirs):
        dir_path = f"/dir_{d:04d}"
        vfs.mkdir(dir_path)
        for f in range(n_files):
            vfs.touch(f"{dir_path}/file_{f:05d}.bin")

def run_once(n_dirs, n_files, n_ops=10_000):
    vfs = VFS()
    populate(vfs, n_dirs, n_files)

    # collect all file paths just once
    paths = []
    root = vfs.table.get(vfs.root_id)
    for dir_name in root.iter_names():
        child_dir = vfs.table.get(root.get_child(dir_name))
        for fname in child_dir.iter_names():
            paths.append(f"/{dir_name}/{fname}")

    samples = []
    for _ in range(n_ops):
        p = random.choice(paths)
        t0 = time.perf_counter()
        vfs.read(p)
        samples.append((time.perf_counter() - t0) * 1e6)  # µs

    return {
        "dirs": n_dirs,
        "files/dir": n_files,
        "objects": len(paths),
        "p50 µs": stat.median(samples),
        "p95 µs": stat.quantiles(samples, n=20)[18],
        "mean µs": stat.mean(samples),
    }

configs = [(20, 200), (100, 1000), (300, 2000)]  # tweak as needed
results = [run_once(d, f) for d, f in tqdm(configs)]

df = pd.DataFrame(results)
print(df.to_string(index=False))   # plain‑text table in the terminal

# ─── quick plot ──────────────────────────────────────────────────────────────────
plt.figure(figsize=(6,4))
plt.plot(df["objects"], df["p50 µs"], marker="o", label="median")
plt.plot(df["objects"], df["p95 µs"], marker="s", label="p95")
plt.xlabel("number of files")
plt.ylabel("latency (µs)")
plt.title("Random read latency vs directory size")
plt.xscale("log")
plt.legend()
plt.grid(True)
plt.tight_layout()
out = "latency_vs_size.png"
plt.savefig(out, dpi=150)
print(f"\nLatency plot saved → {out}")

