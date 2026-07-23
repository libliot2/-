#!/usr/bin/env python3
"""Promote the validated final synthesis report to the canonical report alias."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs/final/final_research_report.md"
TARGET = ROOT / "outputs/reports/final_report.md"


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    TARGET.write_bytes(SOURCE.read_bytes())
    print("promoted outputs/final/final_research_report.md -> outputs/reports/final_report.md")


if __name__ == "__main__":
    main()
