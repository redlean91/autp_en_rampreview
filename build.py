import os
import shutil
import subprocess
from pathlib import Path

# =========================================
# Paths
# =========================================

ROOT = Path(__file__).parent.resolve()

BIN_DIR = ROOT / "bin"
SCRIPT_DIR = BIN_DIR / "script"

README = ROOT / "README.md"

LAZARUS_DIR = ROOT / "src" / "lazarus"
GO_DIR = ROOT / "src" / "go"

# =========================================
# Create folders
# =========================================

SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================
# Copy README
# =========================================

shutil.copyfile(README, BIN_DIR / "ZRamPreview.txt")

# =========================================
# Version info
# =========================================

VERSION = "v0.3rc7"

try:
    GITHASH = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True
    ).strip()
except subprocess.CalledProcessError:
    GITHASH = "unknown"

FULLVERSION = f"{VERSION} ( {GITHASH} )"

print(f"Version: {FULLVERSION}")

# =========================================
# Generate Pascal version file
# =========================================

ver_pas = f"""unit Ver;

{{$mode objfpc}}{{$H+}}
{{$CODEPAGE UTF-8}}

interface

const
  Version = '{FULLVERSION}';

implementation

end.
"""

(LAZARUS_DIR / "ver.pas").write_text(
    ver_pas,
    encoding="utf-8",
    newline="\r\n"
)

# =========================================
# Generate Go version file
# =========================================

ver_go = f'''package main

const version = "{FULLVERSION}"
'''

(GO_DIR / "ver.go").write_text(
    ver_go,
    encoding="utf-8",
    newline="\r\n"
)

# =========================================
# Build Go executable
# =========================================
print("\nBuilding Go executable...")

env = os.environ.copy()
env["GOPATH"] = os.path.expanduser("~/go")
env["GO111MODULE"] = "off"

repo_root = ROOT

result = subprocess.run(
    [
        "go.exe",
        "build",
        "-x",
        "-ldflags=-s",
        "-o",
        str(BIN_DIR / "ZRamPreview.exe"),
        "./src/go"
    ],
    cwd=repo_root,
    env=env
)

if result.returncode != 0:
    raise SystemExit("Go build failed.")

# =========================================
# Build Lazarus projects
# =========================================

LAZBUILD = r"C:\lazarus\lazbuild.exe"

projects = [
    LAZARUS_DIR / "RamPreview.lpi",
    LAZARUS_DIR / "Output.lpi",
    LAZARUS_DIR / "Extram.lpi"
]

for project in projects:
    print(f"\nBuilding {project.name}...")

    result = subprocess.run(
        [
            LAZBUILD,
            "--build-all",
            str(project)
        ]
    )

    if result.returncode != 0:
        raise SystemExit(f"Failed building {project.name}")

# =========================================
# Optional install
# =========================================

"""
AVIUTL = ROOT / "aviutl"

(AVIUTL / "script").mkdir(parents=True, exist_ok=True)

shutil.copy2(BIN_DIR / "ZRamPreview.auf", AVIUTL)
shutil.copy2(BIN_DIR / "ZRamPreview.auo", AVIUTL)
shutil.copy2(BIN_DIR / "ZRamPreview.exe", AVIUTL)
shutil.copy2(BIN_DIR / "script" / "Extram.dll", AVIUTL / "script")
"""

print("\nBuild completed successfully.")
input("Press Enter to exit...")