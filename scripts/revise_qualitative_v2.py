#!/usr/bin/env python3
"""Apply the independently reviewed qualitative and alignment corrections."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from pipeline_common import ROOT


SOURCE_RUN = ROOT / "outputs/agent_runs/20260723_expanded_eligibility"
ROUND2_RUN = (
    ROOT
    / "outputs/agent_runs/20260723_independent_review_extension_v2"
    / "revised_qualitative"
)
PROCESSED = ROOT / "data/processed"
QUALITATIVE = ROOT / "outputs/qualitative"


RELATION_OVERRIDES = {
    # Reviewer B/C: adjacent content domains, non-overlapping periods, or
    # conditional preferences are not direct contradictions.
    ("P01", "q5_1_english_materials"): (
        "EXPANSION",
        "英文材料与英文口语不是同一内容域；保留为相邻困难的情境扩展。",
    ),
    ("P01", "q5_1_assessment_mix"): (
        "EXPANSION",
        "任务很多且重要不等于任务困难；不作为汇聚证据。",
    ),
    ("P01", "q5_5_assessment_rules_support"): (
        "EXPANSION",
        "一般学校制度说明不等于评价规则支持；两者可同时成立。",
    ),
    ("P01", "q4_1_adjust_expression"): (
        "EXPANSION",
        "主动调整表达与在部分场景感到受限可以并存，不构成相反方向。",
    ),
    ("P02", "q3_1_local_knowledge_barrier / q3_1_self_withdrawal"): (
        "EXPANSION",
        "总体友好印象没有直接测量地方知识边界或减少参与频率。",
    ),
    ("P02", "q5_1_group_project / q5_3_good_student_groupwork"): (
        "EXPANSION",
        "初期困难与后来尚可/有进步时段不同，且两个问卷项目也非同一命题。",
    ),
    ("P02", "q5_2_transfer_prior_strengths"): (
        "EXPANSION",
        "问卷指既有优势用于香港课堂，访谈指返内地后的优势，场景不等价。",
    ),
    ("P02", "q8_2_support_request_text（教师关注）"): (
        "EXPANSION",
        "希望可获得关注与不希望显眼的特别关心体现强度和可见性条件。",
    ),
    ("P02", "q3_2_help_hk_peer_invitation / q3_3_member"): (
        "SILENCE",
        "Q3.2限选且访谈未说明主动接近者背景；未勾选不构成否定证据。",
    ),
    ("P03", "q3_3_member"): (
        "EXPANSION",
        "朋友、社团和外出为成员感提供情境，但不直接复述主观成员陈述。",
    ),
    ("P03", "q7_1_peer_network"): (
        "EXPANSION",
        "核心友谊和活动参与不等于进入稳定群体，属于网络门槛的情境扩展。",
    ),
    ("P03", "q5_1_assessment_mix"): (
        "EXPANSION",
        "耗时和指导不足不等于任务最终完成困难；保留为任务负担扩展。",
    ),
    ("P03", "q5_3_good_student_extracurricular"): (
        "EXPANSION",
        "参加社团不直接验证好学生价值判断发生变化。",
    ),
}


def transcript_lines(participant_id: str) -> dict[str, tuple[str, str]]:
    path = PROCESSED / "interviews" / f"interview_{participant_id}_numbered.md"
    pattern = re.compile(r"^\[(L\d{4})\]\s+([^:]+):\s?(.*)$")
    lines: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            lines[match.group(1)] = (match.group(2), match.group(3))
    return lines


def range_text(participant_id: str, start: str, end: str) -> str:
    lines = transcript_lines(participant_id)
    selected = [
        lines[f"L{number:04d}"][1]
        for number in range(int(start[1:]), int(end[1:]) + 1)
    ]
    return " ".join(selected)


def revise_segments() -> pd.DataFrame:
    segments = pd.read_csv(
        QUALITATIVE / "coded_segments_master.csv", dtype=str, keep_default_na=False
    )

    def update(participant: str, start: str, **values: str) -> None:
        mask = segments["participant_id"].eq(participant) & segments["line_start"].eq(start)
        if int(mask.sum()) != 1:
            raise ValueError(f"Expected one segment for {participant}:{start}")
        for key, value in values.items():
            segments.loc[mask, key] = value

    update(
        "P03",
        "L0011",
        line_end="L0012",
        exact_quote=range_text("P03", "L0011", "L0012"),
        analytic_note=(
            "参与者把香港课堂讨论的任务必要性与此前可退出的讨论经验并置；"
            "“社恐”只按日常自我描述处理。"
        ),
    )
    update(
        "P03",
        "L0014",
        line_end="L0015",
        exact_quote=range_text("P03", "L0014", "L0015"),
        primary_code="SYSTEM_ASSESSMENT_RULES",
        secondary_code="NON_CULTURAL_ALTERNATIVE",
        analytic_note="对正式课程及其内容缺乏事前信息，使第一天处于陌生状态。",
    )
    update(
        "P02",
        "L0148",
        primary_code="LEARNER_IDENTITY_RENEGOTIATION",
        secondary_code="",
    )
    update(
        "P02",
        "L0231",
        primary_code="SYSTEM_ASSESSMENT_RULES",
        secondary_code="NON_CULTURAL_ALTERNATIVE",
    )
    update(
        "P02",
        "L0248",
        primary_code="PEER_INVITATION",
        secondary_code="NON_CULTURAL_ALTERNATIVE",
    )
    update(
        "P01",
        "L0023",
        primary_code="GRADUAL_ADAPTATION_PATH",
        secondary_code="SELF_INITIATED_ADAPTATION",
    )

    for row in segments.itertuples(index=False):
        source = range_text(row.participant_id, row.line_start, row.line_end)
        if row.exact_quote not in source:
            raise ValueError(
                f"Revised quote mismatch: {row.participant_id} "
                f"{row.line_start}-{row.line_end}"
            )
        lines = transcript_lines(row.participant_id)
        for number in range(int(row.line_start[1:]), int(row.line_end[1:]) + 1):
            if lines[f"L{number:04d}"][0] != "Participant":
                raise ValueError(f"Non-participant line in revised segment: {row}")

    ROUND2_RUN.mkdir(parents=True, exist_ok=True)
    QUALITATIVE.mkdir(parents=True, exist_ok=True)
    segments.to_csv(
        ROUND2_RUN / "coded_segments_master_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    segments.to_csv(
        QUALITATIVE / "coded_segments_master.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return segments


def revise_codebook(segments: pd.DataFrame) -> None:
    codebook = pd.read_csv(
        SOURCE_RUN / "qualitative_synthesis/proposed_qualitative_codebook.csv",
        dtype=str,
        keep_default_na=False,
    )
    codebook.loc[
        codebook["code_id"].eq("GRADUAL_ADAPTATION_PATH"), "status"
    ] = "ACTIVE"
    used = set(segments["primary_code"]) | set(segments["secondary_code"]) - {""}
    active = set(
        codebook.loc[codebook["status"].isin(["ACTIVE", "PROPOSED"]), "code_id"]
    )
    if used - active:
        raise ValueError(f"Unknown revised codes: {sorted(used - active)}")
    codebook.to_csv(
        ROUND2_RUN / "qualitative_codebook_v2_full.csv",
        index=False,
        encoding="utf-8-sig",
    )

    public = codebook.loc[codebook["status"].isin(["ACTIVE", "PROPOSED"])].copy()
    inductive = public["source"].isin(["INDUCTIVE", "MIXED"])
    public.loc[inductive, "example"] = ""
    public.loc[inductive, "notes"] = public.loc[inductive, "status"].map(
        {
            "ACTIVE": "经独立复核后已应用的归纳过程码；不用于频率或类型推断。",
            "PROPOSED": "解释性候选概念，尚未系统回填全部片段；不用于频率或覆盖判断。",
        }
    )
    public.to_csv(
        PROCESSED / "qualitative_codebook.csv",
        index=False,
        encoding="utf-8-sig",
    )


def revise_framework() -> pd.DataFrame:
    framework = pd.read_csv(
        QUALITATIVE / "framework_matrix.csv", dtype=str, keep_default_na=False
    )
    relationship = framework["theme"].eq("归属、网络、求助与亲密关系分层")
    framework.loc[relationship, "P01_summary"] = (
        "问卷认可复合“信任并谈心”陈述，访谈却否认有能够交心的朋友，"
        "构成未解决的直接分歧；功能支持另行存在。"
    )
    framework.loc[relationship, "shared_pattern"] = (
        "成员感、复合“信任并谈心”题、求助可用性、朋友圈构成和深层亲密"
        "应分开分析；问卷本身不能拆出信任与谈心的各自比例。"
    )
    tension = framework["theme"].eq("问卷—访谈测量张力")
    framework.loc[tension, "P01_summary"] = (
        "英文材料与英文口语是相邻但不同内容域；复合“信任并谈心”题与"
        "访谈否认交心构成直接分歧。"
    )
    framework.loc[tension, "P02_summary"] = (
        "入学年级不一致且访谈现场错配问卷；总体友好印象只扩展、"
        "不反驳问卷中的具体地方知识边界。"
    )
    framework.loc[tension, "shared_pattern"] = (
        "只在同一构念、重叠时段和相反方向时判为分歧；其他不等价配对"
        "改为扩展或沉默。"
    )
    framework.to_csv(
        ROUND2_RUN / "framework_matrix_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    framework.to_csv(
        QUALITATIVE / "framework_matrix.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return framework


def adjudicate_alignments() -> pd.DataFrame:
    outputs = []
    for participant in ["P01", "P02", "P03"]:
        frame = pd.read_csv(
            SOURCE_RUN / participant / "survey_interview_alignment.csv",
            dtype=str,
            keep_default_na=False,
        )
        revised_rows = []
        for row in frame.to_dict("records"):
            original = row["relationship_type"]
            key = (participant, row["survey_variable"])
            final, decision = RELATION_OVERRIDES.get(
                key,
                (
                    original,
                    "逐行复核后保留原关系类型；未发现更强的构念、时段或方向冲突。",
                ),
            )
            if final == "CONVERGENCE":
                same_construct, overlap, opposite = "TRUE", "TRUE", "FALSE"
            elif final == "DIVERGENCE":
                same_construct, overlap, opposite = "TRUE", "TRUE", "TRUE"
            elif final == "EXPANSION":
                same_construct, overlap, opposite = (
                    "PARTIAL_OR_ADJACENT",
                    "UNCERTAIN_OR_BROADER",
                    "FALSE",
                )
            else:
                same_construct, overlap, opposite = (
                    "NOT_ASSESSABLE",
                    "NOT_ASSESSABLE",
                    "NOT_ASSESSABLE",
                )
            row["original_relationship_type"] = original
            row["same_construct"] = same_construct
            row["overlapping_timeframe"] = overlap
            row["opposite_direction"] = opposite
            row["relationship_type"] = final
            row["adjudication_decision"] = decision
            revised_rows.append(row)
        revised = pd.DataFrame(revised_rows)
        revised.to_csv(
            ROUND2_RUN / f"{participant}_survey_interview_alignment_v2.csv",
            index=False,
            encoding="utf-8-sig",
        )
        outputs.append(revised)
    combined = pd.concat(outputs, ignore_index=True)
    invalid_divergence = combined[
        combined["relationship_type"].eq("DIVERGENCE")
        & ~(
            combined["same_construct"].eq("TRUE")
            & combined["overlapping_timeframe"].eq("TRUE")
            & combined["opposite_direction"].eq("TRUE")
        )
    ]
    if not invalid_divergence.empty:
        raise ValueError("A revised divergence failed the three-part comparability rule")
    combined.to_csv(
        ROUND2_RUN / "alignment_adjudication_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary = (
        combined.groupby(["original_relationship_type", "relationship_type"])
        .size()
        .rename("n")
        .reset_index()
    )
    summary.to_csv(
        ROUND2_RUN / "alignment_relationship_summary_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return combined


def main() -> None:
    ROUND2_RUN.mkdir(parents=True, exist_ok=True)
    segments = revise_segments()
    revise_codebook(segments)
    revise_framework()
    alignments = adjudicate_alignments()
    counts = alignments["relationship_type"].value_counts().to_dict()
    print(
        f"qualitative v2 revised segments={len(segments)} "
        f"alignments={len(alignments)} relationships={counts}"
    )


if __name__ == "__main__":
    main()
