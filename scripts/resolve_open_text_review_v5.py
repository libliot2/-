#!/usr/bin/env python3
"""Apply verified reviewer resolutions to fifth-round open-text canonical data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/processed/survey_open_text_corpus.csv"
CODEBOOK = ROOT / "data/processed/open_text_codebook.csv"
CODED = ROOT / "outputs/open_text/open_text_coded_responses.csv"
THEMES = ROOT / "outputs/tables/open_text_theme_summary.csv"
OPEN_CLOSED = ROOT / "outputs/open_text/open_closed_alignment.csv"
OPEN_INTERVIEW = ROOT / "outputs/open_text/open_text_interview_alignment.csv"
CONTEXT = (
    ROOT
    / "outputs/agent_runs/20260724_open_text_v5/integration_inputs/open_closed_context.csv"
)


def split_codes(value: str) -> list[str]:
    return [part.strip() for part in str(value).split(";") if part.strip()]


def join_codes(values: list[str]) -> str:
    return ";".join(dict.fromkeys(values))


def theme_rows(coded: pd.DataFrame, question_id: str, basis: str) -> pd.DataFrame:
    rows = coded[coded["question_id"].eq(question_id)].copy()
    if basis.startswith("EVENT_DIRECTION="):
        return rows[rows["event_direction"].eq(basis.split("=", 1)[1])]
    if basis.startswith("ANY_OF:"):
        candidates = set(basis.removeprefix("ANY_OF:").split("|"))
        return rows[
            rows["final_codes"].map(
                lambda value: bool(set(split_codes(value)) & candidates)
            )
        ]
    return rows[
        rows["final_codes"].map(lambda value: basis in set(split_codes(value)))
    ]


def main() -> None:
    corpus = pd.read_csv(CORPUS, keep_default_na=False)
    pending = corpus["analyzable"].eq("YES") & corpus["exclusion_or_warning"].eq(
        "PENDING_SEMANTIC_CONFIRMATION"
    )
    corpus.loc[pending, "exclusion_or_warning"] = "SEMANTIC_ANALYSIS_COMPLETED"

    coded = pd.read_csv(CODED, keep_default_na=False)
    for public_id in ["OT-R06-Q81", "OT-R18-Q81", "OT-R22-Q81"]:
        mask = coded["public_text_id"].eq(public_id)
        if mask.sum() != 1:
            raise ValueError(f"Expected one coded row for {public_id}")
        values = [
            code for code in split_codes(coded.loc[mask, "final_codes"].iloc[0])
            if code != "OTC45"
        ]
        coded.loc[mask, "final_codes"] = join_codes(values)
    r15 = coded["public_text_id"].eq("OT-R15-Q81")
    values = split_codes(coded.loc[r15, "final_codes"].iloc[0])
    if "OTC47" not in values:
        values.append("OTC47")
    coded.loc[r15, "final_codes"] = join_codes(values)

    replacements = {
        ("OT-R01-Q81", "researcher_inference"): (
            "在该叙述中，沟通调节、任务完成和接纳感相伴；共同话题仍与部分互动距离并存。"
        ),
        ("OT-R03-Q81", "theoretical_interpretation"): (
            "该叙述把同伴支架、课堂参与机会与后续线上和线下关系并列；是否存在接续作用仍待检验。"
        ),
        ("OT-R03-Q81", "researcher_inference"): (
            "同伴邀请、可理解沟通与任务后的持续关系通道在同一叙述中出现。"
        ),
        ("OT-R13-Q81", "researcher_inference"): (
            "个人技能、任务角色和后续互动在同一叙述中出现；其关系方向不能由本回答确定。"
        ),
        ("OT-R15-Q81", "researcher_inference"): (
            "既有熟人优先、初期外围位置和后续受邀依次出现；不能据此确定关系结构的作用方向。"
        ),
    }
    resolved_ids = {
        "OT-R01-Q81",
        "OT-R03-Q81",
        "OT-R06-Q81",
        "OT-R13-Q81",
        "OT-R15-Q81",
        "OT-R18-Q81",
        "OT-R22-Q81",
    }
    for (public_id, column), value in replacements.items():
        mask = coded["public_text_id"].eq(public_id)
        coded.loc[mask, column] = value
    coded["review_status"] = coded["public_text_id"].map(
        lambda value: (
            "REVIEWER_RESOLVED"
            if value in resolved_ids
            else "MAIN_AGENT_VERIFIED"
        )
    )

    codebook = pd.read_csv(CODEBOOK, keep_default_na=False)
    if "example_text_id" in codebook.columns:
        codebook = codebook.drop(columns=["example_text_id"])
    if "OTC47" not in set(codebook["code_id"]):
        codebook = pd.concat(
            [
                codebook,
                pd.DataFrame(
                    [
                        {
                            "code_id": "OTC47",
                            "code_name": "SEQUENTIAL_DISTANCE_TO_ENTRY",
                            "definition": (
                                "同一回答先叙述初期门槛或未获邀，后叙述进入事件；"
                                "不表示距离在进入后仍持续。"
                            ),
                            "include_when": "两个阶段或事件顺序清楚，后段进入是焦点",
                            "exclude_when": (
                                "进入与距离在相近时期持续并存；或回答只包含进入/距离一端"
                            ),
                            "example_excerpt": "",
                            "inductive_or_deductive": "MIXED",
                            "related_research_question": "RQ1",
                            "related_theory": "temporal trajectory; school belonging",
                            "status": "ACTIVE",
                            "notes": "与OTC19持续并存分开；当前仅一条。",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    codebook.insert(
        codebook.columns.get_loc("example_excerpt") + 1, "example_text_id", ""
    )
    codebook["example_excerpt"] = ""
    approved = coded[
        coded["excerpt_status"].eq("VERBATIM_SAFE")
        & coded["deidentified_excerpt"].astype(str).str.strip().ne("")
    ].sort_values("public_text_id")
    for index, row in codebook.iterrows():
        candidates = approved[
            approved["final_codes"].map(
                lambda value: row["code_id"] in set(split_codes(value))
            )
        ]
        if candidates.empty:
            continue
        source = candidates.iloc[0]
        codebook.loc[index, "example_excerpt"] = source["deidentified_excerpt"]
        codebook.loc[index, "example_text_id"] = source["public_text_id"]
    codebook = codebook.sort_values(
        "code_id", key=lambda series: series.str.extract(r"(\d+)")[0].astype(int)
    )

    themes = pd.read_csv(THEMES, keep_default_na=False)
    mixed = themes["theme"].eq("进入与距离在同一回答中并存")
    if mixed.any():
        themes.loc[mixed, "theme"] = "焦点事件方向为混合（并存或顺序反转）"
        themes.loc[mixed, "counting_basis"] = "EVENT_DIRECTION=MIXED"
        themes.loc[mixed, "interpretation_caution"] = (
            "表示26名本题作答者中的焦点方向分类，不是经历率；"
            "其中持续并存5名、先有距离后转为进入1名。"
        )
    themes = themes[
        ~themes["theme"].isin(["进入与距离持续并存", "先有距离后转为进入"])
    ]
    insertion = pd.DataFrame(
        [
            {
                "question_id": "Q8.1",
                "theme": "进入与距离持续并存",
                "counting_basis": "OTC19",
                "unique_respondents": 0,
                "valid_open_text_n": 26,
                "illustrative_text_ids": "OT-R01-Q81;OT-R17-Q81;OT-R35-Q81",
                "negative_or_contrasting_cases": "OT-R15-Q81（属于顺序反转，不计持续并存）",
                "interpretation_caution": (
                    "表示26名本题作答者中的主动提及，不是经历率；"
                    "持续并存可发生于不同场景，不能推成稳定类型。"
                ),
            },
            {
                "question_id": "Q8.1",
                "theme": "先有距离后转为进入",
                "counting_basis": "OTC47",
                "unique_respondents": 0,
                "valid_open_text_n": 26,
                "illustrative_text_ids": "OT-R15-Q81",
                "negative_or_contrasting_cases": "OT-R01-Q81;OT-R17-Q81（进入后仍保留距离）",
                "interpretation_caution": (
                    "仅一条顺序叙述；不能视为普遍轨迹，也不能证明邀请造成转变。"
                ),
            },
        ]
    )
    themes = pd.concat([themes, insertion], ignore_index=True)
    for index, row in themes.iterrows():
        selected = theme_rows(coded, row["question_id"], row["counting_basis"])
        themes.loc[index, "unique_respondents"] = int(
            selected["public_respondent_id"].nunique()
        )
    q_order = {"Q8.1": 1, "Q8.2": 2}
    themes["_order"] = themes["question_id"].map(q_order)
    themes = themes.sort_values(["_order"], kind="stable").drop(columns="_order")

    open_closed = pd.read_csv(OPEN_CLOSED, keep_default_na=False)
    divergence_specs = {
        ("OT-R04-Q81", "q3_1_local_knowledge_barrier"): (
            "开放回答把刚插班时本地童年或流行话题造成的距离描述为“常常”，"
            "封闭题同构念初期频率为“很少”；构念、时段和方向相反。",
            "频率词门槛、最初三个月边界、回忆和题意理解差异均可能解释。",
        ),
        ("OT-R05-Q81", "q3_1_language_humour_barrier"): (
            "开放回答把刚插班时粤语俚语或本地日常跟不上描述为“常常”，"
            "封闭题同构念初期频率为“很少”；构念、时段和方向相反。",
            "频率词门槛、最初三个月边界、回忆和题意理解差异均可能解释。",
        ),
    }
    open_closed["review_status"] = "MAIN_AGENT_VERIFIED"
    for key, (rationale, alternative) in divergence_specs.items():
        mask = open_closed["public_text_id"].eq(key[0]) & open_closed[
            "closed_variable"
        ].eq(key[1])
        if mask.sum() != 1:
            raise ValueError(f"Expected one alignment for {key}, got {mask.sum()}")
        open_closed.loc[mask, "relationship_type"] = "DIVERGENCE"
        open_closed.loc[mask, "alignment_rationale"] = rationale
        open_closed.loc[mask, "alternative_explanation"] = alternative
        open_closed.loc[mask, "review_status"] = "REVIEWER_RESOLVED"

    context = pd.read_csv(CONTEXT, keep_default_na=False)
    coded_by_id = coded.set_index("public_text_id")
    member_ids = ["OT-R01-Q81", "OT-R17-Q81", "OT-R31-Q81", "OT-R35-Q81"]
    additions = []
    for public_id in member_ids:
        existing = open_closed[
            open_closed["public_text_id"].eq(public_id)
            & open_closed["closed_variable"].eq("q3_3_member")
        ]
        if not existing.empty:
            continue
        source = context[
            context["public_text_id"].eq(public_id)
            & context["survey_variable"].eq("q3_3_member")
        ]
        if len(source) != 1:
            raise ValueError(f"Expected one member context row for {public_id}")
        response = source.iloc[0]["survey_response"]
        rationale = (
            "开放回答同时描述进入与持续局部距离；封闭题概括后期成员感。"
            "两者层次或时段不同，开放题扩展了整体成员感背后的具体事件。"
        )
        additions.append(
            {
                "public_text_id": public_id,
                "public_respondent_id": coded_by_id.loc[
                    public_id, "public_respondent_id"
                ],
                "question_id": "Q8.1",
                "open_text_codes": coded_by_id.loc[public_id, "final_codes"],
                "closed_question_id": "Q3.3",
                "closed_variable": "q3_3_member",
                "closed_response": response,
                "relationship_type": "EXPANSION",
                "alignment_rationale": rationale,
                "alternative_explanation": (
                    "开放题聚焦初期或具体事件，封闭题概括后期完整学期；"
                    "回忆、量表压缩和回答门槛也可能产生该配置。"
                ),
                "confidence": "MEDIUM",
                "review_status": "REVIEWER_RESOLVED",
            }
        )
    if additions:
        open_closed = pd.concat(
            [open_closed, pd.DataFrame(additions)], ignore_index=True
        )
    # Synchronise codes in all alignment rows after reviewer code changes.
    open_closed["open_text_codes"] = open_closed["public_text_id"].map(
        coded_by_id["final_codes"]
    )
    open_closed = open_closed.sort_values(
        ["question_id", "public_text_id", "closed_variable"], kind="stable"
    )

    open_interview = pd.read_csv(OPEN_INTERVIEW, keep_default_na=False)
    open_interview["review_status"] = "MAIN_AGENT_VERIFIED"

    corpus.to_csv(CORPUS, index=False, encoding="utf-8-sig")
    coded.to_csv(CODED, index=False, encoding="utf-8-sig")
    codebook.to_csv(CODEBOOK, index=False, encoding="utf-8-sig")
    themes.to_csv(THEMES, index=False, encoding="utf-8-sig")
    open_closed.to_csv(OPEN_CLOSED, index=False, encoding="utf-8-sig")
    open_interview.to_csv(OPEN_INTERVIEW, index=False, encoding="utf-8-sig")
    print(
        "review resolutions applied "
        f"codes={len(codebook)} themes={len(themes)} "
        f"open_closed={len(open_closed)} "
        f"relations={open_closed['relationship_type'].value_counts().to_dict()}"
    )


if __name__ == "__main__":
    main()
