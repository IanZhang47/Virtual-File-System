# Virtual File-System Prototype

A minimal in-memory file system in Python. It mirrors core OS concepts—hierarchical directories, inodes, metadata—and lets you experiment with different directory-index strategies and measure their impact on lookup, write, and delete performance at scale.

## Features

- **Core operations**: `mkdir`, `touch`, `write`, `read`, `ls`, `rm`  
- **Persistent state**: gzip-pickled snapshot (`.vfs_state.pkl.gz` by default)  
- **CLI & REPL**: one-shot commands or interactive shell via `vfs`  
- **Index options**: hand-rolled B-tree vs. `bintrees.RBTree`  
- **Benchmarks**:
  - `fs-bench` (read-latency harness)  
  - `bench-fs` (write/delete + memory usage)  
  - `compare-trees` (B-tree vs. RB-tree insert/lookup)

## Installation

```bash
git clone <repo-url> filesystem-prototype
cd filesystem-prototype

python3 -m venv .venv
source .venv/bin/activate       # on Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
````

## Console-Scripts

After installation you get these commands in your venv’s `bin/`:

| Command         | What it does                                                    |
| --------------- | --------------------------------------------------------------- |
| `vfs`           | FS operations & REPL (`vfs mkdir …`, `vfs repl`)                |
| `fs-bench`      | Built-in read-latency benchmark (`fs.bench:main`)               |
| `bench-fs`      | Write/delete & memory-usage benchmark (`scripts.bench_fs:main`) |
| `compare-trees` | Compare B-tree vs. RB-tree (`scripts.compare_trees:main`)       |

### Examples

```bash
vfs mkdir /docs
vfs write /docs/hello.txt "Hello, FS!"
vfs ls /docs
vfs read /docs/hello.txt
vfs rm /docs/hello.txt

fs-bench --dirs 100 --files 1000 --ops 20000

bench-fs

compare-trees
```

## Project Structure

```
filesystem-prototype/
├─ fs/                        # core package
│   ├─ index/
│   │   ├─ btree.py           # in-memory B-tree
│   │   └─ rbtree.py          # wrapper around bintrees.RBTree
│   ├─ node.py                # Inode, Directory, File
│   ├─ vfs.py                 # mkdir/touch/write/read/ls/rm
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

## Running the Tests

```bash
pytest -q
```

All tests should pass with zero warnings.


This project uses the MIT license. See [LICENSE](LICENSE) for details.

```
```
