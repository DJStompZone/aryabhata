# tests/test_cli.py
import subprocess
import sys
import os

def test_cli_runs_and_exits_cleanly():
    cmd = [sys.executable, "-m", "aryabhata", "2"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    assert proc.returncode == 0
    assert "Aryabhata square root" in proc.stdout
