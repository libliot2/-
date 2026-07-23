#!/usr/bin/env python3
"""Small, theory-constrained second-round explorations and robustness checks."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from analyze_survey import CONSTRUCTS, ORDINAL_LABELS, ordinal
from pipeline_common import ROOT


PROCESSED = ROOT / "data/processed"
TABLES = ROOT / "outputs/tables"
REPORTS = ROOT / "outputs/reports"
ROUND2_RUN = ROOT / "outputs/agent_runs/20260723_independent_review_extension_v2"
REVISED_QUAL = ROUND2_RUN / "revised_qualitative"

FINDING_CLASSES = {
    "robust finding",
    "plausible exploratory finding",
    "weak signal",
    "unsupported",
}

SUPPORT_LABELS = {
    "q5_5_cantonese_support": "粤语日常交流支持",
    "q5_5_english_support": "英文教材或英语学习适应支持",
    "q5_5_traditional_chinese_support": "繁体字及学科词汇支持",
    "q5_5_assessment_rules_support": "课程、作业和评分规则说明",
    "q5_5_participation_presentation_support": "课堂参与、小组合作和口头汇报训练",
    "q5_5_peer_buddy_support": "朋辈伙伴或学习伙伴支持",
    "q5_5_emotional_anti_exclusion_support": "情绪支持、归属感支持或反排斥支持",
    "q5_5_parent_system_explanation_support": "向家长解释香港学校制度和要求",
}

SUPPORT_STATUS = {
    "已获得，而且帮助较大": "received_major_help",
    "已获得，但帮助有限": "received_limited_help",
    "没有获得，但希望获得": "unmet_wanted",
}

PLATFORM_LABELS = {
    "wechat": "微信或朋友圈",
    "qq": "QQ或QQ空间",
    "xiaohongshu": "小红书",
    "bilibili": "哔哩哔哩",
    "douyin": "抖音",
    "whatsapp": "WhatsApp",
    "instagram": "Instagram",
    "youtube": "YouTube",
    "discord": "Discord",
    "telegram": "Telegram",
    "game_chat": "线上游戏内聊天",
}

Q5_4_LABELS = {
    "q5_4_help_homeroom_teacher": "班主任",
    "q5_4_help_subject_teacher": "科任老师",
    "q5_4_help_hk_peer": "香港本地同学",
    "q5_4_help_mainland_peer": "具有内地生活或教育背景的同学",
    "q5_4_help_family": "父母或其他家庭成员",
    "q5_4_help_counselling": "学校辅导或心理支持",
    "q5_4_help_school_orientation": "学校迎新、适应课程或朋辈辅导",
    "q5_4_help_tutor": "补习老师或校外教育机构",
    "q5_4_help_online_info": "网络平台、论坛或社交媒体信息",
    "q5_4_help_other": "其他",
    "q5_4_help_none": "没有获得明显帮助",
}


def public_count(value: int) -> str:
    return "<3" if value < 3 else str(value)


def public_percent(value: int, denominator: int) -> str:
    return "SUPPRESSED" if value < 3 else f"{100 * value / denominator:.1f}%"


def add_row(
    rows: list[dict[str, Any]],
    finding_id: str,
    domain: str,
    finding_class: str,
    analysis: str,
    numerator: str | int = "",
    denominator: str | int = "",
    estimate: str = "",
    sensitivity_result: str = "",
    evidence_source: str = "",
    interpretation_limit: str = "",
) -> None:
    if finding_class not in FINDING_CLASSES:
        raise ValueError(f"Invalid finding class: {finding_class}")
    rows.append(
        {
            "finding_id": finding_id,
            "domain": domain,
            "finding_class": finding_class,
            "analysis": analysis,
            "numerator": numerator,
            "denominator": denominator,
            "estimate": estimate,
            "sensitivity_result": sensitivity_result,
            "evidence_source": evidence_source,
            "interpretation_limit": interpretation_limit,
        }
    )


def eligible_survey() -> pd.DataFrame:
    frame = pd.read_csv(
        PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False
    )
    return frame.loc[frame["eligible"].eq("TRUE")].copy()


def linked_case_positions(
    frame: pd.DataFrame, rows: list[dict[str, Any]]
) -> pd.DataFrame:
    scores = pd.read_csv(PROCESSED / "survey_construct_scores.csv")
    mapping = pd.read_csv(
        PROCESSED / "interview_survey_map.csv", dtype=str, keep_default_na=False
    )
    score_columns = [
        "peer_cultural_boundary",
        "school_belonging",
        "academic_difficulty",
        "academic_rule_understanding",
        "unmet_support_count",
    ]
    merged = mapping.merge(scores, on="survey_row_id", validate="one_to_one")
    position_rows = []
    for record in merged.itertuples(index=False):
        for column in score_columns:
            distribution = scores[column].dropna()
            value = float(getattr(record, column))
            q1 = float(distribution.quantile(0.25, interpolation="midpoint"))
            q3 = float(distribution.quantile(0.75, interpolation="midpoint"))
            if value < q1:
                broad_position = "BELOW_SAMPLE_IQR"
            elif value > q3:
                broad_position = "ABOVE_SAMPLE_IQR"
            else:
                broad_position = "WITHIN_SAMPLE_IQR"
            percentile = 100 * float((distribution <= value).mean())
            position_rows.append(
                {
                    "participant_id": record.participant_id,
                    "construct": column,
                    "case_value": value,
                    "sample_q1": q1,
                    "sample_median": float(distribution.median()),
                    "sample_q3": q3,
                    "empirical_percentile_le": percentile,
                    "broad_position": broad_position,
                }
            )
            if record.participant_id in {"P01", "P02"}:
                add_row(
                    rows,
                    f"CASEPOS_{record.participant_id}_{column}",
                    "linked_case_position",
                    "plausible exploratory finding",
                    f"{record.participant_id}：{column} 的样本内宽位置",
                    estimate=broad_position,
                    evidence_source=(
                        "data/processed/survey_construct_scores.csv;"
                        "data/processed/interview_survey_map.csv"
                    ),
                    interpretation_limit=(
                        "只作当前35份样本内定位；不是抽样代表性、类型或总体百分位。"
                    ),
                )
    restricted = ROUND2_RUN / "restricted_extension"
    restricted.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(position_rows)
    result.to_csv(
        restricted / "linked_case_position_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return result


def support_status_analysis(
    frame: pd.DataFrame, rows: list[dict[str, Any]]
) -> pd.DataFrame:
    status_rows = []
    valid_categories = set(SUPPORT_STATUS) | {"没有获得，也不需要"}
    for variable, label in SUPPORT_LABELS.items():
        valid = frame.loc[frame[variable].isin(valid_categories), variable]
        for status, status_id in SUPPORT_STATUS.items():
            count = int(valid.eq(status).sum())
            status_rows.append(
                {
                    "variable_name": variable,
                    "support_label": label,
                    "status": status_id,
                    "valid_n": len(valid),
                    "n": count,
                    "percentage": 100 * count / len(valid),
                }
            )
            add_row(
                rows,
                f"SUPPORT_{variable}_{status_id}",
                "support_status",
                "robust finding",
                f"{label}：{status_id}",
                numerator=public_count(count),
                denominator=len(valid),
                estimate=public_percent(count, len(valid)),
                evidence_source="data/processed/survey_clean.csv",
                interpretation_limit=(
                    "当前非概率样本的直接状态分布；不估计总体需求率或支持效果。"
                ),
            )
    result = pd.DataFrame(status_rows)
    restricted = ROUND2_RUN / "restricted_extension"
    result.to_csv(
        restricted / "support_three_status_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return result


def support_source_sensitivity(
    frame: pd.DataFrame, rows: list[dict[str, Any]]
) -> pd.DataFrame:
    ordinary = list(Q5_4_LABELS)
    group_valid = ~frame["q5_4_help_cannot_remember"].eq("选择")
    selected_count = frame[ordinary].eq("选择").sum(axis=1)
    compliant = group_valid & selected_count.le(3)
    result_rows = []
    for variable, label in Q5_4_LABELS.items():
        full_n = int(frame.loc[group_valid, variable].eq("选择").sum())
        strict_n = int(frame.loc[compliant, variable].eq("选择").sum())
        result_rows.append(
            {
                "variable_name": variable,
                "source_label": label,
                "endorsement_valid_n": int(group_valid.sum()),
                "endorsement_n": full_n,
                "limit_compliant_valid_n": int(compliant.sum()),
                "limit_compliant_n": strict_n,
            }
        )
        add_row(
            rows,
            f"Q54_{variable}",
            "support_source_sensitivity",
            "plausible exploratory finding",
            f"{label}：全有效回答与限选合规子集",
            numerator=public_count(full_n),
            denominator=int(group_valid.sum()),
            estimate=public_percent(full_n, int(group_valid.sum())),
            sensitivity_result=(
                f"limit-compliant {public_count(strict_n)}/{int(compliant.sum())}"
            ),
            evidence_source="data/processed/survey_clean.csv",
            interpretation_limit=(
                "表单未执行最多三项；主结果是勾选率，合规子集只是敏感性检查。"
            ),
        )
    result = pd.DataFrame(result_rows)
    result.to_csv(
        ROUND2_RUN / "restricted_extension/support_source_sensitivity_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return result


def platform_pair_analysis(
    frame: pd.DataFrame, rows: list[dict[str, Any]]
) -> pd.DataFrame:
    pre_valid = ~(
        frame["q6_1_pre_cannot_remember"].eq("选择")
        | frame["q6_1_pre_unwilling"].eq("选择")
    )
    later_valid = ~(
        frame["q6_2_later_cannot_remember"].eq("选择")
        | frame["q6_2_later_unwilling"].eq("选择")
    )
    paired_valid = pre_valid & later_valid
    result_rows = []
    for key, label in PLATFORM_LABELS.items():
        pre = frame.loc[paired_valid, f"q6_1_pre_{key}"].eq("选择")
        later = frame.loc[paired_valid, f"q6_2_later_{key}"].eq("选择")
        states = {
            "retained": int((pre & later).sum()),
            "adopted": int((~pre & later).sum()),
            "stopped": int((pre & ~later).sum()),
            "neither": int((~pre & ~later).sum()),
        }
        for state, count in states.items():
            result_rows.append(
                {
                    "platform": label,
                    "state": state,
                    "paired_valid_n": int(paired_valid.sum()),
                    "n": count,
                    "percentage": 100 * count / int(paired_valid.sum()),
                }
            )
            add_row(
                rows,
                f"PLATFORM_{key}_{state}",
                "paired_platform_transition",
                "robust finding",
                f"{label}：{state}",
                numerator=public_count(count),
                denominator=int(paired_valid.sum()),
                estimate=public_percent(count, int(paired_valid.sum())),
                evidence_source="data/processed/survey_clean.csv",
                interpretation_limit=(
                    "同一参与者的两段回顾性勾选；说明媒体组合，不说明融入、身份或平台效果。"
                ),
            )
    result = pd.DataFrame(result_rows)
    result.to_csv(
        ROUND2_RUN / "restricted_extension/platform_paired_transition_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return result


def platform_function_analysis(
    frame: pd.DataFrame, rows: list[dict[str, Any]]
) -> pd.DataFrame:
    labels = {
        "q6_5_separate_relations": "分别维持内地与香港关系",
        "q6_5_different_expression": "不同平台采用不同表达",
        "q6_5_hk_platform_participation": "香港常用平台帮助参与活动或获取校内信息",
        "q6_5_old_network_emotional_support": "旧平台与老友网络提供情绪支持",
        "q6_5_multiple_roles": "多个平台承担不同作用",
        "q6_5_online_rule_barrier": "平台或线上规则形成信息/参与障碍",
    }
    result_rows = []
    for variable, label in labels.items():
        values = ordinal(frame[variable])
        count = int(values.ge(4).sum())
        valid_n = int(values.notna().sum())
        result_rows.append(
            {
                "variable_name": variable,
                "item_label": label,
                "positive_n": count,
                "valid_n": valid_n,
                "positive_percentage": 100 * count / valid_n,
            }
        )
        add_row(
            rows,
            f"PLATFORM_FUNCTION_{variable}",
            "platform_function",
            "robust finding",
            label,
            numerator=public_count(count),
            denominator=valid_n,
            estimate=public_percent(count, valid_n),
            evidence_source="data/processed/survey_clean.csv",
            interpretation_limit=(
                "题项自报的功能或经验，不验证平台机制、实际行为频率或文化融入。"
            ),
        )
    return pd.DataFrame(result_rows)


def construct_score(
    frame: pd.DataFrame,
    variables: list[str],
    required_fraction: float,
    aggregation: str,
) -> pd.Series:
    numeric = pd.DataFrame({column: ordinal(frame[column]) for column in variables})
    required = math.ceil(len(variables) * required_fraction)
    if aggregation == "mean":
        score = numeric.mean(axis=1, skipna=True)
    elif aggregation == "median":
        score = numeric.median(axis=1, skipna=True)
    else:
        raise ValueError(aggregation)
    return score.where(numeric.notna().sum(axis=1) >= required)


def spearman_pair(x: pd.Series, y: pd.Series) -> tuple[int, float]:
    pair = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    return len(pair), float(spearmanr(pair["x"], pair["y"]).statistic)


def leave_one_out_range(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    pair = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    estimates = []
    for index in pair.index:
        reduced = pair.drop(index)
        estimates.append(float(spearmanr(reduced["x"], reduced["y"]).statistic))
    return min(estimates), max(estimates)


def association_robustness(
    frame: pd.DataFrame, rows: list[dict[str, Any]]
) -> pd.DataFrame:
    result_rows = []
    variants = [
        ("A1_standard_80pct_mean", 0.8, "mean"),
        ("A1_complete_case_mean", 1.0, "mean"),
        ("A1_60pct_mean", 0.6, "mean"),
        ("A1_80pct_median", 0.8, "median"),
    ]
    for variant, fraction, aggregation in variants:
        boundary = construct_score(
            frame, CONSTRUCTS["peer_cultural_boundary"], fraction, aggregation
        )
        belonging = construct_score(
            frame, CONSTRUCTS["school_belonging"], fraction, aggregation
        )
        valid_n, rho = spearman_pair(boundary, belonging)
        loo_low, loo_high = leave_one_out_range(boundary, belonging)
        result_rows.append(
            {
                "analysis_id": variant,
                "valid_n": valid_n,
                "rho": rho,
                "loo_rho_min": loo_low,
                "loo_rho_max": loo_high,
                "finding_class": "plausible exploratory finding",
            }
        )
        add_row(
            rows,
            f"ROBUST_{variant}",
            "association_robustness",
            "plausible exploratory finding",
            variant,
            denominator=valid_n,
            estimate=f"rho={rho:.3f}",
            sensitivity_result=f"leave-one-out [{loo_low:.3f}, {loo_high:.3f}]",
            evidence_source="data/processed/survey_clean.csv",
            interpretation_limit=(
                "方向对计分与单案删除较稳，但资格口径事后扩展、样本非概率且为回顾性；不支持因果。"
            ),
        )

    explain = frame["q4_1_explain_differences"].map(ORDINAL_LABELS).astype(float)
    reduce = frame["q4_1_reduce_misunderstanding"].map(ORDINAL_LABELS).astype(float)
    fatigue = frame["q4_1_brokerage_fatigue"].map(ORDINAL_LABELS).astype(float)
    alternative = pd.concat([explain, reduce], axis=1).mean(axis=1, skipna=True)
    complete_alternative = alternative.where(
        pd.concat([explain, reduce], axis=1).notna().sum(axis=1).eq(2)
    )
    for variant, x in [
        ("A4_original_explain_item", explain),
        ("A4_participation_mean_at_least_one_item", alternative),
        ("A4_participation_mean_both_items", complete_alternative),
    ]:
        valid_n, rho = spearman_pair(x, fatigue)
        loo_low, loo_high = leave_one_out_range(x, fatigue)
        result_rows.append(
            {
                "analysis_id": variant,
                "valid_n": valid_n,
                "rho": rho,
                "loo_rho_min": loo_low,
                "loo_rho_max": loo_high,
                "finding_class": "weak signal",
            }
        )
        add_row(
            rows,
            f"ROBUST_{variant}",
            "association_robustness",
            "weak signal",
            variant,
            denominator=valid_n,
            estimate=f"rho={rho:.3f}",
            sensitivity_result=f"leave-one-out [{loo_low:.3f}, {loo_high:.3f}]",
            evidence_source="data/processed/survey_clean.csv",
            interpretation_limit=(
                "对合理参与编码不稳，只能描述特定单项；不得进入主体发现或解释为中介保护作用。"
            ),
        )
    result = pd.DataFrame(result_rows)
    result.to_csv(
        ROUND2_RUN / "restricted_extension/association_robustness_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return result


def qualitative_configuration(
    rows: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    configuration = pd.DataFrame(
        [
            {
                "participant_id": "P01",
                "initial_interfaces": "口语任务、表达限制、组队速度",
                "entry_arrangement": "同背景同伴带入信息与关系",
                "support_configuration": "非正式翻译、规则说明、午餐与介绍朋友",
                "later_relationship_pattern": "功能支持与复合信任谈心题分歧并存",
                "tradeoff_or_negative_case": "支持安全圈与跨背景拓展动力下降并存",
                "evidence": "P01 L0010; L0016-L0018; L0021-L0023",
            },
            {
                "participant_id": "P02",
                "initial_interfaces": "地区粤语接口、一般友好与具体适应压力",
                "entry_arrangement": "同伴主动接近、少数密友",
                "support_configuration": "亲属住宿、即时答疑、朋友代为沟通；偏好不显眼支持",
                "later_relationship_pattern": "广泛可相处与少数深关系并存",
                "tradeoff_or_negative_case": "希望支持可获得但反对过度特殊关照",
                "evidence": "P02 L0024; L0041; L0092-L0093; L0212; L0239-L0246",
            },
            {
                "participant_id": "P03",
                "initial_interfaces": "快速粤语、自由分组、课程与任务摩擦",
                "entry_arrangement": "同桌放慢语速并邀请参与",
                "support_configuration": "同伴、家庭资源与较晚教师介入组合",
                "later_relationship_pattern": "核心关系与稳定群体自评张力并存",
                "tradeoff_or_negative_case": "较低问卷困难位置与具体摩擦叙述并存",
                "evidence": "restricted third-case line ranges",
            },
        ]
    )
    leave_one_case_out = pd.DataFrame(
        [
            {
                "theme_id": "CFG01",
                "theme": "任务、语言与关系进入在具体场景交叠",
                "direct_support_cases_n": 1,
                "partial_support_cases_n": 2,
                "survives_removing_any_one_case": "NO",
                "finding_class": "plausible exploratory finding",
                "decision": "只有受限第三案例提供完整同场景事件链；不得写成三案共同机制。",
            },
            {
                "theme_id": "CFG02",
                "theme": "支持的来源、正式度、时机与可见性需分开",
                "direct_support_cases_n": 3,
                "partial_support_cases_n": 0,
                "survives_removing_any_one_case": "YES",
                "finding_class": "plausible exploratory finding",
                "decision": "三案以不同配置支持；仍只作回顾性个案解释。",
            },
            {
                "theme_id": "CFG03",
                "theme": "成员感、复合信任谈心题、求助、亲密与群体门槛不等价",
                "direct_support_cases_n": 3,
                "partial_support_cases_n": 0,
                "survives_removing_any_one_case": "YES",
                "finding_class": "plausible exploratory finding",
                "decision": "跨案仍成立，但问卷复合题不能拆成信任和谈心的总体比例。",
            },
            {
                "theme_id": "CFG04",
                "theme": "稳定文化中介角色",
                "direct_support_cases_n": 1,
                "partial_support_cases_n": 0,
                "survives_removing_any_one_case": "NO",
                "finding_class": "weak signal",
                "decision": "仅有一项明确学校差异解释事件；不进入主体发现。",
            },
            {
                "theme_id": "CFG05",
                "theme": "访谈中的平台—受众—功能机制",
                "direct_support_cases_n": 0,
                "partial_support_cases_n": 0,
                "survives_removing_any_one_case": "YES",
                "finding_class": "robust finding",
                "decision": "三份访谈均无可核对机制链；只说明访谈证据沉默，不说明平台无作用。",
            },
        ]
    )
    restricted = ROUND2_RUN / "restricted_extension"
    configuration.to_csv(
        restricted / "case_configuration_matrix_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    leave_one_case_out.to_csv(
        restricted / "leave_one_case_out_themes_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    for record in leave_one_case_out.itertuples(index=False):
        if record.finding_class == "weak signal":
            continue
        add_row(
            rows,
            f"QUAL_{record.theme_id}",
            "qualitative_configuration",
            record.finding_class,
            record.theme,
            denominator=record.direct_support_cases_n + record.partial_support_cases_n,
            sensitivity_result=(
                f"leave-one-case-out={record.survives_removing_any_one_case}"
            ),
            evidence_source=(
                "outputs/agent_runs/20260723_independent_review_extension_v2/"
                "restricted_extension/case_configuration_matrix_v2.csv"
            ),
            interpretation_limit=record.decision,
        )
    return configuration, leave_one_case_out


def alignment_summary(rows: list[dict[str, Any]]) -> pd.DataFrame:
    alignment = pd.read_csv(
        REVISED_QUAL / "alignment_adjudication_v2.csv",
        dtype=str,
        keep_default_na=False,
    )
    summary = (
        alignment["relationship_type"]
        .value_counts()
        .rename_axis("relationship_type")
        .rename("n")
        .reset_index()
    )
    for record in summary.itertuples(index=False):
        add_row(
            rows,
            f"ALIGNMENT_{record.relationship_type}",
            "alignment_adjudication",
            "robust finding",
            f"75条对照经三条件复核后：{record.relationship_type}",
            numerator=int(record.n),
            denominator=len(alignment),
            estimate=f"{100 * int(record.n) / len(alignment):.1f}%",
            evidence_source=(
                "outputs/agent_runs/20260723_independent_review_extension_v2/"
                "revised_qualitative/alignment_adjudication_v2.csv"
            ),
            interpretation_limit="这是证据关系分类，不是参与者或主题频率。",
        )
    return summary


def write_report(
    positions: pd.DataFrame,
    support: pd.DataFrame,
    q54: pd.DataFrame,
    platforms: pd.DataFrame,
    platform_functions: pd.DataFrame,
    robustness: pd.DataFrame,
    theme_sensitivity: pd.DataFrame,
    alignment: pd.DataFrame,
) -> None:
    p01 = positions[positions["participant_id"].eq("P01")].set_index("construct")
    p02 = positions[positions["participant_id"].eq("P02")].set_index("construct")
    top_full = q54.sort_values("endorsement_n", ascending=False).head(2)
    support_pivot = support.pivot(
        index="support_label", columns="status", values=["n", "valid_n"]
    )
    platform_pivot = platforms.pivot(index="platform", columns="state", values="n")
    a1 = robustness[robustness["analysis_id"].str.startswith("A1_")]
    a4 = robustness[robustness["analysis_id"].str.startswith("A4_")]
    report = f"""# 第二轮补充探索

