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
    ["python3", "scripts/revise_qualitative_v2.py"],
    ["python3", "scripts/exploratory_extension_v2.py"],
    ["python3", "scripts/write_literature_comparison.py"],
    ["python3", "scripts/write_round2_reports.py"],
    ["python3", "scripts/write_main_report.py", "--final"],
]

TARGET_MODES = {
    "data/processed/survey_codebook.csv": "REGENERATED",
    "data/processed/survey_clean.csv": "REGENERATED",
    "data/processed/interview_survey_map.csv": "REGENERATED",
    "data/processed/survey_construct_scores.csv": "REGENERATED",
    "data/processed/qualitative_codebook.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/tables/sample_flow.csv": "REGENERATED",
    "outputs/tables/missingness_by_item.csv": "REGENERATED",
    "outputs/tables/sample_characteristics.csv": "REGENERATED",
    "outputs/tables/survey_item_statistics.csv": "REGENERATED",
    "outputs/tables/support_gap_analysis.csv": "REGENERATED",
    "outputs/tables/platform_transition_analysis.csv": "REGENERATED",
    "outputs/tables/exploratory_constructs.csv": "REGENERATED",
    "outputs/tables/exploratory_associations.csv": "REGENERATED",
    "outputs/tables/survey_open_text_summary.csv": "REGENERATED",
    "outputs/tables/exploratory_extension_v2.csv": "REGENERATED",
    "outputs/tables/joint_display.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/qualitative/framework_matrix.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/qualitative/coded_segments_master.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/repository_inventory.md": "REGENERATED",
    "outputs/reports/survey_mapping_report.md": "REGENERATED",
    "outputs/reports/data_quality_report.md": "REGENERATED",
    "outputs/reports/linkage_report.md": "REGENERATED",
    "outputs/reports/sample_description.md": "REGENERATED",
    "outputs/reports/construct_assessment.md": "REGENERATED",
    "outputs/reports/survey_findings.md": "REGENERATED",
    "outputs/reports/exploratory_analysis.md": "REGENERATED",
    "outputs/reports/transcript_preparation_report.md": "REGENERATED",
    "outputs/reports/transcript_preparation_details.csv": "REGENERATED",
    "outputs/reports/cross_case_analysis.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/integrated_findings.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/literature_comparison.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/exploratory_extension_v2.md": "REGENERATED",
    "outputs/reports/revision_log_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/final_report_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/final_report.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/agent_run_manifest.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/quantitative_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/qualitative_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/integration_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/reproducibility_privacy_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_names() -> list[str]:
    dynamic = [
        path.relative_to(ROOT).as_posix()
        for pattern in ["data/processed/linked_cases/*.md", "data/processed/interviews/*.md"]
        for path in sorted(ROOT.glob(pattern))
    ]
    return list(TARGET_MODES) + dynamic


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
            "target_mode": TARGET_MODES.get(name, "REGENERATED"),
            "status": "PASS" if before[name] == after[name] else "FAIL",
            "hash_before": before[name],
            "hash_after": after[name],
        }
        for name in names
    ]
    result = pd.DataFrame(rows)
    output = ROOT / "outputs/reports/reproducibility_results_v2.csv"
    result.to_csv(output, index=False, encoding="utf-8-sig")
    failures = result[result["status"] == "FAIL"]
    print(f"reproducibility checked={len(result)} failures={len(failures)}")
    if not failures.empty:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
