# 开放题方法与整合独立审查

## 审查范围与结论

本审查独立核对第五轮计划与共享架构、52条正式开放题编码、46个正式代码、45行主题汇总、89项开放—封闭题判断、6项开放题—封闭题—访谈三源判断，以及修订后的 `findings_register.csv`、证据矩阵、joint display、最终报告和执行摘要。未读取另一名 reviewer 的报告，也未修改任何 canonical 文件。

总体裁决：**有条件通过，须在最终验证前完成方法一致性修订。** 公开报告对主动提及、未回答、支持建议、数字平台和文化中介的解释总体克制；主要问题不在主题结论本身，而在主审状态尚未闭合、开放题证据层在登记表中标错、joint display 多列出一个不存在的分歧类型，以及自动验证尚未覆盖这些状态。

严重度定义：`HIGH` 表示若不修复会使正式交付对分析状态或证据范围产生实质误导；`MODERATE` 表示不改变主要主题人数，但会削弱方法透明度或推断纪律；`LOW` 表示交付状态或表述不一致。

## 问题与修改建议

### OTM-01 — canonical 整合表仍是代理建议状态，却被公开报告描述为已经过主流程复核

- **严重度：HIGH**
- **证据：**
  - `outputs/open_text/open_closed_alignment.csv` 的89行 `review_status` 全部为 `AGENT_PROPOSED`。
  - `outputs/open_text/open_text_interview_alignment.csv` 的6行 `review_status` 全部为 `AGENT_PROPOSED`。
  - `outputs/open_text/open_text_coded_responses.csv` 的52行仅标为 `SYNTHESIS_ADJUDICATED`，没有主 agent 核验状态。
  - 与此相对，`outputs/reports/open_closed_integration.md:56` 写明关系类型“已经过主流程的结构、原回答和严格分歧条件复核”，最终报告也把这些文件当作正式证据层。
- **影响：** 当前文件可以证明代理已经提出并协调判断，却不能从状态字段证明主 agent 已逐项核验。公开方法叙述比 canonical 状态超前。
- **建议：**
  1. 主 agent 对52条正式编码、89项开放—封闭判断和6项三源判断完成实质抽查或逐项核验；
  2. 只对已核验行改为明确状态，例如 `MAIN_AGENT_VERIFIED`；经 reviewer 修订的行可用 `REVIEWER_RESOLVED`；
  3. 若未完成核验，则公开报告必须改称“代理提出／综合裁决”，不能称“主流程已复核”；
  4. 验证脚本应拒绝最终文件仍含 `AGENT_PROPOSED` 或只有 `SYNTHESIS_ADJUDICATED`。

### OTM-02 — findings register 把26名开放题自选作答者误标为 complete survey sample

- **严重度：HIGH**
- **证据：**
  - `outputs/final/findings_register.csv` 中 F105、F110、F204、F211、F402、F404 的 `evidence_scope` 使用了 `complete survey sample`，但相应开放题证据只来自Q8.1或Q8.2各26名自选作答者。
  - `scripts/integrate_open_text_v5.py:103`、`:124` 和 `:145` 将该错误写入可复现生成逻辑。
  - 最终报告第11节正确区分了35份封闭题、两题各26名开放题、3份访谈和文献四层，因此登记表与正文互相矛盾。
- **影响：** 即使 finding statement 内写有“26名作答者”，`evidence_scope` 仍会把自选开放题子样本错误提升为完整问卷样本层，违反本轮将开放题设为独立证据层的目标。
- **建议：**
  1. 在登记表允许值中新增并统一使用 `open-text respondent sub-sample`；
  2. F110、F211、F402改为该层；F105按实际证据改为 `open-text respondent sub-sample; within-case linked evidence; cross-case interpretation`；
  3. F204区分 `complete survey sample; open-text respondent sub-sample; within-case linked evidence`；
  4. F404改为 `open-text respondent sub-sample; within-case linked evidence`；
  5. 同步修改生成脚本，并在验证中禁止只有26名开放题证据的结论标为 `complete survey sample`。

