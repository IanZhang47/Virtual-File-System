class InodeTable:
    def __init__(self) -> None:
        self._next_id = 0
        self._table: dict[int, "Inode"] = {}

    def allocate(self, inode: "Inode") -> int:
        inode.id = self._next_id
        self._table[self._next_id] = inode
        self._next_id += 1
        return inode.id

    def get(self, inode_id: int) -> "Inode":
        return self._table[inode_id]

