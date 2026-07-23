#!/usr/bin/env python3
"""Reproduce the isolated Survey Analyst outputs for the 2026-07-23 run.

The script reads only the canonical processed survey and codebook. It never
reads raw platform metadata, IP addresses, remarks, or questionnaire sequence
numbers, and it writes only to the Survey Analyst worker directory.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


ROOT = Path(__file__).resolve().parents[3]
INPUT_SURVEY = ROOT / "data/processed/survey_clean.csv"
INPUT_CODEBOOK = ROOT / "data/processed/survey_codebook.csv"
OUT = ROOT / "outputs/agent_runs/20260723_full_pipeline/survey"
OUT.mkdir(parents=True, exist_ok=True)

RUN_ID = "20260723_full_pipeline"
N_PERMUTATIONS = 50_000
N_BOOTSTRAPS = 10_000

SPECIAL_VALUES = {
    "BLANK",
    "NOT_APPLICABLE",
    "CANNOT_REMEMBER",
    "UNWILLING_TO_ANSWER",
    "INVALID_RESPONSE",
}

BOUNDARY_MAP = {"从未": 1, "很少": 2, "有时": 3, "经常": 4, "非常经常": 5}
AGREEMENT_MAP = {
    "完全不同意": 1,
    "比较不同意": 2,
    "不确定": 3,
    "比较同意": 4,
    "完全同意": 5,
}
DIFFICULTY_MAP = {
    "完全不困难": 1,
    "比较不困难": 2,
    "一般": 3,
    "比较困难": 4,
    "非常困难": 5,
}
LANGUAGE_FREQUENCY_MAP = {
    "几乎不用": 1,
    "偶尔使用": 2,
    "有时使用": 3,
    "经常使用": 4,
    "几乎每天使用": 5,
}


def pct(n: int | float, d: int | float) -> float:
    return round(100 * n / d, 1) if d else math.nan


def qstats(values: pd.Series) -> tuple[float, float, float, float]:
    values = pd.to_numeric(values, errors="coerce").dropna()
    if values.empty:
        return (math.nan, math.nan, math.nan, math.nan)
    q1 = float(values.quantile(0.25))
    med = float(values.median())
    q3 = float(values.quantile(0.75))
    return (med, q1, q3, q3 - q1)


def fmt_num(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:.{digits}f}"


def fmt_pct(n: int, d: int) -> str:
    return f"{n}/{d}（{pct(n, d):.1f}%）" if d else "NA"


def write_csv(frame: pd.DataFrame, filename: str) -> None:
    frame.to_csv(OUT / filename, index=False, encoding="utf-8-sig")


survey = pd.read_csv(INPUT_SURVEY)
codebook = pd.read_csv(INPUT_CODEBOOK)

# Eligibility can be decoded as bool or string depending on the pandas version.
eligible_mask = survey["eligible"].astype(str).str.casefold().eq("true")
eligible = survey.loc[eligible_mask].copy()
if len(eligible) != 24:
    raise ValueError(f"Expected 24 eligible rows, found {len(eligible)}")

# Deliberately drop restricted/internal administrative fields before analysis.
for prohibited in (
    "questionnaire_sequence",
    "survey_row_id",
    "exclusion_reason",
    "duplicate_flag",
    "data_quality_flag",
):
    if prohibited in eligible:
        eligible = eligible.drop(columns=prohibited)

cb = codebook.set_index("variable_name", drop=False)


def cb_value(variable: str, field: str, default: str = "") -> str:
    if variable not in cb.index:
        return default
    value = cb.loc[variable, field]
    return default if pd.isna(value) else str(value)


def special_counts(series: pd.Series) -> dict[str, int]:
    values = series.fillna("BLANK").astype(str)
    return {key: int((values == key).sum()) for key in sorted(SPECIAL_VALUES)}


def valid_series(series: pd.Series) -> pd.Series:
    values = series.fillna("BLANK").astype(str)
    return series.loc[~values.isin(SPECIAL_VALUES)]


def distribution(series: pd.Series, include_special: bool = False) -> dict[str, int]:
    values = series.fillna("BLANK").astype(str)
    if not include_special:
        values = values.loc[~values.isin(SPECIAL_VALUES)]
    counts = values.value_counts(dropna=False)
    return {str(key): int(value) for key, value in counts.items()}


def ordinal_map(variable: str) -> dict[str, int] | None:
    if variable.startswith("q3_1_"):
        return BOUNDARY_MAP
    if (
        variable.startswith("q3_3_")
        or variable.startswith("q4_1_")
        or variable.startswith("q5_2_")
        or variable.startswith("q6_5_")
    ):
        return AGREEMENT_MAP
    if variable.startswith("q5_1_"):
        return DIFFICULTY_MAP
    if variable.startswith("q2_12_"):
        return LANGUAGE_FREQUENCY_MAP
    return None


# ---------------------------------------------------------------------------
# Sample characteristics
# ---------------------------------------------------------------------------

sample_rows: list[dict[str, object]] = []


def add_categorical_characteristic(
    variable: str,
    display_label: str,
    note: str = "",
) -> None:
    series = eligible[variable]
    valid = valid_series(series)
    specials = special_counts(series)
    for category, count in distribution(series).items():
        sample_rows.append(
            {
                "section": "sample_characteristics",
                "variable_name": variable,
                "question_id": cb_value(variable, "question_id"),
                "item": display_label,
                "category_or_statistic": category,
                "value": "",
                "n": count,
                "percent_of_valid": pct(count, len(valid)),
                "valid_n": len(valid),
                "blank_n": specials["BLANK"],
                "not_applicable_n": specials["NOT_APPLICABLE"],
                "cannot_remember_n": specials["CANNOT_REMEMBER"],
                "unwilling_n": specials["UNWILLING_TO_ANSWER"],
                "invalid_n": specials["INVALID_RESPONSE"],
                "analytic_note": note,
            }
        )


def add_multiselect_characteristic(
    variable: str,
    display_label: str,
    note: str = "多选题；百分比以全部24名合资格参与者为分母，合计可超过100%。",
) -> None:
    series = eligible[variable].fillna("未选择").astype(str)
    selected = int((series == "选择").sum())
    sample_rows.append(
        {
            "section": "sample_characteristics",
            "variable_name": variable,
            "question_id": cb_value(variable, "question_id"),
            "item": display_label,
            "category_or_statistic": "选择",
            "value": "",
            "n": selected,
            "percent_of_valid": pct(selected, len(eligible)),
            "valid_n": len(eligible),
            "blank_n": 0,
            "not_applicable_n": 0,
            "cannot_remember_n": 0,
            "unwilling_n": 0,
            "invalid_n": 0,
            "analytic_note": note,
        }
    )


add_categorical_characteristic("q1_3_entry_grade", "第一次进入香港本地学校的年级")
add_categorical_characteristic("q2_1_current_status", "当前主要状态")
add_categorical_characteristic("q2_2_current_residence", "当前主要居住地")
add_categorical_characteristic("q2_3_gender", "性别")

year_values = pd.to_numeric(eligible["q2_4_entry_year"], errors="coerce")
year_valid = year_values.dropna()
year_med, year_q1, year_q3, year_iqr = qstats(year_valid)
sample_rows.append(
    {
        "section": "sample_characteristics",
        "variable_name": "q2_4_entry_year",
        "question_id": "Q2.4",
        "item": "第一次进入香港本地学校的年份",
        "category_or_statistic": "年份汇总（为降低披露风险，不列逐年小单元格）",
        "value": json.dumps(
            {
                "median": year_med,
                "q1": year_q1,
                "q3": year_q3,
                "iqr": year_iqr,
                "min": float(year_valid.min()),
                "max": float(year_valid.max()),
            },
            ensure_ascii=False,
        ),
        "n": "",
        "percent_of_valid": "",
        "valid_n": len(year_valid),
        "blank_n": int(year_values.isna().sum()),
        "not_applicable_n": 0,
        "cannot_remember_n": int(
            (eligible["q2_4_entry_year"].astype(str) == "CANNOT_REMEMBER").sum()
        ),
        "unwilling_n": int(
            (eligible["q2_4_entry_year"].astype(str) == "UNWILLING_TO_ANSWER").sum()
        ),
        "invalid_n": 0,
        "analytic_note": "回顾性年份；不据此推断时期效应。",
    }
)

for variable, label in (
    ("q2_5_hk_school_duration", "香港本地小学或中学累计就读时间"),
    ("q2_6_hk_transfer_count", "进入香港本地学校后再次转校"),
    ("q2_7_school_type", "就读时间最长的香港本地学校类型"),
):
    add_categorical_characteristic(variable, label)

for variable, label in (
    ("q2_8_language_cantonese", "教学语言：粤语"),
    ("q2_8_language_mandarin", "教学语言：普通话"),
    ("q2_8_language_english", "教学语言：英语"),
    ("q2_8_language_mixed", "教学语言：不同学科使用不同语言"),
    ("q2_8_language_other", "教学语言：其他"),
    ("q2_8_language_cannot_remember", "教学语言：记不清"),
    ("q2_8_language_unwilling", "教学语言：不愿回答"),
):
    add_multiselect_characteristic(variable, label)

add_categorical_characteristic("q2_9_prior_region", "迁居香港前主要上学地区")
for variable, label in (
    ("q2_10_reason_family_move", "迁居原因：家庭整体迁居"),
    ("q2_10_reason_parent_work", "迁居原因：父母工作或事业安排"),
    ("q2_10_reason_reunion", "迁居原因：与家人团聚"),
    ("q2_10_reason_different_education", "迁居原因：接受不同教育制度"),
    ("q2_10_reason_future_opportunity", "迁居原因：升学或未来发展机会"),
    ("q2_10_reason_personal", "迁居原因：个人意愿"),
    ("q2_10_reason_other", "迁居原因：其他"),
    ("q2_10_reason_unwilling", "迁居原因：不愿回答"),
):
    add_multiselect_characteristic(variable, label)

add_categorical_characteristic(
    "q2_11_cantonese_timing_uncertain",
    "粤语水平（时点不确定）",
    "最终问卷写“来香港之前”，导出写“插班初期”；仅报告分布，不作时序或前置能力解释。",
)

for variable, label in (
    ("q2_12_mandarin_frequency", "香港校内后期与同学使用普通话频率"),
    ("q2_12_cantonese_frequency", "香港校内后期与同学使用粤语频率"),
    ("q2_12_english_frequency", "香港校内后期与同学使用英语频率"),
):
    add_categorical_characteristic(variable, label)
    numeric = eligible[variable].map(LANGUAGE_FREQUENCY_MAP)
    med, q1, q3, iqr = qstats(numeric)
    sample_rows.append(
        {
            "section": "sample_characteristics",
            "variable_name": variable,
            "question_id": cb_value(variable, "question_id"),
            "item": label,
            "category_or_statistic": "ordinal_summary",
            "value": json.dumps(
                {"median": med, "q1": q1, "q3": q3, "iqr": iqr},
                ensure_ascii=False,
            ),
            "n": "",
            "percent_of_valid": "",
            "valid_n": int(numeric.notna().sum()),
            "blank_n": 0,
            "not_applicable_n": int(
                (eligible[variable] == "NOT_APPLICABLE").sum()
            ),
            "cannot_remember_n": int(
                (eligible[variable] == "CANNOT_REMEMBER").sum()
            ),
            "unwilling_n": int(
                (eligible[variable] == "UNWILLING_TO_ANSWER").sum()
            ),
            "invalid_n": 0,
            "analytic_note": "1=几乎不用，5=几乎每天使用；顺序型描述。",
        }
    )

sample_characteristics = pd.DataFrame(sample_rows)
write_csv(sample_characteristics, "sample_characteristics.csv")


# ---------------------------------------------------------------------------
# Item-level thematic statistics
# ---------------------------------------------------------------------------

item_roles = {
    "peer_boundary",
    "peer_entry_support",
    "school_belonging",
    "identity_negotiation",
    "brokerage_participation",
    "brokerage_pressure",
    "academic_difficulty",
    "academic_rule_understanding",
    "learner_identity",
    "support_resources",
    "platform_function",
    "platform_practices",
    "peer_network",
}

item_rows: list[dict[str, object]] = []
for variable in codebook.loc[codebook["analysis_role"].isin(item_roles), "variable_name"]:
    if variable not in eligible.columns:
        continue
    response_type = cb_value(variable, "response_type")
    role = cb_value(variable, "analysis_role")
    series = eligible[variable]
    specials = special_counts(series)
    valid = valid_series(series)
    mapping = ordinal_map(variable)
    numeric = series.map(mapping) if mapping else pd.Series(np.nan, index=series.index)
    med, q1, q3, iqr = qstats(numeric)
    high_n = int((numeric >= 4).sum()) if mapping else ""
    selected_n = int((series == "选择").sum()) if response_type == "multiple_choice" else ""
    selected_pct = (
        pct(selected_n, len(eligible)) if response_type == "multiple_choice" else ""
    )
    item_rows.append(
        {
            "variable_name": variable,
            "question_id": cb_value(variable, "question_id"),
            "item_text": cb_value(variable, "item_text")
            or cb_value(variable, "question_text"),
            "analysis_role": role,
            "response_type": response_type,
            "eligible_n": len(eligible),
            "valid_n": len(valid),
            "frequency_distribution": json.dumps(
                distribution(series), ensure_ascii=False
            ),
            "selected_n": selected_n,
            "selected_percent": selected_pct,
            "median": med,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "high_response_n": high_n,
            "high_response_percent": (
                pct(high_n, int(numeric.notna().sum())) if mapping else ""
            ),
            "blank_n": specials["BLANK"],
            "not_applicable_n": specials["NOT_APPLICABLE"],
            "cannot_remember_n": specials["CANNOT_REMEMBER"],
            "unwilling_n": specials["UNWILLING_TO_ANSWER"],
            "invalid_n": specials["INVALID_RESPONSE"],
            "analytic_note": (
                "多选题；selected_percent以24为分母。"
                if response_type == "multiple_choice"
                else "顺序题的中位数与IQR只使用1–5实质响应。"
                if mapping
                else "单选分布；特殊响应不进入valid_n。"
            ),
        }
    )

survey_item_statistics = pd.DataFrame(item_rows)
write_csv(survey_item_statistics, "survey_item_statistics.csv")


# ---------------------------------------------------------------------------
# Support gap analysis
# ---------------------------------------------------------------------------

support_rows: list[dict[str, object]] = []
support_variables = [
    variable
    for variable in codebook.loc[
        codebook["analysis_role"].eq("support_gap"), "variable_name"
    ]
    if variable in eligible.columns
]
for variable in support_variables:
    series = eligible[variable]
    valid = valid_series(series)
    specials = special_counts(series)
    categories = {
        "obtained_helpful_n": "已获得，而且帮助较大",
        "obtained_limited_n": "已获得，但帮助有限",
        "unmet_need_n": "没有获得，但希望获得",
        "not_needed_n": "没有获得，也不需要",
    }
    row: dict[str, object] = {
        "variable_name": variable,
        "question_id": cb_value(variable, "question_id"),
        "support_item": cb_value(variable, "item_text"),
        "eligible_n": len(eligible),
        "valid_n": len(valid),
    }
    for field, label in categories.items():
        count = int((series == label).sum())
        row[field] = count
        row[field.replace("_n", "_percent")] = pct(count, len(valid))
    row.update(
        {
            "not_applicable_n": specials["NOT_APPLICABLE"],
            "cannot_remember_n": specials["CANNOT_REMEMBER"],
            "unwilling_n": specials["UNWILLING_TO_ANSWER"],
            "blank_n": specials["BLANK"],
            "analytic_note": "“已获得但帮助有限”与“没有获得但希望获得”保持为不同类别。",
        }
    )
    support_rows.append(row)

support_gap = pd.DataFrame(support_rows)
write_csv(support_gap, "support_gap_analysis.csv")


# ---------------------------------------------------------------------------
# Paired platform transition description
# ---------------------------------------------------------------------------

platform_pairs = [
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
    ("other", "其他"),
    ("low_use", "较少使用数字平台"),
    ("cannot_remember", "记不清"),
    ("unwilling", "不愿回答"),
]

platform_rows: list[dict[str, object]] = []
for suffix, platform in platform_pairs:
    pre_var = f"q6_1_pre_{suffix}"
    later_var = f"q6_2_later_{suffix}"
    if pre_var not in eligible.columns:
        continue
    pre_selected = eligible[pre_var].eq("选择")
    if later_var not in eligible.columns:
        platform_rows.append(
            {
                "platform": platform,
                "pre_variable": pre_var,
                "later_variable": "MISSING_EXPORT_COLUMN",
                "eligible_n": len(eligible),
                "pre_selected_n": int(pre_selected.sum()),
                "pre_selected_percent": pct(int(pre_selected.sum()), len(eligible)),
                "later_selected_n": "",
                "later_selected_percent": "",
                "retained_n": "",
                "gained_n": "",
                "lost_n": "",
                "neither_n": "",
                "comparable": False,
                "analytic_note": "Q6.2对应导出列缺失，不能重建或作时点比较。",
            }
        )
        continue
    later_selected = eligible[later_var].eq("选择")
    platform_rows.append(
        {
            "platform": platform,
            "pre_variable": pre_var,
            "later_variable": later_var,
            "eligible_n": len(eligible),
            "pre_selected_n": int(pre_selected.sum()),
            "pre_selected_percent": pct(int(pre_selected.sum()), len(eligible)),
            "later_selected_n": int(later_selected.sum()),
            "later_selected_percent": pct(int(later_selected.sum()), len(eligible)),
            "retained_n": int((pre_selected & later_selected).sum()),
            "gained_n": int((~pre_selected & later_selected).sum()),
            "lost_n": int((pre_selected & ~later_selected).sum()),
            "neither_n": int((~pre_selected & ~later_selected).sum()),
            "comparable": True,
            "analytic_note": "同一合资格记录的描述性配对；多选平台并存，不能解释为文化认同或平台效果。",
        }
    )

platform_transition = pd.DataFrame(platform_rows)
write_csv(platform_transition, "platform_transition_analysis.csv")


# ---------------------------------------------------------------------------
# Open-text aggregate manual coding (no quotations or row identifiers output)
# ---------------------------------------------------------------------------

# Response positions refer only to the stable order of the 24 eligible rows in
# survey_clean.csv. Coding is multi-label and does not exclude similar wording.
q81_theme_positions = {
    "小组作业、课程任务或活动成为边界/进入事件": {1, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22},
    "同伴主动邀请、解释或协助": {11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22},
    "午餐、放学或课间等日常互动延续关系": {4, 11, 13, 14, 15, 16, 18, 20, 21, 22},
    "粤语、本地知识或共同成长经验形成进入障碍": {6, 12, 13, 14, 15, 16, 19, 21, 23},
    "明确描述距离、独处、插不上话或未获组队": {1, 6, 12, 15, 19, 23},
}
q82_theme_positions = {
    "需要适应时间，困难不等于能力不足或不愿参与": {6, 11, 12, 13, 14, 15, 17, 18, 20, 21, 23},
    "清楚说明课程、作业、评价、术语或隐藏规则": {13, 14, 15, 16, 18, 19, 20, 21, 22},
    "同伴主动交流、结对或搭建新老生桥梁": {12, 15, 16, 17, 18, 20, 21, 22, 23},
    "减少刻板预设并了解个人具体情况": {4, 6, 11, 13, 14, 15, 17, 23},
    "关注情绪、焦虑或适应压力": {1, 6, 12, 15, 17, 24},
    "语言与学科词汇支持": {15, 16, 20, 21, 23},
}

open_text_rows: list[dict[str, object]] = []
for question, variable, mapping in (
    ("Q8.1", "q8_1_boundary_event_text", q81_theme_positions),
    ("Q8.2", "q8_2_support_request_text", q82_theme_positions),
):
    nonblank = int(
        (
            ~eligible[variable]
            .fillna("BLANK")
            .astype(str)
            .isin({"BLANK", ""})
        ).sum()
    )
    for theme, positions in mapping.items():
        open_text_rows.append(
            {
                "question_id": question,
                "theme": theme,
                "coded_response_n": len(positions),
                "nonblank_response_n": nonblank,
                "percent_of_nonblank": pct(len(positions), nonblank),
                "coding_note": "人工多标签内容归纳；计数可重叠；未输出原文；相似措辞未用于排除记录。",
            }
        )

open_text_theme_counts = pd.DataFrame(open_text_rows)
write_csv(open_text_theme_counts, "open_text_theme_counts.csv")


# ---------------------------------------------------------------------------
# Exploratory construct assessment
# ---------------------------------------------------------------------------

construct_specs = {
    "peer_boundary": {
        "label": "插班初期同伴文化边界",
        "items": [
            "q3_1_language_humour_barrier",
            "q3_1_local_knowledge_barrier",
            "q3_1_background_assumption",
            "q3_1_mainland_grouping_assumption",
            "q3_1_self_withdrawal",
        ],
        "mapping": BOUNDARY_MAP,
        "minimum_items": 4,
        "status": "RETAINED_EXPLORATORY",
        "decision": "五项同向描述初期边界经历；Q3.1第6项缺列不重建，且其为积极认识同学行为，不纳入本指标。",
    },
    "school_belonging": {
        "label": "香港校内后期学校归属",
        "items": [
            "q3_3_member",
            "q3_3_trusted_peer",
            "q3_3_included_group",
            "q3_3_authentic_self",
            "q3_3_knows_help_peer",
        ],
        "mapping": AGREEMENT_MAP,
        "minimum_items": 4,
        "status": "RETAINED_EXPLORATORY",
        "decision": "五项同向覆盖成员感、可信同伴、参与、自我表达与求助对象。",
    },
    "academic_difficulty": {
        "label": "插班初期教育适应困难",
        "items": [
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
        "mapping": DIFFICULTY_MAP,
        "minimum_items": 7,
        "status": "RETAINED_EXPLORATORY",
        "decision": "九项均为初期教育制度、语言与参与难度；保持探索性，不声称单维或经验证。",
    },
    "academic_rule_understanding": {
        "label": "香港校内后期学术规则理解",
        "items": [
            "q5_2_good_assignment",
            "q5_2_assessment_rules",
            "q5_2_discussion_rules",
            "q5_2_transfer_prior_strengths",
            "q5_2_distinguish_rules_ability",
        ],
        "mapping": AGREEMENT_MAP,
        "minimum_items": 4,
        "status": "RETAINED_EXPLORATORY",
        "decision": "五项共同指向后期规则掌握与既有学习资源的重新运用；内部一致性仅属描述。",
    },
    "brokerage_participation_candidate": {
        "label": "文化中介参与候选",
        "items": ["q4_1_explain_differences", "q4_1_reduce_misunderstanding"],
        "mapping": AGREEMENT_MAP,
        "minimum_items": 2,
        "status": "NOT_COMBINED",
        "decision": "解释差异与减少误解并非同一行为；样本中两项相关极低且均有明显天花板，保持分项。",
    },
    "brokerage_pressure_candidate": {
        "label": "文化中介压力候选",
        "items": ["q4_1_brokerage_fatigue", "q4_1_dual_marginality"],
        "mapping": AGREEMENT_MAP,
        "minimum_items": 2,
        "status": "NOT_COMBINED",
        "decision": "解释疲惫与双重边缘感是不同结果，只有两项且一致性有限，保持分项。",
    },
    "platform_differentiation_candidate": {
        "label": "平台功能分化候选",
        "items": [
            "q6_5_separate_relations",
            "q6_5_different_expression",
            "q6_5_multiple_roles",
        ],
        "mapping": AGREEMENT_MAP,
        "minimum_items": 2,
        "status": "NOT_COMBINED",
        "decision": "关系分工、表达调整与多平台功能并存相关但不等同；内部一致性有限且有天花板，保持分项。",
    },
}


def cronbach_alpha(matrix: pd.DataFrame) -> float:
    values = matrix.to_numpy(dtype=float)
    k = values.shape[1]
    if k < 2 or values.shape[0] < 3:
        return math.nan
    total_variance = np.var(values.sum(axis=1), ddof=1)
    if total_variance == 0:
        return math.nan
    item_variances = np.var(values, axis=0, ddof=1).sum()
    return float(k / (k - 1) * (1 - item_variances / total_variance))


construct_scores: dict[str, pd.Series] = {}
construct_rows: list[dict[str, object]] = []
for name, spec in construct_specs.items():
    matrix = (
        eligible[spec["items"]]
        .replace(spec["mapping"])
        .apply(pd.to_numeric, errors="coerce")
    )
    complete = matrix.dropna()
    score = matrix.mean(axis=1, skipna=True)
    score.loc[matrix.notna().sum(axis=1) < spec["minimum_items"]] = np.nan
    construct_scores[name] = score

    pairwise_rhos: list[float] = []
    for i in range(matrix.shape[1]):
        for j in range(i + 1, matrix.shape[1]):
            pair = matrix.iloc[:, [i, j]].dropna()
            if (
                len(pair) >= 3
                and pair.iloc[:, 0].nunique() > 1
                and pair.iloc[:, 1].nunique() > 1
            ):
                pairwise_rhos.append(
                    float(spearmanr(pair.iloc[:, 0], pair.iloc[:, 1]).statistic)
                )
    med, q1, q3, iqr = qstats(score)
    two_item_rho = pairwise_rhos[0] if len(spec["items"]) == 2 else math.nan
    spearman_brown = (
        2 * two_item_rho / (1 + two_item_rho)
        if len(spec["items"]) == 2 and two_item_rho > -1
        else math.nan
    )
    construct_rows.append(
        {
            "construct_name": name,
            "construct_label": spec["label"],
            "status": spec["status"],
            "items": "|".join(spec["items"]),
            "item_count": len(spec["items"]),
            "scoring": "题项1–5编码后取均值；不插补。",
            "minimum_items_required": spec["minimum_items"],
            "scored_n": int(score.notna().sum()),
            "median": med,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "observed_min": float(score.min()),
            "observed_max": float(score.max()),
            "complete_case_n": len(complete),
            "cronbach_alpha_descriptive": cronbach_alpha(complete),
            "median_pairwise_spearman": (
                float(np.median(pairwise_rhos)) if pairwise_rhos else math.nan
            ),
            "two_item_spearman_brown": spearman_brown,
            "decision": spec["decision"],
            "validation_warning": "自编题项的探索性指标，不是经验证量表；alpha不证明单维性或效度。",
        }
    )

exploratory_constructs = pd.DataFrame(construct_rows)
write_csv(exploratory_constructs, "exploratory_constructs.csv")


# ---------------------------------------------------------------------------
# Five RQ-driven exploratory associations
# ---------------------------------------------------------------------------


def numeric_item(variable: str, mapping: dict[str, int]) -> pd.Series:
    return eligible[variable].map(mapping)


helpful_support_count = (
    eligible[support_variables].eq("已获得，而且帮助较大").sum(axis=1)
)
cross_context_network = eligible["q7_1_peer_network"].isin(
    {"同时维持几个不同背景的朋友圈", "根据课程、兴趣和场景进入不同群体"}
).astype(int)

association_specs = [
    {
        "analysis_id": "A1",
        "research_question": "RQ1",
        "x_label": "插班初期同伴文化边界探索性均值",
        "y_label": "香港校内后期学校归属探索性均值",
        "x": construct_scores["peer_boundary"],
        "y": construct_scores["school_belonging"],
        "interpretation_guardrail": "两个时点、回顾性自报；相关不表示边界经历造成后期归属。",
    },
    {
        "analysis_id": "A2",
        "research_question": "RQ2",
        "x_label": "插班初期教育适应困难探索性均值",
        "y_label": "香港校内后期学术规则理解探索性均值",
        "x": construct_scores["academic_difficulty"],
        "y": construct_scores["academic_rule_understanding"],
        "interpretation_guardrail": "初期困难与后期规则理解不是同一纵向量尺；正相关可由暴露、回忆或反应方式等产生。",
    },
    {
        "analysis_id": "A3",
        "research_question": "RQ1/RQ2",
        "x_label": "Q5.5获得且帮助较大的支持项目数（0–8）",
        "y_label": "香港校内后期学校归属探索性均值",
        "x": helpful_support_count,
        "y": construct_scores["school_belonging"],
        "interpretation_guardrail": "支持数是描述性计数，不等同支持强度；无法确定方向或排除共同原因。",
    },
    {
        "analysis_id": "A4",
        "research_question": "RQ1",
        "x_label": "Q4.1_4解释两地差异",
        "y_label": "Q4.1_6解释/翻译/中间人疲惫",
        "x": numeric_item("q4_1_explain_differences", AGREEMENT_MAP),
        "y": numeric_item("q4_1_brokerage_fatigue", AGREEMENT_MAP),
        "interpretation_guardrail": "仅为两个单项；文化中介行为与压力未合成为量表。",
    },
    {
        "analysis_id": "A5",
        "research_question": "RQ3",
        "x_label": "Q6.5_5多个平台承担不同作用",
        "y_label": "跨背景/情境化同伴网络指示变量",
        "x": numeric_item("q6_5_multiple_roles", AGREEMENT_MAP),
        "y": cross_context_network,
        "interpretation_guardrail": "网络类别被简化为探索性二分，且对照组很小；平台实践不是融入或身份指标。",
    },
]


def permutation_spearman(
    x: np.ndarray, y: np.ndarray, seed: int
) -> tuple[float, float]:
    x_rank = rankdata(x).astype(float)
    y_rank = rankdata(y).astype(float)
    x_centered = x_rank - x_rank.mean()
    y_centered = y_rank - y_rank.mean()
    denominator = math.sqrt(
        float(np.dot(x_centered, x_centered) * np.dot(y_centered, y_centered))
    )
    observed = float(np.dot(x_centered, y_centered) / denominator)
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(N_PERMUTATIONS):
        permuted = rng.permutation(y_centered)
        permuted_rho = float(np.dot(x_centered, permuted) / denominator)
        exceed += abs(permuted_rho) >= abs(observed) - 1e-12
    p_value = (exceed + 1) / (N_PERMUTATIONS + 1)
    return observed, p_value


def bootstrap_spearman_ci(
    x: np.ndarray, y: np.ndarray, seed: int
) -> tuple[float, float, int]:
    rng = np.random.default_rng(seed)
    estimates: list[float] = []
    n = len(x)
    for _ in range(N_BOOTSTRAPS):
        indices = rng.integers(0, n, size=n)
        x_sample = x[indices]
        y_sample = y[indices]
        if len(np.unique(x_sample)) < 2 or len(np.unique(y_sample)) < 2:
            continue
        estimates.append(float(spearmanr(x_sample, y_sample).statistic))
    if not estimates:
        return (math.nan, math.nan, 0)
    lower, upper = np.percentile(estimates, [2.5, 97.5])
    return float(lower), float(upper), len(estimates)


def rho_magnitude(rho: float) -> str:
    absolute = abs(rho)
    if absolute < 0.10:
        return "可忽略"
    if absolute < 0.30:
        return "小"
    if absolute < 0.50:
        return "中等"
    return "大"


association_rows: list[dict[str, object]] = []
short_flag = pd.to_numeric(
    eligible.get("completion_seconds"), errors="coerce"
).lt(300)
for index, spec in enumerate(association_specs, start=1):
    pair = pd.concat(
        [spec["x"].rename("x"), spec["y"].rename("y")], axis=1
    ).dropna()
    x = pair["x"].to_numpy(dtype=float)
    y = pair["y"].to_numpy(dtype=float)
    rho, p_value = permutation_spearman(x, y, 20260723 + index)
    ci_lower, ci_upper, bootstrap_valid = bootstrap_spearman_ci(
        x, y, 20261723 + index
    )
    sensitivity_pair = pair.loc[~short_flag.reindex(pair.index).fillna(False)]
    if (
        len(sensitivity_pair) >= 3
        and sensitivity_pair["x"].nunique() > 1
        and sensitivity_pair["y"].nunique() > 1
    ):
        sensitivity_rho = float(
            spearmanr(sensitivity_pair["x"], sensitivity_pair["y"]).statistic
        )
    else:
        sensitivity_rho = math.nan
    association_rows.append(
        {
            "analysis_id": spec["analysis_id"],
            "research_question": spec["research_question"],
            "x": spec["x_label"],
            "y": spec["y_label"],
            "method": f"Spearman rho；双侧Monte Carlo置换{N_PERMUTATIONS}次",
            "n": len(pair),
            "rho": rho,
            "effect_magnitude_descriptive": rho_magnitude(rho),
            "p_permutation": p_value,
            "bootstrap_ci_95_lower": ci_lower,
            "bootstrap_ci_95_upper": ci_upper,
            "bootstrap_valid_resamples": bootstrap_valid,
            "bh_fdr_q": math.nan,
            "sensitivity_n_excluding_lt300s": len(sensitivity_pair),
            "sensitivity_rho_excluding_lt300s": sensitivity_rho,
            "interpretation_guardrail": spec["interpretation_guardrail"],
        }
    )

exploratory_associations = pd.DataFrame(association_rows)


def benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    values = p_values.to_numpy(dtype=float)
    m = len(values)
    order = np.argsort(values)
    adjusted = np.empty(m, dtype=float)
    ranked = values[order] * m / np.arange(1, m + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted[order] = np.minimum(ranked, 1.0)
    return pd.Series(adjusted, index=p_values.index)


exploratory_associations["bh_fdr_q"] = benjamini_hochberg(
    exploratory_associations["p_permutation"]
)
write_csv(exploratory_associations, "exploratory_associations.csv")


# ---------------------------------------------------------------------------
# Markdown reports
# ---------------------------------------------------------------------------

sample_description_md = f"""# 完整合资格问卷样本描述