### OTM-03 — joint display 为Q8.2支持期待列出了并不存在的 DIVERGENCE

- **严重度：HIGH**
- **证据：**
  - `outputs/reports/open_closed_integration.md:12-14` 和正式CSV一致显示Q8.2为8项 `CONVERGENCE`、33项 `EXPANSION`、2项 `SILENCE`、0项 `DIVERGENCE`。
  - 三源表中Q8.2的3项也全为 `EXPANSION`，没有分歧。
  - 但 `outputs/tables/joint_display.csv` 的“开放题支持期待—封闭题支持状态”行写成 `EXPANSION; DIVERGENCE; CONVERGENCE; SILENCE`；该错误来自 `scripts/integrate_open_text_v5.py:219`。
  - 最终报告第11节又正确写明开放—封闭题唯一严格分歧属于Q8.1。
- **影响：** joint display 凭空增加了一个Q8.2分歧类别，削弱严格分歧标准和表间一致性。
- **建议：** 将该行改为 `EXPANSION; CONVERGENCE; SILENCE`，同步修改生成脚本；自动验证应按题目比较 joint display 所列关系类型与两份底层 alignment 的实际并集。

### OTM-04 — “两名独立编码者”未说明是相互隔离的AI代理，可能被误读为人工双人编码

- **严重度：MODERATE**
- **证据：**
  - `outputs/final/final_research_report.md:33`、`outputs/final/executive_summary.md:5` 和 `outputs/final/methods_and_audit_summary.md:20` 均使用“两名独立编码者”。
  - 审计摘要第22—28行另行提到 subagent，但主体方法段和摘要没有明确说明第五轮的两条编码路径、综合与初始整合均由AI代理执行。
- **影响：** 读者可能把该安排理解为两名独立人工研究者编码，进而误认为具有人际编码一致性证据。当前设计是两条相互隔离的AI分析路径加综合与主审，不等同人工双人编码，也没有报告人工编码一致性或成员核查。
- **建议：** 在最终报告和摘要首次出现处明确写为“两个相互隔离、互不读取对方结果的AI编码代理”，并说明第三个AI综合代理提出协调结果、主 agent 负责正式裁决、独立 reviewer 只审查不直接改稿；明确这是一种审计与反例搜索安排，不是人工 inter-coder reliability 估计。

### OTM-05 — 受限逐回答文件的“理论解释／研究者推断”仍有未限定的因果措辞

- **严重度：MODERATE**
- **证据：**
  - `OT-R03-Q81` 的 `theoretical_interpretation` 写“同伴支架把课堂参与机会接续为线上和线下关系”。
  - `OT-R01-Q81`、`OT-R03-Q81`、`OT-R13-Q81`、`OT-R15-Q81` 的 `researcher_inference` 分别使用“帮助……获得接纳”“使一次任务连接”“把个人技能转成……并连接”“关系结构造成”等定向语言。
  - 公开报告已经把这些内容弱化为“可能接续”“事件结构”或“不能验证因果链”，说明主要报告结论没有被这些措辞带偏。
- **影响：** 尽管字段明确标为研究者推断，AGENTS.md 的非因果语言规则仍适用于分析产物；这些句子也可能在后续复用时被误当成已识别机制。
- **建议：** 改为“在该叙述中与……相伴”“可能构成接续条件”“参与者将……理解为”等非定向表达；保留替代解释，不把共同任务或同伴行动写成已证明的结果原因。

### OTM-06 — 自动验证未检查主审闭环、证据层级和joint display关系并集

