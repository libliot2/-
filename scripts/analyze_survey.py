#!/usr/bin/env python3
"""Stage 5 complete-sample survey analysis."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from pipeline_common import (
    BLANK,
    CANNOT_REMEMBER,
    INVALID,
    NOT_APPLICABLE,
    ROOT,
    UNWILLING,
    safe_percent,
    write_csv,
)

PROCESSED = ROOT / "data/processed"
TABLES = ROOT / "outputs/tables"
REPORTS = ROOT / "outputs/reports"
SPECIAL = {BLANK, CANNOT_REMEMBER, INVALID, NOT_APPLICABLE, UNWILLING}

MULTISELECT_GROUP_SPECIAL = {
    "q2_8_": ["q2_8_language_cannot_remember", "q2_8_language_unwilling"],
    "q2_10_": ["q2_10_reason_unwilling"],
    "q3_2_": ["q3_2_help_cannot_remember"],
    "q5_3_": ["q5_3_good_student_cannot_remember"],
    "q5_4_": ["q5_4_help_cannot_remember"],
    "q6_1_pre_": ["q6_1_pre_cannot_remember", "q6_1_pre_unwilling"],
    "q6_2_later_": ["q6_2_later_cannot_remember", "q6_2_later_unwilling"],
}


CONSTRUCTS = {
    "peer_cultural_boundary": [
        "q3_1_language_humour_barrier",
        "q3_1_local_knowledge_barrier",
        "q3_1_background_assumption",
        "q3_1_mainland_grouping_assumption",
        "q3_1_self_withdrawal",
    ],
    "school_belonging": [
        "q3_3_member",
        "q3_3_trusted_peer",
        "q3_3_included_group",
        "q3_3_authentic_self",
        "q3_3_knows_help_peer",
    ],
    "academic_difficulty": [
        "q5_1_traditional_chinese",
        "q5_1_cantonese_class",
        "q5_1_english_materials",
        "q5_1_answer_format",
        "q5_1_class_participation",
        "q5_1_group_project",
        "q5_1_presentation",
        "q5_1_assessment_mix",
        "q5_1_hidden_rules",
    ],
    "academic_rule_understanding": [
        "q5_2_good_assignment",
        "q5_2_assessment_rules",
        "q5_2_discussion_rules",
        "q5_2_transfer_prior_strengths",
        "q5_2_distinguish_rules_ability",
    ],
}

ORDINAL_LABELS = {
    "几乎不用": 1,
    "偶尔使用": 2,
    "有时使用": 3,
    "经常使用": 4,
    "几乎每天使用": 5,
    "从未": 1,
    "很少": 2,
    "有时": 3,
    "经常": 4,
    "非常经常": 5,
    "完全不同意": 1,
    "比较不同意": 2,
    "不确定": 3,
    "比较同意": 4,
    "完全同意": 5,
    "完全不困难": 1,
    "比较不困难": 2,
    "一般": 3,
    "比较困难": 4,
    "非常困难": 5,
}


def eligible_frame() -> pd.DataFrame:
    frame = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    eligible = frame[frame["eligible"] == "TRUE"].copy()
    for column in eligible:
        eligible[column] = eligible[column].map(lambda value: value.strip() if isinstance(value, str) else value)
    return eligible


def ordinal(series: pd.Series) -> pd.Series:
    return series.map(ORDINAL_LABELS).astype(float)


def quantiles(values: pd.Series) -> tuple[float, float, float]:
    values = values.dropna()
    if values.empty:
        return math.nan, math.nan, math.nan
    return (
        float(values.median()),
        float(values.quantile(0.25, interpolation="midpoint")),
        float(values.quantile(0.75, interpolation="midpoint")),
    )

def multiselect_valid_mask(frame: pd.DataFrame, variable: str) -> pd.Series:
    for prefix, special_columns in MULTISELECT_GROUP_SPECIAL.items():
        if variable.startswith(prefix) and variable not in special_columns:
            available = [column for column in special_columns if column in frame]
            if available:
                return ~frame[available].eq("选择").any(axis=1)
    return pd.Series(True, index=frame.index)


def write_sample_characteristics(frame: pd.DataFrame) -> None:
    variables = {
        "q2_1_current_status": "当前主要状态",
        "q2_2_current_residence": "当前主要居住地",
        "q2_3_gender": "性别",
        "q1_3_entry_grade": "首次香港本地学校插班年级",
        "q2_5_hk_school_duration": "香港本地学校累计就读时长",
        "q2_6_hk_transfer_count": "后续转校次数",
        "q2_7_school_type": "就读时间最长的学校类型",
        "q2_9_prior_region": "迁港前主要就学地区",
        "q2_11_cantonese_timing_uncertain": "粤语水平（时点不确定）",
        "q4_2_overall_fit": "当前总体适合感",
        "q7_1_peer_network": "香港校内后期同伴网络",
    }
    rows: list[dict[str, Any]] = []
    for variable, label in variables.items():
        series = frame[variable]
        valid = series[~series.isin(SPECIAL)]
        valid_n = len(valid)
        for category, count in valid.value_counts().items():
            suppress = count < 3
            rows.append(
                {
                    "variable_name": variable,
                    "variable_label": label,
                    "category": category,
                    "valid_n": valid_n,
                    "n": "<3" if suppress else int(count),
                    "percentage": "SUPPRESSED" if suppress else f"{100 * count / valid_n:.1f}",
                    "small_cell_suppressed": "TRUE" if suppress else "FALSE",
                }
            )
        for special in [BLANK, NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING, INVALID]:
            count = int((series == special).sum())
            if count:
                rows.append(
                    {
                        "variable_name": variable,
                        "variable_label": label,
                        "category": special,
                        "valid_n": valid_n,
                        "n": "<3" if count < 3 else count,
                        "percentage": "",
                        "small_cell_suppressed": "TRUE" if count < 3 else "FALSE",
                    }
                )
    multiple_choice_variables = {
        **{
            "q2_8_language_cantonese": "教学语言：粤语",
            "q2_8_language_mandarin": "教学语言：普通话",
            "q2_8_language_english": "教学语言：英语",
            "q2_8_language_mixed": "教学语言：混合/其他课堂语言",
            "q2_8_language_other": "教学语言：其他",
        },
        **{
            "q2_10_reason_family_move": "迁移原因：家庭整体迁居",
            "q2_10_reason_parent_work": "迁移原因：父母工作或事业安排",
            "q2_10_reason_reunion": "迁移原因：与家人团聚",
            "q2_10_reason_different_education": "迁移原因：接受不同教育制度",
            "q2_10_reason_future_opportunity": "迁移原因：升学或未来发展机会",
            "q2_10_reason_personal": "迁移原因：个人意愿",
            "q2_10_reason_other": "迁移原因：其他",
        },
    }
    for variable, label in multiple_choice_variables.items():
        mask = multiselect_valid_mask(frame, variable)
        valid_n = int(mask.sum())
        count = int(frame.loc[mask, variable].eq("选择").sum())
        rows.append(
            {
                "variable_name": variable,
                "variable_label": label,
                "category": "选择",
                "valid_n": valid_n,
                "n": "<3" if count < 3 else count,
                "percentage": "SUPPRESSED" if count < 3 else f"{100 * count / valid_n:.1f}",
                "small_cell_suppressed": "TRUE" if count < 3 else "FALSE",
            }
        )
    write_csv(
        TABLES / "sample_characteristics.csv",
        [
            "variable_name",
            "variable_label",
            "category",
            "valid_n",
            "n",
            "percentage",
            "small_cell_suppressed",
        ],
        rows,
    )

    entry_year = pd.to_numeric(frame["q2_4_entry_year"], errors="coerce")
    duration = pd.to_numeric(frame["completion_seconds"], errors="coerce")
    report = f"""# 样本描述

