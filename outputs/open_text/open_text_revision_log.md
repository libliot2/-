# 开放题第五轮审查处置记录

## 处置原则

主agent逐项读取两份独立review，回到受限语料、正式编码、封闭题上下文和编号访谈核验。只有能够由原回答或规范字段确认的问题才修改；reviewer没有直接改动canonical文件。下表的公共文本ID与公开代码一致，内部问卷序号、参与者代号和访谈行号不在本记录披露。

| 问题 | reviewer意见 | 核查结果 | 实际修改 | 证据与脚本 | 状态 |
|---|---|---|---|---|---|
| OTEA-001 | “混合6名”把持续并存与顺序反转合并 | 确认：OTC19为5名；另1名先有距离后转为进入 | 保留焦点方向16进入/4距离/6混合；新增OTC47并分报持续并存5、顺序反转1；更新主题表、登记册、矩阵、joint display、摘要和正文 | `open_text_coded_responses.csv`；`open_text_theme_summary.csv`；`resolve_open_text_review_v5.py` | resolved |
| OTEA-002 | 直接成员感代码有3条超出定义 | 确认：相关回答只有邀请、日常活动或舒服感，没有直接成员感用语 | 删除3条OTC45；直接成员感由21修订为18；所有公开报告同步 | OTC45代码定义；`q81_critical_incident_analysis.md` | resolved |
| OTEA-003 | 公开代码本例句绕过逐回答摘录状态，2条例句非连续子串 | 确认 | 新增`example_text_id`；代码本例句只从22条`VERBATIM_SAFE`正式摘录选择，无安全例句的5个代码留空 | `open_text_codebook.csv`；`resolve_open_text_review_v5.py` | resolved |
| OTEA-004 | 两项“常常”对“很少”可能漏判分歧 | 确认构念、初期时段和方向均对应 | 将OT-R04-Q81地方参照项及OT-R05-Q81语言/俚语项改为`DIVERGENCE`；加上既有OT-R13-Q81后共3项 | `open_closed_alignment.csv`；`open_closed_integration.md` | resolved |
| OTEA-005 | 报告中的5项成员感比较未全部进入正式alignment | 确认有4项只在上下文中核对 | 补入4条Q3.3成员感正式判断，逐条记录变量、回答、关系、替代解释和置信度；总判断数由89增至93 | `open_closed_alignment.csv`；`resolve_open_text_review_v5.py` | resolved |
| OTEA-006 | 公开joint display含受限个案代码 | 确认 | 全部替换为“一个/另一个链接个案”等非绑定表述；review报告中的具体代码亦作隐私遮盖 | `joint_display.csv`；公开隐私扫描 | resolved |
| OTEA-007 / OTM-02 | findings register把26名开放题作答者标成完整问卷样本 | 确认 | 新增并使用`survey open-text sub-sample`；只有F204同时保留35份封闭题和26份开放题两个范围 | `findings_register.csv`；`integrate_open_text_v5.py`；`validate_final_delivery.py` | resolved |
| OTEA-008 / OTM-01 | 正式文件仍是代理建议或待确认状态 | 确认 | 52条编码改为`MAIN_AGENT_VERIFIED`或`REVIEWER_RESOLVED`；93项开放—封闭及6项三源对照全部关闭主审状态；52条语料关闭待确认状态 | `resolve_open_text_review_v5.py`；`validate_open_text_v5.py` | resolved |
| OTEA-009 | 回答者ID正则错误，验证器漏查语义问题 | 确认公共回答者ID实际为`Rxx` | 修正正则；加入代码本例句、混合方向、直接成员感、review状态、证据层和关系分布阻断检查 | `validate_open_text_v5.py` | resolved |
| OTM-03 | Q8.2 joint display列出底层不存在的分歧 | 确认Q8.2为33扩展、8一致、2未覆盖、0分歧 | 删除Q8.2行的`DIVERGENCE`；验证器比较每题底层关系并集 | `joint_display.csv`；`integrate_open_text_v5.py` | resolved |
| OTM-04 | “两名独立编码者”可能被误解为人工双人编码 | 确认 | 正文、执行摘要、方法摘要和专题综合明确为两个隔离AI编码代理、一个AI综合代理及主agent/reviewer闭环；声明不是人工编码者间一致性估计 | `final_research_report.md`；`executive_summary.md` | resolved |
| OTM-05 | 受限推断字段含未限定定向措辞 | 确认review列举的字段 | 改为“同一叙述中相伴/并列/方向不能确定”，保留替代解释 | `open_text_coded_responses.csv`；`resolve_open_text_review_v5.py` | resolved |
| OTM-06 | 自动验证未覆盖主审、证据层和joint display并集 | 确认 | 新增阻断检查，并固定review后应为47码、47主题、93项对照及51/36/3/3分布 | `validate_open_text_v5.py` | resolved |
| OTM-07 | 三份专题文件仍称“草稿” | 确认 | 删除Q8.1、Q8.2及链接个案报告中的“草稿”状态 | 三份公开专题报告 | resolved |

## 处置后的规范数字

- 可分析开放回答：Q8.1 26条，Q8.2 26条，共52条；
- 正式代码：47个；
- 主题汇总：47行，每题分母26；
- Q8.1焦点方向：进入16、距离4、混合6；混合内持续并存5、顺序反转1；
- 直接成员感：18/26名Q8.1作答者主动表达；
- 开放—封闭对照：93项，其中扩展51、一致36、未覆盖3、严格分歧3；
- 三源对照：6项，其中扩展5、一致1；
- 公开代码本例句：42个代码有经批准逐字来源，5个代码因无安全摘录留空。

全部修订均保留原始代理建议于受限`outputs/agent_runs/`，没有覆盖v1—v3、此前最终整理成果或独立review原始结论。
