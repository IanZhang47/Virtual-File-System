import subprocess, sys, os

def run(state, cmd: str) -> str:
    proc = subprocess.run(
        [sys.executable, "-m", "fs.cli", "-s", state, *cmd.split()],
        check=True,
        stdout=subprocess.PIPE,
    )
    return proc.stdout.decode().strip()

def test_cli_smoke(tmp_path):
    state_file = tmp_path / "vfs.pkl.gz"
    run(str(state_file), "mkdir /a")
    run(str(state_file), 'write /a/x.txt "hi"')
    out = run(str(state_file), "read /a/x.txt")
    assert out == "hi"

