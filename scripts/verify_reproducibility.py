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
    ["python3", "scripts/prepare_open_text_v5.py"],
    ["python3", "scripts/build_open_text_context_v5.py"],
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
    ["python3", "scripts/explore_theory_configurations_v3.py"],
    ["python3", "scripts/validate_round3.py"],
    ["python3", "scripts/integrate_open_text_v5.py"],
    ["python3", "scripts/resolve_open_text_review_v5.py"],
    ["python3", "scripts/promote_final_delivery.py"],
    ["python3", "scripts/validate_final_delivery.py"],
    ["python3", "scripts/validate_open_text_v5.py"],
]

TARGET_MODES = {
    "data/processed/survey_codebook.csv": "REGENERATED",
    "data/processed/survey_clean.csv": "REGENERATED",
    "data/processed/interview_survey_map.csv": "REGENERATED",
    "data/processed/survey_construct_scores.csv": "REGENERATED",
    "data/processed/qualitative_codebook.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "data/processed/survey_open_text_corpus.csv": "REGENERATED_RESTRICTED",
    "data/processed/open_text_codebook.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
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
    "outputs/reports/final_report.md": "REGENERATED_FROM_FINAL_DELIVERY",
    "outputs/reports/agent_run_manifest.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/quantitative_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/qualitative_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/integration_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/reproducibility_privacy_audit_v2.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/agent_runs/20260723_multi_theory_abductive_v3/synthesis/construct_quantiles_v3.csv": "REGENERATED",
    "outputs/agent_runs/20260723_multi_theory_abductive_v3/synthesis/anomaly_configurations_v3.csv": "REGENERATED",
    "outputs/agent_runs/20260723_multi_theory_abductive_v3/synthesis/anomaly_counts_public_v3.csv": "REGENERATED",
    "outputs/agent_runs/20260723_multi_theory_abductive_v3/synthesis/open_text_prompt_pattern_audit_v3.csv": "REGENERATED",
    "outputs/theory/framework_inventory_v3.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/theory/cross_framework_matrix_v3.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/tables/mechanism_propositions_v3.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/tables/open_text_theme_summary.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/open_text/open_text_analysis_plan.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/open_text/shared_schema_v5.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/open_text/coding_reconciliation.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/open_text/q81_critical_incident_analysis.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/open_text/q82_support_needs_analysis.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/open_text/open_text_coded_responses.csv": "FROZEN_ANALYTIC_INPUT_RESTRICTED",
    "outputs/open_text/open_closed_alignment.csv": "FROZEN_ANALYTIC_INPUT_RESTRICTED",
    "outputs/open_text/open_text_interview_alignment.csv": "FROZEN_ANALYTIC_INPUT_RESTRICTED",
    "outputs/agent_runs/20260724_open_text_v5/integration_inputs/open_closed_context.csv": "REGENERATED_RESTRICTED",
    "outputs/reports/open_closed_integration.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/open_text_linked_case_analysis.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/open_text_qualitative_synthesis.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/open_text_validation_report.md": "REGENERATED",
    "outputs/reports/open_text_pipeline_summary.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/open_text_evidence_audit.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/open_text_method_audit.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/open_text/open_text_revision_log.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/theoretical_exploration_plan_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/framework_notes_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/cross_framework_synthesis_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/abductive_exploration_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/proposed_analytical_framework_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/theoretical_extension_report_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/final_report_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/pipeline_summary_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reports/validation_report_v3.md": "REGENERATED",
    "outputs/reports/theoretical_revision_log_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/theoretical_fit_audit_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/reviews/multi_perspective_evidence_audit_v3.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_synthesis_plan.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/findings_register.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/version_reconciliation.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/evidence_hierarchy.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_analytical_framework.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_research_report.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/executive_summary.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/key_findings_one_page.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/research_question_evidence_matrix.csv": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/methods_and_audit_summary.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/artifact_index.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_evidence_audit.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_editorial_review.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_review_resolution.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_project_summary.md": "FROZEN_ANALYTIC_INPUT_PROMOTED",
    "outputs/final/final_validation_report.md": "REGENERATED",
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
