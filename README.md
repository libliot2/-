# 内地—香港学校插班经历者的学校适应、同伴关系与数字生活

本仓库保存一项本科课程层级的探索性链接混合方法研究。项目分析具有内地—香港学校插班经历者的同伴边界、学校归属、教育制度适应和数字平台实践，并通过三轮分析、独立复核及最终版本协调形成可审计的研究成果。

> **最终版本：** `analysis-final`<br>
> **最终验证：** 18/18 项通过；完整本地再生检查 81/81 项通过<br>
> **数据边界：** 原始问卷、访谈、逐行转写和问卷—访谈连接表不提交 Git

## 合作者快速导航

`analysis-final`是当前规范结论，但仓库同时保留了研究设计、早期版本、独立审查、理论扩展和可复现脚本。可按目的选择入口：

| 想了解的内容 | 建议先读 | 继续追踪 |
|---|---|---|
| 5分钟掌握研究 | [一页式发现摘要](outputs/final/key_findings_one_page.md) | [执行摘要](outputs/final/executive_summary.md) |
| 完整研究结论 | [最终研究报告](outputs/final/final_research_report.md) | [研究问题—证据矩阵](outputs/final/research_question_evidence_matrix.csv) |
| 样本、资格口径和方法 | [研究设计](docs/research_design.md) | [分析决定](notes/analysis_decisions.md)、[方法与审计摘要](outputs/final/methods_and_audit_summary.md) |
| 结论如何跨版本变化 | [版本协调](outputs/final/version_reconciliation.md) | [最终结论登记册](outputs/final/findings_register.csv) |
| 第二轮独立复核 | [v2修订记录](outputs/reports/revision_log_v2.md) | [量化审查](outputs/reviews/quantitative_audit_v2.md)、[质性审查](outputs/reviews/qualitative_audit_v2.md)、[整合审查](outputs/reviews/integration_audit_v2.md) |
| 第三轮理论再分析 | [理论扩展报告](outputs/reports/theoretical_extension_report_v3.md) | [跨框架综合](outputs/reports/cross_framework_synthesis_v3.md)、[机制命题](outputs/tables/mechanism_propositions_v3.csv) |
| 文献依据 | [文献综述](docs/literature_context/literature_review.md) | [证据索引](docs/literature_context/evidence_index.csv)、[参考文献](docs/literature_context/references.bib) |
| 隐私、复现与质量保证 | [最终验证](outputs/final/final_validation_report.md) | [隐私与复现审查](outputs/reviews/reproducibility_privacy_audit_v2.md)、[最终证据审查](outputs/final/final_evidence_audit.md) |
| 继续运行或修改分析 | [分析流水线](docs/analysis_pipeline.md) | [数据契约](docs/data_contract.md)、`scripts/` |

## 研究问题

1. **同伴边界、归属与文化中介：** 学生如何进入并协商香港学校中的同伴关系？边界事件、成员感、身份表达和具体文化解释行动如何并存？
2. **教育制度适应与学生身份：** 学生如何识别课堂、任务、评价与未明说规则？这些经验如何关联其能力判断和“好学生”标准？
3. **数字平台与关系实践：** 新旧平台如何承担旧关系维系、学校信息、同伴互动和表达功能？平台能够解释什么、不能解释什么？

## 数据与研究设计

- 35 份有效问卷，最终扩展资格口径下排除 0 份；
- 旧口径中的 11 份被重新分类为有效，而非数据质量不合格；
- 3 份访谈与问卷记录唯一链接；
- 84 条规范质性编码片段；
- 75 条问卷—访谈对照，包括：
  - 34 条扩展；
  - 21 条一致；
  - 11 条未覆盖；
  - 9 条分歧。

问卷描述完整样本；三份访谈只用于解释链接个案、矛盾和可能机制，不代表完整样本或总体。研究为非概率、回顾性、横截面设计，不支持因果推断。

详细方法见：

- [研究设计](docs/research_design.md)
- [分析流水线](docs/analysis_pipeline.md)
- [数据契约](docs/data_contract.md)
- [最终方法与审计摘要](outputs/final/methods_and_audit_summary.md)