## 范围与分级

本轮只执行独立复核所指向的少量分析。`robust finding` 表示当前数据与预先写明规则下可重复的描述，不表示总体可推广；`plausible exploratory finding` 表示证据可追溯且有竞争解释；`weak signal` 只进入稳健性与未来研究；`unsupported` 解释不保留。公开表为 `outputs/tables/exploratory_extension_v2.csv`，第三案例精确位置、全部逐行对照和个案配置保留在受限层。

## 1. 三名访谈对象在完整问卷中的位置

P01 的同伴边界位于样本 IQR 内，学校归属低于样本 IQR，学业困难位于 IQR 内，规则理解低于 IQR，未满足支持数高于 IQR。P02 的五项位置均在样本 IQR 内。第三案例的精确位置只在受限表报告；公开可说的是，其较低学业困难问卷位置与访谈中的多项具体摩擦叙述并存。以上均为 `plausible exploratory finding`，只说明样本内对照位置，不说明统计代表性或访谈选择逻辑。

## 2. 问卷—访谈不一致的重新裁决

75 条对照全部增加“同构念、时段重叠、方向相反”三项判断。修订后的关系计数为：{", ".join(f"{row.relationship_type}={row.n}" for row in alignment.itertuples(index=False))}。P01 的复合“信任并谈心”问卷陈述与访谈否认交心被保留为直接 divergence；P02 的入学年级分歧也保留。英文材料—英文口语、初期—后期、限选未勾选、一般制度—评价规则及希望关注—反对显眼特殊关照等配对改为 expansion 或 silence。受限第三案例的明显任务强度分歧保留，但不在公开层连接匿名代号、背景和行号。