## Material Passport

- Material ID: `{RUN_ID}-survey-sample`
- Verification Status: `ANALYZED`
- Source: `data/processed/survey_clean.csv`（仅 `eligible==TRUE`）
- Eligible sample: 24
- Restricted fields used: 无

## 样本边界

本报告只描述24份合资格问卷，不估计全港目标人口比例。原始提交35份、排除11份；排除流程由主代理的 `outputs/tables/sample_flow.csv` 与 `outputs/reports/data_quality_report.md` 管理。本分析没有因开放题措辞相似而排除任何记录，也没有读取或输出受限管理字段。

## 主要样本特征

- 当前居住：中国内地17人（70.8%），香港7人（29.2%）。当前主要状态以在中国内地大专院校或大学就读9人（37.5%）、在香港大专院校或大学就读7人（29.2%）、毕业后主要在香港以外生活或工作6人（25.0%）为主。
- 性别题有效回答23人，其中女13人、男10人，另有1人不愿回答。
- 首次进入香港本地学校的年份中位数为{fmt_num(year_med, 0)}，IQR为{fmt_num(year_q1, 1)}–{fmt_num(year_q3, 1)}，范围{fmt_num(float(year_valid.min()), 0)}–{fmt_num(float(year_valid.max()), 0)}。年份仅作样本背景，未检验时期效应。
- 香港本地学校累计就读时间：2年至不足3年11人，3年至不足5年11人，其余2人少于2年。进入香港本地学校后未再次转校19人，转过1次5人。
- 就读时间最长的学校以资助学校11人、直接资助计划学校6人、官立学校4人为主。教学语言为多选：粤语21人、英语21人、不同学科使用不同语言12人、普通话5人。
- 迁居前主要在华南地区上学17人（70.8%），显示样本地区构成集中。迁居原因是多选：升学或未来发展机会15人；父母工作/事业安排与接受不同教育制度各9人。
- 香港校内后期与同学的语言使用中，普通话中位数4（IQR 3.00–4.25）、粤语中位数4（IQR 3.00–5.00）、英语中位数3（IQR 2.75–3.00）；这些是频率顺序题，不表示能力或身份。

