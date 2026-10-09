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

result = subprocess.run(
    [sys.executable, str(BRBUILD_DIR / "Run.py"), PROJECT_NAME, *forward_args],
    env=environment,
)

if result.returncode != 0:
    raise SystemExit(result.returncode)

# The purchase list names the item symbols the build produced, so it is rebuilt from them once
# the build has succeeded: the file in the repository is then always the build's own item set,
# with each entry in the group the project's rules put it in.
subprocess.run(
    [sys.executable, str(PROJECT_DIR / "tools" / "generate_sortpurchase.py")],
    check=True,
)
