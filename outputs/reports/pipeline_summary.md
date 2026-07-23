# 流水线总结

## 总体状态

Stages 0–15 已按依赖顺序实际执行。扩展资格决定解决了旧版唯一不合资格访谈的范围问题，没有硬性阻塞。最终自动验证状态：**PASS**（48 项通过，0 项失败）。

## 阶段结果

| 阶段 | 结果 |
|---|---|
| 0 库存 | 研究设计、最终问卷、1 个 35×160 工作表、3 份 DOCX 访谈、冻结文献包均可读；访谈指南缺失并记录 |
| 1 原始资料 | 4 个来源文件建立 SHA-256 基线；全程校验未变 |
| 2 映射/codebook | 160 个导出字段全部进入 codebook；版本冲突和缺失导出列明确标记 |
| 3 清洗/资格 | 35 份全部保留；V2 合资格 35、排除 0；旧口径排除的 11 份明确重分类；特殊缺失保持分开 |
| 4 链接 | 3 个文件均唯一匹配且 V2 合资格；0 未解决、0 歧义、0 重复 |
| 5 问卷 | 描述统计、支持缺口、平台转变、开放题辅助扫描和 5 项探索性关联完成 |
| 6–7 档案/转录 | 3 个链接档案、3 份脱敏编号转录完成 |
| 8 个案 | 三个链接个案分别由独立 subagent 完成；公开交付对跨版本间接识别风险作最小化 |
| 9 质性综合 | 84 条编码片段、40 个 canonical codes、13 个框架主题；引文逐字核验 |
| 10 混合整合 | 9 个联合展示主题，覆盖四层证据及 expansion/divergence/silence |
| 11 文献 | 只用冻结规范文献包比较；区分直接、相邻和理论证据 |
| 12–14 报告/审查/修订 | 初稿、两项独立审查和审查后终稿完成 |
| 15 验证 | 原始资料、计数、链接、引文、隐私、主张和可复现性自动检查完成 |

## 明确警告和跳过

- 资格口径在 V1 分析、审查和结果可见后扩展；V1 的 24/35 与 V2 的 35/35 对照属于事后口径敏感性，不是资格组比较。
- 问卷粤语题时点措辞冲突；Q3.1 一项和后期微博列缺失，未重建。
- 少量共享网络与异常短作答时长只作质量标记，不据此排除。
- 三份访谈包括一份整理式记录和两份未经录音核对的机器转写；个案选择理由未记录。
- A1 与 A4 在 V2 样本中 BH-FDR q<0.05，仍仅是非概率、小样本、事后扩展口径下的探索性排序关联。
- 回归、因子分析、因果模型和不等价题项的伪前后变化分均跳过。
- 三个链接个案不能支持主题饱和、总体频率或统计代表性。
- 小格、开放题原话、受限问卷序号、身份键和原始未脱敏资料不进入公开输出。

## 自动执行与 Git

本次使用 Survey Analyst、三个 Linked Case Agent、Qualitative Synthesis Agent、Mixed-Methods Integration Agent 及两个独立 Reviewer subagent；主代理负责依赖控制、canonical 提升、审查修订、再生和验证，没有使用串行 fallback。

Git 由主代理自动管理。原始问卷、原始访谈、参与者级 processed/qualitative 产物及独立 Overleaf 仓库均不进入公开历史；受限产物只保留在本地工作区供授权审计和再现。`analysis-v1` 保持不变，V2 完成交付使用 annotated tag `analysis-v2`。

```text
f1250c2 (HEAD -> main, tag: analysis-v1) chore: validate and finalise analysis pipeline
64971e3 docs: add independently reviewed final report
cc3ea0e analysis: add reproducible mixed-methods pipeline
9faee95 chore: initialise public-safe research repository
```