合资格完整问卷样本为 **n={len(frame)}**。现有数据包没有提供足以确认具体招募方式的完整过程记录，因此按非概率样本处理；以下比例只描述本样本。

- 首次进入香港本地学校年份中位数为 {int(entry_year.median())} 年，范围 {int(entry_year.min())}–{int(entry_year.max())} 年（valid n={entry_year.notna().sum()}）。
- 完成问卷时间中位数为 {int(duration.median())} 秒（valid n={duration.notna().sum()}）。
- 背景分类频数见 `outputs/tables/sample_characteristics.csv`；为降低稀有组合披露风险，背景小格 `n<3` 已抑制。
- 学校教学语言和迁移原因是多选题，不能与单选背景类别相加比较。
- Q2.11 的时间措辞在最终问卷与导出之间不一致，因此只标为“粤语水平（时点不确定）”，不解释为明确的迁港前基线。
"""
    (REPORTS / "sample_description.md").write_text(report, encoding="utf-8")


def item_stats(frame: pd.DataFrame) -> pd.DataFrame:
    codebook = pd.read_csv(PROCESSED / "survey_codebook.csv", dtype=str, keep_default_na=False)
    rows: list[dict[str, Any]] = []
    excluded_roles = {"restricted_linkage", "excluded_privacy", "data_quality", "eligibility", "demographic", "open_text"}
    for spec in codebook.itertuples(index=False):
        if spec.variable_name not in frame or spec.analysis_role in excluded_roles:
            continue
        series = frame[spec.variable_name]
        if spec.response_type == "matrix" and spec.analysis_role != "support_gap":
            numeric = ordinal(series)
            median, q1, q3 = quantiles(numeric)
            valid_n = int(numeric.notna().sum())
            for score in range(1, 6):
                count = int((numeric == score).sum())
                rows.append(
                    {
                        "variable_name": spec.variable_name,
                        "question_id": spec.question_id,
                        "item_text": spec.source_column,
                        "analysis_role": spec.analysis_role,
                        "statistic_type": "ordinal_distribution",
                        "response_or_statistic": str(score),
                        "n": count,
                        "valid_n": valid_n,
                        "percentage": safe_percent(count, valid_n),
                        "median": f"{median:.2f}" if not math.isnan(median) else "",
                        "q1": f"{q1:.2f}" if not math.isnan(q1) else "",
                        "q3": f"{q3:.2f}" if not math.isnan(q3) else "",
                        "special_response_counts": "|".join(
                            f"{special}:{int((series == special).sum())}"
                            for special in [BLANK, NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING, INVALID]
                            if int((series == special).sum())
                        ),
                    }
                )
        elif spec.response_type in {"single_choice", "multiple_choice"} or spec.analysis_role == "support_gap":
            group_mask = (
                multiselect_valid_mask(frame, spec.variable_name)
                if spec.response_type == "multiple_choice"
                else pd.Series(True, index=frame.index)
            )
            valid = series[group_mask & ~series.isin(SPECIAL)]
            valid_n = len(valid)
            for category, count in valid.value_counts().items():
                rows.append(
                    {
                        "variable_name": spec.variable_name,
                        "question_id": spec.question_id,
                        "item_text": spec.source_column,
                        "analysis_role": spec.analysis_role,
                        "statistic_type": (
                            "support_status_distribution"
                            if spec.analysis_role == "support_gap"
                            else spec.response_type
                        ),
                        "response_or_statistic": category,
                        "n": int(count),
                        "valid_n": valid_n,
                        "percentage": safe_percent(int(count), valid_n),
                        "median": "",
                        "q1": "",
                        "q3": "",
                        "special_response_counts": "|".join(
                            f"{special}:{int((series == special).sum())}"
                            for special in [BLANK, NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING, INVALID]
                            if int((series == special).sum())
                        ),
                    }
                )
    result = pd.DataFrame(rows)
    result.to_csv(TABLES / "survey_item_statistics.csv", index=False, encoding="utf-8-sig")
    return result


def write_support_gaps(frame: pd.DataFrame) -> pd.DataFrame:
    codebook = pd.read_csv(PROCESSED / "survey_codebook.csv", dtype=str, keep_default_na=False)
    items = codebook[codebook["analysis_role"] == "support_gap"]
    rows = []
    categories = [
        "已获得，而且帮助较大",
        "已获得，但帮助有限",
        "没有获得，但希望获得",
        "没有获得，也不需要",
    ]
    for spec in items.itertuples(index=False):
        series = frame[spec.variable_name]
        valid = series[series.isin(categories)]
        row: dict[str, Any] = {
            "variable_name": spec.variable_name,
            "item_text": spec.source_column,
            "valid_n": len(valid),
        }
        for category in categories:
            count = int((valid == category).sum())
            key = {
                "已获得，而且帮助较大": "received_major_help",
                "已获得，但帮助有限": "received_limited_help",
                "没有获得，但希望获得": "unmet_wanted",
                "没有获得，也不需要": "not_received_not_needed",
            }[category]
            row[f"{key}_n"] = count
            row[f"{key}_pct"] = safe_percent(count, len(valid))
        row["blank_n"] = int((series == BLANK).sum())
        row["not_applicable_n"] = int((series == NOT_APPLICABLE).sum())
        row["cannot_remember_n"] = int((series == CANNOT_REMEMBER).sum())
        row["unwilling_n"] = int((series == UNWILLING).sum())
        row["invalid_n"] = int((series == INVALID).sum())
        rows.append(row)
    result = pd.DataFrame(rows).sort_values("unmet_wanted_n", ascending=False)
    result.to_csv(TABLES / "support_gap_analysis.csv", index=False, encoding="utf-8-sig")
    return result


def write_platform_transition(frame: pd.DataFrame) -> pd.DataFrame:
    platforms = [
        ("wechat", "微信或朋友圈"),
        ("qq", "QQ或QQ空间"),
        ("xiaohongshu", "小红书"),
        ("bilibili", "哔哩哔哩"),
        ("douyin", "抖音"),
        ("weibo", "微博"),
        ("whatsapp", "WhatsApp"),
        ("instagram", "Instagram"),
        ("youtube", "YouTube"),
        ("discord", "Discord"),
        ("telegram", "Telegram"),
        ("game_chat", "线上游戏内聊天"),
    ]
    pre_valid = ~(
        (frame["q6_1_pre_cannot_remember"] == "选择")
        | (frame["q6_1_pre_unwilling"] == "选择")
    )
    later_valid = ~(
        (frame["q6_2_later_cannot_remember"] == "选择")
        | (frame["q6_2_later_unwilling"] == "选择")
    )
    rows = []
    for key, label in platforms:
        pre_col = f"q6_1_pre_{key}"
        later_col = f"q6_2_later_{key}"
        pre_n = int((frame.loc[pre_valid, pre_col] == "选择").sum())
        pre_den = int(pre_valid.sum())
        if later_col in frame:
            later_n = int((frame.loc[later_valid, later_col] == "选择").sum())
            later_den = int(later_valid.sum())
            change = 100 * later_n / later_den - 100 * pre_n / pre_den
            later_pct = safe_percent(later_n, later_den)
            availability = "AVAILABLE"
        else:
            later_n, later_den, later_pct, change = "", "", "", math.nan
            availability = "MISSING_FROM_EXPORT"
        rows.append(
            {
                "platform": label,
                "pre_valid_n": pre_den,
                "pre_selected_n": pre_n,
                "pre_percentage": safe_percent(pre_n, pre_den),
                "later_valid_n": later_den,
                "later_selected_n": later_n,
                "later_percentage": later_pct,
                "percentage_point_change": f"{change:.1f}" if not math.isnan(change) else "",
                "later_export_status": availability,
            }
        )
    result = pd.DataFrame(rows)
    result.to_csv(TABLES / "platform_transition_analysis.csv", index=False, encoding="utf-8-sig")
    return result


def cronbach_alpha(complete: pd.DataFrame) -> float:
    if complete.shape[1] < 2 or len(complete) < 3:
        return math.nan
    item_variance = complete.var(axis=0, ddof=1).sum()
    total_variance = complete.sum(axis=1).var(ddof=1)
    if total_variance == 0:
        return math.nan
    k = complete.shape[1]
    return float((k / (k - 1)) * (1 - item_variance / total_variance))


def write_constructs(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    score_rows = pd.DataFrame({"survey_row_id": frame["survey_row_id"]})
    summary_rows = []
    for name, variables in CONSTRUCTS.items():
        numeric = pd.DataFrame({column: ordinal(frame[column]) for column in variables})
        required = math.ceil(len(variables) * 0.8)
        score = numeric.mean(axis=1, skipna=True).where(numeric.notna().sum(axis=1) >= required)
        complete = numeric.dropna()
        alpha = cronbach_alpha(complete)
        score_rows[name] = score
        median, q1, q3 = quantiles(score)
        summary_rows.append(
            {
                "construct_name": name,
                "item_count": len(variables),
                "scoring_rule": f"1–5 item mean; require at least {required} valid items",
                "scored_n": int(score.notna().sum()),
                "complete_case_n": len(complete),
                "median": f"{median:.2f}",
                "q1": f"{q1:.2f}",
                "q3": f"{q3:.2f}",
                "cronbach_alpha_exploratory": f"{alpha:.3f}" if not math.isnan(alpha) else "",
                "status": "RETAINED_DESCRIPTIVE",
                "warning": "Exploratory indicator; not a validated scale.",
            }
        )
    support_columns = [
        f"q5_5_{name}_support"
        for name in [
            "cantonese",
            "english",
            "traditional_chinese",
            "assessment_rules",
            "participation_presentation",
            "peer_buddy",
            "emotional_anti_exclusion",
            "parent_system_explanation",
        ]
    ]
    valid_support_categories = {
        "已获得，而且帮助较大",
        "已获得，但帮助有限",
        "没有获得，但希望获得",
        "没有获得，也不需要",
    }
    support_valid_n = frame[support_columns].isin(valid_support_categories).sum(axis=1)
    support_complete = support_valid_n >= math.ceil(len(support_columns) * 0.8)
    score_rows["support_items_valid_n"] = support_valid_n
    score_rows["unmet_support_count"] = (
        frame[support_columns]
        .eq("没有获得，但希望获得")
        .sum(axis=1)
        .where(support_complete)
    )
    score_rows["major_help_support_count"] = (
        frame[support_columns]
        .eq("已获得，而且帮助较大")
        .sum(axis=1)
        .where(support_complete)
    )
    score_rows.to_csv(PROCESSED / "survey_construct_scores.csv", index=False, encoding="utf-8-sig")
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(TABLES / "exploratory_constructs.csv", index=False, encoding="utf-8-sig")
    report = """# 探索性构念评估

