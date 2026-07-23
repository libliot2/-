# 第三轮自动验证报告

总体结果：**PASS**

## 检查结果

| 检查 | 状态 | 说明 |
|---|---|---|
| v3_required_outputs | PASS | missing=none |
| v3_framework_inventory | PASS | cards=12; invalid_fit=0 |
| v3_five_role_outputs | PASS | missing=none |
| v3_agent_evidence_schema | PASS | rows=67; invalid_fit=0 |
| v3_each_role_mixed_evidence | PASS | roles_without_both=none |
| v3_transcript_line_anchors | PASS | invalid=none |
| v3_cross_framework_matrix | PASS | phenomena=10 |
| v3_matrix_evidence_resolves | PASS | bad_paths=none; bad_ids=none |
| v3_mechanism_classification | PASS | rows=11; classes=['contradicted', 'cross-framework robust', 'framework-dependent', 'plausible but under-evidenced', 'unsupported'] |
| v3_mechanism_limits_complete | PASS | all required limitation and testing fields populated |
| v3_review_issue_closure | PASS | missing=none |
| v3_source_files_unchanged | PASS | sources=4; mismatches=none |
| v3_git_source_diff | PASS | no tracked source diff |
| v3_sample_and_linkage | PASS | survey=35/35 eligible; links=3 unique |
| v3_coded_evidence_baseline | PASS | segments=84 |
| v3_public_privacy | PASS | files=12; hits=none |
| v3_final_scope_guardrails | PASS | missing=none |
| v3_no_unqualified_causal_language | PASS | unqualified_lines=0 |
| v3_v2_preserved | PASS | final_report_v2 matches analysis-v3 |

## 验证边界

- 第二版数值、唯一链接和84条编码证据链作为已验证基线，并在本轮再次核对关键计数。
- 理论代理的访谈行号由脚本检查存在性；逐字引语的84条机械验证沿用第二轮完整验证。理论贴合仍需独立审查和 revision log 闭环。
- 解释性综合属于版本控制的冻结分析判断；异常组合和开放题相似度由脚本再生。
- 公开文件不含问卷序号、受限个案ID或访谈行号；完整证据仅保存在被 Git 忽略的受限 agent 目录。

## 结论

第三轮关键数字、映射、证据锚点、框架分级、机制限制、隐私、源文件完整性和非因果边界全部通过。
