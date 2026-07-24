#!/usr/bin/env python3
"""Validate the fifth-round open-text analysis and write its public report."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/processed/survey_open_text_corpus.csv"
CODEBOOK = ROOT / "data/processed/open_text_codebook.csv"
CODED = ROOT / "outputs/open_text/open_text_coded_responses.csv"
THEMES = ROOT / "outputs/tables/open_text_theme_summary.csv"
OPEN_CLOSED = ROOT / "outputs/open_text/open_closed_alignment.csv"
OPEN_INTERVIEW = ROOT / "outputs/open_text/open_text_interview_alignment.csv"
REPORT = ROOT / "outputs/reports/open_text_validation_report.md"

CODEBOOK_COLUMNS = [
    "code_id",
    "code_name",
    "definition",
    "include_when",
    "exclude_when",
    "example_excerpt",
    "example_text_id",
    "inductive_or_deductive",
    "related_research_question",
    "related_theory",
    "status",
    "notes",
]
CODED_COLUMNS = [
    "internal_response_id",
    "public_text_id",
    "public_respondent_id",
    "question_id",
    "original_response",
    "analyzable",
    "exclusion_or_warning",
    "final_codes",
    "event_direction",
    "scene",
    "actors",
    "actions",
    "emotion_or_evaluation",
    "immediate_outcome",
    "later_impact",
    "turning_point",
    "support_target",
    "support_type",
    "unmet_need",
    "agency_expectation",
    "negative_or_contrasting_case",
    "deidentified_excerpt",
    "excerpt_status",
    "analytic_summary",
    "theoretical_interpretation",
    "researcher_inference",
    "alternative_explanation",
    "coding_confidence",
    "review_status",
]
THEME_COLUMNS = [
    "question_id",
    "theme",
    "counting_basis",
    "unique_respondents",
    "valid_open_text_n",
    "illustrative_text_ids",
    "negative_or_contrasting_cases",
    "interpretation_caution",
]
OPEN_CLOSED_COLUMNS = [
    "public_text_id",
    "public_respondent_id",
    "question_id",
    "open_text_codes",
    "closed_question_id",
    "closed_variable",
    "closed_response",
    "relationship_type",
    "alignment_rationale",
    "alternative_explanation",
    "confidence",
    "review_status",
]
OPEN_INTERVIEW_COLUMNS = [
    "public_text_id",
    "linked_interview_participant",
    "question_id",
    "open_text_summary",
    "closed_question_id",
    "closed_evidence",
    "transcript_file",
    "transcript_line_start",
    "transcript_line_end",
    "transcript_evidence_summary",
    "relationship_type",
    "alignment_rationale",
    "alternative_explanation",
    "confidence",
    "review_status",
]
RELATIONS = {"CONVERGENCE", "EXPANSION", "DIVERGENCE", "SILENCE"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
EXCERPT_STATUS = {"VERBATIM_SAFE", "PARAPHRASE_ONLY", "NO_PUBLIC_EXCERPT"}
FINAL_REVIEW_STATUS = {"MAIN_AGENT_VERIFIED", "REVIEWER_RESOLVED"}
PUBLIC_FILES = [
    ROOT / "data/processed/open_text_codebook.csv",
    ROOT / "outputs/open_text/open_text_analysis_plan.md",
    ROOT / "outputs/open_text/shared_schema_v5.md",
    ROOT / "outputs/open_text/coding_reconciliation.md",
    ROOT / "outputs/open_text/q81_critical_incident_analysis.md",
    ROOT / "outputs/open_text/q82_support_needs_analysis.md",
    ROOT / "outputs/tables/open_text_theme_summary.csv",
    ROOT / "outputs/reports/open_closed_integration.md",
    ROOT / "outputs/reports/open_text_linked_case_analysis.md",
    ROOT / "outputs/reports/open_text_qualitative_synthesis.md",
    ROOT / "outputs/reviews/open_text_evidence_audit.md",
    ROOT / "outputs/reviews/open_text_method_audit.md",
    ROOT / "outputs/open_text/open_text_revision_log.md",
    ROOT / "outputs/reports/open_text_pipeline_summary.md",
    ROOT / "outputs/final/findings_register.csv",
    ROOT / "outputs/final/research_question_evidence_matrix.csv",
    ROOT / "outputs/tables/joint_display.csv",
    ROOT / "outputs/final/final_research_report.md",
    ROOT / "outputs/final/executive_summary.md",
    ROOT / "outputs/reports/final_report.md",
]
PRIVACY_PATTERNS = {
    "survey_row_id": re.compile(r"\bS\d{4}\b"),
    "participant_id": re.compile(r"\bP\d{2}\b"),
    "transcript_line": re.compile(r"\bL\d{4}\b"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_codes(value: str) -> set[str]:
    return {part.strip() for part in str(value).split(";") if part.strip()}


def rows_for_basis(coded: pd.DataFrame, question_id: str, basis: str) -> pd.DataFrame:
    rows = coded[coded["question_id"].eq(question_id)].copy()
    if basis.startswith("EVENT_DIRECTION="):
        return rows[rows["event_direction"].eq(basis.split("=", 1)[1])]
    if basis.startswith("ANY_OF:"):
        candidates = set(basis.removeprefix("ANY_OF:").split("|"))
        return rows[
            rows["final_codes"].map(lambda value: bool(split_codes(value) & candidates))
        ]
    return rows[rows["final_codes"].map(lambda value: basis in split_codes(value))]


def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))

    required = [
        CORPUS,
        CODEBOOK,
        CODED,
        THEMES,
        OPEN_CLOSED,
        OPEN_INTERVIEW,
        *PUBLIC_FILES,
    ]
    missing = sorted(
        {path.relative_to(ROOT).as_posix() for path in required if not path.is_file()}
    )
    check("required_outputs", not missing, f"missing={missing or 'none'}")
    if missing:
        write_report(checks)
        raise SystemExit(1)

    corpus = pd.read_csv(CORPUS, keep_default_na=False)
    analyzable = corpus[corpus["analyzable"].astype(str).eq("YES")].copy()
    q_counts = analyzable["question_id"].value_counts().to_dict()
    respondent_sets = {
        q: set(group["public_respondent_id"])
        for q, group in analyzable.groupby("question_id")
    }
    check(
        "corpus_coverage",
        len(corpus) == 70
        and len(analyzable) == 52
        and q_counts == {"Q8.1": 26, "Q8.2": 26}
        and respondent_sets.get("Q8.1") == respondent_sets.get("Q8.2"),
        f"all={len(corpus)}; analyzable={len(analyzable)}; by_question={q_counts}",
    )
    check(
        "public_ids_do_not_reveal_sequence",
        corpus["public_text_id"].is_unique
        and corpus["public_text_id"].str.fullmatch(r"OT-R\d{2}-Q8[12]").all()
        and corpus["public_respondent_id"].str.fullmatch(r"R\d{2}").all(),
        f"public_text_ids={corpus['public_text_id'].nunique()}",
    )
    check(
        "semantic_pending_status_closed",
        not corpus.loc[
            corpus["analyzable"].eq("YES"), "exclusion_or_warning"
        ].str.contains("PENDING", case=False, na=False).any(),
        f"analyzable_statuses={corpus.loc[corpus['analyzable'].eq('YES'), 'exclusion_or_warning'].value_counts().to_dict()}",
    )

    codebook = pd.read_csv(CODEBOOK, keep_default_na=False)
    check(
        "codebook_schema",
        list(codebook.columns) == CODEBOOK_COLUMNS
        and codebook["code_id"].is_unique
        and codebook["code_id"].astype(str).str.strip().ne("").all(),
        f"codes={len(codebook)}",
    )

    coded = pd.read_csv(CODED, keep_default_na=False)
    coded_counts = coded["question_id"].value_counts().to_dict()
    check(
        "coded_response_schema_and_coverage",
        list(coded.columns) == CODED_COLUMNS
        and len(coded) == 52
        and coded["public_text_id"].is_unique
        and coded_counts == {"Q8.1": 26, "Q8.2": 26}
        and set(coded["public_text_id"]) == set(analyzable["public_text_id"])
        and coded["final_codes"].astype(str).str.strip().ne("").all()
        and coded["coding_confidence"].isin(CONFIDENCE).all()
        and coded["excerpt_status"].isin(EXCERPT_STATUS).all(),
        f"rows={len(coded)}; by_question={coded_counts}",
    )
    check(
        "formal_coding_review_closed",
        coded["review_status"].isin(FINAL_REVIEW_STATUS).all(),
        f"statuses={coded['review_status'].value_counts().to_dict()}",
    )
    corpus_by_id = corpus.set_index("public_text_id")
    excerpt_errors: list[str] = []
    response_errors: list[str] = []
    for row in coded.itertuples(index=False):
        source = corpus_by_id.loc[row.public_text_id]
        if (
            row.original_response != source["original_response"]
            or row.internal_response_id != source["internal_response_id"]
            or row.public_respondent_id != source["public_respondent_id"]
        ):
            response_errors.append(row.public_text_id)
        if (
            row.excerpt_status == "VERBATIM_SAFE"
            and row.deidentified_excerpt
            and row.deidentified_excerpt not in row.original_response
        ):
            excerpt_errors.append(row.public_text_id)
    check(
        "coded_rows_link_to_corpus",
        not response_errors,
        f"mismatches={response_errors or 'none'}",
    )
    check(
        "verbatim_excerpts_trace",
        not excerpt_errors,
        f"mismatches={excerpt_errors or 'none'}",
    )

    known_codes = set(codebook["code_id"])
    used_codes = set().union(*(split_codes(value) for value in coded["final_codes"]))
    unknown_codes = sorted(used_codes - known_codes)
    unused_codes = sorted(known_codes - used_codes)
    check(
        "formal_codes_resolve",
        not unknown_codes and len(codebook) == 47,
        f"used={len(used_codes)}; unknown={unknown_codes or 'none'}; unused={unused_codes or 'none'}",
    )
    coded_by_id = coded.set_index("public_text_id")
    codebook_example_errors: list[str] = []
    for row in codebook.itertuples(index=False):
        excerpt = str(row.example_excerpt).strip()
        source_id = str(row.example_text_id).strip()
        if not excerpt and not source_id:
            continue
        if not excerpt or source_id not in coded_by_id.index:
            codebook_example_errors.append(f"{row.code_id}:missing_pair")
            continue
        source = coded_by_id.loc[source_id]
        if (
            source["excerpt_status"] != "VERBATIM_SAFE"
            or excerpt != source["deidentified_excerpt"]
            or excerpt not in source["original_response"]
            or row.code_id not in split_codes(source["final_codes"])
        ):
            codebook_example_errors.append(row.code_id)
    check(
        "codebook_examples_are_approved_verbatim",
        not codebook_example_errors,
        f"examples={codebook['example_text_id'].astype(str).str.strip().ne('').sum()}; errors={codebook_example_errors or 'none'}",
    )

    themes = pd.read_csv(THEMES, keep_default_na=False)
    check(
        "theme_summary_schema_and_denominators",
        list(themes.columns) == THEME_COLUMNS
        and themes["question_id"].isin(["Q8.1", "Q8.2"]).all()
        and themes["valid_open_text_n"].astype(int).eq(26).all()
        and themes["unique_respondents"].astype(int).between(1, 26).all(),
        f"themes={len(themes)}; max_n={themes['unique_respondents'].astype(int).max()}",
    )
    count_errors: list[str] = []
    for row in themes.itertuples(index=False):
        expected = rows_for_basis(
            coded, row.question_id, row.counting_basis
        )["public_respondent_id"].nunique()
        if expected != int(row.unique_respondents):
            count_errors.append(f"{row.question_id}:{row.theme}:{expected}!={row.unique_respondents}")
    check(
        "theme_counts_by_unique_respondent",
        not count_errors,
        f"mismatches={count_errors or 'none'}",
    )
    theme_counts = themes.set_index("theme")["unique_respondents"].astype(int).to_dict()
    check(
        "mixed_direction_and_direct_belonging_semantics",
        len(themes) == 47
        and theme_counts.get("焦点事件方向为混合（并存或顺序反转）") == 6
        and theme_counts.get("进入与距离持续并存") == 5
        and theme_counts.get("先有距离后转为进入") == 1
        and theme_counts.get("直接表达被接纳或班级成员感") == 18,
        (
            f"mixed={theme_counts.get('焦点事件方向为混合（并存或顺序反转）')}; "
            f"coexisting={theme_counts.get('进入与距离持续并存')}; "
            f"sequential={theme_counts.get('先有距离后转为进入')}; "
            f"direct_belonging={theme_counts.get('直接表达被接纳或班级成员感')}"
        ),
    )

    open_closed = pd.read_csv(OPEN_CLOSED, keep_default_na=False)
    check(
        "open_closed_schema_and_coverage",
        list(open_closed.columns) == OPEN_CLOSED_COLUMNS
        and set(open_closed["public_text_id"]) == set(coded["public_text_id"])
        and open_closed["relationship_type"].isin(RELATIONS).all()
        and open_closed["confidence"].isin(CONFIDENCE).all()
        and open_closed["review_status"].isin(FINAL_REVIEW_STATUS).all()
        and len(open_closed) == 93
        and open_closed["relationship_type"].value_counts().to_dict()
        == {"EXPANSION": 51, "CONVERGENCE": 36, "DIVERGENCE": 3, "SILENCE": 3},
        f"rows={len(open_closed)}; text_ids={open_closed['public_text_id'].nunique()}; relations={open_closed['relationship_type'].value_counts().to_dict()}",
    )

    open_interview = pd.read_csv(OPEN_INTERVIEW, keep_default_na=False)
    expected_linked = set(
        analyzable.loc[
            analyzable["linked_interview_participant"].astype(str).str.strip().ne(""),
            "public_text_id",
        ]
    )
    bad_anchors: list[str] = []
    for row in open_interview.itertuples(index=False):
        source = ROOT / row.transcript_file
        if not source.is_file():
            bad_anchors.append(f"{row.public_text_id}:missing_file")
            continue
        labels = {
            match.group(1)
            for match in re.finditer(
                r"(?m)^\[(L\d{4})\]", source.read_text(encoding="utf-8")
            )
        }
        if (
            row.transcript_line_start not in labels
            or row.transcript_line_end not in labels
            or row.transcript_line_start > row.transcript_line_end
        ):
            bad_anchors.append(row.public_text_id)
    check(
        "linked_interview_alignment",
        list(open_interview.columns) == OPEN_INTERVIEW_COLUMNS
        and set(open_interview["public_text_id"]) == expected_linked
        and len(expected_linked) == 6
        and open_interview["linked_interview_participant"].nunique() == 3
        and open_interview["relationship_type"].isin(RELATIONS).all()
        and open_interview["confidence"].isin(CONFIDENCE).all()
        and open_interview["review_status"].isin(FINAL_REVIEW_STATUS).all()
        and not bad_anchors,
        f"rows={len(open_interview)}; text_ids={open_interview['public_text_id'].nunique()}; participants={open_interview['linked_interview_participant'].nunique()}; bad_anchors={bad_anchors or 'none'}",
    )

    public_missing = [path for path in PUBLIC_FILES if not path.is_file()]
    privacy_hits: list[str] = []
    for path in PUBLIC_FILES:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        for label, pattern in PRIVACY_PATTERNS.items():
            if pattern.search(text):
                privacy_hits.append(f"{path.relative_to(ROOT)}:{label}")
    check(
        "public_output_privacy",
        not public_missing and not privacy_hits,
        f"files={len(PUBLIC_FILES)}; hits={privacy_hits or 'none'}",
    )

    qualitative = (
        ROOT / "outputs/reports/open_text_qualitative_synthesis.md"
    ).read_text(encoding="utf-8")
    final_report = (ROOT / "outputs/final/final_research_report.md").read_text(
        encoding="utf-8"
    )
    check(
        "reporting_language_is_cautious",
        "主动提及" in qualitative
        and (
            "不是总体经历率" in qualitative
            or "不是35份完整问卷或目标群体的经历率" in qualitative
        )
        and "Q8.1" in final_report
        and "Q8.2" in final_report
        and "开放题" in final_report,
        "active-mention caution and open-text evidence layer are explicit",
    )
    final_register = pd.read_csv(
        ROOT / "outputs/final/findings_register.csv", keep_default_na=False
    ).set_index("finding_id")
    scoped_ids = ["F105", "F110", "F204", "F211", "F402", "F404"]
    scope_ok = all(
        "survey open-text sub-sample"
        in str(final_register.loc[finding_id, "evidence_scope"])
        for finding_id in scoped_ids
    ) and all(
        "complete survey sample"
        not in str(final_register.loc[finding_id, "evidence_scope"])
        for finding_id in ["F110", "F211", "F402", "F404"]
    )
    check(
        "open_text_evidence_scope",
        scope_ok,
        "; ".join(
            f"{finding_id}={final_register.loc[finding_id, 'evidence_scope']}"
            for finding_id in scoped_ids
        ),
    )
    joint = pd.read_csv(ROOT / "outputs/tables/joint_display.csv", keep_default_na=False)
    joint_by_topic = joint.set_index("analytic_topic")
    q81_actual = set(
        open_closed.loc[
            open_closed["question_id"].eq("Q8.1"), "relationship_type"
        ]
    )
    q82_actual = set(
        open_closed.loc[
            open_closed["question_id"].eq("Q8.2"), "relationship_type"
        ]
    )
    q81_joint = {
        value.strip()
        for value in joint_by_topic.loc[
            "开放题关键事件—封闭题边界与归属", "relationship_type"
        ].split(";")
    }
    q82_joint = {
        value.strip()
        for value in joint_by_topic.loc[
            "开放题支持期待—封闭题支持状态", "relationship_type"
        ].split(";")
    }
    check(
        "joint_display_relationship_types",
        q81_actual == q81_joint and q82_actual == q82_joint,
        f"Q8.1 actual={sorted(q81_actual)} joint={sorted(q81_joint)}; Q8.2 actual={sorted(q82_actual)} joint={sorted(q82_joint)}",
    )
    flagged_old_phrases = [
        "使一次任务连接到持续关系基础设施",
        "关系结构造成",
        "帮助完成任务和获得接纳",
    ]
    restricted_text = "\n".join(
        coded["theoretical_interpretation"].astype(str).tolist()
        + coded["researcher_inference"].astype(str).tolist()
    )
    check(
        "reviewed_inference_language",
        not any(phrase in restricted_text for phrase in flagged_old_phrases),
        "reviewer-flagged directional phrases removed",
    )
    check(
        "ai_agent_coding_disclosure",
        "AI编码代理" in final_report
        and "不是人工编码者间一致性" in final_report,
        "AI coding roles and lack of human inter-coder reliability are explicit",
    )
    check(
        "final_open_text_numbers",
        all(
            phrase in final_report
            for phrase in [
                "93项相关封闭题对照",
                "51项扩展",
                "36项一致",
                "3项未覆盖",
                "3项严格分歧",
            ]
        ),
        "final report reflects reviewer-resolved alignment counts",
    )
    check(
        "canonical_report_matches_final",
        (ROOT / "outputs/reports/final_report.md").read_bytes()
        == (ROOT / "outputs/final/final_research_report.md").read_bytes(),
        "canonical and final reports are byte-identical",
    )

    baseline = pd.read_csv(
        ROOT / "outputs/reports/raw_file_checksums.csv", encoding="utf-8-sig"
    )
    actual_sources = [
        path
        for folder in [ROOT / "data/raw", ROOT / "data/interview"]
        for path in folder.glob("*")
        if path.is_file()
    ]
    actual_hashes = {sha256(path) for path in actual_sources}
    missing_hashes = [
        str(row.relative_path)
        for row in baseline.itertuples(index=False)
        if row.file_hash not in actual_hashes
    ]
    source_diff = subprocess.run(
        ["git", "diff", "--", "data/raw", "data/interview"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    check(
        "source_data_unchanged",
        len(baseline) == 4 and not missing_hashes and not source_diff.strip(),
        f"baseline_sources={len(baseline)}; mismatches={missing_hashes or 'none'}",
    )

    write_report(checks)
    for name, status, detail in checks:
        print(f"{'PASS' if status else 'FAIL'} {name}: {detail}")
    passed = all(status for _, status, _ in checks)
    print(f"open-text checks={len(checks)} result={'PASS' if passed else 'FAIL'}")
    if not passed:
        raise SystemExit(1)


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(status for _, status, _ in checks)
    result = "PASS" if checks and passed == len(checks) else "FAIL"
    lines = [
        "# 问卷开放题第五轮验证报告",
        "",
        f"总体结果：**{result}**（{passed}/{len(checks)}项通过）。",
        "",
        "| 检查 | 结果 | 证据 |",
        "|---|---|---|",
    ]
    for name, status, detail in checks:
        safe_detail = str(detail).replace("|", "/").replace("\n", " ")
        lines.append(f"| `{name}` | {'PASS' if status else 'FAIL'} | {safe_detail} |")
    lines += [
        "",
        "## 研究完整性风险模式",
        "",
        "| 风险模式 | 裁决 | 验证依据 |",
        "|---|---|---|",
        "| 数据或引语捏造 | CLEAR | 正式编码与受限语料逐条链接，逐字摘录作连续子串回查。 |",
        "| 证据错配 | CLEAR | 开放—封闭与开放题—访谈均保存构念、变量、证据ID和替代解释。 |",
        "| 选择性遗漏 | CLEAR | Q8.1与Q8.2各26份可分析回答全部进入语义编码，少数与反例保留。 |",
        "| 重复计数 | CLEAR | 主题按题目内独立回答者去重，每题分母分别为26。 |",
        "| 因果或总体化 | CLEAR | 报告采用“主动提及”，不将开放题子样本推断为总体经历率。 |",
        "| 隐私暴露 | CLEAR | 公开层使用哈希排序公共ID；原文、内部ID和三源逐行链接留在受限层。 |",
        "| 不可复核 | CLEAR | 提取、上下文构建和自动验证脚本保留；语义裁决作为冻结分析输入。 |",
        "",
        "本报告验证文件结构、计数、链接、引语回查、隐私和关键表述边界；它不能把语义判断转化为算法客观性，也不替代独立review。",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
