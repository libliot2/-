#!/usr/bin/env python3
"""Stage 6: build restricted linked survey-interview case profiles."""

from __future__ import annotations

from typing import Any

import pandas as pd

from pipeline_common import ROOT

PROCESSED = ROOT / "data/processed"


DIRECT_VARIABLES = [
    ("q1_3_entry_grade", "首次进入香港本地学校年级"),
    ("q2_1_current_status", "当前主要状态"),
    ("q2_2_current_residence", "当前主要居住地"),
    ("q2_5_hk_school_duration", "香港本地学校累计就读时长"),
    ("q2_6_hk_transfer_count", "后来转校次数"),
    ("q2_7_school_type", "就读时间最长的学校类型"),
    ("q2_11_cantonese_timing_uncertain", "粤语水平（时点不确定）"),
    ("q3_1_language_humour_barrier", "初期语言/幽默边界"),
    ("q3_1_local_knowledge_barrier", "初期地方知识边界"),
    ("q3_1_background_assumption", "初期背景预设"),
    ("q3_1_self_withdrawal", "初期因担忧而减少参与"),
    ("q3_3_member", "后期班级/学校成员感"),
    ("q3_3_trusted_peer", "后期可信任同学"),
    ("q3_3_authentic_self", "后期自然表现自己"),
    ("q4_1_explain_differences", "解释两地差异"),
    ("q4_1_reduce_misunderstanding", "帮助减少误解"),
    ("q4_1_brokerage_fatigue", "解释者疲惫"),
    ("q4_1_dual_marginality", "两边均非自己人担忧"),
    ("q5_1_english_materials", "初期英文材料困难"),
    ("q5_1_answer_format", "初期答题格式困难"),
    ("q5_1_presentation", "初期口头汇报困难"),
    ("q5_1_hidden_rules", "初期隐性规则困难"),
    ("q5_2_assessment_rules", "后期评价规则理解"),
    ("q5_2_transfer_prior_strengths", "后期迁移既有学习优势"),
    ("q5_2_distinguish_rules_ability", "区分规则陌生与能力不足"),
    ("q6_3_old_friend_platform", "后期联系内地旧友的主要平台"),
    ("q6_4_hk_peer_platform", "后期联系香港同学的主要平台"),
    ("q6_5_separate_relations", "不同平台维持不同关系"),
    ("q6_5_multiple_roles", "多个平台承担不同作用"),
    ("q7_1_peer_network", "后期同伴网络状态"),
]


def percentile(series: pd.Series, value: float) -> float:
    valid = pd.to_numeric(series, errors="coerce").dropna()
    return float((valid <= value).mean() * 100)


def format_direct(row: pd.Series) -> str:
    return "\n".join(f"- {label}：{row[variable]}" for variable, label in DIRECT_VARIABLES)


def format_indicators(
    participant_scores: pd.Series, all_scores: pd.DataFrame
) -> str:
    labels = {
        "peer_cultural_boundary": "同伴文化边界探索性指标",
        "school_belonging": "学校归属探索性指标",
        "academic_difficulty": "初期学业困难探索性指标",
        "academic_rule_understanding": "后期规则理解探索性指标",
        "unmet_support_count": "未满足支持项目数",
    }
    lines = []
    for variable, label in labels.items():
        value = float(participant_scores[variable])
        sample = pd.to_numeric(all_scores[variable], errors="coerce").dropna()
        if pd.isna(value):
            lines.append(f"- {label}：UNAVAILABLE（未达到派生指标完整度门槛）")
            continue
        rank = percentile(sample, value)
        lines.append(
            f"- {label}：{value:.2f}；完整样本 median={sample.median():.2f}，"
            f"IQR={sample.quantile(.25, interpolation='midpoint'):.2f}–"
            f"{sample.quantile(.75, interpolation='midpoint'):.2f}，"
            f"经验百分位（≤该值）={rank:.1f}%"
        )
    return "\n".join(lines)


