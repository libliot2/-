# Agent 运行清单

运行 ID：`20260723_full_pipeline`

| 角色 | 执行方式 | 依赖完成后启动 | 独立输出 | 状态 |
|---|---|---|---|---|
| Main Agent | 主代理 | — | canonical processed data、master files、报告与 Git | 完成 |
| Survey Analyst | subagent | 问卷清洗与 codebook | `outputs/agent_runs/20260723_full_pipeline/survey/` | 完成并由主代理复核/重现 |
| Linked Case P01 | subagent | 链接、档案、编号转录、问卷发现 | `outputs/agent_runs/20260723_full_pipeline/P01/` | 完成 |
| Linked Case P02 | subagent | 链接、档案、编号转录、问卷发现 | `outputs/agent_runs/20260723_full_pipeline/P02/` | 完成 |
| 第三份访谈 | 规则性跳过 | 资格筛选 | 脱敏编号转录与排除说明 | 问卷记录不合资格，不作个案分析 |
| Qualitative Synthesis | subagent | 两个合资格个案完成 | `outputs/agent_runs/20260723_full_pipeline/qualitative_synthesis/` | 完成并通过 47 条引文核验 |
| Mixed-Methods Integration | subagent | 问卷分析与质性综合完成 | `outputs/agent_runs/20260723_full_pipeline/mixed_methods/` | 完成并提升 10 主题联合展示 |
| Reviewer A | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/20260723_full_pipeline/reviews/evidence_audit.md` | 完成 |
| Reviewer B | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/20260723_full_pipeline/reviews/privacy_method_audit.md` | 完成 |

## 依赖与写入控制

- 个案 subagent 只在问卷清洗、链接、档案与转录准备后启动。
- 质性综合只在两个合资格个案完成后启动；混合方法整合只在问卷和质性主文件完成后启动。
- 所有 worker 写入角色隔离目录；只有主代理提升 canonical master、修订报告并运行验证。
- 两名 reviewer 未参与初稿或上游分析，只提交审计意见，没有直接编辑初稿。
