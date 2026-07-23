#!/usr/bin/env python3
"""Regenerate canonical outputs and verify byte-for-byte reproducibility."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pandas as pd

from pipeline_common import ROOT


COMMANDS = [
    ["python3", "scripts/prepare_data.py"],
    ["python3", "scripts/analyze_survey.py"],
    ["python3", "scripts/build_linked_profiles.py"],
    ["python3", "scripts/prepare_interviews.py"],
    ["python3", "scripts/promote_qualitative_synthesis.py"],
    ["python3", "scripts/promote_mixed_methods.py"],
    ["python3", "scripts/write_literature_comparison.py"],
    ["python3", "scripts/write_main_report.py", "--final"],
]

STATIC_TARGETS = [
    "data/processed/survey_codebook.csv",
    "data/processed/survey_clean.csv",
    "data/processed/interview_survey_map.csv",
    "data/processed/survey_construct_scores.csv",
    "data/processed/qualitative_codebook.csv",
    "outputs/tables/sample_flow.csv",
    "outputs/tables/sample_characteristics.csv",
    "outputs/tables/survey_item_statistics.csv",
    "outputs/tables/support_gap_analysis.csv",
    "outputs/tables/platform_transition_analysis.csv",
    "outputs/tables/exploratory_constructs.csv",
    "outputs/tables/exploratory_associations.csv",
    "outputs/tables/joint_display.csv",
    "outputs/qualitative/framework_matrix.csv",
    "outputs/qualitative/coded_segments_master.csv",
    "outputs/reports/survey_findings.md",
    "outputs/reports/cross_case_analysis.md",
    "outputs/reports/integrated_findings.md",
    "outputs/reports/literature_comparison.md",
    "outputs/reports/final_report.md",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_names() -> list[str]:
    dynamic = [
        path.relative_to(ROOT).as_posix()
        for pattern in ["data/processed/linked_cases/*.md", "data/processed/interviews/*.md"]
        for path in sorted(ROOT.glob(pattern))
    ]
    return STATIC_TARGETS + dynamic


def snapshot(names: list[str]) -> dict[str, str]:
    missing = [name for name in names if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing reproducibility targets: {missing}")
    return {name: digest(ROOT / name) for name in names}


def main() -> None:
    names = target_names()
    before = snapshot(names)
    for command in COMMANDS:
        subprocess.run(command, cwd=ROOT, check=True)
    if target_names() != names:
        raise RuntimeError("Dynamic reproducibility target set changed during regeneration")
    after = snapshot(names)
    rows = [
        {
            "relative_path": name,
            "status": "PASS" if before[name] == after[name] else "FAIL",
            "hash_before": before[name],
            "hash_after": after[name],
        }
        for name in names
    ]
    result = pd.DataFrame(rows)
    output = ROOT / "outputs/reports/reproducibility_results.csv"
    result.to_csv(output, index=False, encoding="utf-8-sig")
    failures = result[result["status"] == "FAIL"]
    print(f"reproducibility checked={len(result)} failures={len(failures)}")
    if not failures.empty:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