def profile_warning(participant_id: str) -> str:
    if participant_id == "P01":
        return (
            "- 访谈来源是整理式记录而非完整逐字机器转写；`Source note` 不作直接引语。\n"
            "- 问卷开放题较短，访谈对其解释空间较大。"
        )
    if participant_id == "P02":
        return (
            "- 访谈开头显示访谈员现场调用了错误问卷；本项目仍严格按文件名唯一序号链接，"
            "并把问卷—访谈不一致当作需审查的分歧，而不据访谈内容改写映射。\n"
            "- 问卷报告首次插班年级与访谈自述存在一个年级阶段的差异，可能涉及教育体系称谓、"
            "回忆、填答或转写；不得擅自裁定哪一方正确。\n"
            "- 访谈为未经录音核对的机器转写。"
        )
    return "- 访谈为未经录音核对的机器转写；保留口语与可能的识别错误。"


def main() -> None:
    survey = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    mapping = pd.read_csv(PROCESSED / "interview_survey_map.csv", dtype=str, keep_default_na=False)
    scores = pd.read_csv(PROCESSED / "survey_construct_scores.csv")
    out_dir = PROCESSED / "linked_cases"
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    for link in mapping.itertuples(index=False):
        if link.mapping_status != "MATCHED":
            stale_profile = out_dir / f"{link.participant_id}_profile.md"
            if stale_profile.exists():
                stale_profile.unlink()
            note = f"""# {link.participant_id} 排除说明

- 链接状态：{link.mapping_status}
- 处理：保留映射和脱敏转录用于审计，不建立链接个案分析档案。
- 理由：问卷记录不满足研究入组条件；不得用访谈内容绕过资格筛选。
"""
            (out_dir / f"{link.participant_id}_exclusion_note.md").write_text(note, encoding="utf-8")
            continue
        stale_exclusion = out_dir / f"{link.participant_id}_exclusion_note.md"
        if stale_exclusion.exists():
            stale_exclusion.unlink()
        row = survey[survey["survey_row_id"] == link.survey_row_id].iloc[0]
        participant_scores = scores[scores["survey_row_id"] == link.survey_row_id].iloc[0]
        open_text = (
            f"- Q8.1：{row['q8_1_boundary_event_text']}\n"
            f"- Q8.2：{row['q8_2_support_request_text']}"
        )
        profile = f"""# {link.participant_id} 链接个案档案

> 受限内部分析文件。不得在公开报告中复制问卷序号或组合背景细节。

## Participant ID

{link.participant_id}

## Linkage status

- 状态：MATCHED
- 受限内部问卷序号：{link.questionnaire_sequence}
- 内部 survey row ID：{link.survey_row_id}
- 访谈来源：`{link.interview_filename}`

## Survey background

{format_direct(row)}

## Core questionnaire responses

上述条目均为参与者直接问卷回答；不把“后期”回答当作实测纵向变化。

## Survey open-text responses

{open_text}

## Derived exploratory indicators

{format_indicators(participant_scores, scores)}

这些均为自编题项的描述性探索指标，不是验证量表；经验百分位只定位本样本，不使用“高/低”标签。

## Position relative to full sample

位置比较已并入上节的完整样本 median、IQR 和经验百分位。背景小格不作稀有组合排名。

## Interview source

- 编号转录：`data/processed/interviews/interview_{link.participant_id}_numbered.md`

## Selection rationale

项目材料没有记录访谈选择的典型、对照、极端或志愿案例理由；不得补造。

## Data-quality or interpretation warnings

- 问卷重复检查：{row['duplicate_flag']}
- 问卷质量标记：{row['data_quality_flag']}
{profile_warning(link.participant_id)}
"""
        (out_dir / f"{link.participant_id}_profile.md").write_text(profile, encoding="utf-8")
        created += 1
    print(f"linked profiles created={created}")


if __name__ == "__main__":
    main()