本分析仅保留四个概念一致、方向一致且缺失可管理的描述性指标：同伴文化边界、学校归属、初期学业适应困难、后期学术规则理解。逐题得分为 1–5，至少 80% 题项有效才计算个人均值。

`outputs/tables/exploratory_constructs.csv` 报告完整个案数、中位数、IQR 和仅供诊断的 Cronbach α。α 不被用作“量表已验证”的证据；分析样本量为 35，各构念的实际有效 n 另见表中 `scored_n`，所有结果均属探索性。

文化中介参与、文化中介压力和平台功能分工没有合成为指标：其项目数少，且内容本身代表不同维度。它们保留逐项描述，避免为便利而把概念不同的内容合并。

支持项目数只在 8 个 Q5.5 项目中至少 7 项为四类有效状态时计算；`NOT_APPLICABLE`、`CANNOT_REMEMBER`、`UNWILLING_TO_ANSWER`、`BLANK` 和 `INVALID_RESPONSE` 都不计作“未获重大帮助”的 0。该规则与题组的 80% 完整度门槛一致。
"""
    (REPORTS / "construct_assessment.md").write_text(report, encoding="utf-8")
    return score_rows, summary


def permutation_spearman(x: np.ndarray, y: np.ndarray, seed: int) -> tuple[float, float]:
    x_rank = rankdata(x).astype(float)
    y_rank = rankdata(y).astype(float)
    x_centered = x_rank - x_rank.mean()
    y_centered = y_rank - y_rank.mean()
    denominator = math.sqrt(float(np.dot(x_centered, x_centered) * np.dot(y_centered, y_centered)))
    observed = float(np.dot(x_centered, y_centered) / denominator)
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(50000):
        permuted = rng.permutation(y_centered)
        permuted_rho = float(np.dot(x_centered, permuted) / denominator)
        exceed += abs(permuted_rho) >= abs(observed) - 1e-12
    return observed, (exceed + 1) / 50001


def bootstrap_spearman(x: np.ndarray, y: np.ndarray, seed: int) -> tuple[float, float, int]:
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(10000):
        indices = rng.integers(0, len(x), len(x))
        x_sample, y_sample = x[indices], y[indices]
        if len(np.unique(x_sample)) < 2 or len(np.unique(y_sample)) < 2:
            continue
        estimates.append(float(spearmanr(x_sample, y_sample).statistic))
    low, high = np.quantile(estimates, [0.025, 0.975])
    return float(low), float(high), len(estimates)


def bh_fdr(values: list[float]) -> list[float]:
    array = np.asarray(values, dtype=float)
    order = np.argsort(array)
    ranked = array[order] * len(array) / np.arange(1, len(array) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty(len(array), dtype=float)
    adjusted[order] = np.minimum(ranked, 1.0)
    return adjusted.tolist()


def write_associations(scores: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    score_indexed = scores.set_index("survey_row_id")
    frame_indexed = frame.set_index("survey_row_id")
    numeric_explain = ordinal(frame_indexed["q4_1_explain_differences"])
    numeric_fatigue = ordinal(frame_indexed["q4_1_brokerage_fatigue"])
    numeric_platform_roles = ordinal(frame_indexed["q6_5_multiple_roles"])
    cross_context_network = frame_indexed["q7_1_peer_network"].isin(
        {"同时维持几个不同背景的朋友圈", "根据课程、兴趣和场景进入不同群体"}
    ).astype(int)
    specs = [
        ("A1", "RQ1", score_indexed["peer_cultural_boundary"], score_indexed["school_belonging"], "初期同伴文化边界探索性均值", "后期学校归属探索性均值", "两个时点均为回顾性自报；相关不表示边界经历造成后期归属。"),
        ("A2", "RQ2", score_indexed["academic_difficulty"], score_indexed["academic_rule_understanding"], "初期教育适应困难探索性均值", "后期学术规则理解探索性均值", "初期困难与后期理解不是同一纵向量尺；正相关可来自暴露、回忆、反应方式或其他因素。"),
        ("A3", "RQ1/RQ2", score_indexed["major_help_support_count"], score_indexed["school_belonging"], "获得且帮助较大的支持项目数", "后期学校归属探索性均值", "支持项目数不等于支持强度；方向和共同原因均不能确定。"),
        ("A4", "RQ1", numeric_explain, numeric_fatigue, "解释两地差异单项", "解释者/中间人疲惫单项", "两个单项不构成量表；中介行为不能自动等同为压力。"),
        ("A5", "RQ3", numeric_platform_roles, cross_context_network, "多平台承担不同作用单项", "跨背景/情境化同伴网络指示变量", "网络类别被探索性二分且对照组小；平台实践不是融入或身份指标。"),
    ]
    rows = []
    short = pd.to_numeric(frame_indexed["completion_seconds"], errors="coerce").lt(300)
    for index, (analysis_id, rq, x, y, x_label, y_label, guardrail) in enumerate(specs, start=1):
        pair = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
        x_values = pair["x"].to_numpy(float)
        y_values = pair["y"].to_numpy(float)
        rho, p = permutation_spearman(x_values, y_values, 20260723 + index)
        ci_low, ci_high, boot_n = bootstrap_spearman(x_values, y_values, 20261723 + index)
        sensitivity = pair.loc[~short.reindex(pair.index).fillna(False)]
        sensitivity_rho = (
            float(spearmanr(sensitivity["x"], sensitivity["y"]).statistic)
            if len(sensitivity) >= 3 and sensitivity["x"].nunique() > 1 and sensitivity["y"].nunique() > 1
            else math.nan
        )
        rows.append(
            {
                "analysis_id": analysis_id,
                "research_question": rq,
                "x": x_label,
                "y": y_label,
                "method": "Spearman rho; two-sided Monte Carlo permutation (50,000)",
                "valid_n": len(pair),
                "effect_size_rho": rho,
                "p_permutation": p,
                "bootstrap_ci_95_lower": ci_low,
                "bootstrap_ci_95_upper": ci_high,
                "bootstrap_valid_resamples": boot_n,
                "bh_fdr_q": math.nan,
                "sensitivity_n_excluding_lt300s": len(sensitivity),
                "sensitivity_rho_excluding_lt300s": sensitivity_rho,
                "interpretation_guardrail": guardrail,
            }
        )
    adjusted = bh_fdr([row["p_permutation"] for row in rows])
    for row, q in zip(rows, adjusted, strict=True):
        row["bh_fdr_q"] = q
    result = pd.DataFrame(rows)
    result.to_csv(TABLES / "exploratory_associations.csv", index=False, encoding="utf-8-sig")
    retained = result.loc[result["bh_fdr_q"] < 0.05, "analysis_id"].tolist()
    report_rows = "\n".join(
        f"- `{row.analysis_id}`：valid n={row.valid_n}，ρ={row.effect_size_rho:.3f}，"
        f"bootstrap 95% CI=[{row.bootstrap_ci_95_lower:.3f}, {row.bootstrap_ci_95_upper:.3f}]，"
        f"置换 p={row.p_permutation:.4f}，BH-FDR q={row.bh_fdr_q:.4f}。"
        for row in result.itertuples(index=False)
    )
    report = f"""# 探索性关联分析

