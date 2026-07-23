#!/usr/bin/env python3
"""Stage 15 automated validation for the complete analysis pipeline."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pandas as pd

from pipeline_common import INTERVIEW_DIR, ROOT, SURVEY_PATH

REPORTS = ROOT / "outputs/reports"
TABLES = ROOT / "outputs/tables"
PROCESSED = ROOT / "data/processed"
QUALITATIVE = ROOT / "outputs/qualitative"

checks: list[dict[str, str]] = []


def record(check_id: str, status: str, detail: str) -> None:
    checks.append({"check_id": check_id, "status": status, "detail": detail})


def require(condition: bool, check_id: str, detail: str) -> None:
    record(check_id, "PASS" if condition else "FAIL", detail)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_checksum_path(alias: str) -> Path:
    if alias == "data/raw/SURVEY_SOURCE.xlsx":
        return SURVEY_PATH
    match = re.fullmatch(r"data/interview/INTERVIEW_SOURCE_(\d{2})\.docx", alias)
    if match:
        sources = sorted(INTERVIEW_DIR.glob("*.docx"))
        return sources[int(match.group(1)) - 1]
    return ROOT / alias


def numbered_lines(participant_id: str) -> dict[str, tuple[str, str]]:
    path = PROCESSED / "interviews" / f"interview_{participant_id}_numbered.md"
    result = {}
    pattern = re.compile(r"^\[(L\d{4})\]\s+([^:]+):\s?(.*)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            result[match.group(1)] = (match.group(2), match.group(3))
    return result


def validate_required_files() -> None:
    required = [
        PROCESSED / "survey_codebook.csv",
        PROCESSED / "survey_clean.csv",
        PROCESSED / "interview_survey_map.csv",
        PROCESSED / "qualitative_codebook.csv",
        QUALITATIVE / "framework_matrix.csv",
        QUALITATIVE / "coded_segments_master.csv",
        TABLES / "sample_characteristics.csv",
        TABLES / "survey_item_statistics.csv",
        TABLES / "support_gap_analysis.csv",
        TABLES / "platform_transition_analysis.csv",
        TABLES / "exploratory_associations.csv",
        TABLES / "joint_display.csv",
        REPORTS / "survey_findings.md",
        REPORTS / "cross_case_analysis.md",
        REPORTS / "integrated_findings.md",
        REPORTS / "literature_comparison.md",
        REPORTS / "draft_report.md",
        REPORTS / "final_report.md",
        REPORTS / "agent_run_manifest.md",
        REPORTS / "pipeline_summary.md",
        REPORTS / "reproducibility_results.csv",
        REPORTS / "review_resolution.md",
        ROOT / "outputs/agent_runs/20260723_full_pipeline/reviews/evidence_audit.md",
        ROOT / "outputs/agent_runs/20260723_full_pipeline/reviews/privacy_method_audit.md",
    ]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    require(not missing, "required_outputs", f"missing={missing or 'none'}")


def validate_raw() -> None:
    baseline = pd.read_csv(REPORTS / "raw_file_checksums.csv", dtype=str)
    mismatches = []
    for row in baseline.itertuples(index=False):
        path = resolve_checksum_path(row.relative_path)
        if not path.is_file() or sha256(path) != row.file_hash:
            mismatches.append(row.relative_path)
    require(len(baseline) == 4, "raw_baseline_count", f"baseline files={len(baseline)}")
    require(not mismatches, "raw_unchanged", f"mismatches={mismatches or 'none'}")


def validate_survey() -> None:
    codebook = pd.read_csv(PROCESSED / "survey_codebook.csv", dtype=str, keep_default_na=False)
    survey = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    require(len(codebook) == 160, "survey_codebook_rows", f"rows={len(codebook)}")
    require(
        codebook["variable_name"].nunique() == 160
        and codebook["source_column"].str.len().gt(0).all(),
        "survey_mapping_complete",
        "all 160 export positions have unique canonical variable names and nonblank source headers",
    )
    require(len(survey) == 35, "survey_total", f"rows={len(survey)}")
    eligible_n = int((survey["eligible"] == "TRUE").sum())
    require(eligible_n == 24, "survey_eligible", f"eligible={eligible_n}")
    require(int((survey["eligible"] == "FALSE").sum()) == 11, "survey_excluded", "excluded=11")
    require(
        not survey["duplicate_flag"].eq("EXACT_RESPONSE_DUPLICATE").any(),
        "survey_exact_duplicates",
        "no exact full-response duplicates",
    )
    prohibited_columns = {"admin_user_id", "admin_submit_time", "admin_source_detail", "admin_ip", "admin_remarks"}
    require(
        not prohibited_columns.intersection(survey.columns),
        "survey_privacy_columns",
        "direct/quasi-direct platform metadata excluded",
    )
    constructs = pd.read_csv(TABLES / "exploratory_constructs.csv")
    require(
        set(constructs["status"]) == {"RETAINED_DESCRIPTIVE"},
        "construct_status",
        "four exploratory descriptive indicators only",
    )
    associations = pd.read_csv(TABLES / "exploratory_associations.csv")
    require(len(associations) == 5, "association_count", f"analyses={len(associations)}")
    require(
        int((associations["bh_fdr_q"] < 0.05).sum()) == 0,
        "association_multiplicity",
        "no BH-FDR q<0.05; all treated as exploratory",
    )
    flow = pd.read_csv(TABLES / "sample_flow.csv", dtype=str, keep_default_na=False)
    flow_counts = {
        row.stage: int(row.n)
        for row in flow.itertuples(index=False)
        if row.stage in {"原始提交", "合资格样本", "排除"}
    }
    require(
        flow_counts == {"原始提交": 35, "合资格样本": 24, "排除": 11},
        "sample_flow_consistency",
        f"flow={flow_counts}",
    )
    exclusions = survey.loc[survey["eligible"] == "FALSE", "exclusion_reason"]
    require(
        len(exclusions) == 11 and exclusions.str.len().gt(0).all(),
        "exclusions_traceable",
        "all 11 excluded rows have explicit reasons",
    )
    stats = pd.read_csv(TABLES / "survey_item_statistics.csv", dtype=str, keep_default_na=False)
    support_stats = (
        stats.loc[stats["analysis_role"] == "support_gap"]
        .groupby("variable_name")["valid_n"]
        .first()
        .astype(int)
        .sort_index()
    )
    support = (
        pd.read_csv(TABLES / "support_gap_analysis.csv")
        .set_index("variable_name")["valid_n"]
        .astype(int)
        .sort_index()
    )
    require(
        support_stats.equals(support)
        and set(stats.loc[stats["analysis_role"] == "support_gap", "statistic_type"])
        == {"support_status_distribution"},
        "support_table_consistency",
        "generic item table agrees with dedicated support-gap valid n",
    )


def validate_linkage() -> None:
    survey = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    mapping = pd.read_csv(PROCESSED / "interview_survey_map.csv", dtype=str, keep_default_na=False)
    require(len(mapping) == 3, "linkage_files", f"interviews={len(mapping)}")
    require(mapping["participant_id"].is_unique, "linkage_participant_unique", "participant IDs unique")
    require(mapping["questionnaire_sequence"].is_unique, "linkage_sequence_unique", "restricted sequences unique")
    statuses = mapping["mapping_status"].value_counts().to_dict()
    require(statuses == {"MATCHED": 2, "INELIGIBLE": 1}, "linkage_statuses", f"statuses={statuses}")
    merged = mapping.merge(
        survey[["survey_row_id", "eligible"]], on="survey_row_id", how="left", validate="one_to_one"
    )
    correct = (
        merged.loc[merged["mapping_status"] == "MATCHED", "eligible"].eq("TRUE").all()
        and merged.loc[merged["mapping_status"] == "INELIGIBLE", "eligible"].eq("FALSE").all()
    )
    require(correct, "linkage_eligibility", "matched cases eligible; ineligible case excluded")
    matched_ids = set(mapping.loc[mapping["mapping_status"] == "MATCHED", "participant_id"])
    nonmatched_ids = set(mapping.loc[mapping["mapping_status"] != "MATCHED", "participant_id"])
    matched_profiles_exist = all(
        (PROCESSED / "linked_cases" / f"{participant}_profile.md").is_file()
        for participant in matched_ids
    )
    nonmatched_profiles_absent = all(
        not (PROCESSED / "linked_cases" / f"{participant}_profile.md").exists()
        for participant in nonmatched_ids
    )
    require(
        matched_profiles_exist and nonmatched_profiles_absent,
        "linked_profiles",
        "profiles exist only for the two eligible linked cases",
    )


def validate_transcripts_and_quotes() -> None:
    line_counts = {}
    sequential_ok = True
    mapping = pd.read_csv(PROCESSED / "interview_survey_map.csv", dtype=str, keep_default_na=False)
    participants = mapping["participant_id"].tolist()
    matched_ids = set(mapping.loc[mapping["mapping_status"] == "MATCHED", "participant_id"])
    for participant in participants:
        lines = numbered_lines(participant)
        line_counts[participant] = len(lines)
        expected = [f"L{number:04d}" for number in range(1, len(lines) + 1)]
        sequential_ok = sequential_ok and list(lines) == expected
    require(
        sequential_ok,
        "transcript_line_stability",
        "all three restricted transcript copies have stable sequential line labels",
    )
    master = pd.read_csv(QUALITATIVE / "coded_segments_master.csv", dtype=str, keep_default_na=False)
    quote_errors = []
    p01_role_errors = []
    for row in master.itertuples(index=False):
        lines = numbered_lines(row.participant_id)
        selected = [
            lines[f"L{number:04d}"]
            for number in range(int(row.line_start[1:]), int(row.line_end[1:]) + 1)
        ]
        combined = " ".join(text for _, text in selected)
        if row.exact_quote not in combined:
            quote_errors.append(f"{row.participant_id}:{row.line_start}-{row.line_end}")
        if row.participant_id == "P01" and any(role != "Participant" for role, _ in selected):
            p01_role_errors.append(f"{row.line_start}-{row.line_end}")
    require(not quote_errors, "qualitative_quotes_verbatim", f"errors={quote_errors or 'none'}")
    require(not p01_role_errors, "p01_quote_source", f"non-participant ranges={p01_role_errors or 'none'}")
    require(
        set(master["participant_id"]) == matched_ids,
        "qualitative_case_scope",
        "only the two eligible linked cases are coded",
    )
    require(
        set(master["confidence"]) <= {"HIGH", "MEDIUM", "LOW"},
        "qualitative_confidence_enum",
        "confidence enum valid",
    )


def validate_integration() -> None:
    joint = pd.read_csv(TABLES / "joint_display.csv", dtype=str, keep_default_na=False)
    require(
        set(joint["relationship_type"]) <= {"CONVERGENCE", "EXPANSION", "DIVERGENCE", "SILENCE"},
        "joint_relationship_enum",
        "relationship types valid",
    )
    require(len(joint) >= 4, "joint_topics", f"topics={len(joint)}")
    sources_present = joint["source_files"].str.len().gt(0).all()
    require(sources_present, "joint_traceability", "all topics list source files")


def validate_reproducibility() -> None:
    result = pd.read_csv(REPORTS / "reproducibility_results.csv", dtype=str, keep_default_na=False)
    require(len(result) >= 20, "reproducibility_scope", f"canonical targets={len(result)}")
    failures = result.loc[result["status"] != "PASS", "relative_path"].tolist()
    require(not failures, "canonical_reproducibility", f"non-reproducible={failures or 'none'}")


def validate_public_privacy() -> None:
    files = [
        path
        for path in (ROOT / "outputs").rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".csv"}
    ]
    patterns = {
        "questionnaire_sequence_value": re.compile(r"(?:访谈-序号|问卷序号[:：]\s*)\d+"),
        "survey_row_id": re.compile(r"\bS00\d+\b"),
        "raw_ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "email_address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "phone_number": re.compile(r"(?<!\d)1\d{10}(?!\d)"),
        "raw_survey_basename": re.compile(r"\d{6,}问卷[^/\\\n]*\.xlsx"),
    }
    findings = []
    for path in files:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        for label, pattern in patterns.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}:{label}")
    require(not findings, "public_privacy_scan", f"findings={findings or 'none'}")


def validate_git_privacy() -> None:
    allowed_outputs = {
        "outputs/reports/agent_run_manifest.md",
        "outputs/reports/final_report.md",
        "outputs/reports/pipeline_summary.md",
        "outputs/reports/review_resolution.md",
        "outputs/reports/validation_report.md",
    }
    allowed_processed = {
        "data/processed/qualitative_codebook.csv",
        "data/processed/survey_codebook.csv",
    }

    def prohibited(path: str) -> bool:
        if path.startswith(("data/raw/", "data/interview/")):
            return True
        if path.startswith("data/processed/") and path not in allowed_processed:
            return True
        if path.startswith("outputs/") and path not in allowed_outputs:
            return True
        return False

    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    tracked_findings = [path for path in tracked if prohibited(path)]
    require(
        not tracked_findings,
        "git_index_privacy",
        f"prohibited tracked paths={tracked_findings or 'none'}",
    )
    object_lines = subprocess.run(
        ["git", "rev-list", "--objects", "--all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    historical_paths = [line.split(" ", 1)[1] for line in object_lines if " " in line]
    history_findings = sorted({path for path in historical_paths if prohibited(path)})
    require(
        not history_findings,
        "git_history_privacy",
        f"prohibited paths reachable from refs={history_findings or 'none'}",
    )


def validate_final_claims() -> None:
    final = (REPORTS / "final_report.md").read_text(encoding="utf-8")
    require("完整问卷样本" in final, "report_distinguishes_survey", "full survey section present")
    require("链接个案" in final, "report_distinguishes_cases", "linked-case section present")
    require("文献" in final, "report_distinguishes_literature", "literature comparison present")
    require("24" in final and "35" in final and "11" in final, "report_sample_counts", "35/24/11 represented")
    source_refs = [
        "sample_flow.csv",
        "survey_item_statistics.csv",
        "support_gap_analysis.csv",
        "platform_transition_analysis.csv",
        "coded_segments_master.csv",
        "joint_display.csv",
    ]
    missing_refs = [source for source in source_refs if source not in final]
    require(not missing_refs, "report_source_traceability", f"missing source mentions={missing_refs or 'none'}")
    causal_lines = []
    for number, line in enumerate(final.splitlines(), start=1):
        if re.search(r"导致|造成|证明|产生了独立效果", line) and not re.search(
            r"不|不能|无法|未|可能|不足以|并非", line
        ):
            causal_lines.append(number)
    require(not causal_lines, "unsupported_causal_language", f"unqualified lines={causal_lines or 'none'}")


def write_report() -> int:
    result = pd.DataFrame(checks)
    result.to_csv(REPORTS / "validation_results.csv", index=False, encoding="utf-8-sig")
    failures = result[result["status"] == "FAIL"]
    warnings = [
        "一份访谈文件唯一映射至不合资格问卷记录，已按合同排除链接个案分析。",
        "合资格访谈包含一份整理式记录和一份未经录音核对、存在工具情境风险的机器转写。",
        "Q2.11 时点措辞冲突，Q3.1 第6项与 Q6.2 微博列缺失。",
        "五项探索性关联经 BH-FDR 校正后均无 q<0.05；未运行回归或因子分析。",
        "开放题为关键词辅助多标签扫描；未宣称质性饱和或总体流行程度。",
    ]
    status = "PASS" if failures.empty else "FAIL"
    table = "\n".join(
        f"| {row.check_id} | {row.status} | {row.detail} |"
        for row in result.itertuples(index=False)
    )
    report = f"""# 自动验证报告

总体结果：**{status}**

## 检查结果

| 检查 | 状态 | 说明 |
|---|---|---|
{table}

## 明确保留的警告与跳过分析

{chr(10).join(f'- {warning}' for warning in warnings)}

## 结论

{"所有核心检查通过；最终主张可回溯至生成表或带行号的访谈证据。" if failures.empty else "存在核心失败，不能创建完成标签；须修复后重跑验证。"}
"""
    (REPORTS / "validation_report.md").write_text(report, encoding="utf-8")
    return 0 if failures.empty else 1


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    validate_required_files()
    validate_raw()
    validate_survey()
    validate_linkage()
    validate_transcripts_and_quotes()
    validate_integration()
    validate_reproducibility()
    validate_public_privacy()
    validate_git_privacy()
    validate_final_claims()
    raise SystemExit(write_report())


if __name__ == "__main__":
    main()
