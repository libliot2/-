# Course-report appendix validation

Overall result: **PASS** (21/21 checks passed).

This report validates the newly generated appendix artefacts only. It does not replace or restate the status of the full historical analysis bundle.

| Check | Result | Detail |
|---|---|---|
| `questionnaire_fragment_reproducible` | PASS | generated fragment matches the administered questionnaire source |
| `survey_fragment_reproducible` | PASS | generated fragment matches validated aggregate survey tables |
| `open_text_fragment_reproducible` | PASS | generated fragment matches the selected validated theme table |
| `survey_role_coverage` | PASS | roles=17; variables=121 |
| `appendix_sections_present` | PASS | six intended appendix sections present |
| `appendix_toc_is_section_level` | PASS | printed contents retain Appendix A--F while suppressing appendix sublevels |
| `body_to_appendix_navigation` | PASS | method and findings provide entry points to all six appendix sections |
| `reader_friendly_question_labels` | PASS | sub-item labels use instrument-style parentheses rather than code underscores |
| `open_text_translation_and_coding_anchor` | PASS | selected themes have English labels and traceable non-participant coding anchors |
| `no_stable_case_or_response_alias` | PASS | hits=none |
| `no_rare_interview_source_format_split` | PASS | source-format limitations are reported without exact small-cell counts |
| `interview_publication_boundaries_present` | PASS | consent, paraphrase, source-quality and non-generalisation limits remain adjacent to interview evidence |
| `special_response_states_remain_distinct` | PASS | special response categories remain named, distinct and excluded from valid denominators |
| `direct_small_cells_suppressed` | PASS | exact participant-cell hits=0 |
| `cross_table_platform_suppression` | PASS | marginals and selected paired-transition rows use complementary protection |
| `transition_algebra_does_not_recover_small_margin` | PASS | recovered exact small margins=none |
| `instrument_notes_match_quality_audit` | PASS | selection-limit and Q5.3 conflict notes present |
| `special_response_rule_not_repeated_per_row` | PASS | special states remain defined once without repeated row-level prose |
| `no_reclassification_narrative` | PASS | excluded user-specified reclassification narrative |
| `protected_source_tree_unchanged` | PASS | git diff reports no changes under data/raw or data/interview |
| `cjk_build_configuration` | PASS | XeLaTeX CJK configuration and appendix input present |

The validation compares generated fragments with their public aggregate sources, checks section coverage and selected privacy controls, and verifies that protected source trees have no Git diff. It does not validate the objective truth of retrospective accounts or convert reviewed qualitative judgments into computational facts.
