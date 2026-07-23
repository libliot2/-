# Agent 运行清单

运行 ID：`20260723_expanded_eligibility`

| 角色 | 执行方式 | 依赖完成后启动 | 独立输出 | 状态 |
|---|---|---|---|---|
| Main Agent | 主代理 | — | canonical processed data、master files、报告与 Git | 完成 |
| Survey Analyst | subagent | 问卷清洗与 codebook | `outputs/agent_runs/20260723_expanded_eligibility/survey/` | 完成并由主代理复核/重现 |
| Linked Case Agents（3） | 三个独立 subagent | 链接、档案、编号转录、问卷发现 | 受限角色目录 | 全部完成 |
| Qualitative Synthesis | subagent | 三个链接个案完成 | `outputs/agent_runs/20260723_expanded_eligibility/qualitative_synthesis/` | 完成并提升 84 条编码片段 |
| Mixed-Methods Integration | subagent | 问卷分析与质性综合完成 | `outputs/agent_runs/20260723_expanded_eligibility/mixed_methods/` | 完成并提升 9 个联合展示主题 |
| Evidence Reviewer | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/20260723_expanded_eligibility/reviews/evidence_audit.md` | 完成 |
| Privacy and Method Reviewer | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/20260723_expanded_eligibility/reviews/privacy_method_audit.md` | 完成 |

## 依赖与写入控制

- 个案 subagent 只在问卷清洗、链接、档案与转录准备后启动。
- 质性综合只在三个链接个案完成后启动；混合方法整合只在问卷和质性主文件完成后启动。
- 所有 worker 写入角色隔离目录；只有主代理提升 canonical master、修订报告并运行验证。
- 两名 reviewer 未参与初稿或上游分析，只提交审计意见，没有直接编辑初稿。
- 本环境支持 subagent，未使用串行 fallback。
