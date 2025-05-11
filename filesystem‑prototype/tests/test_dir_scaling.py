from fs.vfs import VFS

def test_dir_scaling():
    vfs = VFS()
    for i in range(10_000):
        vfs.touch(f"/big/f{i:05d}")
    assert vfs.read("/big/f00000") == b""
    assert len(vfs.ls("/big")) == 10_000

