#!/usr/bin/env python3
"""Second-round automated and manual-audit closure validation."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pandas as pd

from pipeline_common import INTERVIEW_DIR, ROOT, SURVEY_PATH


REPORTS = ROOT / "outputs/reports"
REVIEWS = ROOT / "outputs/reviews"
TABLES = ROOT / "outputs/tables"
PROCESSED = ROOT / "data/processed"
QUALITATIVE = ROOT / "outputs/qualitative"
ROUND2_RUN = ROOT / "outputs/agent_runs/20260723_independent_review_extension_v2"
REVISED_QUAL = ROUND2_RUN / "revised_qualitative"

CHECKS: list[dict[str, str]] = []

CURRENT_PUBLIC = [
    REPORTS / "final_report.md",
    REPORTS / "final_report_v2.md",
    REPORTS / "exploratory_extension_v2.md",
    REPORTS / "revision_log_v2.md",
    REPORTS / "agent_run_manifest.md",
    REPORTS / "cross_case_analysis.md",
    REPORTS / "integrated_findings.md",
    REPORTS / "draft_report.md",
    TABLES / "exploratory_extension_v2.csv",
    TABLES / "joint_display.csv",
    REVIEWS / "quantitative_audit_v2.md",
    REVIEWS / "qualitative_audit_v2.md",
    REVIEWS / "integration_audit_v2.md",
    REVIEWS / "reproducibility_privacy_audit_v2.md",
    REPORTS / "validation_report_v2.md",
    REPORTS / "pipeline_summary_v2.md",
]

ALLOWED_TRACKED_OUTPUTS = {
    "outputs/reports/agent_run_manifest.md",
    "outputs/reports/final_report.md",
    "outputs/reports/final_report_v2.md",
    "outputs/reports/exploratory_extension_v2.md",
    "outputs/reports/revision_log_v2.md",
    "outputs/reports/validation_report.md",
    "outputs/reports/validation_report_v2.md",
    "outputs/reports/pipeline_summary.md",
    "outputs/reports/pipeline_summary_v2.md",
    "outputs/reports/review_resolution.md",
    "outputs/tables/exploratory_extension_v2.csv",
    "outputs/reviews/quantitative_audit_v2.md",
    "outputs/reviews/qualitative_audit_v2.md",
    "outputs/reviews/integration_audit_v2.md",
    "outputs/reviews/reproducibility_privacy_audit_v2.md",
}
ALLOWED_PROCESSED = {
    "data/processed/qualitative_codebook.csv",
    "data/processed/survey_codebook.csv",
}


def record(check_id: str, condition: bool, detail: str) -> None:
    CHECKS.append(
        {"check_id": check_id, "status": "PASS" if condition else "FAIL", "detail": detail}
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_checksum_path(alias: str) -> Path:
    if alias == "data/raw/SURVEY_SOURCE.xlsx":
        return SURVEY_PATH
    match = re.fullmatch(r"data/interview/INTERVIEW_SOURCE_(\d{2})\.docx", alias)
    if match:
        return sorted(INTERVIEW_DIR.glob("*.docx"))[int(match.group(1)) - 1]
    return ROOT / alias


def transcript_lines(participant: str) -> dict[str, tuple[str, str]]:
    path = PROCESSED / "interviews" / f"interview_{participant}_numbered.md"
    pattern = re.compile(r"^\[(L\d{4})\]\s+([^:]+):\s?(.*)$")
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            result[match.group(1)] = (match.group(2), match.group(3))
    return result


def validate_required() -> None:
    required = [
        PROCESSED / "survey_codebook.csv",
        PROCESSED / "survey_clean.csv",
        PROCESSED / "survey_construct_scores.csv",
        PROCESSED / "interview_survey_map.csv",
        PROCESSED / "qualitative_codebook.csv",
        QUALITATIVE / "coded_segments_master.csv",
        QUALITATIVE / "framework_matrix.csv",
        TABLES / "missingness_by_item.csv",
        TABLES / "sample_characteristics.csv",
        TABLES / "survey_item_statistics.csv",
        TABLES / "support_gap_analysis.csv",
        TABLES / "exploratory_associations.csv",
        TABLES / "exploratory_extension_v2.csv",
        TABLES / "joint_display.csv",
        REPORTS / "exploratory_extension_v2.md",
        REPORTS / "revision_log_v2.md",
        REPORTS / "final_report_v2.md",
        REPORTS / "final_report.md",
        REPORTS / "reproducibility_results_v2.csv",
        REVIEWS / "quantitative_audit_v2.md",
        REVIEWS / "qualitative_audit_v2.md",
        REVIEWS / "integration_audit_v2.md",
        REVIEWS / "reproducibility_privacy_audit_v2.md",
        REVISED_QUAL / "alignment_adjudication_v2.csv",
        ROUND2_RUN / "restricted_extension/linked_case_position_v2.csv",
        ROUND2_RUN / "restricted_extension/case_configuration_matrix_v2.csv",
        ROUND2_RUN / "restricted_extension/leave_one_case_out_themes_v2.csv",
    ]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    record("v2_required_outputs", not missing, f"missing={missing or 'none'}")


def validate_raw() -> None:
    baseline = pd.read_csv(REPORTS / "raw_file_checksums.csv", dtype=str)
    mismatches = []
    for row in baseline.itertuples(index=False):
        path = resolve_checksum_path(row.relative_path)
        if not path.is_file() or sha256(path) != row.file_hash:
            mismatches.append(row.relative_path)
    record("v2_raw_baseline_count", len(baseline) == 4, f"source hashes={len(baseline)}")
    record("v2_raw_unchanged", not mismatches, f"mismatches={mismatches or 'none'}")


def validate_survey() -> None:
    survey = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    codebook = pd.read_csv(
        PROCESSED / "survey_codebook.csv", dtype=str, keep_default_na=False
    )
    record(
        "v2_sample_flow",
        len(survey) == 35
        and survey["eligible"].eq("TRUE").sum() == 35
        and survey["eligible"].eq("FALSE").sum() == 0
        and survey["eligibility_reclassification"].eq("NEWLY_INCLUDED_V2").sum() == 11,
        "total=35; eligible=35; excluded=0; reclassified=11",
    )
    record(
        "v2_ethical_gates",
        survey["q0_1_consent"].eq("同意参加").all()
        and survey["q1_4_age18"].eq("是").all(),
        "all records pass consent and adult-status gates",
    )
    expected_flags = {
        "MULTISELECT_LIMIT_EXCEEDED_Q2_10": 8,
        "MULTISELECT_LIMIT_EXCEEDED_Q3_2": 14,
        "MULTISELECT_LIMIT_EXCEEDED_Q5_4": 9,
    }
    actual_flags = {
        flag: int(survey["data_quality_flag"].str.contains(flag).sum())
        for flag in expected_flags
    }
    record(
        "v2_multiselect_limits",
        actual_flags == expected_flags,
        f"over-limit counts={actual_flags}",
    )
    record(
        "v2_multiselect_exclusive_conflict",
        survey["data_quality_flag"]
        .str.contains("MULTISELECT_EXCLUSIVE_CONFLICT_Q5_3")
        .any(),
        "Q5.3 mutually exclusive combination is detected and retained as a flag",
    )
    parent_rows = codebook["response_type"].isin(["matrix", "multiple_choice"])
    record(
        "v2_codebook_parent_item_semantics",
        codebook.loc[parent_rows, "question_text"].str.len().gt(0).all()
        and codebook.loc[parent_rows, "item_text"].str.len().gt(0).all()
        and (
            codebook.loc[parent_rows, "question_text"]
            != codebook.loc[parent_rows, "item_text"]
        ).all(),
        "matrix/multiple-choice parent questions and item labels are distinct",
    )
    record(
        "v2_codebook_source_mapping",
        len(codebook) == 160
        and codebook["variable_name"].nunique() == 160
        and codebook["source_column"].str.len().gt(0).all(),
        "160 unique export positions retain nonblank source headers",
    )
    missingness = pd.read_csv(
        TABLES / "missingness_by_item.csv", dtype=str, keep_default_na=False
    ).set_index("variable_name")
    q54_missing = missingness.loc["q5_4_help_hk_peer"]
    record(
        "v2_group_missingness_propagation",
        q54_missing["valid_n"] == "34"
        and int(q54_missing["cannot_remember_n"]) > 0,
        "Q5.4 group-level special response is excluded from ordinary-option denominator",
    )
    stats = pd.read_csv(
        TABLES / "survey_item_statistics.csv", dtype=str, keep_default_na=False
    )
    q54 = stats[
        stats["variable_name"].isin(
            ["q5_4_help_hk_peer", "q5_4_help_mainland_peer"]
        )
        & stats["response_or_statistic"].eq("选择")
    ]
    pairs = {
        row.variable_name: (int(row.n), int(row.valid_n))
        for row in q54.itertuples(index=False)
    }
    record(
        "v2_q54_denominators",
        pairs
        == {
            "q5_4_help_hk_peer": (23, 34),
            "q5_4_help_mainland_peer": (19, 34),
        },
        f"Q5.4 selected counts/valid n={pairs}",
    )
    matrix = stats[stats["statistic_type"].eq("ordinal_distribution")]
    distribution_ok = True
    for _, group in matrix.groupby("variable_name"):
        distribution_ok &= int(group["n"].astype(int).sum()) == int(
            group["valid_n"].astype(int).iloc[0]
        )
    record(
        "v2_matrix_distribution_sums",
        distribution_ok and matrix["variable_name"].nunique() == 42,
        f"ordinal variables checked={matrix['variable_name'].nunique()}",
    )
    sample = pd.read_csv(
        TABLES / "sample_characteristics.csv", dtype=str, keep_default_na=False
    )
    record(
        "v2_multiselect_background_coverage",
        sample["variable_name"].str.startswith("q2_8_").any()
        and sample["variable_name"].str.startswith("q2_10_").any(),
        "teaching-language and migration-reason multiple choices are included",
    )
    open_text = pd.read_csv(
        TABLES / "survey_open_text_summary.csv", dtype=str, keep_default_na=False
    )
    record(
        "v2_open_text_guardrail",
        open_text["interpretation_limit"]
        .str.contains("Keyword index only", regex=False)
        .all(),
        "open-text output is labelled as an index rather than semantic prevalence",
    )


def validate_linkage() -> None:
    mapping = pd.read_csv(
        PROCESSED / "interview_survey_map.csv", dtype=str, keep_default_na=False
    )
    record(
        "v2_linkage_unique",
        len(mapping) == 3
        and mapping["mapping_status"].eq("MATCHED").all()
        and mapping["participant_id"].is_unique
        and mapping["questionnaire_sequence"].is_unique
        and mapping["survey_row_id"].is_unique,
        "three mappings are MATCHED and one-to-one",
    )
    profiles = [
        PROCESSED / "linked_cases" / f"{participant}_profile.md"
        for participant in mapping["participant_id"]
    ]
    record(
        "v2_linked_profiles",
        all(path.is_file() for path in profiles),
        "all matched cases have regenerated restricted profiles",
    )


def validate_qualitative() -> None:
    master = pd.read_csv(
        QUALITATIVE / "coded_segments_master.csv", dtype=str, keep_default_na=False
    )
    quote_errors = []
    speaker_errors = []
    for row in master.itertuples(index=False):
        lines = transcript_lines(row.participant_id)
        selected = [
            lines[f"L{number:04d}"]
            for number in range(int(row.line_start[1:]), int(row.line_end[1:]) + 1)
        ]
        combined = " ".join(text for _, text in selected)
        if row.exact_quote not in combined:
            quote_errors.append(f"{row.participant_id}:{row.line_start}-{row.line_end}")
        if any(speaker != "Participant" for speaker, _ in selected):
            speaker_errors.append(f"{row.participant_id}:{row.line_start}-{row.line_end}")
    record(
        "v2_quotes_verbatim",
        len(master) == 84 and not quote_errors,
        f"segments={len(master)}; quote_errors={quote_errors or 'none'}",
    )
    record(
        "v2_quote_speakers",
        not speaker_errors,
        f"non-participant ranges={speaker_errors or 'none'}",
    )
    corrected_context = master[
        master["participant_id"].eq("P03")
        & master["line_start"].isin(["L0011", "L0014"])
    ]
    record(
        "v2_context_ranges_corrected",
        set(corrected_context["line_end"]) == {"L0012", "L0015"},
        "review-identified machine-sentence continuations are included",
    )
    recodes = {
        ("P01", "L0023"): "GRADUAL_ADAPTATION_PATH",
        ("P02", "L0148"): "LEARNER_IDENTITY_RENEGOTIATION",
        ("P02", "L0231"): "SYSTEM_ASSESSMENT_RULES",
        ("P02", "L0248"): "PEER_INVITATION",
        ("P03", "L0014"): "SYSTEM_ASSESSMENT_RULES",
    }
    actual = {
        (row.participant_id, row.line_start): row.primary_code
        for row in master.itertuples(index=False)
        if (row.participant_id, row.line_start) in recodes
    }
    record(
        "v2_semantic_recodes",
        actual == recodes,
        "all reviewer-identified primary-code corrections are applied",
    )
    codebook = pd.read_csv(
        PROCESSED / "qualitative_codebook.csv", dtype=str, keep_default_na=False
    )
    proposed = codebook["status"].eq("PROPOSED")
    record(
        "v2_proposed_code_boundary",
        codebook.loc[proposed, "notes"]
        .str.contains("尚未系统回填", regex=False)
        .all()
        and codebook.loc[
            codebook["code_id"].eq("GRADUAL_ADAPTATION_PATH"), "status"
        ].eq("ACTIVE").all(),
        "applied inductive code is ACTIVE; unused candidates remain explicit PROPOSED",
    )
    alignment = pd.read_csv(
        REVISED_QUAL / "alignment_adjudication_v2.csv",
        dtype=str,
        keep_default_na=False,
    )
    relation_counts = alignment["relationship_type"].value_counts().to_dict()
    record(
        "v2_alignment_full_adjudication",
        len(alignment) == 75
        and relation_counts
        == {"EXPANSION": 34, "CONVERGENCE": 21, "SILENCE": 11, "DIVERGENCE": 9},
        f"rows={len(alignment)}; relationship counts={relation_counts}",
    )
    divergence = alignment["relationship_type"].eq("DIVERGENCE")
    record(
        "v2_divergence_three_part_rule",
        alignment.loc[divergence, "same_construct"].eq("TRUE").all()
        and alignment.loc[divergence, "overlapping_timeframe"].eq("TRUE").all()
        and alignment.loc[divergence, "opposite_direction"].eq("TRUE").all(),
        "all retained divergences pass construct/time/direction criteria",
    )


def validate_extension_and_integration() -> None:
    extension = pd.read_csv(
        TABLES / "exploratory_extension_v2.csv", dtype=str, keep_default_na=False
    )
    allowed = {
        "robust finding",
        "plausible exploratory finding",
        "weak signal",
        "unsupported",
    }
    record(
        "v2_finding_class_enum",
        set(extension["finding_class"]) <= allowed,
        f"classes={sorted(set(extension['finding_class']))}",
    )
    record(
        "v2_unsupported_removed",
        not extension["finding_class"].eq("unsupported").any(),
        "no unsupported interpretation remains in the finding table",
    )
    numeric_small = pd.to_numeric(extension["numerator"], errors="coerce").isin([1, 2])
    record(
        "v2_extension_small_cell_suppression",
        not numeric_small.any()
        and extension.loc[extension["numerator"].eq("<3"), "estimate"]
        .eq("SUPPRESSED")
        .all(),
        "public extension table suppresses n<3",
    )
    platform = pd.read_csv(
        ROUND2_RUN / "restricted_extension/platform_paired_transition_v2.csv"
    )
    platform_sums = platform.groupby("platform")["n"].sum()
    record(
        "v2_paired_platform_states",
        platform_sums.eq(35).all() and len(platform_sums) == 11,
        "retained/adopted/stopped/neither sum to paired n for 11 platforms",
    )
    robustness = pd.read_csv(
        ROUND2_RUN / "restricted_extension/association_robustness_v2.csv"
    )
    a1 = robustness[robustness["analysis_id"].str.startswith("A1_")]
    a4 = robustness[robustness["analysis_id"].str.startswith("A4_")]
    record(
        "v2_a1_robustness",
        len(a1) == 4
        and a1["rho"].lt(0).all()
        and a1["loo_rho_max"].lt(0).all()
        and a1["finding_class"].eq("plausible exploratory finding").all(),
        "four A1 variants and leave-one-out ranges remain negative",
    )
    record(
        "v2_a4_downgrade",
        len(a4) == 3
        and a4["finding_class"].eq("weak signal").all()
        and abs(a4["rho"].max() - a4["rho"].min()) > 0.15,
        "A4 alternative encodings vary materially and are all weak signal",
    )
    themes = pd.read_csv(
        ROUND2_RUN / "restricted_extension/leave_one_case_out_themes_v2.csv",
        dtype=str,
        keep_default_na=False,
    )
    record(
        "v2_leave_one_case_out",
        len(themes) >= 5
        and themes["survives_removing_any_one_case"].isin(["YES", "NO"]).all(),
        "configuration themes record single-case dependency",
    )
    joint = pd.read_csv(TABLES / "joint_display.csv", dtype=str, keep_default_na=False)
    record(
        "v2_joint_relationship_coverage",
        set(joint["relationship_type"])
        == {"CONVERGENCE", "EXPANSION", "DIVERGENCE", "SILENCE"},
        f"joint types={sorted(set(joint['relationship_type']))}",
    )
    record(
        "v2_joint_topic_type_granularity",
        not (
            joint["relationship_type"].eq("DIVERGENCE")
            & joint["analytic_topic"].str.contains("资格|V1|V2", regex=True)
        ).any(),
        "analysis-specification sensitivity is not mislabelled as source divergence",
    )


def validate_reproducibility() -> None:
    result = pd.read_csv(
        REPORTS / "reproducibility_results_v2.csv",
        dtype=str,
        keep_default_na=False,
    )
    failures = result.loc[result["status"].ne("PASS"), "relative_path"].tolist()
    record(
        "v2_reproducibility_scope",
        len(result) >= 45,
        f"versioned targets={len(result)}",
    )
    record(
        "v2_reproducibility_modes",
        set(result["target_mode"])
        == {"REGENERATED", "FROZEN_ANALYTIC_INPUT_PROMOTED"},
        f"target modes={sorted(set(result['target_mode']))}",
    )
    record(
        "v2_reproducibility_pass",
        not failures,
        f"non-reproducible targets={failures or 'none'}",
    )


def validate_review_closure() -> None:
    log = (REPORTS / "revision_log_v2.md").read_text(encoding="utf-8")
    required_ids = [
        *(f"QA-{number:03d}" for number in range(1, 9)),
        *(f"QL-{number:03d}" for number in range(1, 8)),
        *(f"MM-{number:03d}" for number in range(1, 6)),
        *(f"RP-{number:03d}" for number in range(1, 7)),
    ]
    missing = [issue_id for issue_id in required_ids if issue_id not in log]
    record(
        "v2_review_issue_closure",
        not missing,
        f"missing issue dispositions={missing or 'none'}",
    )
    record(
        "v2_revision_status_enum",
        not re.search(r"\|\s*(?:pending|open|unresolved)\s*\|", log, re.I),
        "all revision-log rows have final retained/revised/removed/added status",
    )


def validate_public_privacy() -> None:
    files = [path for path in CURRENT_PUBLIC if path.is_file()]
    patterns = {
        "restricted_third_case_id": re.compile(r"\bP03\b"),
        "questionnaire_sequence_value": re.compile(r"(?:访谈-序号|问卷序号[:：]\s*)\d+"),
        "survey_row_id": re.compile(r"\bS00\d+\b"),
        "transcript_line_id": re.compile(r"\bL\d{4}\b"),
        "raw_ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "phone": re.compile(r"(?<!\d)1\d{10}(?!\d)"),
        "raw_survey_basename": re.compile(r"\d{6,}问卷[^/\\\n]*\.xlsx"),
        "numeric_small_fraction": re.compile(r"\b[12]/(?:29|30|31|32|33|34|35)\b"),
        "sensitive_one_two_records": re.compile(
            r"(?:一|二|两|1|2)\s*份(?:整理|机器转写|短时|共享网络|旧口径原因|实际迁居)"
        ),
    }
    findings = []
    for path in files:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        for label, pattern in patterns.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}:{label}")
    record(
        "v2_current_public_privacy",
        not findings,
        f"files scanned={len(files)}; findings={findings or 'none'}",
    )


def validate_git_privacy() -> None:
    def prohibited(path: str) -> bool:
        if path.startswith(("data/raw/", "data/interview/")):
            return True
        if path.startswith("data/processed/") and path not in ALLOWED_PROCESSED:
            return True
        if path.startswith("outputs/") and path not in ALLOWED_TRACKED_OUTPUTS:
            return True
        return False

    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    findings = [path for path in tracked if prohibited(path)]
    record(
        "v2_git_index_privacy",
        not findings,
        f"prohibited tracked paths={findings or 'none'}",
    )
    raw_diff = subprocess.run(
        ["git", "diff", "--", "data/raw"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    record(
        "v2_git_raw_diff",
        not raw_diff,
        "no tracked raw-data diff",
    )


def validate_final_claims() -> None:
    final = (REPORTS / "final_report_v2.md").read_text(encoding="utf-8")
    canonical = (REPORTS / "final_report.md").read_bytes()
    record(
        "v2_final_alias",
        canonical == (REPORTS / "final_report_v2.md").read_bytes(),
        "final_report.md and final_report_v2.md are byte-identical",
    )
    required_phrases = [
        "35 份全部合资格、排除 0",
        "旧口径排除的 11 份",
        "可以信任并谈心",
        "23/34",
        "19/34",
        "plausible exploratory finding",
        "weak signal",
        "三份访谈",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in final]
    record(
        "v2_final_required_claims",
        not missing,
        f"missing required phrases={missing or 'none'}",
    )
    record(
        "v2_composite_item_preserved",
        "可信任同学为 35/35" not in final
        and "至少有一位可以信任并谈心的同学" in final
        and "不能拆成“信任”和“谈心”" in final,
        "Q3.3 composite meaning is preserved",
    )
    record(
        "v2_a4_not_main_finding",
        "A4" in final and "降为 `weak signal`" in final,
        "A4 is explicitly downgraded",
    )
    causal_lines = []
    for number, line in enumerate(final.splitlines(), start=1):
        if re.search(r"导致|造成|证明|形成了|支撑正向归属|解释如何发生", line) and not re.search(
            r"不|不能|无法|未|可能|不足以|并非|删除", line
        ):
            causal_lines.append(number)
    record(
        "v2_no_unsupported_causal_language",
        not causal_lines,
        f"unqualified lines={causal_lines or 'none'}",
    )
    record(
        "v2_no_generalisation_from_three",
        "不能代表完整样本" in final and "不能代表完整样本或支持饱和" in final,
        "linked cases are explicitly non-representative",
    )


def write_report() -> int:
    result = pd.DataFrame(CHECKS)
    result.to_csv(
        REPORTS / "validation_results_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    failures = result[result["status"].eq("FAIL")]
    status = "PASS" if failures.empty else "FAIL"
    table = "\n".join(
        f"| {row.check_id} | {row.status} | {row.detail} |"
        for row in result.itertuples(index=False)
    )
    report = f"""# 第二轮自动验证报告

