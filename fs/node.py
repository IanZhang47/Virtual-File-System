from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Iterable
from .index.btree  import BTree
from .index.rbtree import RBTree


@dataclass
class Meta:
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    size: int = 0
    perms: str = "rw"         # simple: "r", "w", "rw"

@dataclass
class Inode:
    id: int
    is_dir: bool
    meta: Meta = field(default_factory=Meta)

class Directory(Inode):
    def __init__(self, id_: int):
        super().__init__(id_, is_dir=True)
        self.children = RBTree()      # key → inode_id  (log‑time index)

    # simple wrappers so vfs.py stays unchanged
    def add_child(self, name: str, inode_id: int):
        self.children[name] = inode_id

    def get_child(self, name: str) -> int:
        return self.children[name]          # raises KeyError if absent

    def del_child(self, name: str):
        del self.children[name]

    def iter_names(self):
        return self.children.keys()         # already sorted

class File(Inode):
    def __init__(self, id_: int, content: bytes | bytearray = b""):
        super().__init__(id_, is_dir=False)
        self.content = bytearray(content)
        self.meta.size = len(self.content)