## 工具版本警告

Q2.11 的最终问卷题干为“来香港之前”，导出题干为“插班初期”。24人的响应均保留，但本分析仅将其列为“时点不确定的粤语背景”，不把它当作确定的迁港前能力，也不用于时序比较或关联检验。Q3.1第6项与Q6.2微博等导出列缺失；缺失列没有被重建。

## 可追溯输出

所有分类频数、有效n、百分比与特殊响应计数见 `sample_characteristics.csv`。年份采用汇总统计，避免逐年小单元格披露。
"""
(OUT / "sample_description.md").write_text(sample_description_md, encoding="utf-8")


def item_record(variable: str) -> pd.Series:
    return survey_item_statistics.loc[
        survey_item_statistics["variable_name"].eq(variable)
    ].iloc[0]


def selected_text(variable: str) -> str:
    row = item_record(variable)
    return fmt_pct(int(row["selected_n"]), 24)


survey_findings_md = f"""# 完整合资格问卷样本发现

## Material Passport

- Material ID: `{RUN_ID}-survey-findings`
- Verification Status: `ANALYZED`
- Source: `survey_item_statistics.csv`、`support_gap_analysis.csv`、`platform_transition_analysis.csv`、`open_text_theme_counts.csv`
- Scope: 24份合资格、回顾性横截面自报问卷

