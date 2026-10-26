#!/usr/bin/env python3
"""Offline reproduction from bundled EIA source bytes through fixed outputs."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

root = Path(__file__).resolve().parent
env = dict(os.environ, OPENBLAS_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
commands = [
    [sys.executable, str(root / "inputs/scripts/build_panel.py")],
    [sys.executable, str(root / "inputs/scripts/verify_panel.py")],
    [sys.executable, str(root / "analysis/run_analysis.py"), "--self-test"],
    [sys.executable, str(root / "analysis/run_analysis.py"), "--reproduce"],
]
for command in commands:
    subprocess.run(command, cwd=root, env=env, check=True)
reference = json.loads((root / "reference_checksums.json").read_text(encoding="utf-8"))
for relative, expected in reference.items():
    actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"Reference checksum mismatch: {relative}; {actual} != {expected}")
subprocess.run([sys.executable, str(root / "figures/plot_figures.py")], cwd=root, env=env, check=True)
print("PASS: raw EIA inputs, complete panel, all six fixed result CSVs and scientific figures reproduced offline.")
print("This command does not reproduce the separate California synthetic-control benchmark.")
