# 问卷开放题第五轮验证报告

总体结果：**PASS**（25/25项通过）。

| 检查 | 结果 | 证据 |
|---|---|---|
| `required_outputs` | PASS | missing=none |
| `corpus_coverage` | PASS | all=70; analyzable=52; by_question={'Q8.1': 26, 'Q8.2': 26} |
| `public_ids_do_not_reveal_sequence` | PASS | public_text_ids=70 |
| `semantic_pending_status_closed` | PASS | analyzable_statuses={'SEMANTIC_ANALYSIS_COMPLETED': 52} |
| `codebook_schema` | PASS | codes=47 |
| `coded_response_schema_and_coverage` | PASS | rows=52; by_question={'Q8.1': 26, 'Q8.2': 26} |
| `formal_coding_review_closed` | PASS | statuses={'MAIN_AGENT_VERIFIED': 45, 'REVIEWER_RESOLVED': 7} |
| `coded_rows_link_to_corpus` | PASS | mismatches=none |
| `verbatim_excerpts_trace` | PASS | mismatches=none |
| `formal_codes_resolve` | PASS | used=47; unknown=none; unused=none |
| `codebook_examples_are_approved_verbatim` | PASS | examples=42; errors=none |
| `theme_summary_schema_and_denominators` | PASS | themes=47; max_n=18 |
| `theme_counts_by_unique_respondent` | PASS | mismatches=none |
| `mixed_direction_and_direct_belonging_semantics` | PASS | mixed=6; coexisting=5; sequential=1; direct_belonging=18 |
| `open_closed_schema_and_coverage` | PASS | rows=93; text_ids=52; relations={'EXPANSION': 51, 'CONVERGENCE': 36, 'DIVERGENCE': 3, 'SILENCE': 3} |
| `linked_interview_alignment` | PASS | rows=6; text_ids=6; participants=3; bad_anchors=none |
| `public_output_privacy` | PASS | files=20; hits=none |
| `reporting_language_is_cautious` | PASS | active-mention caution and open-text evidence layer are explicit |
| `open_text_evidence_scope` | PASS | F105=survey open-text sub-sample; within-case linked evidence; cross-case interpretation; F110=survey open-text sub-sample; F204=complete survey sample; survey open-text sub-sample; within-case linked evidence; F211=survey open-text sub-sample; F402=survey open-text sub-sample; F404=survey open-text sub-sample; within-case linked evidence |
| `joint_display_relationship_types` | PASS | Q8.1 actual=['CONVERGENCE', 'DIVERGENCE', 'EXPANSION', 'SILENCE'] joint=['CONVERGENCE', 'DIVERGENCE', 'EXPANSION', 'SILENCE']; Q8.2 actual=['CONVERGENCE', 'EXPANSION', 'SILENCE'] joint=['CONVERGENCE', 'EXPANSION', 'SILENCE'] |
| `reviewed_inference_language` | PASS | reviewer-flagged directional phrases removed |
| `ai_agent_coding_disclosure` | PASS | AI coding roles and lack of human inter-coder reliability are explicit |
| `final_open_text_numbers` | PASS | final report reflects reviewer-resolved alignment counts |
| `canonical_report_matches_final` | PASS | canonical and final reports are byte-identical |
| `source_data_unchanged` | PASS | baseline_sources=4; mismatches=none |

## 研究完整性风险模式

| 风险模式 | 裁决 | 验证依据 |
|---|---|---|
| 数据或引语捏造 | CLEAR | 正式编码与受限语料逐条链接，逐字摘录作连续子串回查。 |
| 证据错配 | CLEAR | 开放—封闭与开放题—访谈均保存构念、变量、证据ID和替代解释。 |
| 选择性遗漏 | CLEAR | Q8.1与Q8.2各26份可分析回答全部进入语义编码，少数与反例保留。 |
| 重复计数 | CLEAR | 主题按题目内独立回答者去重，每题分母分别为26。 |
| 因果或总体化 | CLEAR | 报告采用“主动提及”，不将开放题子样本推断为总体经历率。 |
| 隐私暴露 | CLEAR | 公开层使用哈希排序公共ID；原文、内部ID和三源逐行链接留在受限层。 |
| 不可复核 | CLEAR | 提取、上下文构建和自动验证脚本保留；语义裁决作为冻结分析输入。 |

本报告验证文件结构、计数、链接、引语回查、隐私和关键表述边界；它不能把语义判断转化为算法客观性，也不替代独立review。