只运行五个由研究问题预先约束的 Spearman 相关：

{report_rows}

五个检验统一使用 BH-FDR 校正；校正后 q<0.05 的分析为：{", ".join(retained) if retained else "无"}。这些仍是口径扩展后非概率小样本中的探索性排序关联，不构成总体、因果或验证性结论。尤其是“初期困难—后期规则理解”的正相关可能反映回顾性对比、规则学习过程、共同反应方式或其他未测因素，不能解释为困难带来掌握；解释差异与疲惫的负向关联也不能解释为中介行为具有保护作用。未运行回归或因子分析。
"""
    (REPORTS / "exploratory_analysis.md").write_text(report, encoding="utf-8")
    return result


def write_open_text_summary(frame: pd.DataFrame) -> pd.DataFrame:
    definitions = [
        ("groupwork_turning_point", "小组作业/组队/汇报成为关系事件", ["小组", "组队", "project", "汇报"]),
        ("language_local_knowledge", "语言、粤语梗或本地知识边界", ["粤语", "本地", "话题", "梗", "听不懂", "插不上"]),
        ("active_invitation", "明确的同伴邀请或沟通调适词组索引", ["主动邀请", "邀请我", "叫我", "拉我", "放慢语速"]),
        ("distance_exclusion", "距离、落单、旁观或难以进入", ["距离", "落单", "旁观", "融不进", "游离", "插不进"]),
        ("explicit_rules_support", "希望清楚解释课程、答题或评分规则", ["评分", "规则", "课程", "教材", "答题", "课堂要求", "体系"]),
        ("peer_buddy_support", "明确的朋辈结对或分组支持词组索引", ["结对", "伙伴", "主动交流", "协助分组", "安排同学"]),
        ("emotional_time_support", "希望给予情绪支持或适应时间", ["情绪", "心理", "压力", "焦虑", "时间适应", "适应需要时间"]),
    ]
    rows = []
    for variable in ["q8_1_boundary_event_text", "q8_2_support_request_text"]:
        valid = frame.loc[frame[variable] != BLANK, variable]
        for theme_id, label, keywords in definitions:
            count = int(valid.map(lambda text: any(keyword.lower() in text.lower() for keyword in keywords)).sum())
            rows.append(
                {
                    "survey_variable": variable,
                    "theme_id": theme_id,
                    "theme_label": label,
                    "keyword_rule": "|".join(keywords),
                    "nonblank_n": len(valid),
                    "matched_response_n": count,
                    "matched_percentage": safe_percent(count, len(valid)),
                    "interpretation_limit": "Keyword index only; not semantically validated theme prevalence; overlapping matches.",
                }
            )
    result = pd.DataFrame(rows)
    result.to_csv(TABLES / "survey_open_text_summary.csv", index=False, encoding="utf-8-sig")
    return result


def row_for_matrix(stats: pd.DataFrame, variable: str) -> pd.DataFrame:
    return stats[stats["variable_name"] == variable]


def pct_high(stats: pd.DataFrame, variable: str) -> tuple[int, int, float]:
    rows = row_for_matrix(stats, variable)
    high = int(rows.loc[rows["response_or_statistic"].isin(["4", "5"]), "n"].sum())
    valid_n = int(rows["valid_n"].max())
    return high, valid_n, 100 * high / valid_n


def write_findings(
    frame: pd.DataFrame,
    stats: pd.DataFrame,
    support: pd.DataFrame,
    platforms: pd.DataFrame,
    associations: pd.DataFrame,
    open_text: pd.DataFrame,
) -> None:
    boundary = pct_high(stats, "q3_1_language_humour_barrier")
    local_knowledge = pct_high(stats, "q3_1_local_knowledge_barrier")
    belonging = pct_high(stats, "q3_3_member")
    trusted = pct_high(stats, "q3_3_trusted_peer")
    hidden_rules = pct_high(stats, "q5_1_hidden_rules")
    english = pct_high(stats, "q5_1_english_materials")
    rule_clear = pct_high(stats, "q5_2_assessment_rules")
    distinguish = pct_high(stats, "q5_2_distinguish_rules_ability")
    top_unmet_n = int(support["unmet_wanted_n"].max())
    support_top = support[support["unmet_wanted_n"] == top_unmet_n]
    pre_top_n = int(platforms["pre_selected_n"].max())
    pre_top = platforms[platforms["pre_selected_n"] == pre_top_n]
    later_available = platforms[platforms["later_export_status"] == "AVAILABLE"].copy()
    later_available["later_selected_n"] = pd.to_numeric(later_available["later_selected_n"])
    later_top_n = int(later_available["later_selected_n"].max())
    later_top = later_available[later_available["later_selected_n"] == later_top_n]
    network = frame["q7_1_peer_network"].value_counts()
    open_q1 = int((frame["q8_1_boundary_event_text"] != BLANK).sum())
    open_q2 = int((frame["q8_2_support_request_text"] != BLANK).sum())
    support_label = "；".join(support_top["item_text"].tolist())
    support_prefix = "并列最高项目" if len(support_top) > 1 else "最高项目"
    later_label = "、".join(later_top["platform"].tolist())
    later_prefix = "并列最高" if len(later_top) > 1 else "最高"
    report = f"""# 完整问卷样本发现

