#!/usr/bin/env python3
"""Validate the generated public-safe course-report appendices."""

from __future__ import annotations

import importlib.util
import itertools
import re
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OVERLEAF = ROOT / "6a58bbb68d0662ee12b5ab75"
SRC = OVERLEAF / "src"
REPORT = ROOT / "outputs" / "course_report" / "appendix_validation_report.md"
BUILDER_PATH = ROOT / "scripts" / "build_course_report_appendix.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("appendix_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load appendix builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = load_builder()
    questionnaire = (SRC / "appendix_questionnaire.tex").read_text(encoding="utf-8")
    survey = (SRC / "appendix_survey_results.tex").read_text(encoding="utf-8")
    open_text = (SRC / "appendix_open_text.tex").read_text(encoding="utf-8")
    master = (SRC / "appendix_analysis.tex").read_text(encoding="utf-8")
    main_tex = (OVERLEAF / "main.tex").read_text(encoding="utf-8")
    method_tex = (SRC / "3method.tex").read_text(encoding="utf-8")
    findings_tex = (SRC / "4findings.tex").read_text(encoding="utf-8")
    figure_script = (
        ROOT / "scripts" / "build_course_report_figures.py"
    ).read_text(encoding="utf-8")

    checks: list[tuple[str, bool, str]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append((name, bool(passed), detail))

    add(
        "questionnaire_fragment_reproducible",
        questionnaire == builder.questionnaire_to_latex(),
        "generated fragment matches the administered questionnaire source",
    )
    add(
        "survey_fragment_reproducible",
        survey == builder.survey_results_to_latex(),
        "generated fragment matches validated aggregate survey tables",
    )
    add(
        "open_text_fragment_reproducible",
        open_text == builder.open_text_to_latex(),
        "generated fragment matches the selected validated theme table",
    )

    survey_stats = pd.read_csv(builder.SURVEY_STATS, encoding="utf-8-sig")
    expected_roles = {role for _, roles in builder.DOMAIN_ROLES for role in roles}
    actual_roles = set(survey_stats["analysis_role"].dropna().astype(str))
    add(
        "survey_role_coverage",
        actual_roles == expected_roles and survey_stats["variable_name"].nunique() == 121,
        f"roles={len(actual_roles)}; variables={survey_stats['variable_name'].nunique()}",
    )

    section_titles = [
        "Questionnaire Instrument as Administered",
        "Aggregated Linked-Interview Evidence Summary",
        "Public-Safe Aggregate Questionnaire Summaries",
        "Open-Ended Response Analysis",
        "Exploratory Indicators and Mixed-Methods Integration",
        "Reproducibility, Data Boundaries and Privacy",
    ]
    add(
        "appendix_sections_present",
        all(title in master for title in section_titles),
        "six intended appendix sections present",
    )
    add(
        "appendix_toc_is_section_level",
        r"\addtocontents{toc}{\protect\setcounter{tocdepth}{1}}" in main_tex,
        "printed contents retain Appendix A--F while suppressing appendix sublevels",
    )
    add(
        "body_to_appendix_navigation",
        all(
            label in method_tex + "\n" + (SRC / "4findings.tex").read_text(encoding="utf-8")
            for label in [
                "app:questionnaire",
                "app:interviews",
                "app:survey-results",
                "app:open-text",
                "app:extended-analysis",
                "app:reproducibility",
            ]
        ),
        "method and findings provide entry points to all six appendix sections",
    )
    add(
        "reader_friendly_question_labels",
        "Q5.1(1)" in survey
        and r"Q5.1\_1" not in survey
        and "sixth item under Q5.1" in master,
        "sub-item labels use instrument-style parentheses rather than code underscores",
    )
    add(
        "open_text_translation_and_coding_anchor",
        "Theme (authors' translation)" in open_text
        and "Peer-initiated invitation" in open_text
        and r"\texttt{OTC02}" in open_text
        and "not a respondent" in master,
        "selected themes have English labels and traceable non-participant coding anchors",
    )

    forbidden_aliases = [
        r"\bP0[1-3]\b",
        r"\bOT-R\d+",
        r"\bInterview [ABC]\b",
        r"internal_response_id",
        r"public_text_id",
    ]
    public_text = "\n".join([master, survey, open_text])
    alias_hits = [
        pattern for pattern in forbidden_aliases if re.search(pattern, public_text)
    ]
    add(
        "no_stable_case_or_response_alias",
        not alias_hits,
        "hits=" + (", ".join(alias_hits) if alias_hits else "none"),
    )
    add(
        "no_rare_interview_source_format_split",
        "Two records were machine-generated" not in public_text
        and "one record was available as a structured summary" not in public_text
        and "One source was a summary-style record" not in method_tex
        and "two were machine transcripts" not in method_tex
        and "the summary-style record" not in method_tex
        and "the machine transcripts" not in method_tex
        and "structured-summary records" not in public_text
        and "structured-summary records" not in method_tex,
        "source-format limitations are reported without exact small-cell counts",
    )
    add(
        "interview_publication_boundaries_present",
        all(
            phrase in master
            for phrase in [
                "consent did not explicitly authorize",
                "are paraphrases",
                "at most medium confidence",
                "do not establish prevalence",
            ]
        ),
        "consent, paraphrase, source-quality and non-generalisation limits remain adjacent to interview evidence",
    )
    add(
        "special_response_states_remain_distinct",
        all(
            phrase in method_tex + "\n" + master
            for phrase in [
                "not applicable",
                "cannot remember",
                "unwilling to answer",
                "invalid response",
            ]
        )
        and "rather than treated as disagreement or zero" in method_tex,
        "special response categories remain named, distinct and excluded from valid denominators",
    )

    exact_small_pattern = re.compile(r"(?<![<\d])(?:1|2)/(?:26|3[0-5])")
    small_hits = exact_small_pattern.findall(survey + "\n" + open_text)
    add(
        "direct_small_cells_suppressed",
        not small_hits,
        f"exact participant-cell hits={len(small_hits)}",
    )
    add(
        "cross_table_platform_suppression",
        "微信或朋友圈 & selected: S (cross-table suppression)" in survey
        and "Instagram & selected: S (cross-table suppression)" in survey
        and "WeChat & 26/35 & S & 6/35 & S" in survey
        and "WhatsApp & S & 26/35 & S & 9/35" in survey
        and "Instagram & S & 22/35 & S & S" in survey,
        "marginals and selected paired-transition rows use complementary protection",
    )

    published_transition_cells = {
        "WeChat": (26, None, 6, None),
        "WhatsApp": (None, 26, None, 9),
        "Instagram": (None, 22, None, None),
    }
    recovered_small: list[str] = []
    for platform, published in published_transition_cells.items():
        feasible: list[tuple[int, int, int, int]] = []
        domains = [
            [value] if value is not None else range(36) for value in published
        ]
        for candidate in itertools.product(*domains):
            if sum(candidate) == 35:
                feasible.append(candidate)
        pre_use = {retained + stopped for retained, _, stopped, _ in feasible}
        later_use = {retained + adopted for retained, adopted, _, _ in feasible}
        for label, values in [("pre", pre_use), ("later", later_use)]:
            if len(values) == 1 and next(iter(values)) in {1, 2}:
                recovered_small.append(
                    f"{platform}:{label}={next(iter(values))}"
                )
    add(
        "transition_algebra_does_not_recover_small_margin",
        not recovered_small,
        "recovered exact small margins="
        + (", ".join(recovered_small) if recovered_small else "none"),
    )

    add(
        "instrument_notes_match_quality_audit",
        "Q2.10, Q3.2 and Q5.4" in master
        and "mutually inconsistent selections" in master,
        "selection-limit and Q5.3 conflict notes present",
    )
    add(
        "instrument_scope_and_export_boundaries",
        "instrument is reproduced unchanged" in master.lower()
        and "migration- and grade-specific" in master
        and "multiple-response unwilling-to-answer flags" in master
        and "where those fields were present in the export" in master,
        "instrument scope and unavailable export fields are disclosed without reconstructing data",
    )
    add(
        "complete_codebook_traceability",
        "data/processed/open_text_codebook.csv" in master
        and all(code in master for code in ["OTC08", "OTC12", "OTC28", "OTC30", "OTC32"]),
        "all codes used in the selected theme table are defined or linked to the complete codebook",
    )
    add(
        "indicator_direction_and_missingness",
        "Higher values represent more boundary or difficulty" in master
        and "maximum observable count of seven" in master
        and "opportunity-sensitive association" in master,
        "indicator directions and A3 opportunity-sensitive missingness are explicit",
    )
    add(
        "analysis_snapshot_recorded",
        "analysis-v5-" in master
        and "open-text" in master
        and "2026-08-04" in master,
        "appendix records its analysis-source tag and audit date",
    )
    disclosed_small_phrases = [
        "two had not received",
        "Two of 26",
        "One of the 26 respondents",
        "One of 26 Q8.1",
        "one of 26 Q8.2",
        "five described acceptance",
        "while one described",
        "one account welcomed",
        "while another did not want",
    ]
    add(
        "cross_report_small_cell_consistency",
        not any(phrase in findings_tex for phrase in disclosed_small_phrases)
        and "complementary small-cell counts are suppressed" in findings_tex
        and "Non-receipt states combined" in figure_script
        and "two peer-integration non-receipt states are combined" in findings_tex,
        "body text and support figure follow the appendix small-cell disclosure rule",
    )
    add(
        "special_response_rule_not_repeated_per_row",
        survey.count("special responses excluded from valid N") == 0
        and "Special responses are excluded from the valid denominator" in survey,
        "special states remain defined once without repeated row-level prose",
    )
    add(
        "no_reclassification_narrative",
        "11 responses" not in public_text
        and "11份" not in public_text
        and "无效问卷" not in public_text,
        "excluded user-specified reclassification narrative",
    )

    raw_status = subprocess.run(
        ["git", "diff", "--quiet", "--", "data/raw", "data/interview"],
        cwd=ROOT,
        check=False,
    ).returncode
    add(
        "protected_source_tree_unchanged",
        raw_status == 0,
        "git diff reports no changes under data/raw or data/interview",
    )

    add(
        "cjk_build_configuration",
        r"\usepackage{xeCJK}" in main_tex
        and "FandolSong-Regular.otf" in main_tex
        and r"\input{src/appendix_analysis}" in main_tex,
        "XeLaTeX CJK configuration and appendix input present",
    )

    passed = sum(ok for _, ok, _ in checks)
    status = "PASS" if passed == len(checks) else "FAIL"
    lines = [
        "# Course-report appendix validation",
        "",
        f"Overall result: **{status}** ({passed}/{len(checks)} checks passed).",
        "",
        "This report validates the newly generated appendix artefacts only. It does "
        "not replace or restate the status of the full historical analysis bundle.",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for name, ok, detail in checks:
        lines.append(f"| `{name}` | {'PASS' if ok else 'FAIL'} | {detail} |")
    lines.extend(
        [
            "",
            "The validation compares generated fragments with their public aggregate "
            "sources, checks section coverage and selected privacy controls, and verifies "
            "that protected source trees have no Git diff. It does not validate the "
            "objective truth of retrospective accounts or convert reviewed qualitative "
            "judgments into computational facts.",
            "",
        ]
    )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{status}: {passed}/{len(checks)}")
    print(REPORT)
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