## 证据层次与结论状态

本项目刻意区分五种证据范围，避免把三份访谈推广到35份问卷或把文献当作参与者资料：

| 证据范围 | 可以回答 | 不能回答 |
|---|---|---|
| 完整问卷样本 | 当前35份问卷中的分布、分母和探索性关联 | 香港所有插班生的总体情况 |
| 访谈子样本 | 三份访谈覆盖了哪些经验 | 主题饱和或总体频率 |
| 个案内链接 | 同一人的问卷与访谈如何一致、扩展或分歧 | 哪一种资料源必然“更真实” |
| 跨个案解释 | 三案有哪些共同分析边界、差异和反例 | 固定适应类型或共同因果路径 |
| 文献解释 | 当前发现与既有研究如何相容、扩展或冲突 | 替代本项目的问卷和访谈证据 |

最终结论另分为：

- **A — Core findings：** 经复核后仍有直接支持，可进入摘要与结论；
- **B — Qualified findings：** 有支持，但必须限定样本、时段或题意；
- **C — Exploratory interpretations：** 依赖理论框架或少量个案，只进入讨论；
- **D — Unsupported or rejected claims：** 不进入最终主体，只保留在审计记录。

逐条分级见[证据层级](outputs/final/evidence_hierarchy.md)和[最终结论登记册](outputs/final/findings_register.csv)。

## 核心发现

1. **同伴边界不等于整体低归属。** 插班初期，本地知识障碍为 14/35，语言或幽默障碍为 5/31，参与退缩为 11/33；香港校内后期成员感为 30/33，复合信任谈心题为 35/35。
2. **任务困难不等于能力不足。** 初期较常见困难包括小组项目 23/34、繁体字 23/32、粤语课堂 22/34、混合评价 22/35、口头汇报 18/33和答题格式 16/34。
3. **规则理解与任务困难可以并存。** 香港校内后期 32/34 认同理解评价方式，30/34 认同能够区分规则不熟悉与能力不足；初期和后期题项不是等值前后测。
4. **获得支持不等于支持充分。** “帮助较大”“帮助有限”和“未获得但希望获得”是不同状态，不能合并为是否获得支持。
5. **平台变化更接近并存与功能分工。** 微信有 26/35 保留、6/35 停止；WhatsApp 有 26/35 后期采用，Instagram 有 22/35 后期采用。
6. **平台和文化中介均有明确解释边界。** 平台选择不能代理文化认同或本地同伴圈进入；少量具体解释行动也不能证明稳定的文化中介身份。

完整证据及限定条件见：

- [最终研究报告](outputs/final/final_research_report.md)
- [执行摘要](outputs/final/executive_summary.md)
- [一页式发现摘要](outputs/final/key_findings_one_page.md)
- [研究问题—证据矩阵](outputs/final/research_question_evidence_matrix.csv)
- [证据层级](outputs/final/evidence_hierarchy.md)

## 最终分析框架

项目最终采用四组最小概念：

1. 制度接口与学术社会化；
2. 同伴边界与关系机会；
3. 关系功能与支持可用性；
4. 任务经验、规则理解、成员感和关系层次等多维结果。

数字平台被视为关系和信息通道；时间、学校安排、家庭资源、费用、个性与既有关系作为竞争解释。该框架用于组织资料和提出后续问题，不是已验证的因果模型。

详见[最终分析框架](outputs/final/final_analytical_framework.md)。

## 仓库结构

```text
.
├── docs/                    # 研究设计、数据契约、流水线和文献背景
├── research_materials/      # 问卷研究材料
├── scripts/                 # 清洗、分析、报告生成与验证脚本
├── .github/                 # GitHub Actions与依赖更新配置
├── data/
│   ├── raw/                 # 受限原始问卷，本地保留，不进入 Git
│   ├── interview/           # 受限原始访谈，本地保留，不进入 Git
│   └── processed/           # 公开代码本及受限参与者级派生资料
├── outputs/
│   ├── final/               # 当前应优先阅读的最终交付
│   ├── reports/             # v1—v3 报告、修订及流水线记录
│   ├── reviews/             # 独立审查记录
│   ├── tables/              # 获准提交的汇总/探索表格
│   └── theory/              # 第三轮理论框架比较
└── notes/                   # 分析决定及口径变更记录
```

