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
| survey_eligible | PASS | eligible=24 |
| survey_excluded | PASS | excluded=11 |
| survey_exact_duplicates | PASS | no exact full-response duplicates |
| survey_privacy_columns | PASS | direct/quasi-direct platform metadata excluded |
| construct_status | PASS | four exploratory descriptive indicators only |
| association_count | PASS | analyses=5 |
| association_multiplicity | PASS | no BH-FDR q<0.05; all treated as exploratory |
| sample_flow_consistency | PASS | flow={'原始提交': 35, '合资格样本': 24, '排除': 11} |
| exclusions_traceable | PASS | all 11 excluded rows have explicit reasons |
| support_table_consistency | PASS | generic item table agrees with dedicated support-gap valid n |
| linkage_files | PASS | interviews=3 |
| linkage_participant_unique | PASS | participant IDs unique |
| linkage_sequence_unique | PASS | restricted sequences unique |
| linkage_statuses | PASS | statuses={'MATCHED': 2, 'INELIGIBLE': 1} |
| linkage_eligibility | PASS | matched cases eligible; ineligible case excluded |
| linked_profiles | PASS | profiles exist only for the two eligible linked cases |
| transcript_line_stability | PASS | all three restricted transcript copies have stable sequential line labels |
| qualitative_quotes_verbatim | PASS | errors=none |
| p01_quote_source | PASS | non-participant ranges=none |
| qualitative_case_scope | PASS | only the two eligible linked cases are coded |
| qualitative_confidence_enum | PASS | confidence enum valid |
| joint_relationship_enum | PASS | relationship types valid |
| joint_topics | PASS | topics=10 |
| joint_traceability | PASS | all topics list source files |
| reproducibility_scope | PASS | canonical targets=26 |
| canonical_reproducibility | PASS | non-reproducible=none |
| public_privacy_scan | PASS | findings=none |
| git_index_privacy | PASS | prohibited tracked paths=none |
| git_history_privacy | PASS | prohibited paths reachable from refs=none |
| report_distinguishes_survey | PASS | full survey section present |
| report_distinguishes_cases | PASS | linked-case section present |
| report_distinguishes_literature | PASS | literature comparison present |
| report_sample_counts | PASS | 35/24/11 represented |
| report_source_traceability | PASS | missing source mentions=none |
| unsupported_causal_language | PASS | unqualified lines=none |

## 明确保留的警告与跳过分析

- 一份访谈文件唯一映射至不合资格问卷记录，已按合同排除链接个案分析。
- 合资格访谈包含一份整理式记录和一份未经录音核对、存在工具情境风险的机器转写。
- Q2.11 时点措辞冲突，Q3.1 第6项与 Q6.2 微博列缺失。
- 五项探索性关联经 BH-FDR 校正后均无 q<0.05；未运行回归或因子分析。
- 开放题为关键词辅助多标签扫描；未宣称质性饱和或总体流行程度。

## 结论

所有核心检查通过；最终主张可回溯至生成表或带行号的访谈证据。
