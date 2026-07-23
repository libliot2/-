# 第二轮自动验证报告

总体结果：**PASS**

## 检查结果

| 检查 | 状态 | 说明 |
|---|---|---|
| v2_required_outputs | PASS | missing=none |
| v2_raw_baseline_count | PASS | source hashes=4 |
| v2_raw_unchanged | PASS | mismatches=none |
| v2_sample_flow | PASS | total=35; eligible=35; excluded=0; reclassified=11 |
| v2_ethical_gates | PASS | all records pass consent and adult-status gates |
| v2_multiselect_limits | PASS | over-limit counts={'MULTISELECT_LIMIT_EXCEEDED_Q2_10': 8, 'MULTISELECT_LIMIT_EXCEEDED_Q3_2': 14, 'MULTISELECT_LIMIT_EXCEEDED_Q5_4': 9} |
| v2_multiselect_exclusive_conflict | PASS | Q5.3 mutually exclusive combination is detected and retained as a flag |
| v2_codebook_parent_item_semantics | PASS | matrix/multiple-choice parent questions and item labels are distinct |
| v2_codebook_source_mapping | PASS | 160 unique export positions retain nonblank source headers |
| v2_group_missingness_propagation | PASS | Q5.4 group-level special response is excluded from ordinary-option denominator |
| v2_q54_denominators | PASS | Q5.4 selected counts/valid n={'q5_4_help_hk_peer': (23, 34), 'q5_4_help_mainland_peer': (19, 34)} |
| v2_matrix_distribution_sums | PASS | ordinal variables checked=42 |
| v2_multiselect_background_coverage | PASS | teaching-language and migration-reason multiple choices are included |
| v2_open_text_guardrail | PASS | open-text output is labelled as an index rather than semantic prevalence |
| v2_linkage_unique | PASS | three mappings are MATCHED and one-to-one |
| v2_linked_profiles | PASS | all matched cases have regenerated restricted profiles |
| v2_quotes_verbatim | PASS | segments=84; quote_errors=none |
| v2_quote_speakers | PASS | non-participant ranges=none |
| v2_context_ranges_corrected | PASS | review-identified machine-sentence continuations are included |
| v2_semantic_recodes | PASS | all reviewer-identified primary-code corrections are applied |
| v2_proposed_code_boundary | PASS | applied inductive code is ACTIVE; unused candidates remain explicit PROPOSED |
| v2_alignment_full_adjudication | PASS | rows=75; relationship counts={'EXPANSION': 34, 'CONVERGENCE': 21, 'SILENCE': 11, 'DIVERGENCE': 9} |
| v2_divergence_three_part_rule | PASS | all retained divergences pass construct/time/direction criteria |
| v2_finding_class_enum | PASS | classes=['plausible exploratory finding', 'robust finding', 'weak signal'] |
| v2_unsupported_removed | PASS | no unsupported interpretation remains in the finding table |
| v2_extension_small_cell_suppression | PASS | public extension table suppresses n<3 |
| v2_paired_platform_states | PASS | retained/adopted/stopped/neither sum to paired n for 11 platforms |
| v2_a1_robustness | PASS | four A1 variants and leave-one-out ranges remain negative |
| v2_a4_downgrade | PASS | A4 alternative encodings vary materially and are all weak signal |
| v2_leave_one_case_out | PASS | configuration themes record single-case dependency |
| v2_joint_relationship_coverage | PASS | joint types=['CONVERGENCE', 'DIVERGENCE', 'EXPANSION', 'SILENCE'] |
| v2_joint_topic_type_granularity | PASS | analysis-specification sensitivity is not mislabelled as source divergence |
| v2_reproducibility_scope | PASS | versioned targets=46 |
| v2_reproducibility_modes | PASS | target modes=['FROZEN_ANALYTIC_INPUT_PROMOTED', 'REGENERATED'] |
| v2_reproducibility_pass | PASS | non-reproducible targets=none |
| v2_review_issue_closure | PASS | missing issue dispositions=none |
| v2_revision_status_enum | PASS | all revision-log rows have final retained/revised/removed/added status |
| v2_current_public_privacy | PASS | files scanned=16; findings=none |
| v2_git_index_privacy | PASS | prohibited tracked paths=none |
| v2_git_raw_diff | PASS | no tracked raw-data diff |
| v2_final_alias | PASS | final_report.md and final_report_v2.md are byte-identical |
| v2_final_required_claims | PASS | missing required phrases=none |
| v2_composite_item_preserved | PASS | Q3.3 composite meaning is preserved |
| v2_a4_not_main_finding | PASS | A4 is explicitly downgraded |
| v2_no_unsupported_causal_language | PASS | unqualified lines=none |
| v2_no_generalisation_from_three | PASS | linked cases are explicitly non-representative |

## 验证边界

- 数值与文件再生和冻结解释性判断提升已分开标记；后者不等于算法重新发现主题。
- 84 条引语的逐字与说话人检查为机械验证；代码语义、关系类型和跨案覆盖由四份独立审查及 revision log 闭环。
- 当前公开 allowlist 不包括 `analysis-v2` tag 中的历史报告；第一轮原件保持可追溯，第二轮当前交付执行更严格的小格和跨版本最小化。
- A1 仍是事后资格口径下的探索性结果；A4 仅为 weak signal。

## 结论

第二轮核心检查全部通过；原始资料未变，映射唯一，数字、引语、探索分级、隐私和复现边界一致。
