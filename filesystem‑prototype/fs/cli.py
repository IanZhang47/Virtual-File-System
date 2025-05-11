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
from pathlib import PurePosixPath

from . import persist
from .exceptions import FSException
from .vfs import VFS

# ---------------------------------------------------------------
# global VFS instance (will be assigned in main() after we know
# which snapshot file to load)
# ---------------------------------------------------------------
vfs: VFS


# ========================= helpers ==============================


def _cmd_mkdir(args):  # noqa: D401
    """mkdir -p style directory creation."""
    vfs.mkdir(args.path)


def _cmd_touch(args):  # noqa: D401
    """Create an empty file."""
    vfs.touch(args.path)


def _cmd_write(args):  # noqa: D401
    """Write data to file (creates file if missing)."""
    data = args.data
    if len(data) >= 2 and data[0] == data[-1] and data[0] in {"'", '"'}:
        data = data[1:-1]
    vfs.write(args.path, data)

def _cmd_read(args):  # noqa: D401
    """Print file contents to stdout."""
    data = vfs.read(args.path)
    try:
        # decode as UTF‑8 if possible, else show raw bytes
        print(data.decode())
    except UnicodeDecodeError:
        print(data)


def _cmd_ls(args):  # noqa: D401
    """List directory contents."""
    for name in vfs.ls(args.path):
        print(name)


def _cmd_repl(_args):  # noqa: D401
    """Very small interactive shell."""
    print("📂 virtual‑fs REPL — type 'help' or 'quit'")
    while True:
        try:
            line = input("vfs> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line in {"quit", "exit"}:
            break
        if line == "help":
            print("Commands: mkdir touch write read ls quit")
            continue

        # naïve split (handles quoted strings)
        argv = shlex.split(line)
        try:
            main(argv, preserve_state=True)  # reuse same VFS instance
        except SystemExit:
            # sub‑parser printed its own error / --help, continue REPL
            pass
        except FSException as e:
            print("Error:", e)


# ========================= argparse plumbing ====================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Virtual File‑System CLI")
    parser.add_argument(
        "-s",
        "--state",
        default=".vfs_state.pkl.gz",
        help="Path to snapshot file (default: .vfs_state.pkl.gz)",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # mkdir
    p = sub.add_parser("mkdir", help="Create directory (mkdir -p)")
    p.add_argument("path", type=str)
    p.set_defaults(func=_cmd_mkdir)

    # touch
    p = sub.add_parser("touch", help="Create empty file")
    p.add_argument("path")
    p.set_defaults(func=_cmd_touch)

    # write
    p = sub.add_parser("write", help="Write text/bytes to file")
    p.add_argument("path")
    p.add_argument("data")
    p.set_defaults(func=_cmd_write)

    # read
    p = sub.add_parser("read", help="Print file contents")
    p.add_argument("path")
    p.set_defaults(func=_cmd_read)

    # ls
    p = sub.add_parser("ls", help="List directory contents")
    p.add_argument("path", nargs="?", default="/")
    p.set_defaults(func=_cmd_ls)

    # repl
    p = sub.add_parser("repl", help="Start interactive shell")
    p.set_defaults(func=_cmd_repl)

    return parser


# ========================= entry point ==========================


def main(argv: list[str] | None = None, *, preserve_state: bool = False):
    """
    Parse CLI args, load snapshot, run command, save snapshot.

    Parameters
    ----------
    argv
        The arg list *after* the program name (like sys.argv[1:]).
    preserve_state
        True when invoked from the REPL so we don't re‑load/overwrite
        the global `vfs` each sub‑command; we want the same instance.
    """
    global vfs 

    parser = build_parser()
    args = parser.parse_args(argv)

    # ------------------------------------------------------------------
    # Load or re‑use VFS
    # ------------------------------------------------------------------
    if not preserve_state:
        vfs = persist.load(args.state)

    # ------------------------------------------------------------------
    # Execute the selected sub‑command
    # ------------------------------------------------------------------
    try:
        args.func(args)
    except FSException as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Persist snapshot unless we're inside an interactive REPL call
    # ------------------------------------------------------------------
    if not preserve_state:
        persist.save(vfs, args.state)


if __name__ == "__main__":
    main()

