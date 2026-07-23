#!/usr/bin/env python3
"""Validate and promote the isolated qualitative synthesis to canonical outputs."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd

from pipeline_common import ROOT

RUN = ROOT / "outputs/agent_runs/20260723_full_pipeline/qualitative_synthesis"
PROCESSED = ROOT / "data/processed"
QUALITATIVE = ROOT / "outputs/qualitative"
REPORTS = ROOT / "outputs/reports"

CODEBOOK_FIELDS = [
    "code_id",
    "code_name",
    "parent_code",
    "definition",
    "include_when",
    "exclude_when",
    "example",
    "source",
    "status",
    "notes",
]
SEGMENT_FIELDS = [
    "participant_id",
    "source_file",
    "line_start",
    "line_end",
    "exact_quote",
    "primary_code",
    "secondary_code",
    "time_period",
    "analytic_note",
    "alternative_explanation",
    "confidence",
]
FRAMEWORK_FIELDS = [
    "theme",
    "P01_summary",
    "P01_evidence",
    "P02_summary",
    "P02_evidence",
    "P03_summary",
    "P03_evidence",
    "shared_pattern",
    "difference_or_negative_case",
    "alternative_explanation",
]


def line_contents(participant_id: str) -> dict[str, str]:
    path = PROCESSED / "interviews" / f"interview_{participant_id}_numbered.md"
    result = {}
    pattern = re.compile(r"^\[(L\d{4})\]\s+[^:]+:\s?(.*)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def selected_text(lines: dict[str, str], start: str, end: str) -> str:
    start_n, end_n = int(start[1:]), int(end[1:])
    return " ".join(lines[f"L{number:04d}"] for number in range(start_n, end_n + 1))


def main() -> None:
    codebook = pd.read_csv(RUN / "proposed_qualitative_codebook.csv", dtype=str, keep_default_na=False)
    segments = pd.read_csv(RUN / "coded_segments_master.csv", dtype=str, keep_default_na=False)
    framework = pd.read_csv(RUN / "framework_matrix.csv", dtype=str, keep_default_na=False)
    if list(codebook.columns) != CODEBOOK_FIELDS:
        raise ValueError(f"Codebook schema mismatch: {list(codebook.columns)}")
    if list(segments.columns) != SEGMENT_FIELDS:
        raise ValueError(f"Coded segment schema mismatch: {list(segments.columns)}")
    if set(framework.columns) == set(FRAMEWORK_FIELDS) - {"P03_summary", "P03_evidence"}:
        framework["P03_summary"] = "NOT_ANALYSED_INELIGIBLE"
        framework["P03_evidence"] = ""
        framework = framework[FRAMEWORK_FIELDS]
    if list(framework.columns) != FRAMEWORK_FIELDS:
        raise ValueError(f"Framework schema mismatch: {list(framework.columns)}")
    if set(segments["participant_id"]) - {"P01", "P02"}:
        raise ValueError("Only eligible P01/P02 may appear in canonical coded segments")
    if set(codebook["source"]) - {"DEDUCTIVE", "INDUCTIVE", "MIXED"}:
        raise ValueError("Invalid qualitative code source")
    if set(codebook["status"]) - {"ACTIVE", "MERGED", "RETIRED", "PROPOSED"}:
        raise ValueError("Invalid qualitative code status")
    if set(segments["confidence"]) - {"HIGH", "MEDIUM", "LOW"}:
        raise ValueError("Invalid segment confidence")
    active_codes = set(codebook.loc[codebook["status"].isin(["ACTIVE", "PROPOSED"]), "code_id"])
    for row in segments.itertuples(index=False):
        if row.primary_code not in active_codes:
            raise ValueError(f"Unknown primary code {row.primary_code}")
        if row.secondary_code and row.secondary_code not in active_codes:
            raise ValueError(f"Unknown secondary code {row.secondary_code}")
        lines = line_contents(row.participant_id)
        source = selected_text(lines, row.line_start, row.line_end)
        if row.exact_quote not in source:
            raise ValueError(
                f"Quote mismatch {row.participant_id} {row.line_start}-{row.line_end}: {row.exact_quote}"
            )
    QUALITATIVE.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    codebook.to_csv(PROCESSED / "qualitative_codebook.csv", index=False, encoding="utf-8-sig")
    segments.to_csv(QUALITATIVE / "coded_segments_master.csv", index=False, encoding="utf-8-sig")
    framework.to_csv(QUALITATIVE / "framework_matrix.csv", index=False, encoding="utf-8-sig")
    shutil.copy2(RUN / "cross_case_analysis.md", REPORTS / "cross_case_analysis.md")
    print(
        f"promoted qualitative synthesis segments={len(segments)} "
        f"codes={len(codebook)} themes={len(framework)}"
    )


if __name__ == "__main__":
    main()
