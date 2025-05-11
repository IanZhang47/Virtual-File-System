"""
fs.vfs
======

High‑level virtual file‑system façade.
Implements mkdir/touch/write/read/ls on top of:

* InodeTable  – global registry (id → Inode)
* Directory   – now backed by an in‑memory B‑tree index
* File        – keeps raw bytes in RAM

All paths must be absolute (begin with “/”).
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Iterable

from .exceptions import FileExists, FileNotFound, FSException, NotDirectory
from .inode_table import InodeTable
from .node import Directory, File


class VFS:
    """A minimal, single‑user, in‑memory virtual FS."""

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------
    def __init__(self):
        self.table = InodeTable()
        self.root_id = self.table.allocate(Directory(id_=-1))

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _split_path(self, path: str) -> tuple[int, str]:
        """
        Return (parent_inode_id, final_name).

        Creates intermediate directories if `create_missing` is True.
        """
        p = PurePosixPath(path)
        if not p.is_absolute():
            raise FSException("path must start with '/'")

        parts = p.parts[1:]  # skip root
        cur_id = self.root_id
        for seg in parts[:-1]:
            cur_dir = self.table.get(cur_id)
            if not isinstance(cur_dir, Directory):
                raise NotDirectory(seg)

            # walk or mkdir -p
            try:
                cur_id = cur_dir.get_child(seg)
            except KeyError:
                # auto‑create
                new_id = self.table.allocate(Directory(id_=-1))
                cur_dir.add_child(seg, new_id)
                cur_id = new_id

        return cur_id, parts[-1] if parts else ""

    def _assert_dir(self, inode_id: int, ctx: str = "") -> Directory:
        node = self.table.get(inode_id)
        if not isinstance(node, Directory):
            raise NotDirectory(ctx or "")
        return node

    def mkdir(self, path: str):
        parent_id, name = self._split_path(path)
        parent = self._assert_dir(parent_id, path)
        try:
            parent.get_child(name)
            raise FileExists(name)
        except KeyError:
            new_id = self.table.allocate(Directory(id_=-1))
            parent.add_child(name, new_id)

    def touch(self, path: str):
        parent_id, name = self._split_path(path)
        parent = self._assert_dir(parent_id, path)
        try:
            parent.get_child(name)
            raise FileExists(name)
        except KeyError:
            new_id = self.table.allocate(File(id_=-1))
            parent.add_child(name, new_id)

    def write(self, path: str, data: bytes | str):
        if isinstance(data, str):
            data = data.encode()

        parent_id, name = self._split_path(path)
        parent = self._assert_dir(parent_id, path)

        try:
            inode_id = parent.get_child(name)
            node = self.table.get(inode_id)
            if not isinstance(node, File):
                raise NotDirectory(name)
            node.content[:] = data
            node.meta.size = len(data)
        except KeyError:
            new_id = self.table.allocate(File(id_=-1, content=data))
            parent.add_child(name, new_id)

    def read(self, path: str) -> bytes:
        parent_id, name = self._split_path(path)
        parent = self._assert_dir(parent_id, path)
        try:
            inode_id = parent.get_child(name)
        except KeyError:
            raise FileNotFound(name) from None
        node = self.table.get(inode_id)
        if not isinstance(node, File):
            raise NotDirectory(name)
        return bytes(node.content)

    def ls(self, path: str = "/") -> list[str]:
        if path == "/":
            dir_node = self._assert_dir(self.root_id, "/")
        else:
            parent_id, name = self._split_path(path)
            dir_node = self._assert_dir(
                self.table.get(parent_id).get_child(name), path
            )
        return list(dir_node.iter_names())

    def rm(self, path: str):
        """
        Remove a file or empty directory at `path`.
        """
        parent_id, name = self._split_path(path)
        parent = self._assert_dir(parent_id, path)

        try:
            inode_id = parent.get_child(name)
        except KeyError:
            raise FileNotFound(name)

        parent.del_child(name)