## RQ1：同伴边界、归属与身份协商

插班初期的边界经验并不只表现为直接预设。对本地地区、学校传统或生活经验不熟悉一项有9/24（37.5%）报告“经常/非常经常”；因担心说错或不合群而减少参与为9/23（39.1%）；被默认更适合与其他内地背景学生活动为6/22（27.3%）。粤语俗语、网络用语或笑话障碍达到“经常/非常经常”的为4/23（17.4%）。Q3.1第6项在导出中缺失，不能据此完整描述通过兴趣或活动认识本地同学。

初期认识同学最常被选择的途径是同桌/邻座主动交谈{selected_text("q3_2_help_neighbor")}、课外活动或校队{selected_text("q3_2_help_extracurricular")}、教师安排帮助{selected_text("q3_2_help_teacher_assignment")}和其他内地背景学生介绍{selected_text("q3_2_help_mainland_peer")}。线上群组只有{selected_text("q3_2_help_online_group")}被列为最有帮助的三种方式之一，不能由此推断线上群组不重要，因为题目限制最多三项。

香港校内后期的归属题整体偏高：可信且可谈心的同学为24/24同意；感到是学校或班级一员21/24同意；小组活动通常不被排除22/24同意；能自然表现自己22/24同意；知道可向哪些同学求助22/24同意。高归属分布不能否定初期边界事件，也不能据此声称适应过程由某类支持造成。