可能来源包括时间范围不重叠、问题内容域不同、量表压缩、长期回忆、限选格式、访谈提示和转写质量。没有把任一数据源指定为更真实。

## 3. 支持状态与支持缺口

Q5.5 的三种状态完整保留。较清楚的对照包括：朋辈伙伴支持的“帮助较大”为 {int(support_pivot.loc['朋辈伙伴或学习伙伴支持', ('n', 'received_major_help')])}/{int(support_pivot.loc['朋辈伙伴或学习伙伴支持', ('valid_n', 'received_major_help')])}，情绪/反排斥支持分别有 {int(support_pivot.loc['情绪支持、归属感支持或反排斥支持', ('n', 'received_major_help')])} 份“帮助较大”、{int(support_pivot.loc['情绪支持、归属感支持或反排斥支持', ('n', 'received_limited_help')])} 份“帮助有限”和 {int(support_pivot.loc['情绪支持、归属感支持或反排斥支持', ('n', 'unmet_wanted')])} 份“未获得但希望”。这些是 `robust finding` 的样本内状态分布，不是支持效果。

Q5.4 的导出没有执行“最多三项”。排除题组“记不清”后，被勾选最多的仍是 {top_full.iloc[0]['source_label']}（{top_full.iloc[0]['endorsement_n']}/{top_full.iloc[0]['endorsement_valid_n']}）和 {top_full.iloc[1]['source_label']}（{top_full.iloc[1]['endorsement_n']}/{top_full.iloc[1]['endorsement_valid_n']}）；在符合最多三项的子集中仍居前，但人数变为 {top_full.iloc[0]['limit_compliant_n']}/{top_full.iloc[0]['limit_compliant_valid_n']} 与 {top_full.iloc[1]['limit_compliant_n']}/{top_full.iloc[1]['limit_compliant_valid_n']}。排序稳定属于 `plausible exploratory finding`，不恢复“帮助最大三项”的严格含义。

