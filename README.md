# Virtual File‑System Prototype
````markdown
# Virtual File-System Prototype

A minimal in-memory file system in Python. It mirrors core OS concepts—hierarchical directories, inodes, metadata—and lets you experiment with different directory-index strategies and measure their impact on lookup, write, and delete performance at scale.

## Features

- **Core operations**: `mkdir`, `touch`, `write`, `read`, `ls`, `rm`, `cd`  
- **Persistent state**: gzip-pickled snapshot (`.vfs_state.pkl.gz` by default)  
- **CLI & REPL**: one-shot commands or interactive shell via `vfs repl`  
- **Index options**: hand-rolled B-tree vs. `bintrees.RBTree`  
- **Benchmarks**:
  - `vfs-bench` (read-latency harness)  
  - `bench-fs` (write/delete + memory usage)  
  - `compare-trees` (B-tree vs. RB-tree insert/lookup)

## Installation

```bash
git clone <repo-url> filesystem-prototype
cd filesystem-prototype

python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
````

## Console‐Scripts

After installation, these commands are available in your venv’s `bin/`:

| Command         | Description                                                                        |
| --------------- | ---------------------------------------------------------------------------------- |
| `vfs`           | FS operations (`mkdir`, `touch`, `write`, `read`, `ls`, `rm`, `cd`) and `vfs repl` |
| `fs-bench`      | Built-in read-latency benchmark (`fs.bench:main`)                                  |
| `bench-fs`      | Write/delete & memory-usage benchmark (`scripts.bench_fs:main`)                    |
| `compare-trees` | Compare B-tree vs. RB-tree (`scripts.compare_trees:main`)                          |

---

## Usage

### One-shot commands

```bash
vfs mkdir /docs
vfs write /docs/readme.txt "Hello, FS!"
vfs ls /docs
# → readme.txt
vfs read /docs/readme.txt
# → Hello, FS!
vfs rm /docs/readme.txt
vfs ls /docs
# → (empty)
```

### Interactive REPL

Start a persistent in-memory shell—no need to retype `vfs` each time:

```bash
vfs repl
```

**Example session:**

```text
📂 virtual-fs REPL (cwd=/) — type 'help' or 'quit'
/> help
Commands: mkdir touch write read ls rm cd open repl quit
/> mkdir projects
/> cd projects
/projects> touch demo.txt
/projects> ls
demo.txt
/projects> write demo.txt "Demo FS"
/projects> read demo.txt
Demo FS
/projects> cd /
/> rm /projects/demo.txt    # absolute path still works
/> quit
```

* `help` lists available commands.
* `cd <dir>` changes your current working directory.
* When you exit, the FS state is saved to `.vfs_state.pkl.gz`.

---

## Benchmark Scripts

* **Basic read-latency**

  ```bash
  vfs-bench --dirs 100 --files 1000 --ops 20000
  ```
* **Write/delete + memory**

  ```bash
  bench-fs
  ```
* **Compare tree indexes**

  ```bash
  compare-trees
  ```

Each script prints a table of p50/p95 latencies and peak memory, and saves PNG plots in the working directory.

---

## Project Structure

```
filesystem-prototype/
├─ fs/                        # core package
│   ├─ index/
│   │   ├─ btree.py           # in-memory B-tree
│   │   └─ rbtree.py          # wrapper around bintrees.RBTree
│   ├─ node.py                # Inode, Directory, File
│   ├─ vfs.py                 # mkdir/touch/write/read/ls/rm/cd
│   ├─ persist.py             # snapshot load/save
│   ├─ cli.py                 # console-script entry point
│   └─ bench.py               # built-in read-latency harness
│
├─ scripts/                   # standalone demo & benchmarks
│   ├─ bench_read.py          # quick read-latency demo
│   ├─ bench_fs.py            # full write/delete + memory benchmark
│   └─ compare_trees.py       # B-tree vs. RB-tree comparison
│
├─ tests/                     # pytest suite
│   ├─ test_basic.py
│   ├─ test_vfs_basic.py
│   ├─ test_cli_smoke.py
│   └─ test_dir_scaling.py
│
├─ pyproject.toml             # project metadata & console-scripts
├─ requirements.txt           # pinned dependencies
├─ README.md                  # this file
└─ LICENSE                    # MIT license
```

---

## Running the Tests

```bash
pytest -q
```

All tests should pass with zero warnings.

---

## Contributing

1. Open an issue or discussion with your idea.
2. Fork and create a feature branch.
3. Add tests for new behavior.
4. Submit a pull request.

---

## License

This project uses the MIT license. See [LICENSE](LICENSE) for details.

```
```
