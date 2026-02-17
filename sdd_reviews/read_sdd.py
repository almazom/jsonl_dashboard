#!/usr/bin/env python3
"""Read SDD files and output concatenated content for review."""

import os
from pathlib import Path

sdd_dir = Path("/home/pets/temp/jsonl_dashboard/docs/sdd/artifact-nexus-sdd")
trello_dir = sdd_dir / "trello-cards"

files_to_read = [
    "README.md",
    "requirements.md",
    "gaps.md",
    "trello-cards/KICKOFF.md",
    "trello-cards/BOARD.md",
]

print("# Artifact Nexus SDD Package\n")

for f in files_to_read:
    filepath = sdd_dir / f
    if filepath.exists():
        print(f"\n## FILE: {f}\n")
        with open(filepath) as fh:
            print(fh.read())
    else:
        print(f"\n## FILE: {f} NOT FOUND\n")
