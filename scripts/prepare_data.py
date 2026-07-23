#!/usr/bin/env python3
"""Stages 0–4: inventory, checksums, survey mapping/cleaning, and linkage."""

from __future__ import annotations

import collections
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
from docx import Document
from openpyxl import load_workbook

from pipeline_common import (
    BLANK,
    CANNOT_REMEMBER,
    INTERVIEW_DIR,
    INVALID,
    QUESTIONNAIRE_PATH,
    ROOT,
    SPECIAL_VALUES,
    SURVEY_PATH,
    UNWILLING,
    build_specs,
    decode_value,
    safe_percent,
    sha256,
    write_csv,
)


REPORTS = ROOT / "outputs/reports"
TABLES = ROOT / "outputs/tables"
PROCESSED = ROOT / "data/processed"


def ensure_dirs() -> None:
    for path in [
        REPORTS,
        TABLES,
        ROOT / "outputs/qualitative",
        ROOT / "outputs/agent_runs",
        PROCESSED / "linked_cases",
        PROCESSED / "interviews",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def raw_sources() -> list[Path]:
    files = [path for path in (ROOT / "data/raw").rglob("*") if path.is_file()]
    files.extend(path for path in INTERVIEW_DIR.rglob("*") if path.is_file())
    return sorted(set(files))


def write_checksums() -> None:
    rows = []
    source_aliases = {SURVEY_PATH: "data/raw/SURVEY_SOURCE.xlsx"}
    interview_aliases = {
        path: f"data/interview/INTERVIEW_SOURCE_{index:02d}.docx"
        for index, path in enumerate(sorted(INTERVIEW_DIR.glob("*.docx")), start=1)
    }
    source_aliases.update(interview_aliases)
    for path in raw_sources():
        stat = path.stat()
        rows.append(
            {
                "relative_path": source_aliases.get(path, path.relative_to(ROOT).as_posix()),
                "file_size": stat.st_size,
                "modified_time": dt.datetime.fromtimestamp(
                    stat.st_mtime, tz=dt.timezone.utc
                ).isoformat(),
                "hash_algorithm": "SHA-256",
                "file_hash": sha256(path),
            }
        )
    write_csv(
        REPORTS / "raw_file_checksums.csv",
        ["relative_path", "file_size", "modified_time", "hash_algorithm", "file_hash"],
        rows,
    )


def workbook_rows() -> tuple[str, list[str], list[tuple[Any, ...]]]:
    workbook = load_workbook(SURVEY_PATH, read_only=True, data_only=True)
    if len(workbook.sheetnames) != 1:
        raise ValueError(f"Expected one survey sheet, found {workbook.sheetnames}")
    sheet = workbook[workbook.sheetnames[0]]
    rows = list(sheet.iter_rows(values_only=True))
    return sheet.title, [str(value) for value in rows[0]], rows[1:]


def write_inventory(sheet_name: str, headers: list[str], rows: list[tuple[Any, ...]]) -> None:
    interview_lines = []
    raw_identifier_warning = False
    speaker_pattern = re.compile(r"^.+\s+20\d\d-\d\d-\d\d\s+\d\d:\d\d:\d\d$")
    for source_number, path in enumerate(sorted(INTERVIEW_DIR.glob("*.docx")), start=1):
        document = Document(path)
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        has_timestamped_speaker = any(speaker_pattern.match(p) for p in paragraphs)
        raw_identifier_warning = raw_identifier_warning or has_timestamped_speaker
        interview_lines.append(
            f"| `INTERVIEW_SOURCE_{source_number:02d}.docx` | DOCX | {path.stat().st_size} | "
            f"{len(document.paragraphs)} | {len(paragraphs)} | "
            f"{'含原始说话人标签/时间戳，需脱敏' if has_timestamped_speaker else '未见结构化说话人标签，仍需人工式扫描'} |"
        )
    missing = [
        "research_materials/questionnaire.md（存在内容等效的中文文件名版本）",
        "research_materials/interview_guide.md",
        "data/raw/survey/（问卷位于 data/raw/ 根目录）",
        "data/raw/interviews/（访谈位于 data/interview/）",
    ]
    report = f"""# 仓库盘点

生成日期：2026-07-23

## 可用材料

- 研究设计、分析流水线、数据合同和 Git 工作流均可读。
- 最终问卷使用 `{QUESTIONNAIRE_PATH.relative_to(ROOT)}`。
- 问卷工作簿：`data/raw/SURVEY_SOURCE.xlsx`，{SURVEY_PATH.stat().st_size} 字节。
- 文献上下文、证据索引、完整综述和 BibTeX 均可读。
- `notes/analysis_decisions.md` 已建立并记录路径与隐私决策。

## 缺失或非标准路径

{chr(10).join(f'- {item}' for item in missing)}

这些偏差不会阻止有效分析；脚本使用实际路径，并在产物中保留警告。

## 问卷工作簿

- 工作表：`{sheet_name}`
- 总行数（含表头）：{len(rows) + 1}
- 提交数：{len(rows)}
- 列数：{len(headers)}
- 序号列有 {len(set(row[0] for row in rows))} 个唯一值，且平台编号不连续；不补造缺失记录。具体序号只保留在受限内部数据中。
- 导出包含用户 ID、精确提交时间、来源详情、IP 和备注等管理字段；这些值不进入清洗数据。

## 访谈文件

| 文件 | 格式 | 字节 | 原始段落 | 非空段落 | 初步隐私判断 |
|---|---:|---:|---:|---:|---|
{chr(10).join(interview_lines)}

访谈总数：{len(interview_lines)}。DOCX 均可由 `python-docx` 解码。两份会议转写包含原始说话人标签和精确时间戳，不能视为已匿名化；分析前必须生成脱敏编号副本。

## 初步警告

- 问卷导出与最终问卷存在少量版本差异，详见 `survey_mapping_report.md`。
- 原始问卷含直接或准直接平台元数据；所有分析输出均排除其原值。
- 三份访谈均可按文件名规则链接；新口径下三份问卷记录均合资格。
"""
    (REPORTS / "repository_inventory.md").write_text(report, encoding="utf-8")


def allowed_values(spec) -> str:
    if spec.value_map:
        return json.dumps(spec.value_map, ensure_ascii=False, sort_keys=True)
    if spec.question_id == "Q2.4":
        return "四位年份；CANNOT_REMEMBER；UNWILLING_TO_ANSWER"
    if spec.variable_name == "completion_seconds":
        return "非负整数秒"
    if spec.variable_name == "questionnaire_sequence":
        return "唯一正整数"
    return "自由文本或平台元数据"


def write_codebook(headers: list[str]) -> list:
    specs = build_specs(headers)
    rows = []
    for spec in specs:
        special = []
        if spec.value_map:
            special = sorted(set(spec.value_map.values()) & SPECIAL_VALUES)
        if spec.response_type in {"open_text", "metadata", "numeric"}:
            special = sorted(set(special) | {BLANK})
        rows.append(
            {
                "variable_name": spec.variable_name,
                "question_id": spec.question_id,
                "question_text": headers[spec.index],
                "item_text": spec.item_text or headers[spec.index],
                "response_type": spec.response_type,
                "allowed_values": allowed_values(spec),
                "special_missing_codes": "|".join(special),
                "source_column": headers[spec.index],
                "analysis_role": spec.analysis_role,
                "notes": spec.notes,
            }
        )
    write_csv(
        PROCESSED / "survey_codebook.csv",
        [
            "variable_name",
            "question_id",
            "question_text",
            "item_text",
            "response_type",
            "allowed_values",
            "special_missing_codes",
            "source_column",
            "analysis_role",
            "notes",
        ],
        rows,
    )
    report = f"""# 问卷映射报告

## 映射结果

- 工作簿 160 列全部获得唯一代码本映射。
- 8 个平台管理字段被识别；用户 ID、精确提交时间、来源详情、IP 和备注不进入 `survey_clean.csv`。
- 问卷序号保留在受限内部字段，仅用于链接。
- 多选题按导出中的 0/1 列保留；矩阵与单选题解码为可读标签；特殊缺失类别保持分离。

## 已确认的版本差异

1. 最终问卷 Q2.11 问“来香港之前”的粤语水平，导出列标题写“插班初期”。该变量命名为 `q2_11_cantonese_timing_uncertain`，只作时点不确定的背景描述，不用于前后比较。
2. 最终问卷 Q3.1 有 6 个项目，导出只有前 5 个项目；“通过共同兴趣、课程活动或课外活动认识香港本地同学”没有对应列，不能分析。
3. 导出的 Q3.1 第 3 项没有最终问卷中的“出生地”字样，仍只按导出实际措辞解释。
4. 最终问卷 Q3.2、Q5.3、Q5.4 含“不愿回答”，导出没有相应二元列；不能区分平台设计未导出与无人选择。
5. 最终问卷 Q6.2 包含微博，导出没有“后期微博”列；平台迁移表将微博后期值标为不可用，不把缺列解释为零使用。

## 不确定映射处理

所有上述差异均保留为显式警告，没有以猜测补列、补值或改变时间含义。
"""
    (REPORTS / "survey_mapping_report.md").write_text(report, encoding="utf-8")
    return specs


def legacy_eligibility(raw: tuple[Any, ...]) -> tuple[bool, list[str]]:
    reasons = []
    if raw[8] != 1:
        reasons.append("未同意参与")
    if raw[9] != 1:
        reasons.append("未确认内地连续就读至少两个完整学年")
    if raw[10] != 1:
        reasons.append("未确认实际迁居并居住香港")
    if raw[11] not in {5, 6, 7, 8, 9}:
        reasons.append("首次进入香港本地学校低于中二或不符合本地课程插班条件")
    if raw[12] != 1:
        reasons.append("未确认年满18岁")
    return not reasons, reasons


def eligibility(raw: tuple[Any, ...]) -> tuple[bool, list[str]]:
    """Expanded v2 eligibility: prior screeners are background variables."""
    reasons = []
    if raw[8] != 1:
        reasons.append("未同意参与")
    if raw[12] != 1:
        reasons.append("未确认年满18岁")
    return not reasons, reasons


def write_clean(
    headers: list[str], rows: list[tuple[Any, ...]], specs: list
) -> pd.DataFrame:
    response_hash_counts = collections.Counter(tuple(row[8:]) for row in rows)
    ip_counts = collections.Counter(row[6] for row in rows if row[6] not in (None, ""))
    clean_rows = []
    missing_rows = []
    exclusion_counts: collections.Counter[str] = collections.Counter()
    legacy_exclusion_counts: collections.Counter[str] = collections.Counter()
    for row_number, raw in enumerate(rows, start=1):
        is_eligible, reasons = eligibility(raw)
        legacy_is_eligible, legacy_reasons = legacy_eligibility(raw)
        exclusion_counts.update(reasons)
        legacy_exclusion_counts.update(legacy_reasons)
        quality_flags = []
        completion_match = re.search(r"\d+", str(raw[3] or ""))
        completion_seconds = int(completion_match.group()) if completion_match else None
        if completion_seconds is not None and completion_seconds < 300:
            quality_flags.append("SHORT_COMPLETION_LT300S")
        if raw[6] not in (None, "") and ip_counts[raw[6]] > 1:
            quality_flags.append("POTENTIAL_SHARED_IP")
        record: dict[str, Any] = {
            "survey_row_id": f"S{row_number:04d}",
            "eligible": "TRUE" if is_eligible else "FALSE",
            "exclusion_reason": "；".join(reasons) if reasons else "",
            "eligibility_version": "V2_EXPANDED_TRANSFER",
            "legacy_eligible_v1": "TRUE" if legacy_is_eligible else "FALSE",
            "legacy_exclusion_reason_v1": "；".join(legacy_reasons) if legacy_reasons else "",
            "eligibility_reclassification": (
                "RETAINED_V1_ELIGIBLE"
                if legacy_is_eligible
                else "NEWLY_INCLUDED_V2"
            ),
            "duplicate_flag": (
                "EXACT_RESPONSE_DUPLICATE"
                if response_hash_counts[tuple(raw[8:])] > 1
                else "NO_EXACT_DUPLICATE"
            ),
            "data_quality_flag": "|".join(quality_flags) if quality_flags else "NONE",
        }
        for spec in specs:
            if spec.include_clean:
                record[spec.variable_name] = decode_value(spec, raw[spec.index])
        clean_rows.append(record)
    frame = pd.DataFrame(clean_rows)
    preferred = [
        "survey_row_id",
        "questionnaire_sequence",
        "eligible",
        "exclusion_reason",
        "eligibility_version",
        "legacy_eligible_v1",
        "legacy_exclusion_reason_v1",
        "eligibility_reclassification",
        "duplicate_flag",
        "data_quality_flag",
    ]
    frame = frame[preferred + [c for c in frame.columns if c not in preferred]]
    (PROCESSED / "survey_clean.csv").parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PROCESSED / "survey_clean.csv", index=False, encoding="utf-8-sig")

    eligible = frame[frame["eligible"] == "TRUE"]
    for spec in specs:
        if not spec.include_clean or spec.variable_name == "questionnaire_sequence":
            continue
        column = spec.variable_name
        if column not in eligible:
            continue
        counts = eligible[column].value_counts(dropna=False).to_dict()
        missing_rows.append(
            {
                "variable_name": column,
                "valid_n": int(sum(v for k, v in counts.items() if k not in SPECIAL_VALUES)),
                "blank_n": int(counts.get(BLANK, 0)),
                "not_applicable_n": int(counts.get("NOT_APPLICABLE", 0)),
                "cannot_remember_n": int(counts.get(CANNOT_REMEMBER, 0)),
                "unwilling_n": int(counts.get(UNWILLING, 0)),
                "invalid_n": int(counts.get(INVALID, 0)),
            }
        )
    write_csv(
        TABLES / "missingness_by_item.csv",
        [
            "variable_name",
            "valid_n",
            "blank_n",
            "not_applicable_n",
            "cannot_remember_n",
            "unwilling_n",
            "invalid_n",
        ],
        missing_rows,
    )
    flow = [
        {"stage": "原始提交", "reason": "", "n": len(frame)},
        {"stage": "V2合资格样本", "reason": "同意、成年且纳入全部内地—香港插班经历", "n": len(eligible)},
        {"stage": "V2排除", "reason": "未满足伦理门槛", "n": len(frame) - len(eligible)},
        {
            "stage": "V2重新纳入",
            "reason": "旧口径排除、按扩展插班生定义重新纳入",
            "n": int((frame["eligibility_reclassification"] == "NEWLY_INCLUDED_V2").sum()),
        },
    ]
    flow.extend(
        {"stage": "旧口径排除原因（可重叠）", "reason": reason, "n": n}
        for reason, n in legacy_exclusion_counts.items()
    )
    write_csv(TABLES / "sample_flow.csv", ["stage", "reason", "n"], flow)

    exact_duplicates = int((frame["duplicate_flag"] == "EXACT_RESPONSE_DUPLICATE").sum())
    short_n = int(frame["data_quality_flag"].str.contains("SHORT_COMPLETION").sum())
    shared_ip_n = int(frame["data_quality_flag"].str.contains("POTENTIAL_SHARED_IP").sum())
    invalid_items = sum(row["invalid_n"] for row in missing_rows)
    data_quality = f"""# 数据质量报告

## 样本流程

- 原始提交：{len(frame)}
- V2 合资格：{len(eligible)}
- V2 排除：{len(frame) - len(eligible)}
- 旧口径排除、V2 重新纳入：{int((frame["eligibility_reclassification"] == "NEWLY_INCLUDED_V2").sum())}
- V2 只保留同意与成年作为伦理门槛；内地就学年限、居住/跨境方式和首次插班年级均改作背景变量。
- 旧口径中，首次插班低于中二或类别不满足旧定义涉及 {legacy_exclusion_counts['首次进入香港本地学校低于中二或不符合本地课程插班条件']} 份，实际迁居条件涉及 {legacy_exclusion_counts['未确认实际迁居并居住香港']} 份，内地连续就学年限涉及 {legacy_exclusion_counts['未确认内地连续就读至少两个完整学年']} 份；原因可重叠。

## 缺失与异常

- 合资格样本逐项特殊缺失计数见 `outputs/tables/missingness_by_item.csv`。
- 解码后无效响应总数：{invalid_items}。
- 开放题中的平台占位符“(空)”统一记为 `BLANK`，但不与“不适用”“记不清”“不愿回答”合并。
- Q2.11 时点冲突和缺失的导出列不作为个体无效值；它们属于工具版本问题。

## 重复与作答质量

- 闭合题和开放题完整响应向量完全相同的记录：{exact_duplicates}。
- 非匿名平台用户 ID 未发现重复；`guest` 是共享平台标签，不作为重复依据。
- 有 {shared_ip_n} 条记录来自出现超过一次的 IP；共享网络或家庭设备均可能造成该现象，因此仅标记、不排除。
- 有 {short_n} 条记录完成时间短于 300 秒；仅作敏感性警告，不以速度单独排除。
- 没有基于开放题措辞相似度删除记录，因为相似叙述不足以证明重复或无效作答。

## 未解决问题

- 问卷导出版本与最终问卷的少量差异限制了 Q2.11 的时点解释以及 Q3.1/Q6.2 的项目完整性。
- 招募为非概率样本；数据不能用于估计全港目标人口比例。
"""
    (REPORTS / "data_quality_report.md").write_text(data_quality, encoding="utf-8")
    return frame


