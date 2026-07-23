# Reviewer D：隐私与可复现性复核（公开安全版）

判定：**PASS_WITH_ISSUES**；无 blocker。原始来源 4/4 哈希一致；旧版 26/26 字节复现与 48/48 验证通过，但审查发现验证假阴性。

| issue_id | severity | 问题与证据 | 修改建议 |
|---|---|---|---|
| RP-001 | MAJOR | 旧 final 已最小化受限第三案例，但 cross-case、integration、draft 和 joint display 仍可形成跨版本连接。 | 完整证据留受限层；当前公开衍生版不含受限案例代号、行号和背景组合。 |
| RP-002 | MAJOR | 若干旧报告公开稀有质量、资格或资料形式小格。 | 新版统一概括为“少量”或“资料形式不一”；精确小格只留受限层。 |
| RP-003 | MAJOR | 旧隐私验证正则和扫描清单不足。 | 新增明确 public allowlist、跨版本连接和小格检查。 |
| RP-004 | MINOR | 旧 pipeline summary 的 Git 日志早于实际分析 v2 终点。 | 新 summary 实时记录本轮起点、交付和下一标签。 |
| RP-005 | MAJOR | “可复现”未区分计算再生与冻结解释性判断提升，且遗漏部分目标。 | 扩充目标并标注 `REGENERATED` / `FROZEN_ANALYTIC_INPUT_PROMOTED`。 |
| RP-006 | MINOR | 第二轮交付尚未进入 Git allowlist。 | 更新 `.gitignore` 与 Git 隐私验证，只追踪公开安全产物。 |

旧版报告保存在原 Git tag 和本轮受限归档；第二轮公开交付不复述受限小格。
