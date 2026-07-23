#!/usr/bin/env python3
"""Shared schemas and helpers for the linked mixed-methods pipeline."""

from __future__ import annotations

import csv
import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SURVEY_FILES = sorted((ROOT / "data/raw").glob("*.xlsx"))
if len(SURVEY_FILES) != 1:
    raise RuntimeError(f"Expected exactly one survey workbook, found {len(SURVEY_FILES)}")
SURVEY_PATH = SURVEY_FILES[0]
INTERVIEW_DIR = ROOT / "data/interview"
QUESTIONNAIRE_PATH = (
    ROOT
    / "research_materials/内地迁居香港高年级插班学生的学校适应、同伴关系与数字生活调查.md"
)
RUN_ID = "20260723_expanded_eligibility"

BLANK = "BLANK"
NOT_APPLICABLE = "NOT_APPLICABLE"
CANNOT_REMEMBER = "CANNOT_REMEMBER"
UNWILLING = "UNWILLING_TO_ANSWER"
INVALID = "INVALID_RESPONSE"


@dataclass(frozen=True)
class ColumnSpec:
    index: int
    variable_name: str
    question_id: str
    response_type: str
    analysis_role: str
    value_map: dict[int, str] | None = None
    item_text: str = ""
    notes: str = ""
    include_clean: bool = True


def ordered_map(values: list[str]) -> dict[int, str]:
    return {i + 1: value for i, value in enumerate(values)}


CONSENT = ordered_map(["同意参加", "不同意参加"])
YES_NO_UNCERTAIN = ordered_map(["是", "否", "不确定"])
MOVED_HK = ordered_map(
    [
        "是，我曾迁居并居住在香港",
        "否，我主要居住在内地并每日或频繁往返香港上学",
        "其他情况",
        UNWILLING,
    ]
)
ENTRY_GRADE = ordered_map(
    [
        "小学四年级",
        "小学五年级",
        "小学六年级",
        "中学一年级",
        "中学二年级",
        "中学三年级",
        "中学四年级",
        "中学五年级",
        "中学六年级",
        "从较低年级开始在香港就读，并非中途插班",
        "只进入国际学校，未进入香港本地课程体系",
        "其他",
        CANNOT_REMEMBER,
        UNWILLING,
    ]
)
YES_NO_UNWILLING = ordered_map(["是", "否", UNWILLING])
STATUS = ordered_map(
    [
        "仍在香港本地中学就读",
        "在香港的大专院校或大学就读",
        "在中国内地的大专院校或大学就读",
        "在其他国家或地区的大专院校或大学就读",
        "已毕业，目前主要在香港生活或工作",
        "已毕业，目前主要在香港以外生活或工作",
        "其他",
        UNWILLING,
    ]
)
RESIDENCE = ordered_map(
    ["香港", "中国内地", "澳门", "其他国家或地区", "经常在不同地区之间居住", UNWILLING]
)
GENDER = ordered_map(["女", "男", "非二元性别或其他", UNWILLING])
HK_DURATION = ordered_map(
    [
        "不足1年",
        "1年至不足2年",
        "2年至不足3年",
        "3年至不足5年",
        "5年或以上",
        CANNOT_REMEMBER,
        UNWILLING,
    ]
)
TRANSFER_COUNT = ordered_map(
    ["没有", "有，转过1次", "有，转过2次或以上", CANNOT_REMEMBER, UNWILLING]
)
SCHOOL_TYPE = ordered_map(
    ["官立学校", "资助学校", "直接资助计划学校", "私立本地学校", "不知道", "其他", UNWILLING]
)
REGION = ordered_map(
    [
        "华北地区",
        "华东地区",
        "华南地区",
        "华中地区",
        "西南地区",
        "西北地区",
        "东北地区",
        "其他",
        "不确定",
        UNWILLING,
    ]
)
CANTONESE = ordered_map(
    [
        "完全不会",
        "会一些简单日常用语",
        "可以进行基本交流",
        "可以比较流利地交流",
        "粤语是我经常使用的语言之一",
        CANNOT_REMEMBER,
        UNWILLING,
    ]
)
FREQUENCY = ordered_map(
    ["几乎不用", "偶尔使用", "有时使用", "经常使用", "几乎每天使用", NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING]
)
BOUNDARY_FREQ = ordered_map(
    ["从未", "很少", "有时", "经常", "非常经常", NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING]
)
AGREEMENT = ordered_map(
    ["完全不同意", "比较不同意", "不确定", "比较同意", "完全同意", NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING]
)
DIFFICULTY = ordered_map(
    ["完全不困难", "比较不困难", "一般", "比较困难", "非常困难", NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING]
)
SUPPORT_STATUS = ordered_map(
    [
        "已获得，而且帮助较大",
        "已获得，但帮助有限",
        "没有获得，但希望获得",
        "没有获得，也不需要",
        NOT_APPLICABLE,
        CANNOT_REMEMBER,
        UNWILLING,
    ]
)
OVERALL_FIT = ordered_map(
    [
        "香港的学习和生活环境整体上更适合自己",
        "内地的学习和生活环境整体上更适合自己",
        "内地和香港分别在不同方面更适合自己",
        "两边都能够适应",
        "两边都不完全适合自己",
        "取决于具体场景和交往对象",
        "不确定",
        UNWILLING,
        "其他",
    ]
)
OLD_FRIEND_PLATFORM = ordered_map(
    ["微信", "QQ", "小红书", "Instagram", "WhatsApp", "线上游戏", "其他", "很少与内地老同学联系", NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING]
)
HK_PEER_PLATFORM = ordered_map(
    ["WhatsApp", "Instagram", "微信", "Discord", "Telegram", "线上游戏", "学校指定平台", "其他", "很少在线上联系", NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING]
)
PEER_NETWORK = ordered_map(
    [
        "主要进入香港本地同学的社交圈",
        "主要与内地背景同学交往",
        "同时维持几个不同背景的朋友圈",
        "根据课程、兴趣和场景进入不同群体",
        "仍然较少进入稳定的同伴群体",
        "很难概括",
        "其他",
        CANNOT_REMEMBER,
        UNWILLING,
    ]
)

