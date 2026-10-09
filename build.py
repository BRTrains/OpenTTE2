import os
import subprocess
import sys
from pathlib import Path

# This project directory
PROJECT_DIR = Path(__file__).resolve().parent
PROJECT_NAME = PROJECT_DIR.name

# BRBuild location: sibling directory by default, overridable with BRBUILD_DIR.
BRBUILD_DIR = Path(os.environ.get("BRBUILD_DIR", PROJECT_DIR.parent / "BRBuild")).expanduser().resolve()

if not BRBUILD_DIR.is_dir():
    raise SystemExit(f"BRBuild directory not found: {BRBUILD_DIR}")

# Forward CLI args (e.g. --log)
forward_args = sys.argv[1:]

environment = {**os.environ, "BRBUILD_DIR": str(BRBUILD_DIR)}

subprocess.run(
    [sys.executable, str(BRBUILD_DIR / "Run.py"), PROJECT_NAME, *forward_args],
    check=True,
    env=environment,
)
