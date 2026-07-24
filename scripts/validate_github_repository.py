#!/usr/bin/env python3
"""Validate the GitHub-safe repository without restricted participant data."""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "LICENSE",
    "LICENSE-MIT",
    "LICENSE-CC-BY-4.0",
    "requirements.txt",
    "CITATION.cff",
    "DATA_AVAILABILITY.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".github/workflows/repository-check.yml",
    "outputs/final/final_research_report.md",
    "outputs/final/executive_summary.md",
    "outputs/final/key_findings_one_page.md",
    "outputs/final/findings_register.csv",
    "outputs/final/research_question_evidence_matrix.csv",
    "outputs/final/final_validation_report.md",
    "outputs/reports/final_report.md",
    "data/processed/open_text_codebook.csv",
    "outputs/open_text/coding_reconciliation.md",
    "outputs/open_text/q81_critical_incident_analysis.md",
    "outputs/open_text/q82_support_needs_analysis.md",
    "outputs/open_text/open_text_revision_log.md",
    "outputs/tables/open_text_theme_summary.csv",
    "outputs/tables/joint_display.csv",
    "outputs/reports/open_text_qualitative_synthesis.md",
    "outputs/reports/open_closed_integration.md",
    "outputs/reports/open_text_linked_case_analysis.md",
    "outputs/reports/open_text_validation_report.md",
    "outputs/reports/open_text_pipeline_summary.md",
    "outputs/reviews/open_text_evidence_audit.md",
    "outputs/reviews/open_text_method_audit.md",
]

PROHIBITED_PREFIXES = (
    "data/raw/",
    "data/interview/",
    "data/processed/linked_cases/",
    "data/processed/interviews/",
    "outputs/agent_runs/",
    "outputs/qualitative/",
)

PROHIBITED_EXACT = {
    "data/processed/survey_clean.csv",
    "data/processed/survey_construct_scores.csv",
    "data/processed/interview_survey_map.csv",
    "data/processed/restricted_redaction_terms.txt",
    "data/processed/survey_open_text_corpus.csv",
    "data/processed/open_text_response_adjudication.csv",
    "outputs/open_text/open_text_coded_responses.csv",
    "outputs/open_text/open_closed_alignment.csv",
    "outputs/open_text/open_text_interview_alignment.csv",
}

FINAL_PRIVACY_PATTERNS = {
    "participant_id": re.compile(r"\bP\d{2}\b"),
    "transcript_line": re.compile(r"\bL\d{4}\b"),
    "survey_sequence": re.compile(r"\bS\d{4}\b"),
    "restricted_sequence_field": re.compile(r"questionnaire_sequence"),
}


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_prohibited(path: str) -> bool:
    return path in PROHIBITED_EXACT or path.startswith(PROHIBITED_PREFIXES)


def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))

    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    check("required_files", not missing, f"missing={missing or 'none'}")

    tracked = git_lines("ls-files")
    prohibited_tracked = [path for path in tracked if is_prohibited(path)]
    check(
        "restricted_paths_not_tracked",
        not prohibited_tracked,
        f"paths={prohibited_tracked or 'none'}",
    )

    history_names = git_lines("log", "--all", "--name-only", "--pretty=format:")
    prohibited_history = sorted({path for path in history_names if is_prohibited(path)})
    check(
        "restricted_paths_absent_from_history",
        not prohibited_history,
        f"paths={prohibited_history or 'none'}",
    )

    canonical = ROOT / "outputs/reports/final_report.md"
    final = ROOT / "outputs/final/final_research_report.md"
    check(
        "canonical_report_matches_final",
        canonical.is_file() and final.is_file() and canonical.read_bytes() == final.read_bytes(),
        "canonical and final delivery are byte-identical",
    )

    public_files = sorted((ROOT / "outputs/final").glob("*.md"))
    public_files += sorted((ROOT / "outputs/final").glob("*.csv"))
    public_files += [
        ROOT / "data/processed/open_text_codebook.csv",
        ROOT / "outputs/open_text/coding_reconciliation.md",
        ROOT / "outputs/open_text/q81_critical_incident_analysis.md",
        ROOT / "outputs/open_text/q82_support_needs_analysis.md",
        ROOT / "outputs/tables/open_text_theme_summary.csv",
        ROOT / "outputs/tables/joint_display.csv",
        ROOT / "outputs/reports/open_text_qualitative_synthesis.md",
        ROOT / "outputs/reports/open_closed_integration.md",
        ROOT / "outputs/reports/open_text_linked_case_analysis.md",
        ROOT / "outputs/reports/open_text_validation_report.md",
        ROOT / "outputs/reports/open_text_pipeline_summary.md",
        ROOT / "outputs/reviews/open_text_evidence_audit.md",
        ROOT / "outputs/reviews/open_text_method_audit.md",
    ]
    public_files = sorted({path for path in public_files if path.is_file()})
    privacy_hits: list[str] = []
    for path in public_files:
        text = path.read_text(encoding="utf-8-sig")
        for label, pattern in FINAL_PRIVACY_PATTERNS.items():
            if pattern.search(text):
                privacy_hits.append(f"{path.relative_to(ROOT)}:{label}")
    check(
        "final_outputs_privacy_scan",
        not privacy_hits,
        f"files={len(public_files)}; hits={privacy_hits or 'none'}",
    )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
    missing_links = [
        link
        for link in links
        if "://" not in link
        and not link.startswith("#")
        and not (ROOT / link.split("#", 1)[0]).exists()
    ]
    check(
        "readme_links",
        not missing_links,
        f"links={len(links)}; missing={missing_links or 'none'}",
    )

    with (ROOT / "outputs/final/findings_register.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        findings = list(csv.DictReader(handle))
    allowed_status = {
        "retained",
        "revised",
        "contextual_only",
        "future_research_only",
        "removed",
    }
    bad_status = [
        row.get("finding_id", "")
        for row in findings
        if row.get("final_status", "") not in allowed_status
    ]
    check(
        "findings_register",
        len(findings) >= 33 and not bad_status,
        f"rows={len(findings)}; bad_status={bad_status or 'none'}",
    )

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    citation_fields = [
        "cff-version:",
        "message:",
        "title:",
        "authors:",
        "version:",
        "repository-code:",
    ]
    missing_citation = [field for field in citation_fields if field not in citation]
    check(
        "citation_metadata",
        not missing_citation,
        f"missing={missing_citation or 'none'}",
    )

    passed = all(status for _, status, _ in checks)
    for name, status, detail in checks:
        print(f"{'PASS' if status else 'FAIL'} {name}: {detail}")
    print(f"github repository checks={len(checks)} result={'PASS' if passed else 'FAIL'}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
