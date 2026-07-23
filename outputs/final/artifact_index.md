# 最终成果文件索引

## 规范最终成果（优先阅读）

1. `final_research_report.md`：完整中文课程研究报告；验证后与`outputs/reports/final_report.md`保持逐字一致。
2. `executive_summary.md`：1500—2500字执行摘要。
3. `key_findings_one_page.md`：一页式发现、局限和谨慎建议。
4. `research_question_evidence_matrix.csv`：研究问题—问卷—链接个案—文献证据矩阵。
5. `final_analytical_framework.md`：最小组合框架、关系支持程度及竞争解释。

## 结论和版本审计

- `findings_register.csv`：跨版本结论总表及最终状态。
- `version_reconciliation.md`：v1、v2、v3的稳定、弱化、扩展和删除记录。
- `evidence_hierarchy.md`：A核心、B限定、C探索及D拒绝结论。
- `final_evidence_audit.md`：最终证据与一致性独立审查。
- `final_editorial_review.md`：最终结构和可读性独立审查。
- `final_validation_report.md`：自动与人工复核结果。
- `final_project_summary.md`：最终流水线和版本总结。

## 方法与执行

- `final_synthesis_plan.md`：最后一轮工作计划及开始基线。
- `methods_and_audit_summary.md`：数据、三轮分析、subagent、review、验证及Git摘要。

## 支持性问卷表格

- `outputs/tables/sample_flow.csv`
- `outputs/tables/survey_item_statistics.csv`
- `outputs/tables/support_gap_analysis.csv`
- `outputs/tables/platform_transition_analysis.csv`
- `outputs/tables/exploratory_associations.csv`
- `outputs/tables/exploratory_extension_v2.csv`
- `outputs/tables/joint_display.csv`
- `outputs/tables/mechanism_propositions_v3.csv`

这些表格是最终数字的直接来源；处理后问卷位于`data/processed/`。

## 质性与链接证据

- `data/processed/linked_cases/`：三个linked case profiles（受限，不进入公开Git交付）。
- `data/processed/interviews/`：编号访谈（受限）。
- `data/processed/interview_survey_map.csv`：问卷—访谈唯一连接表（受限）。
- `outputs/qualitative/coded_segments_master.csv`：84条规范编码（受限）。
- `outputs/qualitative/framework_matrix.csv`：主题—个案框架矩阵（受限）。
- `outputs/reports/cross_case_analysis.md`
- `outputs/reports/integrated_findings.md`
- 逐字引语、行号和连接键分布在上述受限processed/qualitative文件及Git忽略的`outputs/agent_runs/`审查对照表中，不进入公开交付。

## 文献与理论

- `docs/literature_context/research_context.md`
- `docs/literature_context/literature_review.md`
- `docs/literature_context/evidence_index.csv`
- `outputs/reports/literature_comparison.md`
- `outputs/reports/theoretical_extension_report_v3.md`
- `outputs/theory/framework_inventory_v3.csv`
- `outputs/theory/cross_framework_matrix_v3.csv`

文献只提供背景与解释，不是当前参与者证据。

## 旧版本与审查记录

- v1：第一轮独立报告从Git历史标签读取；其余基础产物继续保留。
- v2：`outputs/reports/final_report_v2.md`、`revision_log_v2.md`、`validation_report_v2.md`及四份v2 reviewer报告。
- v3：`outputs/reports/final_report_v3.md`、`theoretical_revision_log_v3.md`、`validation_report_v3.md`及两份v3理论reviewer报告。
- 三轮pipeline summaries和agent manifests继续保留在`outputs/reports/`。

旧版本用于审计，不是当前规范结论。最终验证已通过，`outputs/reports/final_report.md`与本目录的`final_research_report.md`相同。
