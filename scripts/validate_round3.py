#!/usr/bin/env python3
"""Validate the round-three theory extension and write its public report."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "outputs/agent_runs/20260723_multi_theory_abductive_v3"
REPORT = ROOT / "outputs/reports/validation_report_v3.md"

REQUIRED = [
    "outputs/reports/theoretical_exploration_plan_v3.md",
    "outputs/theory/framework_inventory_v3.csv",
    "outputs/reports/framework_notes_v3.md",
    "outputs/theory/cross_framework_matrix_v3.csv",
    "outputs/reports/cross_framework_synthesis_v3.md",
    "outputs/reports/abductive_exploration_v3.md",
    "outputs/tables/mechanism_propositions_v3.csv",
    "outputs/reports/proposed_analytical_framework_v3.md",
    "outputs/reviews/theoretical_fit_audit_v3.md",
    "outputs/reviews/multi_perspective_evidence_audit_v3.md",
    "outputs/reports/theoretical_revision_log_v3.md",
    "outputs/reports/theoretical_extension_report_v3.md",
    "outputs/reports/final_report_v3.md",
]
ROLES = [
    "theory_boundary_belonging",
    "theory_institution_identity",
    "theory_brokerage_agency",
    "theory_digital_relations",
    "theory_process_rivals",
]
ROLE_FILES = [
    "analysis_memo.md",
    "framework_coded_evidence.csv",
    "rival_explanations.csv",
    "framework_limits.md",
]
FIT = {"strong fit", "moderate fit", "weak fit", "not supported"}
CLASSES = {
    "cross-framework robust",
    "framework-dependent",
    "plausible but under-evidenced",
    "contradicted",
    "unsupported",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, status: bool, detail: str) -> None:
        checks.append((name, bool(status), detail))

    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    check("v3_required_outputs", not missing, f"missing={missing or 'none'}")

    inventory = pd.read_csv(ROOT / "outputs/theory/framework_inventory_v3.csv")
    check(
        "v3_framework_inventory",
        len(inventory) >= 6 and inventory["fit_preassessment"].isin(FIT).all(),
        f"cards={len(inventory)}; invalid_fit={int((~inventory['fit_preassessment'].isin(FIT)).sum())}",
    )
    missing_role_files = [
        f"{role}/{name}"
        for role in ROLES
        for name in ROLE_FILES
        if not (RUN / role / name).is_file()
    ]
    check(
        "v3_five_role_outputs",
        not missing_role_files,
        f"missing={missing_role_files or 'none'}",
    )

    evidence_rows = 0
    invalid_fit = 0
    missing_dual = []
    invalid_lines = []
    for role in ROLES:
        path = RUN / role / "framework_coded_evidence.csv"
        if not path.exists():
            continue
        data = pd.read_csv(path, keep_default_na=False)
        evidence_rows += len(data)
        invalid_fit += int((~data["fit_assessment"].isin(FIT)).sum())
        if not data["survey_variables"].astype(str).str.strip().any() or not data[
            "transcript_file"
        ].astype(str).str.strip().any():
            missing_dual.append(role)
        for _, row in data.iterrows():
            transcript = str(row["transcript_file"]).strip()
            start, end = str(row["line_start"]).strip(), str(row["line_end"]).strip()
            if not transcript:
                continue
            source = ROOT / transcript
            if not source.is_file():
                invalid_lines.append(f"{row['evidence_id']}:missing transcript")
                continue
            text = source.read_text(encoding="utf-8")
            labels = {
                m.group(1)
                for m in re.finditer(r"(?m)^\[(L\d{4})\]", text)
            }
            if start not in labels or end not in labels or start > end:
                invalid_lines.append(str(row["evidence_id"]))
    check(
        "v3_agent_evidence_schema",
        evidence_rows > 0 and invalid_fit == 0,
        f"rows={evidence_rows}; invalid_fit={invalid_fit}",
    )
    check(
        "v3_each_role_mixed_evidence",
        not missing_dual,
        f"roles_without_both={missing_dual or 'none'}",
    )
    check(
        "v3_transcript_line_anchors",
        not invalid_lines,
        f"invalid={invalid_lines or 'none'}",
    )

    matrix = pd.read_csv(ROOT / "outputs/theory/cross_framework_matrix_v3.csv")
    check(
        "v3_cross_framework_matrix",
        len(matrix) >= 6
        and matrix["fit_assessment"].isin(FIT).all()
        and matrix["rival_explanations"].astype(str).str.strip().all(),
        f"phenomena={len(matrix)}",
    )
    known_ids = set()
    for role in ROLES:
        path = RUN / role / "framework_coded_evidence.csv"
        if path.exists():
            known_ids.update(
                pd.read_csv(path, keep_default_na=False)["evidence_id"].astype(str)
            )
    bad_matrix_paths, bad_matrix_ids = [], []
    for _, row in matrix.iterrows():
        evidence = str(row["evidence"])
        for token in re.findall(r"(?:outputs|data)/[^;:]+", evidence):
            token = token.strip()
            if "*" in token:
                if not list(ROOT.glob(token)):
                    bad_matrix_paths.append(token)
            elif not (ROOT / token).exists():
                bad_matrix_paths.append(token)
        if "restricted " in evidence:
            tail = evidence.split("restricted ", 1)[1]
            for token in re.split(r"[,;]", tail):
                item = token.strip()
                if item and item not in known_ids and not item.startswith("AC"):
                    bad_matrix_ids.append(item)
    check(
        "v3_matrix_evidence_resolves",
        not bad_matrix_paths and not bad_matrix_ids,
        f"bad_paths={bad_matrix_paths or 'none'}; bad_ids={bad_matrix_ids or 'none'}",
    )
    propositions = pd.read_csv(
        ROOT / "outputs/tables/mechanism_propositions_v3.csv"
    )
    check(
        "v3_mechanism_classification",
        propositions["classification"].isin(CLASSES).all(),
        f"rows={len(propositions)}; classes={sorted(propositions['classification'].unique())}",
    )
    required_prop = [
        "supporting_evidence",
        "counterevidence_or_limit",
        "rival_explanation",
        "evidence_scope",
        "current_study_support",
        "future_test",
    ]
    check(
        "v3_mechanism_limits_complete",
        all(propositions[c].astype(str).str.strip().all() for c in required_prop),
        "all required limitation and testing fields populated",
    )
    revision = (
        ROOT / "outputs/reports/theoretical_revision_log_v3.md"
    ).read_text(encoding="utf-8")
    issue_ids = [f"TF-{i:02d}" for i in range(1, 13)] + [
        f"MPE-{i:03d}" for i in range(1, 11)
    ]
    missing_issues = [issue for issue in issue_ids if issue not in revision]
    check(
        "v3_review_issue_closure",
        not missing_issues,
        f"missing={missing_issues or 'none'}",
    )

    baseline = pd.read_csv(
        ROOT / "outputs/reports/raw_file_checksums.csv", encoding="utf-8-sig"
    )
    mismatches = []
    actual_sources = list((ROOT / "data/raw").glob("*")) + list(
        (ROOT / "data/interview").glob("*")
    )
    actual_hashes = {sha(path) for path in actual_sources if path.is_file()}
    for _, row in baseline.iterrows():
        if row["file_hash"] not in actual_hashes:
            mismatches.append(str(row["relative_path"]))
    check(
        "v3_source_files_unchanged",
        not mismatches and len(baseline) == 4,
        f"sources={len(baseline)}; mismatches={mismatches or 'none'}",
    )
    raw_diff = subprocess.run(
        ["git", "diff", "--", "data/raw", "data/interview"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    check("v3_git_source_diff", not raw_diff.strip(), "no tracked source diff")

    clean = pd.read_csv(ROOT / "data/processed/survey_clean.csv")
    mapping = pd.read_csv(ROOT / "data/processed/interview_survey_map.csv")
    check(
        "v3_sample_and_linkage",
        len(clean) == 35
        and int(clean["eligible"].eq(True).sum()) == 35
        and len(mapping) == 3
        and mapping["survey_row_id"].nunique() == 3,
        "survey=35/35 eligible; links=3 unique",
    )
    coded = pd.read_csv(
        ROOT / "outputs/qualitative/coded_segments_master.csv"
    )
    check("v3_coded_evidence_baseline", len(coded) == 84, f"segments={len(coded)}")

    public_files = [ROOT / p for p in REQUIRED if (ROOT / p).suffix == ".md"]
    public_files += [
        ROOT / "outputs/theory/cross_framework_matrix_v3.csv",
        ROOT / "outputs/tables/mechanism_propositions_v3.csv",
    ]
    privacy_patterns = [
        re.compile(r"\bS\d{4}\b"),
        re.compile(r"questionnaire_sequence"),
        re.compile(r"\bP\d{2}\b"),
        re.compile(r"\bL\d{4}\b"),
    ]
    privacy_hits = []
    for path in public_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if any(p.search(text) for p in privacy_patterns):
            privacy_hits.append(path.relative_to(ROOT).as_posix())
    check(
        "v3_public_privacy",
        not privacy_hits,
        f"files={len(public_files)}; hits={privacy_hits or 'none'}",
    )

    final = (ROOT / "outputs/reports/final_report_v3.md").read_text(
        encoding="utf-8"
    )
    required_phrases = [
        "不是已验证模型",
        "三份访谈",
        "竞争解释",
        "不代表完整样本",
        "不受当前资料支持",
    ]
    check(
        "v3_final_scope_guardrails",
        all(x in final for x in required_phrases),
        f"missing={[x for x in required_phrases if x not in final] or 'none'}",
    )
    risky = [
        line
        for line in final.splitlines()
        if re.search(r"(导致|造成|决定了|证明了)", line)
        and not re.search(r"(不能|不|未|并非|无法|不等于)", line)
    ]
    check(
        "v3_no_unqualified_causal_language",
        not risky,
        f"unqualified_lines={len(risky)}",
    )
    v2 = ROOT / "outputs/reports/final_report_v2.md"
    preserved = subprocess.run(
        ["git", "show", "analysis-v3:outputs/reports/final_report_v2.md"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    check(
        "v3_v2_preserved",
        hashlib.sha256(preserved).hexdigest() == sha(v2),
        "final_report_v2 matches analysis-v3",
    )

    passed = all(status for _, status, _ in checks)
    lines = [
        "# 第三轮自动验证报告",
        "",
        f"总体结果：**{'PASS' if passed else 'FAIL'}**",
        "",
        "## 检查结果",
        "",
        "| 检查 | 状态 | 说明 |",
        "|---|---|---|",
    ]
    lines += [
        f"| {name} | {'PASS' if status else 'FAIL'} | {detail} |"
        for name, status, detail in checks
    ]
    lines += [
        "",
        "## 验证边界",
        "",
        "- 第二版数值、唯一链接和84条编码证据链作为已验证基线，并在本轮再次核对关键计数。",
        "- 理论代理的访谈行号由脚本检查存在性；逐字引语的84条机械验证沿用第二轮完整验证。理论贴合仍需独立审查和 revision log 闭环。",
        "- 解释性综合属于版本控制的冻结分析判断；异常组合和开放题相似度由脚本再生。",
        "- 公开文件不含问卷序号、受限个案ID或访谈行号；完整证据仅保存在被 Git 忽略的受限 agent 目录。",
        "",
        "## 结论",
        "",
        (
            "第三轮关键数字、映射、证据锚点、框架分级、机制限制、隐私、"
            f"源文件完整性和非因果边界{'全部通过' if passed else '存在未通过项'}。"
        ),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"round3 validation checks={len(checks)} result={'PASS' if passed else 'FAIL'}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
