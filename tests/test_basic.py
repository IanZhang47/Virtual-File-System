from fs.node import Directory, File
from fs.inode_table import InodeTable

def test_allocate_and_retrieve():
    tbl = InodeTable()
    root_id = tbl.allocate(Directory(id_=-1))
    file_id = tbl.allocate(File(id_=-1, content=b"hello"))

    root = tbl.get(root_id)
    assert root.is_dir

    f = tbl.get(file_id)
    assert not f.is_dir
    assert f.content == b"hello"