身份与文化中介题显示场景性调整与非二元身份理解可以并存：调整语言或表达23/23同意，保留内地生活习惯同时参与香港学校生活22/23同意，不必在“内地/香港”之间只选一种身份20/23同意。解释差异23/23同意、帮助减少误解21/22同意，但解释者疲惫仅4/22同意；双重边缘感则有10/23同意、3/23不确定，显示“参与中介”不能自动等同为获得认可或承担压力。

后期同伴网络为：同时维持不同背景朋友圈11人、按课程/兴趣/场景进入不同群体7人、主要与内地背景同学交往5人、主要进入香港本地同学社交圈1人。此题描述网络结构，不是适应成功/失败排序。

## RQ2：跨教育制度适应与规则理解

插班初期报告“比较/非常困难”的比例较高的项目包括：阅读繁体字17/24（70.8%）、小组项目17/24（70.8%）、完成测验/考试/作业/项目17/24（70.8%）、粤语授课或课堂交流16/24（66.7%）、口头汇报15/24（62.5%）以及答题格式/步骤12/24（50.0%）。英文教材为9/24（37.5%），隐藏规则为8/24（33.3%）。项目分布不同，不应合并为“内地基础不足”。

香港校内后期对规则理解的同意比例也高：清楚好作业标准22/23、理解评价方式22/23、知道何时及如何参与讨论21/23、找到运用既有学习优势的方法21/24、能区分规则不熟与能力不足23/24。初期难度题和后期理解题不是等价的前后测，未计算变化分数。

