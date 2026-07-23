# 第二轮修订日志

| issue/claim | 原结论或问题 | reviewer核查 | 实际修改 | 证据/脚本 | 最终状态 |
|---|---|---|---|---|---|
| QA-001 | 限选题按设计上限解释 | 8/14/9份超限 | 新增逐题质量标记、endorsement与合规子集 | `prepare_data.py; exploratory_extension_v2.csv` | revised |
| QA-002 | Q5.4普通选项分母35 | 题组特殊回答未传播 | 分母改为34，计数23/19不变 | `analyze_survey.py; exploratory_extension_v2.csv` | revised |
| QA-003 | 未检查Q5.3互斥组合 | 存在少量冲突 | 保留原值并标记；不猜测 | `prepare_data.py; data_quality_report.md` | revised |
| QA-004 | 开放题泛词主题频率 | 同学/主动造成误标 | 降为关键词索引，删除机制频率措辞 | `analyze_survey.py; survey_open_text_summary.csv` | revised |
| QA-005 | A4与A1并列主要信号 | 替代参与编码不稳 | A4降为weak signal，仅留限制 | `exploratory_extension_v2.py; association_robustness_v2.csv` | revised |
| QA-006 | codebook母题与项目相同 | 160行语义层未分 | 补入canonical母题、保留source_column | `prepare_data.py; survey_codebook.csv` | revised |
| QA-007 | 构念报告写n_scored | 实际字段scored_n | 修正字段名 | `analyze_survey.py; construct_assessment.md` | revised |
| QA-008 | 旧量化validation覆盖窄 | 关键问题在全PASS下存在 | 新增限选、分母、互斥、替代规格检查 | `validate_round2.py` | revised |
| QL-001 | 少量受限片段截断 | 机器断句下一行补完意义 | 扩展行范围并重验逐字 | `revise_qualitative_v2.py; coded_segments_master_v2.csv` | revised |
| QL-002 | 少数primary code不符定义 | 正式课程、自信、建议、幸运归因误码 | 重编码并检查未知码为零 | `revise_qualitative_v2.py` | revised |
| QL-003/MM-002 | 部分假divergence/convergence | 内容域/时段/限选不可比 | 75条三条件全量裁决；最终DIVERGENCE=9 | `alignment_adjudication_v2.csv` | revised |
| QL-004 | 压缩释义放入引号 | 报告文本非逐字 | 公开报告只保留明确释义 | `write_round2_reports.py` | revised |
| QL-005 | 三案共同任务—关系机制 | 完整事件链只由单案直接支持 | 降为单案依赖的探索性配置 | `leave_one_case_out_themes_v2.csv` | revised |
| QL-006 | 自动验证冒充语义复核 | 旧脚本只能机械查引语 | v2报告分开机械与人工语义检查 | `validate_round2.py` | revised |
| QL-007 | 候选码似已全部应用 | 多数PROPOSED未回填 | 已用渐进码转ACTIVE，其余明确候选 | `qualitative_codebook.csv` | revised |
| MM-001 | 可信任题被拆义 | 原题是信任并谈心复合陈述 | 恢复完整标签，P01保留直接分歧 | `final_report_v2.md; joint_display.csv` | revised |
| MM-003 | joint display宽主题单标签 | 正文与表关系类型不一致 | 按主题×关系类型重建 | `write_round2_reports.py; joint_display.csv` | revised |
| MM-004 | 形成/支撑等隐性生成措辞 | 超出回顾性横断设计 | 改为回顾性配置并存 | `final_report_v2.md` | revised |
| MM-005 | 人物绑定三条路径 | 任一案例移除即丢失一路 | 改为配置矩阵并做leave-one-case-out | `case_configuration_matrix_v2.csv` | revised |
| RP-001 | 其他报告仍连接受限案例 | 旧final之外路径未切断 | 完整证据受限；公开衍生版去连接键 | `write_round2_reports.py` | revised |
| RP-002 | 公开稀有质量小格 | 旧报告精确披露 | 新版概括为少量/资料形式不一 | `final_report_v2.md; validation_report_v2.md` | revised |
| RP-003 | 隐私验证假阴性 | 旧48项全PASS仍漏问题 | 新增明确allowlist与跨版本检查 | `validate_round2.py` | revised |
| RP-004 | 旧summary Git状态滞后 | 记录早于tag终点 | v2 summary记录本轮起点和analysis-v3 | `pipeline_summary_v2.md` | revised |
| RP-005 | 复现边界未分层 | 冻结解释判断被写成算法再生 | 新增target_mode并扩充目标 | `verify_reproducibility.py` | revised |
| RP-006 | v2交付未入Git allowlist | 默认ignore | 只放行公开安全第二轮交付 | `.gitignore; validate_round2.py` | revised |
| EXT-001 | 仅有平台边际变化 | 同一回答者可配对 | 新增retained/adopted/stopped/neither | `exploratory_extension_v2.csv` | added |
| EXT-002 | 只报告未满足支持 | Q5.5可比较三状态 | 新增帮助较大/有限/未满足对照 | `exploratory_extension_v2.csv` | added |
| EXT-003 | 未系统定位访谈案例 | 构念位置可计算 | 三案受限精确定位；公开只给宽位置 | `linked_case_position_v2.csv` | added |
| EXT-004 | A1稳健性未给 | 四规格及LOO方向一致 | 升级为plausible exploratory，不作因果 | `association_robustness_v2.csv` | added |
| DEL-001 | A4一般文化中介结论 | 合理替代编码不稳 | 从主体发现删除 | `final_report_v2.md` | removed |
| DEL-002 | 平台采用代表融入/身份 | 问卷和访谈均不支持 | 删除，不进入发现表 | `exploratory_extension_v2.md` | removed |

## 第一版结论处置总览

- retained：35/35 合资格、0 排除、旧口径 11 份重分类；三份访谈唯一链接；主要矩阵描述；非代表性、回顾性和非因果边界。
- revised：复合信任谈心题、Q5.4 分母与限选含义、开放题索引、joint display、divergence 清单、跨案配置和公开隐私层。
- removed：A4 作为主体主要发现、三案共同任务—关系机制、泛关键词主题频率、平台采用作为融入代理。
- added：案例样本内位置、支持三状态、Q5.4合规子集、个体内平台转换、A1/A4稳健性和单案依赖检查。