SPECIAL_VALUES = {BLANK, NOT_APPLICABLE, CANNOT_REMEMBER, UNWILLING, INVALID}


def build_specs(headers: list[str]) -> list[ColumnSpec]:
    """Return the canonical mapping for the observed 160-column export."""
    if len(headers) != 160:
        raise ValueError(f"Expected 160 survey columns, found {len(headers)}")
    specs: list[ColumnSpec] = [
        ColumnSpec(0, "questionnaire_sequence", "ADMIN_SEQUENCE", "metadata", "restricted_linkage"),
        ColumnSpec(1, "admin_user_id", "ADMIN_USER_ID", "metadata", "excluded_privacy", include_clean=False),
        ColumnSpec(2, "admin_submit_time", "ADMIN_SUBMIT_TIME", "metadata", "excluded_privacy", include_clean=False),
        ColumnSpec(3, "completion_seconds", "ADMIN_DURATION", "numeric", "data_quality"),
        ColumnSpec(4, "admin_source", "ADMIN_SOURCE", "metadata", "excluded_privacy", include_clean=False),
        ColumnSpec(5, "admin_source_detail", "ADMIN_SOURCE_DETAIL", "metadata", "excluded_privacy", include_clean=False),
        ColumnSpec(6, "admin_ip", "ADMIN_IP", "metadata", "excluded_privacy", include_clean=False),
        ColumnSpec(7, "admin_remarks", "ADMIN_REMARKS", "metadata", "excluded_privacy", include_clean=False),
        ColumnSpec(8, "q0_1_consent", "Q0.1", "screening", "eligibility", CONSENT),
        ColumnSpec(9, "q1_1_mainland_two_years", "Q1.1", "screening", "eligibility", YES_NO_UNCERTAIN),
        ColumnSpec(10, "q1_2_moved_hk", "Q1.2", "screening", "eligibility", MOVED_HK),
        ColumnSpec(11, "q1_3_entry_grade", "Q1.3", "screening", "eligibility", ENTRY_GRADE),
        ColumnSpec(12, "q1_4_age18", "Q1.4", "screening", "eligibility", YES_NO_UNWILLING),
        ColumnSpec(13, "q2_1_current_status", "Q2.1", "single_choice", "demographic", STATUS),
        ColumnSpec(14, "q2_2_current_residence", "Q2.2", "single_choice", "demographic", RESIDENCE),
        ColumnSpec(15, "q2_3_gender", "Q2.3", "single_choice", "demographic", GENDER),
        ColumnSpec(16, "q2_4_entry_year", "Q2.4", "numeric", "demographic"),
        ColumnSpec(17, "q2_5_hk_school_duration", "Q2.5", "single_choice", "demographic", HK_DURATION),
        ColumnSpec(18, "q2_6_hk_transfer_count", "Q2.6", "single_choice", "demographic", TRANSFER_COUNT),
        ColumnSpec(19, "q2_7_school_type", "Q2.7", "single_choice", "demographic", SCHOOL_TYPE),
    ]

    def add_binary(indices: range, names: list[str], qid: str, role: str) -> None:
        for idx, name in zip(indices, names, strict=True):
            specs.append(ColumnSpec(idx, name, qid, "multiple_choice", role, {0: "未选择", 1: "选择"}))

    add_binary(
        range(20, 27),
        [
            "q2_8_language_cantonese",
            "q2_8_language_mandarin",
            "q2_8_language_english",
            "q2_8_language_mixed",
            "q2_8_language_other",
            "q2_8_language_cannot_remember",
            "q2_8_language_unwilling",
        ],
        "Q2.8",
        "demographic",
    )
    specs.extend(
        [
            ColumnSpec(27, "q2_9_prior_region", "Q2.9", "single_choice", "demographic", REGION),
        ]
    )
    add_binary(
        range(28, 36),
        [
            "q2_10_reason_family_move",
            "q2_10_reason_parent_work",
            "q2_10_reason_reunion",
            "q2_10_reason_different_education",
            "q2_10_reason_future_opportunity",
            "q2_10_reason_personal",
            "q2_10_reason_other",
            "q2_10_reason_unwilling",
        ],
        "Q2.10",
        "demographic",
    )
    specs.append(
        ColumnSpec(
            36,
            "q2_11_cantonese_timing_uncertain",
            "Q2.11",
            "single_choice",
            "demographic",
            CANTONESE,
            notes="Export says 插班初期; final questionnaire says 来香港之前. Timing is unresolved.",
        )
    )
    for idx, lang in zip(range(37, 40), ["mandarin", "cantonese", "english"], strict=True):
        specs.append(ColumnSpec(idx, f"q2_12_{lang}_frequency", f"Q2.12_{idx-36}", "matrix", "language_use", FREQUENCY))
    boundary_names = [
        "language_humour_barrier",
        "local_knowledge_barrier",
        "background_assumption",
        "mainland_grouping_assumption",
        "self_withdrawal",
    ]
    for idx, name in zip(range(40, 45), boundary_names, strict=True):
        specs.append(ColumnSpec(idx, f"q3_1_{name}", f"Q3.1_{idx-39}", "matrix", "peer_boundary", BOUNDARY_FREQ))
    add_binary(
        range(45, 58),
        [
            "q3_2_help_neighbor",
            "q3_2_help_teacher_assignment",
            "q3_2_help_mainland_peer",
            "q3_2_help_hk_peer_invitation",
            "q3_2_help_groupwork",
            "q3_2_help_extracurricular",
            "q3_2_help_informal_activity",
            "q3_2_help_online_group",
            "q3_2_help_relatives",
            "q3_2_help_self_initiated",
            "q3_2_help_other",
            "q3_2_help_none",
            "q3_2_help_cannot_remember",
        ],
        "Q3.2",
        "peer_entry_support",
    )
    belonging_names = ["member", "trusted_peer", "included_group", "authentic_self", "knows_help_peer"]
    for idx, name in zip(range(58, 63), belonging_names, strict=True):
        specs.append(ColumnSpec(idx, f"q3_3_{name}", f"Q3.3_{idx-57}", "matrix", "school_belonging", AGREEMENT))
    identity_names = [
        "adjust_expression",
        "retain_and_participate",
        "no_binary_identity_choice",
        "explain_differences",
        "reduce_misunderstanding",
        "brokerage_fatigue",
        "dual_marginality",
        "contextual_repertoire",
        "avoid_contentious_topics",
    ]
    identity_roles = [
        "identity_negotiation",
        "identity_negotiation",
        "identity_negotiation",
        "brokerage_participation",
        "brokerage_participation",
        "brokerage_pressure",
        "brokerage_pressure",
        "identity_negotiation",
        "identity_negotiation",
    ]
    for idx, name, role in zip(range(63, 72), identity_names, identity_roles, strict=True):
        specs.append(ColumnSpec(idx, f"q4_1_{name}", f"Q4.1_{idx-62}", "matrix", role, AGREEMENT))
    specs.append(ColumnSpec(72, "q4_2_overall_fit", "Q4.2", "single_choice", "identity_negotiation", OVERALL_FIT))
    difficulty_names = [
        "traditional_chinese",
        "cantonese_class",
        "english_materials",
        "answer_format",
        "class_participation",
        "group_project",
        "presentation",
        "assessment_mix",
        "hidden_rules",
    ]
    for idx, name in zip(range(73, 82), difficulty_names, strict=True):
        specs.append(ColumnSpec(idx, f"q5_1_{name}", f"Q5.1_{idx-72}", "matrix", "academic_difficulty", DIFFICULTY))
    rule_names = ["good_assignment", "assessment_rules", "discussion_rules", "transfer_prior_strengths", "distinguish_rules_ability"]
    for idx, name in zip(range(82, 87), rule_names, strict=True):
        specs.append(ColumnSpec(idx, f"q5_2_{name}", f"Q5.2_{idx-81}", "matrix", "academic_rule_understanding", AGREEMENT))
    add_binary(
        range(87, 98),
        [
            "q5_3_good_student_exam",
            "q5_3_good_student_participation",
            "q5_3_good_student_groupwork",
            "q5_3_good_student_presentation",
            "q5_3_good_student_extracurricular",
            "q5_3_good_student_service",
            "q5_3_good_student_independent_thinking",
            "q5_3_good_student_communication",
            "q5_3_good_student_no_change",
            "q5_3_good_student_other",
            "q5_3_good_student_cannot_remember",
        ],
        "Q5.3",
        "learner_identity",
    )
    add_binary(
        range(98, 110),
        [
            "q5_4_help_homeroom_teacher",
            "q5_4_help_subject_teacher",
            "q5_4_help_hk_peer",
            "q5_4_help_mainland_peer",
            "q5_4_help_family",
            "q5_4_help_counselling",
            "q5_4_help_school_orientation",
            "q5_4_help_tutor",
            "q5_4_help_online_info",
            "q5_4_help_other",
            "q5_4_help_none",
            "q5_4_help_cannot_remember",
        ],
        "Q5.4",
        "support_resources",
    )
    support_names = [
        "cantonese",
        "english",
        "traditional_chinese",
        "assessment_rules",
        "participation_presentation",
        "peer_buddy",
        "emotional_anti_exclusion",
        "parent_system_explanation",
    ]
    for idx, name in zip(range(110, 118), support_names, strict=True):
        specs.append(ColumnSpec(idx, f"q5_5_{name}_support", f"Q5.5_{idx-109}", "matrix", "support_gap", SUPPORT_STATUS))
    add_binary(
        range(118, 134),
        [
            "q6_1_pre_wechat",
            "q6_1_pre_qq",
            "q6_1_pre_xiaohongshu",
            "q6_1_pre_bilibili",
            "q6_1_pre_douyin",
            "q6_1_pre_weibo",
            "q6_1_pre_whatsapp",
            "q6_1_pre_instagram",
            "q6_1_pre_youtube",
            "q6_1_pre_discord",
            "q6_1_pre_telegram",
            "q6_1_pre_game_chat",
            "q6_1_pre_other",
            "q6_1_pre_low_use",
            "q6_1_pre_cannot_remember",
            "q6_1_pre_unwilling",
        ],
        "Q6.1",
        "platform_pre",
    )
    add_binary(
        range(134, 149),
        [
            "q6_2_later_wechat",
            "q6_2_later_qq",
            "q6_2_later_xiaohongshu",
            "q6_2_later_bilibili",
            "q6_2_later_douyin",
            "q6_2_later_whatsapp",
            "q6_2_later_instagram",
            "q6_2_later_youtube",
            "q6_2_later_discord",
            "q6_2_later_telegram",
            "q6_2_later_game_chat",
            "q6_2_later_other",
            "q6_2_later_low_use",
            "q6_2_later_cannot_remember",
            "q6_2_later_unwilling",
        ],
        "Q6.2",
        "platform_later",
    )
    specs.extend(
        [
            ColumnSpec(149, "q6_3_old_friend_platform", "Q6.3", "single_choice", "platform_function", OLD_FRIEND_PLATFORM),
            ColumnSpec(150, "q6_4_hk_peer_platform", "Q6.4", "single_choice", "platform_function", HK_PEER_PLATFORM),
        ]
    )
    platform_names = [
        "separate_relations",
        "different_expression",
        "hk_platform_participation",
        "old_network_emotional_support",
        "multiple_roles",
        "online_rule_barrier",
    ]
    for idx, name in zip(range(151, 157), platform_names, strict=True):
        specs.append(ColumnSpec(idx, f"q6_5_{name}", f"Q6.5_{idx-150}", "matrix", "platform_practices", AGREEMENT))
    specs.extend(
        [
            ColumnSpec(157, "q7_1_peer_network", "Q7.1", "single_choice", "peer_network", PEER_NETWORK),
            ColumnSpec(158, "q8_1_boundary_event_text", "Q8.1", "open_text", "open_text"),
            ColumnSpec(159, "q8_2_support_request_text", "Q8.2", "open_text", "open_text"),
        ]
    )
    specs.sort(key=lambda spec: spec.index)
    if [spec.index for spec in specs] != list(range(160)):
        raise AssertionError("Column specification does not cover every export column exactly once")
    return specs


