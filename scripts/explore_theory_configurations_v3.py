#!/usr/bin/env python3
"""Reproduce the bounded quantitative/open-text checks used in round three."""

from __future__ import annotations

import csv
import difflib
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "outputs/agent_runs/20260723_multi_theory_abductive_v3/synthesis"

LIKERT = {
    "完全不同意": 1,
    "比较不同意": 2,
    "不确定": 3,
    "比较同意": 4,
    "完全同意": 5,
}


def score(series: pd.Series) -> pd.Series:
    return series.map(LIKERT)


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    clean = pd.read_csv(ROOT / "data/processed/survey_clean.csv")
    scores = pd.read_csv(ROOT / "data/processed/survey_construct_scores.csv")
    data = clean.merge(scores, on="survey_row_id", how="left")

    q = data[
        [
            "peer_cultural_boundary",
            "school_belonging",
            "academic_difficulty",
            "academic_rule_understanding",
        ]
    ].quantile([0.25, 0.5, 0.75])
    q.to_csv(RUN / "construct_quantiles_v3.csv", index_label="quantile")

    later_local = data["q6_2_later_whatsapp"].eq(True) | data[
        "q6_2_later_instagram"
    ].eq(True)
    initial_boundary = pd.concat(
        [
            score(data["q3_1_language_humour_barrier"]),
            score(data["q3_1_local_knowledge_barrier"]),
            score(data["q3_1_background_assumption"]),
            score(data["q3_1_mainland_grouping_assumption"]),
            score(data["q3_1_self_withdrawal"]),
        ],
        axis=1,
    ).max(axis=1) >= 4
    q75 = q.loc[0.75]
    median = q.loc[0.5]
    configurations = {
        "AC01_high_boundary_high_belonging": (
            (data["peer_cultural_boundary"] >= q75["peer_cultural_boundary"])
            & (data["school_belonging"] >= q75["school_belonging"])
        ),
        "AC02_high_difficulty_high_rule_mastery": (
            (data["academic_difficulty"] >= q75["academic_difficulty"])
            & (
                data["academic_rule_understanding"]
                >= q75["academic_rule_understanding"]
            )
            & (score(data["q5_2_distinguish_rules_ability"]) >= 4)
        ),
        "AC03_brokerage_items_high_belonging_not_high": (
            (score(data["q4_1_explain_differences"]) >= 4)
            & (score(data["q4_1_reduce_misunderstanding"]) >= 4)
            & (data["school_belonging"] <= median["school_belonging"])
        ),
        "AC04_local_platform_without_local_dominant_network": (
            later_local
            & ~data["q7_1_peer_network"].astype(str).str.contains(
                "香港本地同学为主", regex=False
            )
        ),
        "AC05_old_support_and_hk_platform_participation": (
            (score(data["q6_5_old_network_emotional_support"]) >= 4)
            & (score(data["q6_5_hk_platform_participation"]) >= 4)
        ),
        "AC06_later_membership_with_initial_boundary": (
            (score(data["q3_3_member"]) >= 4) & initial_boundary
        ),
    }
    rows = []
    for config_id, mask in configurations.items():
        eligible = data.loc[data["eligible"].eq(True) & mask.fillna(False)]
        for _, item in eligible.iterrows():
            rows.append(
                {
                    "configuration_id": config_id,
                    "survey_row_id": item["survey_row_id"],
                    "n_configuration": len(eligible),
                    "threshold_basis": "pre-specified quartile/median or item >=4",
                }
            )
    pd.DataFrame(rows).to_csv(
        RUN / "anomaly_configurations_v3.csv", index=False
    )
    with (RUN / "anomaly_counts_public_v3.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "configuration_id",
                "n",
                "reportable",
                "interpretive_scope",
            ],
        )
        writer.writeheader()
        for config_id, mask in configurations.items():
            n = int((data["eligible"].eq(True) & mask.fillna(False)).sum())
            writer.writerow(
                {
                    "configuration_id": config_id,
                    "n": n if n >= 3 else "SUPPRESSED_LT3",
                    "reportable": "yes" if n >= 3 else "no",
                    "interpretive_scope": (
                        "configuration count only; no inferential or representative claim"
                    ),
                }
            )

    open_rows = []
    for column in ["q8_1_boundary_event_text", "q8_2_support_request_text"]:
        values = [
            str(v).strip()
            for v in data.loc[data["eligible"].eq(True), column].dropna()
            if str(v).strip()
            and str(v).strip()
            not in {"BLANK", "NOT_APPLICABLE", "CANNOT_REMEMBER", "UNWILLING"}
        ]
        normalized = [re.sub(r"[\s，。、“”‘’：；！？]", "", v) for v in values]
        pairs = []
        for i in range(len(normalized)):
            for j in range(i + 1, len(normalized)):
                pairs.append(
                    difflib.SequenceMatcher(
                        None, normalized[i], normalized[j]
                    ).ratio()
                )
        open_rows.append(
            {
                "variable": column,
                "nonblank_n": len(values),
                "pairwise_max_similarity": round(max(pairs, default=0), 3),
                "pairs_ge_0_45": sum(x >= 0.45 for x in pairs),
                "pairs_ge_0_60": sum(x >= 0.60 for x in pairs),
                "interpretation": (
                    "Prompt-shaped event grammar is possible; provenance cannot be "
                    "inferred and these texts are not used as independent prevalence counts."
                ),
            }
        )
    pd.DataFrame(open_rows).to_csv(
        RUN / "open_text_prompt_pattern_audit_v3.csv", index=False
    )


if __name__ == "__main__":
    main()