- **严重度：MODERATE**
- **证据：**
  - `scripts/validate_open_text_v5.py:289-333` 只检查alignment的架构、覆盖、关系枚举、置信度和访谈锚点，没有核查 `review_status`。
  - `scripts/validate_open_text_v5.py:357-364` 的谨慎语言检查只要求几个关键词存在，无法捕捉 F110/F211 的错误 `evidence_scope`。
  - 脚本没有将 joint display 的关系类型与正式alignment实际并集比较，因此 OTM-03 可以在结构验证中漏过。
- **影响：** 当前验证即使显示PASS，也不能证明本审查发现的三项核心一致性问题已解决。
- **建议：** 为三项问题增加阻断检查：全部正式语义与整合行须有主审完成状态；开放题专属finding不得标为完整样本；joint display关系类型必须等于其来源表实际出现类型。修订后再生成验证报告。

### OTM-07 — 两份正式专题文件仍标为“草稿”

- **严重度：LOW**
- **证据：**
  - `outputs/open_text/q81_critical_incident_analysis.md:1` 为“Q8.1 关键事件分析草稿”；
  - `outputs/open_text/q82_support_needs_analysis.md:1` 为“Q8.2 支持需求分析草稿”；
  - `outputs/reports/open_text_linked_case_analysis.md` 的资料范围仍称“本公开草稿”。
- **影响：** 文件已被 findings register 和最终报告作为正式证据引用，标题状态与用途不一致。
- **建议：** 完成review处置后删除“草稿”字样，不需改文件路径。

## 通过项

以下项目在本轮材料中通过：

1. **主动提及与经历率区分清楚。** 所有主要人数在专题报告、综合报告、最终报告和摘要中均限定为26名本题作答者中的主动提及；没有把关键词命中当成主题频率。
2. **未回答与未提及没有被当成经验不存在。** 两题各9份空白／无实质内容被保留为资料状态，且公开报告多次说明沉默不是否定。
3. **开放题深度没有被高估。** 报告明确说明开放题比封闭题多事件信息、比访谈短且缺少追问，同一人的三源证据也没有重复计作独立案例。
4. **支持建议与个人缺口大体区分正确。** Q8.2与Q5.5的命题差异得到说明；“已获得且有效”“已获得但有限”“未获得但希望获得”“没有获得也不需要”没有被合并。底层89项判断中，个人“不需要”与群体建议被保留为 `EXPANSION` 而非假分歧。
5. **底层DIVERGENCE标准执行严格。** 89项中只有 `OT-R13-Q81` 同时满足同构念、重叠时段和相反方向；特殊回答、限选未勾选、时段不重合及支持建议均未被误判为分歧。问题仅在 OTM-03 的joint display汇总标签。
6. **四层证据角色在正文中清楚。** 最终报告明确区分35份封闭题、两题各26名开放题、3份链接访谈和文献背景；没有把三份访谈当成完整样本代表。登记表的字段错误见 OTM-02。
7. **joint display和最终报告确有实质修订。** 新增了开放题关键事件、支持期待和数字材料三行，最终报告分别在RQ1、RQ2、RQ3及混合方法整合部分使用开放题，而非仅在附录提及。
8. **文化本质主义受到有效限制。** 报告保留一般新生陌生、班级网络、任务结构、兴趣、个性、学校安排和家庭资源等竞争解释，没有把所有距离归因于“内地—香港文化差异”。
9. **数字平台与文化中介没有被过推。** 平台材料只解释为关系延伸或信息接口；极少主动提及没有被解释为平台无作用。开放题无直接文化中介行为只被用于限制稳定角色结论，没有把沉默当作行为不存在。
10. **摘要与正文主要数字一致。** 两题各26名、共52条、46个代码；Q8.1的16/4/6、15、14、11；Q8.2的12、12、11、8；89项对照的47/38/3/1，以及6项三源对照的1/5均能在底层文件中复现。

## 最终建议

上述问题不表明核心资料损坏，也不要求重做编码。主 agent 应优先关闭 OTM-01、OTM-02 和 OTM-03，再处理透明度、因果措辞和验证覆盖；完成后，本轮方法与整合部分可以通过最终验证。