def decode_value(spec: ColumnSpec, value: Any) -> Any:
    if value is None:
        return BLANK
    if spec.response_type == "open_text":
        text = re.sub(r"\s+", " ", str(value)).strip()
        return BLANK if text in {"", "(空)"} else text
    if spec.variable_name == "completion_seconds":
        match = re.search(r"\d+", str(value))
        return int(match.group()) if match else INVALID
    if spec.variable_name == "questionnaire_sequence":
        try:
            return int(value)
        except (TypeError, ValueError):
            return INVALID
    if spec.question_id == "Q2.4":
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            year = int(value)
            return year if 1900 <= year <= 2026 else INVALID
        text = str(value).strip()
        if text == "记不清":
            return CANNOT_REMEMBER
        if text == "不愿回答":
            return UNWILLING
        return INVALID
    if spec.value_map is not None:
        try:
            key = int(value)
        except (TypeError, ValueError):
            return INVALID
        return spec.value_map.get(key, INVALID)
    return str(value).strip()


def numeric_matrix_value(value: Any) -> float:
    """Convert decoded or raw 1–5 matrix values to numeric, otherwise NaN."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        value = int(value)
        return float(value) if 1 <= value <= 5 else math.nan
    return math.nan


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def safe_percent(n: int, denominator: int) -> str:
    return "" if denominator == 0 else f"{100 * n / denominator:.1f}"