“好学生”理解的多选中，口头表达/展示19/24、独立思考14/24、课堂发言/参与12/24、小组合作12/24被较多选择；8/24仍选择主要看考试成绩。没有人选择“没有明显变化”，但多选题不能测量变化幅度或价值排序。

## 支持资源与缺口

被选为帮助最大的资源包括香港本地同学{selected_text("q5_4_help_hk_peer")}、具有内地经历的同学{selected_text("q5_4_help_mainland_peer")}、科任老师{selected_text("q5_4_help_subject_teacher")}、班主任{selected_text("q5_4_help_homeroom_teacher")}和家庭{selected_text("q5_4_help_family")}。这些频数只描述被选入“最多三项”的资源。

Q5.5中“没有获得但希望获得”的单项人数均为1–2人；与此同时，“已获得但帮助有限”在英文教材/英语适应支持中为17/23、家长制度解释12/22、小组/发言/汇报训练11/23、繁体字与学科词汇9/22、评价规则说明8/22。两类响应在 `support_gap_analysis.csv` 中保持分开：前者是未满足需求，后者是已接触但帮助有限，不能合并成同一缺口。

## RQ3：数字平台作为关系基础设施

可配对的平台选择显示明显的媒体组合重构，而不是单一替代：WhatsApp由插班前0/24到后期19/24（19人新增选择），Instagram由1/24到19/24（18人新增），YouTube由2/24到13/24（11人新增）；微信由23/24到18/24但仍有18人两个时点都选择，QQ由14/24到4/24。Q6.2微博列缺失，不能比较。