完整文件说明见[成果文件索引](outputs/final/artifact_index.md)。

## 分析与脚本工作流

```text
原始问卷
  └─ prepare_data.py → analyze_survey.py
       └─ 完整样本描述与探索性统计

原始访谈
  └─ prepare_interviews.py → build_linked_profiles.py
       └─ promote_qualitative_synthesis.py

问卷 + 链接个案
  └─ promote_mixed_methods.py
       ├─ revise_qualitative_v2.py
       ├─ exploratory_extension_v2.py
       └─ explore_theory_configurations_v3.py

版本化成果
  └─ 报告生成脚本 → promote_final_delivery.py
       └─ validate_final_delivery.py → verify_reproducibility.py
```

脚本按功能分组：

| 功能 | 主要脚本 | 产物 |
|---|---|---|
| 问卷映射与清洗 | `prepare_data.py` | 处理后问卷、代码本、样本流和质量标记 |
| 问卷分析 | `analyze_survey.py` | 描述统计、缺失、构念和探索性关联 |
| 访谈准备与链接 | `prepare_interviews.py`、`build_linked_profiles.py` | 编号访谈、唯一映射和linked case profiles |
| 质性与混合方法提升 | `promote_qualitative_synthesis.py`、`promote_mixed_methods.py` | 规范编码、框架矩阵和joint display |
| 第二轮复核扩展 | `revise_qualitative_v2.py`、`exploratory_extension_v2.py` | 修订后的对照、支持缺口、平台转换和稳健性结果 |
| 第三轮理论探索 | `explore_theory_configurations_v3.py` | 异常配置、提示语审计和理论综合输入 |
| 最终晋升与验证 | `promote_final_delivery.py`、`validate_final_delivery.py`、`verify_reproducibility.py` | 规范报告、最终验证和逐字节再生检查 |

`scripts/agent_runs/`中的文件是早期代理运行留档，不是当前优先入口；新修改应使用根级规范脚本。

## 合作者工作约定

开始修改前请依次阅读：

1. [AGENTS.md](AGENTS.md)；
2. [研究设计](docs/research_design.md)；
3. [分析流水线](docs/analysis_pipeline.md)；
4. [数据契约](docs/data_contract.md)；
5. [最新分析决定](notes/analysis_decisions.md)。

核心约定：

- 不修改`data/raw/`和`data/interview/`中的源文件；
- 不猜测问卷—访谈映射，不在公开文件暴露连接键或逐行证据；
- 完整问卷、访谈子样本、个案内证据、跨案解释和文献背景必须分层；
- 所有数字回到生成表，所有质性主张回到受限行段；
- 不把回顾性横截面资料写成因果或总体结论；
- 新产物分别放入`data/processed/`、`scripts/`和`outputs/`；
- 修改规范报告前先处理相关审查意见，提交前运行相应验证并确认源资料未变。

## 环境与依赖

本轮最终验证使用：

- Python 3.12.9
- pandas 3.0.3
- NumPy 2.1.3
- SciPy 1.17.1
- openpyxl 3.1.5
- python-docx 1.2.0

可在本地创建隔离环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 复现与验证

### 仅克隆 GitHub 仓库

GitHub 版本包含代码、规范、公开安全表格和经审查报告，但不包含原始及参与者级资料。因此，仅凭仓库克隆不能从头重新生成全部分析，也不应把缺少受限资料误报为复现失败。

可以进行脚本语法检查：

```bash
python -m compileall -q scripts
python3 scripts/validate_github_repository.py
```

### 获授权的完整本地环境

完整再生要求本地同时存在：

- `data/raw/`中的一份原始问卷工作簿；
- `data/interview/`中的三份原始访谈；
- 被 `.gitignore` 排除的参与者级处理资料及受限审计文件。

