"""
fs.persist
==========

Tiny snapshot helper for the virtual file‑system.
We pickle‑and‑gzip the entire VFS object so every CLI invocation
can share the same state file.

⚠︎  Prototype‑only:
    Pickle is not secure against untrusted files—don’t use this
    format for real user data.
"""

from __future__ import annotations

import gzip
import pickle
from pathlib import Path
from typing import Union

from .vfs import VFS

def load(path: Union[str, Path]) -> VFS:
    """
    Return a VFS instance loaded from *path*, or a fresh one if the file
    doesn’t exist.
    """
    p = Path(path)
    if not p.exists():
        return VFS()

    with gzip.open(p, "rb") as fh:
        return pickle.load(fh)


def save(vfs: VFS, path: Union[str, Path]) -> None:
    """
    Serialize *vfs* to *path*, overwriting the file.
    """
    p = Path(path)
    with gzip.open(p, "wb") as fh:
        pickle.dump(vfs, fh)