后期与内地老同学联系的主要平台为微信21/24；与香港学校同学联系则为WhatsApp 13/24、Instagram 6/24、微信4/24、Telegram 1/24。分别维持两地关系23/23同意，不同平台上调整表达23/23同意，旧平台和老友提供情绪支持23/23同意，多平台承担不同作用21/22同意。线上规则障碍有8/23同意、8/23不确定、7/23不同意，显示平台加入并不等于没有线上参与门槛。

这些结果只描述平台与关系用途，不能把平台名称解释为文化融入、身份或政治立场，也不能声称某平台促进归属。

## 开放题的补充证据

Q8.1有17份非空回答。多标签归纳中，小组作业/课程任务或活动作为边界或进入事件出现于12份，主动邀请或解释帮助11份，午餐/放学/课间等日常互动10份，语言或本地共同经验障碍9份，明确距离或插不上话6份。Q8.2同样有17份非空回答：11份强调需要适应时间且困难不等于能力不足或不愿参与，9份要求更清楚的课程/评价/术语说明，9份提及同伴结对或桥梁，8份要求减少刻板预设，6份提及情绪关注，5份提及语言/学科词汇支持。

开放题计数可重叠，仅用于描述回答内容，不代表全体样本的主题出现率。相似措辞没有被当作重复或排除依据；为降低披露风险，本报告不复现开放题原文。

## 方法边界

所有数值可追溯至同目录CSV。样本为非概率、回顾性横截面自报；初期与后期题项并非等价纵向测量；自编项目组不是经过验证的量表；平台题是多选且Q6.2有缺列。报告使用“描述”“相关”“提示”，不作因果或全港总体推断。
"""
(OUT / "survey_findings.md").write_text(survey_findings_md, encoding="utf-8")


retained = exploratory_constructs.loc[
    exploratory_constructs["status"].eq("RETAINED_EXPLORATORY")
]
not_combined = exploratory_constructs.loc[
    exploratory_constructs["status"].eq("NOT_COMBINED")
]

construct_lines = []
for _, row in retained.iterrows():
    construct_lines.append(
        f"- **{row['construct_label']}**：n={int(row['scored_n'])}，"
        f"中位数{fmt_num(row['median'])}，IQR {fmt_num(row['q1'])}–"
        f"{fmt_num(row['q3'])}；完整案例alpha={fmt_num(row['cronbach_alpha_descriptive'])}。"
    )
not_combined_lines = []
for _, row in not_combined.iterrows():
    not_combined_lines.append(
        f"- **{row['construct_label']}**：不合成。{row['decision']} "
        f"（描述性alpha={fmt_num(row['cronbach_alpha_descriptive'])}；"
        f"题间Spearman中位数={fmt_num(row['median_pairwise_spearman'])}。）"
    )

construct_assessment_md = f"""# 探索性构念评估