访谈提示支持为何可能被评价为有限：零散非正式帮助不等于系统支持；支持到达过晚可能仍有缺口；显眼的特殊关照可能带来压力；家庭购买资源只是一种可得性配置。这些都是探索性解释，不能判断支持造成归属。

## 4. 平台的辅助作用

同一参与者的成对回顾显示：微信有 {int(platform_pivot.loc['微信或朋友圈', 'retained'])}/35 保留、{int(platform_pivot.loc['微信或朋友圈', 'stopped'])}/35 停用；WhatsApp 有 {int(platform_pivot.loc['WhatsApp', 'adopted'])}/35 后期采用；Instagram 有 {int(platform_pivot.loc['Instagram', 'adopted'])}/35 后期采用。它比边际百分点更直接显示“旧平台持续 + 新平台加入”的组合，属于当前样本内的 `robust finding`。

Q6.5 同时支持关系分开维持、旧网络情绪支持、校内信息参与和多平台角色等自报功能；逐项数字见公开表。三份访谈都没有足以核对的平台—受众—功能事件链，因此平台机制仍是访谈 silence。不能把平台采用解释为文化融入、身份转变或归属效果。

## 5. 机制、路径、负例与单案依赖

把人物命名的“三条路径”改为“初期接口—进入安排—支持配置—后期关系层次—教育路径”的配置矩阵后：