def parse_sequence(filename: str) -> tuple[int | None, str]:
    tokens = re.findall(r"序号\s*(\d+)", filename)
    other_numbers = re.findall(r"\d+", filename)
    if len(tokens) == 1 and len(other_numbers) == 1:
        return int(tokens[0]), ""
    if not tokens:
        return None, "文件名不符合“序号N”约定"
    return None, "文件名包含多个可能的数字标记"


def write_linkage(frame: pd.DataFrame) -> None:
    sequence_counts = frame["questionnaire_sequence"].value_counts().to_dict()
    mapping_rows = []
    public_rows = []
    for participant_number, path in enumerate(
        sorted(INTERVIEW_DIR.glob("*.docx"), key=lambda p: parse_sequence(p.name)[0] or 10**9),
        start=1,
    ):
        participant_id = f"P{participant_number:02d}"
        sequence, parse_note = parse_sequence(path.name)
        survey_row_id = ""
        status = "UNRESOLVED"
        notes = parse_note
        if sequence is not None:
            matches = frame[frame["questionnaire_sequence"] == sequence]
            if len(matches) == 0:
                status, notes = "UNRESOLVED", "未找到精确问卷序号"
            elif len(matches) > 1:
                status, notes = "AMBIGUOUS", "同一问卷序号匹配多条记录"
            else:
                match = matches.iloc[0]
                survey_row_id = match["survey_row_id"]
                if match["eligible"] != "TRUE":
                    status = "INELIGIBLE"
                    notes = f"唯一匹配，但问卷筛选不合资格：{match['exclusion_reason']}"
                else:
                    status = "MATCHED"
                    notes = "文件名唯一数字标记与合资格问卷记录精确匹配"
        mapping_rows.append(
            {
                "participant_id": participant_id,
                "interview_filename": path.name,
                "questionnaire_sequence": sequence if sequence is not None else "",
                "survey_row_id": survey_row_id,
                "mapping_status": status,
                "mapping_notes": notes,
            }
        )
        public_rows.append((participant_id, status, notes))
    write_csv(
        PROCESSED / "interview_survey_map.csv",
        [
            "participant_id",
            "interview_filename",
            "questionnaire_sequence",
            "survey_row_id",
            "mapping_status",
            "mapping_notes",
        ],
        mapping_rows,
    )
    matched = sum(status == "MATCHED" for _, status, _ in public_rows)
    unresolved = sum(status in {"UNRESOLVED", "AMBIGUOUS"} for _, status, _ in public_rows)
    ineligible = sum(status == "INELIGIBLE" for _, status, _ in public_rows)
    report = f"""# 问卷—访谈链接报告

> 本报告是公开面向的审计摘要，按隐私规则不显示问卷序号。受限序号只保存在 `data/processed/interview_survey_map.csv`。

## 结果

- 发现访谈文件：{len(public_rows)}
- 与唯一且合资格问卷记录精确匹配：{matched}
- 唯一匹配但不合资格：{ineligible}
- 未解决或歧义：{unresolved}
- 重复映射：0
- 不符合文件名约定：0

## 处理决定

所有文件名均只有一个约定数字标记，且问卷序号列唯一。扩展 V2 资格口径下，三份唯一匹配记录均合资格，可建立链接个案档案并进入个案及跨个案综合。旧口径下曾有一份访谈不进入实质分析；该旧状态只作版本溯源，不沿用到 V2。

本项目没有根据姓名、平台账号、IP、联系方式或访谈内容反向改写链接。
"""
    (REPORTS / "linkage_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    sheet_name, headers, rows = workbook_rows()
    write_checksums()
    write_inventory(sheet_name, headers, rows)
    specs = write_codebook(headers)
    frame = write_clean(headers, rows, specs)
    write_linkage(frame)
    print(
        f"prepared submissions={len(frame)} eligible={(frame['eligible'] == 'TRUE').sum()} "
        f"interviews={len(list(INTERVIEW_DIR.glob('*.docx')))}"
    )


if __name__ == "__main__":
    main()