## Material Passport

- Material ID: `{RUN_ID}-survey-constructs`
- Verification Status: `ANALYZED`
- Source: `exploratory_constructs.csv`
- Construct status: 探索性指标，不是经验证量表

## 评分规则

题项按1–5同向编码后取个人均值，不插补。5项指标至少需4项有效，9项指标至少需7项有效。特殊响应 `NOT_APPLICABLE`、`CANNOT_REMEMBER`、`UNWILLING_TO_ANSWER`、`BLANK`、`INVALID_RESPONSE` 不进入均值但在项目统计中保持独立。alpha与题间相关仅作本样本内描述，不证明单维性、效度或跨群体可比性。

## 保留作探索性指标

{chr(10).join(construct_lines)}

学术规则理解alpha约0.69，不能据此宣称可靠量表；其保留主要基于题项共同指向后期规则掌握及缺失可控。初期困难指标内部一致性较高也不代表九类困难是单一心理特质。

## 不合成的候选组

{chr(10).join(not_combined_lines)}

后续关联中，文化中介与平台功能只使用预先指定的单项，不把未通过本轮构念评估的候选组包装成量表。

## 已知工具限制

Q3.1第6项在导出中缺失。该项描述通过兴趣/课程/活动认识本地同学，方向与五个边界障碍项不同；本分析没有补造它，也没有将其缺失解释为个体层面缺失。Q2.11时点冲突使其不进入任何构念。Q6.2缺失的微博列不影响Q6.5分项，但限制平台时点比较的完整性。
"""
(OUT / "construct_assessment.md").write_text(
    construct_assessment_md, encoding="utf-8"
)


association_lines = []
for _, row in exploratory_associations.iterrows():
    association_lines.append(
        f"- **{row['analysis_id']}（{row['research_question']}）** "
        f"{row['x']} × {row['y']}：n={int(row['n'])}，"
        f"rho={fmt_num(row['rho'])}，置换p={fmt_num(row['p_permutation'], 3)}，"
        f"95% bootstrap区间[{fmt_num(row['bootstrap_ci_95_lower'])}, "
        f"{fmt_num(row['bootstrap_ci_95_upper'])}]，BH-FDR q="
        f"{fmt_num(row['bh_fdr_q'], 3)}。{row['interpretation_guardrail']}"
    )

exploratory_analysis_md = f"""# 探索性关联分析

## Material Passport

- Material ID: `{RUN_ID}-survey-associations`
- Verification Status: `ANALYZED`
- Source: `exploratory_associations.csv`
- Design: 非概率样本、回顾性横截面自报
- Tests: 5个预先限定的研究问题驱动检验

## 方法

使用Spearman rho。考虑n=22–24及大量并列秩，双侧p值来自{N_PERMUTATIONS:,}次Monte Carlo置换；不确定性用{N_BOOTSTRAPS:,}次配对bootstrap百分位区间描述。5个检验统一采用Benjamini–Hochberg FDR校正。效应大小标签只作描述，不替代区间、样本边界和构念质量判断。

另做一项敏感性检查：排除唯一完成时间短于300秒的合资格记录。该记录未因速度被主分析删除；各敏感性rho见CSV。

## 结果

{chr(10).join(association_lines)}

校正后没有任何关联达到q<0.05。A1呈中等负相关，A2呈中等正相关，但两者的未经校正p值分别约0.05与0.03，且均不通过五项FDR校正。A2的正方向尤其不能写成“初期越困难，后来越理解规则”；它可能反映不同暴露、回顾性辨识、共同反应方式、教学语言或学校安排等。A4的负方向同样不能解释为解释差异减少疲惫，因为它仅由两个天花板/偏态单项构成。

因此，这些分析只生成后续访谈可解释的探索性线索，不提供机制证据，也不支持筛选“典型”或“极端”参与者。

## 统计谬误扫描（11/11）

| 检查 | 结论 |
|---|---|
| Simpson悖论 | 未进行小样本分层推断，无法检验方向反转；不作总体机制判断。 |
| 生态谬误 | 分析单位与推断单位均为问卷个体；未从学校层面推断个体。 |
| Berkson/选择偏差 | 合资格筛选与非概率招募限制外推，列为CAUTION。 |
| 碰撞变量偏差 | 未加入控制变量或回归模型；本轮不适用。 |
| 基率忽视 | 未进行诊断/分类准确度分析；不适用。 |
| 均值回归 | 非按极端分数选组、无等价前后测；未声称改善。 |
| 幸存者偏差 | 没有纵向追踪，但招募与未完成者信息未知，列为抽样局限。 |
| 多重搜寻 | 限定5项并完整报告，使用BH-FDR；无校正后结果。 |
| 分岔路径 | 非预注册探索分析，构念及二分规则带研究者选择空间，列为CAUTION。 |
| 相关即因果 | 全部使用相关语言；设计不支持因果。 |
| 反向因果 | 时点虽有回顾性标签，但同次收集且无观察性时间序列，方向不能确定。 |

## 未执行或跳过

- Q2.11与语言/边界的关联：因最终问卷与导出题干的时点冲突而跳过。
- 因子分析、回归、组间人口学比较：n=24且样本非概率，方法上不支持。
- 初期—后期变化分数：题项并非等价前后测。
- Q6.2微博变化：后期导出列缺失，不能重建。
"""
(OUT / "exploratory_analysis.md").write_text(
    exploratory_analysis_md, encoding="utf-8"
)


print(
    json.dumps(
        {
            "eligible_n": len(eligible),
            "output_directory": str(OUT),
            "files": sorted(path.name for path in OUT.iterdir() if path.is_file()),
            "association_tests": len(exploratory_associations),
            "fdr_q_lt_0_05": int(
                (exploratory_associations["bh_fdr_q"] < 0.05).sum()
            ),
        },
        ensure_ascii=False,
        indent=2,
    )
)
