# 最终成果文件索引

## 规范最终成果（优先阅读）

1. `final_research_report.md`：完整中文课程研究报告；验证后与`outputs/reports/final_report.md`保持逐字一致。
2. `executive_summary.md`：1500—2500字执行摘要。
3. `key_findings_one_page.md`：一页式发现、局限和谨慎建议。
4. `research_question_evidence_matrix.csv`：研究问题—问卷—链接个案—文献证据矩阵。
5. `final_analytical_framework.md`：最小组合框架、关系支持程度及竞争解释。

第五轮开放题结果已经并入上述规范文件；专题方法和证据报告见下方“开放题语义分析”。

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
- `methods_and_audit_summary.md`：数据、五轮分析、subagent、review、验证及Git摘要。

## 支持性问卷表格

- `outputs/tables/sample_flow.csv`
- `outputs/tables/survey_item_statistics.csv`
- `outputs/tables/support_gap_analysis.csv`
- `outputs/tables/platform_transition_analysis.csv`
- `outputs/tables/exploratory_associations.csv`
- `outputs/tables/exploratory_extension_v2.csv`
- `outputs/tables/joint_display.csv`
- `outputs/tables/mechanism_propositions_v3.csv`
- `outputs/tables/open_text_theme_summary.csv`

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

## 开放题语义分析

- `data/processed/open_text_codebook.csv`：47个公开、去识别的正式开放题代码。
- `outputs/open_text/open_text_analysis_plan.md`：第五轮执行计划。
- `outputs/open_text/coding_reconciliation.md`：两条独立编码路径的协调裁决。
- `outputs/open_text/q81_critical_incident_analysis.md`：Q8.1关键事件分析。
- `outputs/open_text/q82_support_needs_analysis.md`：Q8.2支持期待分析。
- `outputs/reports/open_text_qualitative_synthesis.md`：两题全量语义综合、反例与限制。
- `outputs/reports/open_closed_integration.md`：52条开放回答与相关封闭题的问卷内部整合。
- `outputs/reports/open_text_linked_case_analysis.md`：三名链接个案的开放题—封闭题—访谈三源综合。
- `outputs/reviews/open_text_evidence_audit.md`、`outputs/reviews/open_text_method_audit.md`：第五轮独立审查。
- `outputs/reports/open_text_validation_report.md`、`outputs/reports/open_text_pipeline_summary.md`：第五轮验证和流水线总结。

受限且不进入公开Git的文件包括`data/processed/survey_open_text_corpus.csv`、`outputs/open_text/open_text_coded_responses.csv`、`outputs/open_text/open_closed_alignment.csv`、`outputs/open_text/open_text_interview_alignment.csv`及本轮`outputs/agent_runs/`。它们保存原文、内部连接和逐条裁决，供授权审计。

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
- v5：开放题全量语义分析、问卷内部及三源整合、两份独立review和修订记录。
- 各轮pipeline summaries和agent manifests继续保留在`outputs/reports/`。

旧版本用于审计，不是当前规范结论。最终验证已通过，`outputs/reports/final_report.md`与本目录的`final_research_report.md`相同。