本报告只分析 {len(frame)} 份合资格问卷，所有比例均为本样本描述。

## 同伴边界与归属

- 插班初期，语言/幽默进入障碍达到“经常或非常经常”的有 {boundary[0]}/{boundary[1]}（{boundary[2]:.1f}%）；地方知识障碍为 {local_knowledge[0]}/{local_knowledge[1]}（{local_knowledge[2]:.1f}%）。来源：`survey_item_statistics.csv`。
- 香港校内后期，认同“自己是学校或班级一员”的有 {belonging[0]}/{belonging[1]}（{belonging[2]:.1f}%）；认同至少有一位可以信任并谈心的同学有 {trusted[0]}/{trusted[1]}（{trusted[2]:.1f}%）。后者是复合题，不能拆成“信任”和“谈心”的两个比例。
- 同伴网络并非单一路径；各类别见 `sample_characteristics.csv`。由于背景表的小格抑制，不在正文复述稀有类别。

## 教育制度适应

- 初期认为理解未明说规则“比较或非常困难”的有 {hidden_rules[0]}/{hidden_rules[1]}（{hidden_rules[2]:.1f}%）；英文教材相关困难为 {english[0]}/{english[1]}（{english[2]:.1f}%）。
- 后期认同已经理解测验、作业、项目和课堂参与评价方式的有 {rule_clear[0]}/{rule_clear[1]}（{rule_clear[2]:.1f}%）；认同能够区分规则不熟悉与能力不足的有 {distinguish[0]}/{distinguish[1]}（{distinguish[2]:.1f}%）。

