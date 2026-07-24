# 数据可用性与访问边界

## 随仓库提供

本仓库提供：

- 可复现的分析与验证脚本；
- 问卷和质性代码本；
- 汇总统计、机制命题与理论框架表；
- 五轮版本化报告、独立审查记录及最终研究报告；
- 去识别开放题代码本、独立回答者主题汇总和公开综合报告；
- 文献证据索引和参考文献。

这些文件已通过最终公开层隐私检查。完整入口见
[`outputs/final/artifact_index.md`](outputs/final/artifact_index.md)。

## 不随仓库提供

以下文件包含直接或间接识别风险，不进入Git历史：

- 原始问卷工作簿及后台元数据；
- 原始访谈、逐行转写和逐字引语；
- 参与者级清洗问卷和构念得分；
- 问卷—访谈连接表、问卷序号和内部行ID；
- linked case profiles、参与者级编码和受限审查对照；
- 开放题原文语料、逐回答编码、开放—封闭逐项对照及三源逐行对照；
- 可能通过稀有背景组合识别个人的资料。

相关路径由`.gitignore`保护，包括`data/raw/`、`data/interview/`、
参与者级`data/processed/`文件、`outputs/agent_runs/`和
`outputs/qualitative/`。

## 受控访问

私有GitHub仓库不自动构成获批准的研究数据环境。对受限资料的访问须
在仓库之外处理，并满足以下条件：

1. 研究授权、课程或机构负责人及数据控制者允许该用途；
2. 明确访问者、用途、保存期限和销毁安排；
3. 使用获批准的加密存储和传输渠道；
4. 在共享前完成去标识和重识别风险审查；
5. 不把受限资料、密钥或解密凭据写入Git、Issue、Pull Request或
   GitHub Actions日志。

本仓库不承诺对外提供参与者级资料。协作者如需访问，应联系仓库所有者，
说明研究用途和所需字段，由数据控制者单独决定。

## 复现边界

仅克隆GitHub仓库可以审查代码、汇总证据和最终报告，但不能从头再生
涉及参与者级资料的完整流水线。获授权的本地环境可运行：

```bash
python3 scripts/verify_reproducibility.py
python3 scripts/validate_final_delivery.py
```

公开仓库完整性检查不读取任何受限资料：

```bash
python3 scripts/validate_github_repository.py
```
