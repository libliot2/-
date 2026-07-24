#!/usr/bin/env python3
"""Prepare the restricted Q8.1/Q8.2 corpus for semantic coding."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SURVEY = ROOT / "data/processed/survey_clean.csv"
CODEBOOK = ROOT / "data/processed/survey_codebook.csv"
LINKS = ROOT / "data/processed/interview_survey_map.csv"
OUTPUT = ROOT / "data/processed/survey_open_text_corpus.csv"

QUESTIONS = {
    "Q8.1": "q8_1_boundary_event_text",
    "Q8.2": "q8_2_support_request_text",
}
SPECIAL = {
    "",
    "BLANK",
    "NOT_APPLICABLE",
    "CANNOT_REMEMBER",
    "UNWILLING_TO_ANSWER",
    "INVALID_RESPONSE",
}


def build_public_ids(row_ids: list[str]) -> dict[str, str]:
    """Assign stable IDs unrelated to questionnaire sequence or row order."""
    ranked = sorted(
        row_ids,
        key=lambda value: hashlib.sha256(
            f"open-text-v5|{value}".encode("utf-8")
        ).hexdigest(),
    )
    return {row_id: f"R{index:02d}" for index, row_id in enumerate(ranked, 1)}


def main() -> None:
    survey = pd.read_csv(
        SURVEY, dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )
    codebook = pd.read_csv(
        CODEBOOK, dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )
    links = pd.read_csv(
        LINKS, dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )
    if len(survey) != 35 or survey["survey_row_id"].nunique() != 35:
        raise ValueError("Expected 35 unique cleaned survey records.")
    public_ids = build_public_ids(survey["survey_row_id"].tolist())
    linked = (
        links.loc[links["mapping_status"].eq("MATCHED")]
        .set_index("survey_row_id")["participant_id"]
        .to_dict()
    )
    question_text = (
        codebook.loc[codebook["question_id"].isin(QUESTIONS)]
        .drop_duplicates("question_id")
        .set_index("question_id")["question_text"]
        .to_dict()
    )
    rows: list[dict[str, object]] = []
    for record in survey.to_dict("records"):
        row_id = record["survey_row_id"]
        public_respondent = public_ids[row_id]
        for question_id, variable in QUESTIONS.items():
            response = str(record[variable]).strip()
            is_special = response in SPECIAL
            compact_qid = question_id.replace(".", "")
            rows.append(
                {
                    "internal_response_id": f"{row_id}::{question_id}",
                    "public_text_id": f"OT-{public_respondent}-{compact_qid}",
                    "public_respondent_id": public_respondent,
                    "question_id": question_id,
                    "question_text": question_text[question_id],
                    "original_response": response,
                    "respondent_eligibility": record["eligible"],
                    "linked_interview_participant": linked.get(row_id, ""),
                    "response_length": 0 if is_special else len(response),
                    "analyzable": "NO" if is_special else "YES",
                    "exclusion_or_warning": (
                        response if response else "BLANK"
                    )
                    if is_special
                    else "PENDING_SEMANTIC_CONFIRMATION",
                }
            )
    corpus = pd.DataFrame(rows)
    corpus.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    summary = (
        corpus.groupby(["question_id", "analyzable"], dropna=False)
        .size()
        .to_dict()
    )
    print(f"open-text corpus rows={len(corpus)} summary={summary}")


if __name__ == "__main__":
    main()