## 支持与支持缺口

- 未满足支持需求最高计数为 {top_unmet_n}，{support_prefix}为：{support_label}。各项目有效分母及比例见 `support_gap_analysis.csv`。
- 这是获得状况与需求的描述，不能据此判断某类支持具有因果效果。

## 数字平台与关系

- 插班前选择最多的平台为 {"、".join(pre_top['platform'].tolist())}（最高 {pre_top_n} 人）；香港校内后期选择最多的平台为 {later_label}（{later_prefix} {later_top_n} 人）。各自有效分母及比例见 `platform_transition_analysis.csv`。
- 微博缺少后期导出列，标为 `MISSING_FROM_EXPORT`，不解释为无人使用。
- 平台变化只能说明本样本的媒体组合变化，不能作为文化认同、政治身份或融入程度的代理。

## 开放题

- Q8.1 有 {open_q1}/{len(frame)} 份非空回答，Q8.2 有 {open_q2}/{len(frame)} 份非空回答。
- 关键词表只用于定位可能相关的回答，不把泛词或命中数解释为主题频率、机制或“经常交叠”。详见 `survey_open_text_summary.csv`。
- 为降低间接识别风险，本报告不逐字刊载问卷开放题；正式开放题语义结论须回到原回答人工核读，当前索引不构成质性饱和证据。

