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
git clone https://github.com/IanZhang47/Virtual-File-System.git
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

### Examples

```bash
vfs mkdir /docs
vfs write /docs/hello.txt "Hello, FS!"
vfs ls /docs
vfs read /docs/hello.txt
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

