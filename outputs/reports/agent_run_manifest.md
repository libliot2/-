# Agent 运行清单

## 第二轮：独立复核与补充探索

运行 ID：`20260723_independent_review_extension_v2`

| 角色 | 执行方式 | 独立输出 | 是否修改 canonical |
|---|---|---|---|
| Reviewer A：量化与数据 | 独立 subagent | 受限 `reviewer_A/audit.md`；公开 `quantitative_audit_v2.md` | 否 |
| Reviewer B：质性证据 | 独立 subagent | 受限 `reviewer_B/audit.md`；公开 `qualitative_audit_v2.md` | 否 |
| Reviewer C：混合方法 | 独立 subagent | 受限 `reviewer_C/audit.md`；公开 `integration_audit_v2.md` | 否 |
| Reviewer D：隐私与复现 | 主agent独立审查角色 | 受限 `reviewer_D/audit.md`；公开 `reproducibility_privacy_audit_v2.md` | 否 |
| Main Agent | 主代理 | 修订脚本、表格、报告、验证与Git | 是 |

三位 subagent 并行完成 A/B/C；主agent同期只完成 D 的独立审查，待四份审查均封闭后才实施补充探索和 canonical 修订。未使用串行 fallback。完整第一轮角色清单保存在 `analysis-v2`。
