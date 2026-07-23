# 自动验证报告

总体结果：**PASS**

## 检查结果

| 检查 | 状态 | 说明 |
|---|---|---|
| required_outputs | PASS | missing=none |
| raw_baseline_count | PASS | baseline files=4 |
| raw_unchanged | PASS | mismatches=none |
| survey_codebook_rows | PASS | rows=160 |
| survey_mapping_complete | PASS | all 160 export positions have unique canonical variable names and nonblank source headers |
| survey_total | PASS | rows=35 |
| survey_eligible_v2 | PASS | eligible=35 |
| survey_excluded_v2 | PASS | excluded=0 |
| survey_reclassified_v2 | PASS | 11 records excluded under v1 are explicitly reclassified and included |
| survey_legacy_eligibility_audit | PASS | legacy v1 split remains recoverable as 24 eligible / 11 excluded |
| survey_v2_ethical_gates | PASS | all 35 records pass consent and adult-status gates |
| survey_exact_duplicates | PASS | no exact full-response duplicates |
| survey_privacy_columns | PASS | direct/quasi-direct platform metadata excluded |
| construct_status | PASS | four exploratory descriptive indicators only |
| association_count | PASS | analyses=5 |
| association_multiplicity | PASS | BH-FDR q<0.05 only for ['A1', 'A4']; still exploratory |
| sample_flow_consistency | PASS | flow={'原始提交': 35, 'V2合资格样本': 35, 'V2排除': 0, 'V2重新纳入': 11} |
| exclusions_traceable | PASS | no v2 exclusions; legacy reasons retained in separate audit fields |
| support_table_consistency | PASS | generic item table agrees with dedicated support-gap valid n |
| linkage_files | PASS | interviews=3 |
| linkage_participant_unique | PASS | participant IDs unique |
| linkage_sequence_unique | PASS | restricted sequences unique |
| linkage_statuses | PASS | statuses={'MATCHED': 3} |
| linkage_eligibility | PASS | all three uniquely mapped cases are v2 eligible |
| linked_profiles | PASS | profiles exist for all three eligible linked cases |
| transcript_line_stability | PASS | all three restricted transcript copies have stable sequential line labels |
| qualitative_quotes_verbatim | PASS | errors=none |
| p01_quote_source | PASS | non-participant ranges=none |
| qualitative_case_scope | PASS | all and only the three eligible linked cases are coded |
| qualitative_confidence_enum | PASS | confidence enum valid |
| joint_relationship_enum | PASS | relationship types valid |
| joint_topics | PASS | topics=9 |
| joint_traceability | PASS | all topics list source files |
| reproducibility_scope | PASS | canonical targets=26 |
| canonical_reproducibility | PASS | non-reproducible=none |
| public_privacy_scan | PASS | findings=none |
| git_index_privacy | PASS | prohibited tracked paths=none |
| git_history_privacy | PASS | prohibited paths reachable from refs=none |
| report_distinguishes_survey | PASS | full survey section present |
| report_distinguishes_cases | PASS | linked-case section present |
| report_distinguishes_literature | PASS | literature comparison present |
| report_sample_counts | PASS | v2 flow 35 eligible / 0 excluded / 11 reclassified represented |
| report_posthoc_eligibility_timing | PASS | eligibility expansion is disclosed as post-v1-results and requires independent replication |
| report_cross_version_case_minimization | PASS | third-case anonymous ID is not linked to public v2 case details |
| report_small_cell_suppression | PASS | review-identified n<3 background, quality, and platform cells are suppressed |
| public_codebook_privacy | PASS | public codebook excludes retired/merged audit rows and participant-shaped examples |
| report_source_traceability | PASS | missing source mentions=none |
| unsupported_causal_language | PASS | unqualified lines=none |

## 明确保留的警告与跳过分析

- 资格口径在V1分析、审查和结果可见后扩展；旧口径排除的11份现全部纳入，V1/V2差异属于事后口径敏感性。
- 三份访谈包含一份整理式记录和两份未经录音核对、存在不同工具情境风险的机器转写。
- Q2.11 时点措辞冲突，Q3.1 第6项与 Q6.2 微博列缺失。
- A1与A4在V2样本中BH-FDR q<0.05，但仍为非概率、事后扩展口径下的探索性关联；未运行回归或因子分析。
- 开放题为关键词辅助多标签扫描；未宣称质性饱和或总体流行程度。
- 第三个链接个案的完整证据保留在受限层；公开报告已切断跨版本间接识别链。

## 结论

所有核心检查通过；最终主张可回溯至生成表或带行号的访谈证据。
