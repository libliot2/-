# 第三轮流水线总结

## 范围

第三轮在第二版验证基线上完成多理论框架与开放式溯因再分析，没有重新改变问卷资格、映射或 canonical codebook。基线仍为35/35份有效问卷、0份排除、3份唯一链接访谈及84条逐字可追踪编码。

## 执行

运行 ID：`20260723_multi_theory_abductive_v3`

1. 读取项目规范、第二版报告、问卷表、链接个案、编号访谈、编码、framework matrix、joint display和规范文献；
2. 生成计划、12张理论卡片和共享证据契约；
3. 由五个独立理论角色分析边界/归属、制度/身份、中介/能动性、数字关系及过程/替代解释；
4. 生成跨框架矩阵、溯因异常组合、机制命题和提议分析框架；
5. 由两个独立 reviewer 审查理论贴合与多视角证据；
6. 主代理逐项核查审查意见并修订第三版主体报告；
7. 自动验证样本、链接、证据行号、理论分级、机制限制、隐私和源文件完整性。

## 版本化产物

- 框架：`outputs/theory/framework_inventory_v3.csv`、`cross_framework_matrix_v3.csv`
- 综合：`framework_notes_v3.md`、`cross_framework_synthesis_v3.md`
- 探索：`abductive_exploration_v3.md`、`mechanism_propositions_v3.csv`
- 框架提议：`proposed_analytical_framework_v3.md`
- 审查与修订：两份v3审查、`theoretical_revision_log_v3.md`
- 交付：`theoretical_extension_report_v3.md`、`final_report_v3.md`
- 验证：`validation_report_v3.md`

受限的参与者ID、问卷行、访谈行号与理论代理证据保存在被 Git 忽略的 `outputs/agent_runs/20260723_multi_theory_abductive_v3/`，公开产物仅保留可审计的汇总来源。

## 结果分级

最强贴合框架为 boundary work、school belonging、academic socialization 与 relationship functions；ecological/institutional context 和 agency–structure 仅作为审查镜头 strong fit。隐藏课程、学习者身份、时间轨迹、情境身份和平台组合为中等贴合；既有优势转译为 weak fit。具体入学年级/学校类型效应、稳定文化中介身份和可识别网络位置均不受支持。

机制命题按 cross-framework robust、framework-dependent、plausible but under-evidenced、contradicted 和 unsupported 分级；只有前两类进入主体报告。

两名独立 reviewer 共提出12项理论贴合问题和10项多视角证据问题（7项重叠）。主代理已修复对象口径、hidden curriculum、优势转译、机制分级、框架箭头、矩阵证据路径和全称化表述。第三轮自动验证19/19通过；完整再生检查65/65通过。

## Git

本轮保留全部v1/v2文件；开始基线为 `625eeb4444ce00d6b7c659bda2791a88fba1e05e`。由于 `analysis-v3` 已用于第二轮，本轮使用下一未占用版本标签 `analysis-v4`。提交和标签仅在验证通过及 `data/raw/`、`data/interview/` 源文件无变化后创建。
