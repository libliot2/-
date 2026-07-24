#!/usr/bin/env python3
"""Validate and promote fifth-round open/closed/interview integration."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "outputs/agent_runs/20260724_open_text_v5/open_text_integration"
)
OPEN_CLOSED_COLUMNS = [
    "public_text_id",
    "public_respondent_id",
    "question_id",
    "open_text_codes",
    "closed_question_id",
    "closed_variable",
    "closed_response",
    "relationship_type",
    "alignment_rationale",
    "alternative_explanation",
    "confidence",
    "review_status",
]
OPEN_INTERVIEW_COLUMNS = [
    "public_text_id",
    "linked_interview_participant",
    "question_id",
    "open_text_summary",
    "closed_question_id",
    "closed_evidence",
    "transcript_file",
    "transcript_line_start",
    "transcript_line_end",
    "transcript_evidence_summary",
    "relationship_type",
    "alignment_rationale",
    "alternative_explanation",
    "confidence",
    "review_status",
]
RELATIONS = {"CONVERGENCE", "EXPANSION", "DIVERGENCE", "SILENCE"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


def main() -> None:
    paths = {
        "open_closed": SOURCE / "proposed_open_closed_alignment.csv",
        "interview": SOURCE / "proposed_open_text_interview_alignment.csv",
        "open_closed_report": SOURCE / "open_closed_integration_draft.md",
        "linked_report": SOURCE / "linked_case_draft.md",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing integration proposals: {missing}")

    corpus = pd.read_csv(
        ROOT / "data/processed/survey_open_text_corpus.csv", keep_default_na=False
    )
    expected_open = set(
        corpus.loc[corpus["analyzable"].eq("YES"), "public_text_id"]
    )
    open_closed = pd.read_csv(paths["open_closed"], keep_default_na=False)
    if (
        list(open_closed.columns) != OPEN_CLOSED_COLUMNS
        or set(open_closed["public_text_id"]) != expected_open
        or not open_closed["relationship_type"].isin(RELATIONS).all()
        or not open_closed["confidence"].isin(CONFIDENCE).all()
    ):
        raise ValueError("Open/closed integration schema, coverage, or enums invalid")

    context = pd.read_csv(
        ROOT
        / "outputs/agent_runs/20260724_open_text_v5/integration_inputs/open_closed_context.csv",
        keep_default_na=False,
    )
    context_key = {
        (
            row.public_text_id,
            row.survey_variable,
        ): str(row.survey_response)
        for row in context.itertuples(index=False)
    }
    closed_errors = []
    for row in open_closed.itertuples(index=False):
        key = (row.public_text_id, row.closed_variable)
        if key not in context_key or str(row.closed_response) != context_key[key]:
            closed_errors.append(f"{row.public_text_id}:{row.closed_variable}")
    if closed_errors:
        raise ValueError(f"Closed-response trace errors: {closed_errors}")

    interview = pd.read_csv(paths["interview"], keep_default_na=False)
    expected_linked = set(
        corpus.loc[
            corpus["analyzable"].eq("YES")
            & corpus["linked_interview_participant"].astype(str).str.strip().ne(""),
            "public_text_id",
        ]
    )
    if (
        list(interview.columns) != OPEN_INTERVIEW_COLUMNS
        or set(interview["public_text_id"]) != expected_linked
        or len(interview) != 6
        or interview["linked_interview_participant"].nunique() != 3
        or not interview["relationship_type"].isin(RELATIONS).all()
        or not interview["confidence"].isin(CONFIDENCE).all()
    ):
        raise ValueError("Open/interview integration schema, coverage, or enums invalid")
    anchor_errors = []
    for row in interview.itertuples(index=False):
        transcript = ROOT / row.transcript_file
        if not transcript.is_file():
            anchor_errors.append(f"{row.public_text_id}:missing")
            continue
        labels = {
            match.group(1)
            for match in re.finditer(
                r"(?m)^\[(L\d{4})\]", transcript.read_text(encoding="utf-8")
            )
        }
        if (
            row.transcript_line_start not in labels
            or row.transcript_line_end not in labels
            or row.transcript_line_start > row.transcript_line_end
        ):
            anchor_errors.append(row.public_text_id)
    if anchor_errors:
        raise ValueError(f"Transcript anchor errors: {anchor_errors}")

    public_hits = []
    for name in ["open_closed_report", "linked_report"]:
        text = paths[name].read_text(encoding="utf-8")
        for pattern in [r"\bP\d{2}\b", r"\bL\d{4}\b", r"\bS\d{4}\b"]:
            if re.search(pattern, text):
                public_hits.append(f"{name}:{pattern}")
    if public_hits:
        raise ValueError(f"Public report privacy hits: {public_hits}")

    (ROOT / "outputs/open_text").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs/reports").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        paths["open_closed"], ROOT / "outputs/open_text/open_closed_alignment.csv"
    )
    shutil.copyfile(
        paths["interview"],
        ROOT / "outputs/open_text/open_text_interview_alignment.csv",
    )
    shutil.copyfile(
        paths["open_closed_report"],
        ROOT / "outputs/reports/open_closed_integration.md",
    )
    shutil.copyfile(
        paths["linked_report"],
        ROOT / "outputs/reports/open_text_linked_case_analysis.md",
    )
    print(
        "promoted "
        f"open_closed={len(open_closed)} "
        f"relations={open_closed['relationship_type'].value_counts().to_dict()} "
        f"linked={len(interview)}"
    )


if __name__ == "__main__":
    main()
