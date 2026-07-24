#!/usr/bin/env python3
"""Build restricted long-form closed-item context for open-text integration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed"
RUN = ROOT / "outputs/agent_runs/20260724_open_text_v5"
OUTPUT = RUN / "integration_inputs/open_closed_context.csv"

PREFIXES = {
    "Q8.1": ("q3_1_", "q3_2_", "q3_3_", "q4_1_", "q7_1_", "q6_"),
    "Q8.2": ("q5_1_", "q5_2_", "q5_4_", "q5_5_", "q6_"),
}


def main() -> None:
    corpus = pd.read_csv(
        PROCESSED / "survey_open_text_corpus.csv",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )
    survey = pd.read_csv(
        PROCESSED / "survey_clean.csv",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    ).set_index("survey_row_id")
    codebook = pd.read_csv(
        PROCESSED / "survey_codebook.csv",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    ).set_index("variable_name")
    rows: list[dict[str, str]] = []
    analyzable = corpus.loc[corpus["analyzable"].eq("YES")]
    for response in analyzable.to_dict("records"):
        survey_row_id = response["internal_response_id"].split("::", 1)[0]
        prefixes = PREFIXES[response["question_id"]]
        variables = [
            variable
            for variable in survey.columns
            if variable.startswith(prefixes)
        ]
        for variable in variables:
            item = codebook.loc[variable]
            rows.append(
                {
                    "internal_response_id": response["internal_response_id"],
                    "public_text_id": response["public_text_id"],
                    "question_id": response["question_id"],
                    "survey_variable": variable,
                    "question_or_item_text": item["item_text"]
                    or item["question_text"],
                    "survey_response": survey.at[survey_row_id, variable],
                    "comparison_scope": ";".join(
                        prefix.rstrip("_") for prefix in prefixes
                    ),
                }
            )
    result = pd.DataFrame(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(
        f"open-closed context rows={len(result)} "
        f"responses={result['internal_response_id'].nunique()}"
    )


if __name__ == "__main__":
    main()