总体结果：**{status}**

## 检查结果

| 检查 | 状态 | 说明 |
|---|---|---|
{table}

## 验证边界

- 数值与文件再生和冻结解释性判断提升已分开标记；后者不等于算法重新发现主题。
- 84 条引语的逐字与说话人检查为机械验证；代码语义、关系类型和跨案覆盖由四份独立审查及 revision log 闭环。
- 当前公开 allowlist 不包括 `analysis-v2` tag 中的历史报告；第一轮原件保持可追溯，第二轮当前交付执行更严格的小格和跨版本最小化。
- A1 仍是事后资格口径下的探索性结果；A4 仅为 weak signal。

## 结论

{"第二轮核心检查全部通过；原始资料未变，映射唯一，数字、引语、探索分级、隐私和复现边界一致。" if failures.empty else "存在失败，不能封版或创建完成标签。"}
"""
    (REPORTS / "validation_report_v2.md").write_text(report, encoding="utf-8")
    return 0 if failures.empty else 1


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    validate_required()
    validate_raw()
    validate_survey()
    validate_linkage()
    validate_qualitative()
    validate_extension_and_integration()
    validate_reproducibility()
    validate_review_closure()
    validate_public_privacy()
    validate_git_privacy()
    validate_final_claims()
    raise SystemExit(write_report())


if __name__ == "__main__":
    main()