运行：

```bash
python3 scripts/verify_reproducibility.py
python3 scripts/validate_final_delivery.py
```

最终封版时的结果为：

```text
final validation checks=18 result=PASS
reproducibility checked=81 failures=0
```

## 数据隐私与可用性

本项目涉及人类参与者资料。下列内容不会随 Git 仓库分发：

- 原始问卷工作簿及其后台元数据；
- 原始访谈文件和逐行转写；
- 问卷序号、问卷—访谈连接表及内部行 ID；
- 参与者级清洗数据、linked case profiles和逐字证据对照；
- 可能通过稀有背景组合间接识别个人的文件。

私有 GitHub 仓库也不自动构成适合存放这些资料的受控研究数据环境。任何后续共享必须先确认研究授权、访问范围、存储条件与去标识要求，并通过独立隐私审查。当前 `.gitignore` 是数据保护边界的一部分，不应为方便推送而删除相关规则。

完整政策见[数据可用性与访问边界](DATA_AVAILABILITY.md)。

## 分析演变与版本历史

Git标签记录执行批次，报告文件中的`v2`、`v3`记录报告修订代次，两者用途不同：

| Tag | 分析阶段 | 主要变化 | 阅读入口 |
|---|---|---|---|
| `analysis-v1` | 基础端到端分析 | 使用早期较严格资格口径，完成首轮问卷和链接个案分析 | Git历史基线 |
| `analysis-v2` | 扩展资格口径 | 将跨境上学、较低年级插班和无法确认内地连续就读年限者纳入，最终35/35有效 | [流水线总结](outputs/reports/pipeline_summary.md) |
| `analysis-v3` | 独立复核与补充探索 | 修正多选限额、复合题、问卷—访谈裁决、公开隐私和探索性分级 | [v2报告](outputs/reports/final_report_v2.md)、[v2总结](outputs/reports/pipeline_summary_v2.md) |
| `analysis-v4` | 多理论与开放式再分析 | 比较多个理论框架，加入竞争解释、异常组合和机制命题 | [v3报告](outputs/reports/final_report_v3.md)、[v3总结](outputs/reports/pipeline_summary_v3.md) |
| `analysis-final` | 项目总梳理 | 调和全部版本，筛选A/B/C/D级结论，形成课程研究最终交付 | [最终报告](outputs/final/final_research_report.md)、[项目总结](outputs/final/final_project_summary.md) |

重要变化的逐条依据见[v2修订记录](outputs/reports/revision_log_v2.md)、[v3理论修订记录](outputs/reports/theoretical_revision_log_v3.md)和[最终审查处置](outputs/final/final_review_resolution.md)。

## 主要局限

- 资格口径在第一版结果可见后扩展，增加了分析自由度；
- 35 份问卷为非概率小样本，三份访谈选择理由未知；
- 初期、香港校内后期和当前回顾不是等值纵向测量；
- 自编探索指标不是经过验证的标准量表；
- 多选限额、缺失导出列和访谈提纲缺失限制部分解释；
- 当前设计不能识别因果、学校效果或总体代表性。

## 引用

建议引用当前最终版本：

> 内地—香港学校插班经历研究项目（2026）。《内地—香港学校插班经历者的学校适应、同伴关系与数字生活》。Git tag: `analysis-final`。

GitHub可通过[`CITATION.cff`](CITATION.cff)读取机器可读引用信息。

## 许可

- `scripts/`中的原创代码按[MIT License](LICENSE-MIT)授权；
- 原创文档、报告、表格和问卷材料按
  [Creative Commons Attribution 4.0 International](LICENSE-CC-BY-4.0)
  授权；
- 第三方文献、引语和引用材料保留各自权利；
- 受限参与者资料不随任何仓库许可证授权或分发。

完整双许可证说明见[`LICENSE`](LICENSE)。协作和安全报告方式分别见
[`CONTRIBUTING.md`](CONTRIBUTING.md)与[`SECURITY.md`](SECURITY.md)。