- 支持来源、正式度、时机与可见性必须分开，以及成员感、复合信任谈心题、求助、亲密和稳定群体门槛不等价，在逐一移除任一案例后仍可由其余材料支持；均为 `plausible exploratory finding`。
- “任务、语言与关系进入在同一事件链交叠”只有受限第三案例提供完整直接证据，P01/P02 只分别支持任务或同伴侧面；因此从“三案共同机制”降为单案依赖的 `plausible exploratory finding`。
- 稳定文化中介角色只剩有限的明确学校差异解释证据，属于 `weak signal`，不进入主体报告发现。
- 平台机制在三访谈中均沉默是对现有访谈覆盖的 `robust finding`，但不是现实中平台无作用。

## 6. 稳健性与结论分级

A1 在四种计分规格中的 ρ 范围为 {a1['rho'].min():.3f} 至 {a1['rho'].max():.3f}，各规格 leave-one-out 方向均保持负向。它被保留为 `plausible exploratory finding`：方向对缺失门槛、聚合和单案删除较稳，但资格口径在看过第一版结果后扩大，且数据不能识别方向或因果。

A4 在原单项规格和两种合理参与编码中的 ρ 从 {a4['rho'].min():.3f} 到 {a4['rho'].max():.3f}，强度明显变化；加上 V1 不通过 FDR，降为 `weak signal`。A3 对缺失处理方向近似不变但原检验未通过 FDR，也只保留为限制性信号。没有运行回归、因子分析、聚类或中介模型。