## 探索性关联

{chr(10).join(f"- {row.analysis_id}: valid n={row.valid_n}, ρ={row.effect_size_rho:.3f}, bootstrap 95% CI=[{row.bootstrap_ci_95_lower:.3f}, {row.bootstrap_ci_95_upper:.3f}], 置换 p={row.p_permutation:.4f}, BH-FDR q={row.bh_fdr_q:.4f}。" for row in associations.itertuples(index=False))}

五个关联中，A1 与 A4 在原规格下 BH-FDR q<0.05；其余三项没有。第二轮稳健性检查显示 A1 在替代缺失门槛、聚合方式与逐一删除回答时方向保持，分级为 `plausible exploratory finding`；A4 对同样合理的文化中介参与编码不稳，降为 `weak signal`，不进入主体发现。两者均不作总体、因果或验证性结论。
"""
    (REPORTS / "survey_findings.md").write_text(report, encoding="utf-8")


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    frame = eligible_frame()
    write_sample_characteristics(frame)
    stats = item_stats(frame)
    support = write_support_gaps(frame)
    platforms = write_platform_transition(frame)
    scores, _ = write_constructs(frame)
    associations = write_associations(scores, frame)
    open_text = write_open_text_summary(frame)
    write_findings(frame, stats, support, platforms, associations, open_text)
    print(f"survey analysis complete n={len(frame)}")


if __name__ == "__main__":
    main()
