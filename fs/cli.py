"""
fs.cli
======

Command‑line wrapper for the in‑memory virtual file‑system.

Examples
--------
# one‑shot commands ---------------------------------------------
python -m fs.cli mkdir /docs
python -m fs.cli write /docs/hello.txt "hi"
python -m fs.cli ls /docs
python -m fs.cli read /docs/hello.txt

# share a custom snapshot
python -m fs.cli -s my_state.gz mkdir /tmp

# interactive REPL ----------------------------------------------
python -m fs.cli repl
vfs> mkdir /foo
vfs> write /foo/a.txt hello
vfs> read  /foo/a.txt
hello
vfs> quit
"""

from __future__ import annotations

import argparse
import shlex
import sys
import subprocess
from pathlib import PurePosixPath

from . import persist
from .exceptions import FSException, FileNotFound, NotDirectory
from .vfs import VFS

# -------------------------------------------------------------------
# Global VFS instance + current working directory
# -------------------------------------------------------------------
vfs: VFS
cwd = "/"


def _resolve(path: str) -> str:
    """Resolve a user‐entered path against the current working directory."""
    p = PurePosixPath(path)
    if p.is_absolute():
        return str(p)
    return str(PurePosixPath(cwd) / path)


# ====================== command handlers ===========================

def _cmd_mkdir(args):
    vfs.mkdir(_resolve(args.path))


def _cmd_touch(args):
    vfs.touch(_resolve(args.path))


def _cmd_write(args):
    data = args.data
    if len(data) >= 2 and data[0] == data[-1] and data[0] in {"'", '"'}:
        data = data[1:-1]
    vfs.write(_resolve(args.path), data)


def _cmd_read(args):
    out = vfs.read(_resolve(args.path))
    try:
        print(out.decode())
    except UnicodeDecodeError:
        print(out)


def _cmd_ls(args):
    target = args.path or cwd
    for name in vfs.ls(_resolve(target)):
        print(name)


def _cmd_rm(args):
    vfs.rm(_resolve(args.path))


def _cmd_cd(args):
    global cwd
    newdir = _resolve(args.path)
    # verify it’s a directory
    try:
        vfs.ls(newdir)
    except FSException as e:
        print(f"cd: {e}", file=sys.stderr)
        sys.exit(1)
    cwd = newdir.rstrip("/") or "/"


def _cmd_open(args):
    subprocess.run(["xdg-open", args.path], check=False)


def _cmd_repl(_args):
    print(f"📂 virtual-fs REPL (cwd={cwd}) — type 'help' or 'quit'")
    while True:
        try:
            line = input(f"{cwd}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line in {"quit", "exit"}:
            break
        if line == "help":
            print("Commands: mkdir touch write read ls rm cd open repl quit")
            continue
        argv = shlex.split(line)
        try:
            main(argv, preserve_state=True)
        except FSException as e:
            print("Error:", e)
        except SystemExit:
            pass


# ====================== argument parser ============================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Virtual File-System CLI")
    parser.add_argument(
        "-s", "--state",
        default=".vfs_state.pkl.gz",
        help="Path to snapshot file (default: .vfs_state.pkl.gz)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("mkdir", help="Create directory (mkdir -p)")
    p.add_argument("path")
    p.set_defaults(func=_cmd_mkdir)

    p = sub.add_parser("touch", help="Create empty file")
    p.add_argument("path")
    p.set_defaults(func=_cmd_touch)

    p = sub.add_parser("write", help="Write to file (creates if missing)")
    p.add_argument("path")
    p.add_argument("data")
    p.set_defaults(func=_cmd_write)

    p = sub.add_parser("read", help="Read file contents")
    p.add_argument("path")
    p.set_defaults(func=_cmd_read)

    p = sub.add_parser("ls", help="List directory contents")
    p.add_argument("path", nargs="?", default="")
    p.set_defaults(func=_cmd_ls)

    p = sub.add_parser("rm", help="Remove file or empty directory")
    p.add_argument("path")
    p.set_defaults(func=_cmd_rm)

    p = sub.add_parser("cd", help="Change current directory")
    p.add_argument("path")
    p.set_defaults(func=_cmd_cd)

    p = sub.add_parser("open", help="Open file with default application")
    p.add_argument("path")
    p.set_defaults(func=_cmd_open)

    p = sub.add_parser("repl", help="Start interactive shell")
    p.set_defaults(func=_cmd_repl)

    return parser


# ====================== entry point ================================

def main(argv: list[str] | None = None, *, preserve_state: bool = False):
    global vfs, cwd
    parser = build_parser()
    args = parser.parse_args(argv)

    if not preserve_state:
        vfs = persist.load(args.state)

    try:
        args.func(args)
    except FSException as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

    if not preserve_state:
        persist.save(vfs, args.state)


if __name__ == "__main__":
    main()