## 7. 删除的解释

下列解释因不受支持而不进入发现表或主体报告：平台采用代表文化融入；同伴或教师支持造成归属；一次差异解释构成稳定文化中介角色；三名访谈者代表完整样本；从回顾性配置确认单一路径。它们不作为新发现保留。
"""
    (REPORTS / "exploratory_extension_v2.md").write_text(report, encoding="utf-8")


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (ROUND2_RUN / "restricted_extension").mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    frame = eligible_survey()
    positions = linked_case_positions(frame, rows)
    support = support_status_analysis(frame, rows)
    q54 = support_source_sensitivity(frame, rows)
    platforms = platform_pair_analysis(frame, rows)
    platform_functions = platform_function_analysis(frame, rows)
    robustness = association_robustness(frame, rows)
    _, themes = qualitative_configuration(rows)
    alignment = alignment_summary(rows)
    public = pd.DataFrame(rows)
    if set(public["finding_class"]) - FINDING_CLASSES:
        raise ValueError("Invalid public finding classification")
    if public.astype(str).agg(" ".join, axis=1).str.contains(r"\bP03\b").any():
        raise ValueError("Restricted third-case ID leaked into public extension table")
    public.to_csv(
        TABLES / "exploratory_extension_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    write_report(
        positions,
        support,
        q54,
        platforms,
        platform_functions,
        robustness,
        themes,
        alignment,
    )
    print(
        f"extension v2 complete public_rows={len(public)} "
        f"restricted_positions={len(positions)}"
    )


if __name__ == "__main__":
    main()
