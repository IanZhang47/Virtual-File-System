"""
fs.index.rbtree

Thin wrapper around bintrees.RBTree so we import it from our package.
"""
from bintrees import RBTree as _RBTree

class RBTree(_RBTree):
    """Red-black tree mapping keys→values."""
    pass

