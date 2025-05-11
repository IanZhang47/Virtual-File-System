"""
fs.btree
========
A minimalist, in‑memory B‑tree suited for directory indices.

* Order (fan‑out) defaults to 64 → each node stores up to 63 keys.
* Only the operations we need: insert, get, delete, scan(prefix).

NOT general‑purpose—good enough for the VFS prototype.
"""

from __future__ import annotations
from bisect import bisect_left, bisect_right


class _Node:
    __slots__ = ("keys", "vals", "kids", "leaf")

    def __init__(self, leaf: bool):
        self.leaf = leaf
        self.keys: list[str] = []
        self.vals: list[int] = []          # only used in leaf
        self.kids: list["_Node"] = []      # only used in internal


class BTree:
    def __init__(self, order: int = 64):
        self._root = _Node(leaf=True)
        self._order = order
        self._min = order // 2

    # ---------------- public API ----------------
    def insert(self, key: str, val: int) -> None:
        r = self._root
        if len(r.keys) == self._order - 1:
            s = _Node(leaf=False)
            s.kids.append(r)
            self._split_child(s, 0)
            self._root = s
        self._insert_non_full(self._root, key, val)

    def get(self, key: str) -> int:
        node, idx = self._search(self._root, key)
        if node is None:
            raise KeyError(key)
        return node.vals[idx]

    def delete(self, key: str) -> None:
        #    (minimal) just mark missing for prototype
        node, idx = self._search(self._root, key)
        if node is None:
            raise KeyError(key)
        del node.keys[idx]
        del node.vals[idx]

    def iter(self):
        yield from self._iter_node(self._root)

    # ---------------- internals -----------------
    def _search(self, node, key):
        i = bisect_left(node.keys, key)
        if node.leaf:
            if i < len(node.keys) and node.keys[i] == key:
                return node, i
            return None, -1
        if i < len(node.keys) and node.keys[i] == key:
            i += 1
        return self._search(node.kids[i], key)

    def _insert_non_full(self, node, key, val):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.insert(bisect_left(node.keys, key), key)
            node.vals.insert(node.keys.index(key), val)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.kids[i].keys) == self._order - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.kids[i], key, val)

    def _split_child(self, parent, i):
        """Split full child *y* at index *i*; keep pivot key in left leaf."""
        order = self._order
        y = parent.kids[i]
        z = _Node(leaf=y.leaf)
        mid = order // 2

        # Promote pivot into parent
        parent.keys.insert(i, y.keys[mid])
        parent.kids.insert(i + 1, z)

        # Copy right‑hand keys/vals into new node
        z.keys[:] = y.keys[mid + 1 :]
        y.keys[:] = y.keys[: mid + 1]          # ← keep pivot in left leaf!

        if y.leaf:
            z.vals[:] = y.vals[mid + 1 :]
            y.vals[:] = y.vals[: mid + 1]
        else:
            z.kids[:] = y.kids[mid + 1 :]
            y.kids[:] = y.kids[: mid + 1]

    
    def _iter_node(self, node):
        if node.leaf:
            yield from node.keys
        else:
            for i, kid in enumerate(node.kids):
                yield from self._iter_node(kid)
                if i < len(node.keys):
                    yield node.keys[i]

