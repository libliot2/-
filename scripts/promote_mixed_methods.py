#!/usr/bin/env python3
"""Validate and promote isolated mixed-methods integration outputs."""

from __future__ import annotations

import re
import shutil

import pandas as pd

from pipeline_common import ROOT, RUN_ID

RUN = ROOT / "outputs/agent_runs" / RUN_ID / "mixed_methods"
TABLES = ROOT / "outputs/tables"
REPORTS = ROOT / "outputs/reports"

FIELDS = [
    "analytic_topic",
    "survey_evidence",
    "interview_subsample_position",
    "linked_case_evidence",
    "relationship_type",
    "integrated_interpretation",
    "alternative_explanations",
    "limitations",
    "source_files",
]


def main() -> None:
    display = pd.read_csv(RUN / "joint_display.csv", dtype=str, keep_default_na=False)
    if list(display.columns) != FIELDS:
        raise ValueError(f"Joint-display schema mismatch: {list(display.columns)}")
    if set(display["relationship_type"]) - {"CONVERGENCE", "EXPANSION", "DIVERGENCE", "SILENCE"}:
        raise ValueError("Invalid mixed-methods relationship type")
    if len(display) < 4:
        raise ValueError("Joint display must cover at least four major analytic topics")
    combined = "\n".join(display.astype(str).agg(" ".join, axis=1))
    combined += (RUN / "integrated_findings.md").read_text(encoding="utf-8")
    prohibited = [
        r"访谈-序号\d+",
        r"问卷序号[:：]\s*\d+",
        r"\bS00\d+\b",
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    ]
    for pattern in prohibited:
        if re.search(pattern, combined):
            raise ValueError(f"Prohibited identifier pattern in mixed-methods output: {pattern}")
    TABLES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    display.to_csv(TABLES / "joint_display.csv", index=False, encoding="utf-8-sig")
    shutil.copy2(RUN / "integrated_findings.md", REPORTS / "integrated_findings.md")
    print(f"promoted mixed-methods topics={len(display)}")


if __name__ == "__main__":
    main()
