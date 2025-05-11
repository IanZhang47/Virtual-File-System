from fs.vfs import VFS

def test_mkdir_touch_write_read_ls():
    vfs = VFS()
    vfs.mkdir("/docs")
    vfs.touch("/docs/hello.txt")
    vfs.write("/docs/hello.txt", "hi")
    assert vfs.read("/docs/hello.txt") == b"hi"
    assert vfs.ls("/") == ["docs"]
    assert vfs.ls("/docs") == ["hello.txt"]

