#!/usr/bin/env python3
"""Write public-safe second-round reviews, integration, revision log, and report."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline_common import ROOT


REPORTS = ROOT / "outputs/reports"
REVIEWS = ROOT / "outputs/reviews"
TABLES = ROOT / "outputs/tables"
PROCESSED = ROOT / "data/processed"
ROUND2_RUN = ROOT / "outputs/agent_runs/20260723_independent_review_extension_v2"
PRESERVED = ROUND2_RUN / "preserved_first_round_reports"

JOINT_FIELDS = [
    "analytic_topic",
    "survey_evidence",
    "interview_subsample_position",
    "linked_case_evidence",
    "relationship_type",
    "integrated_interpretation",
    "alternative_explanations",
    "limitations",
    "source_files",
]


def preserve_first_round() -> None:
    PRESERVED.mkdir(parents=True, exist_ok=True)
    for name in [
        "final_report.md",
        "cross_case_analysis.md",
        "integrated_findings.md",
        "draft_report.md",
    ]:
        source = REPORTS / name
        target = PRESERVED / name
        if source.is_file() and not target.exists():
            target.write_bytes(source.read_bytes())


def write_public_reviews() -> None:
    REVIEWS.mkdir(parents=True, exist_ok=True)
    quantitative = """# Reviewer A：量化与数据复核（公开安全版）

判定：**PASS_WITH_ISSUES**；无 blocker。完整逐列复算和小格证据保存在受限 reviewer 输出。

| issue_id | severity | 问题与证据 | 修改建议 |
|---|---|---|---|
| QA-001 | MAJOR | Q2.10、Q3.2、Q5.4 分别有 8/35、14/35、9/35 超过问卷限选；旧清洗未检测。 | 保留回答但逐题标记；把 Q5.4 当 endorsement，并报告限选合规子集。 |
| QA-002 | MINOR | Q5.4 题组特殊回答未传播至普通选项分母。 | 普通选项有效 n 改为 34，特殊状态保持独立。 |
| QA-003 | MINOR | Q5.3 有少量互斥组合。 | 标记、不猜测参与者本意，并做排除敏感性。 |
| QA-004 | MINOR | 开放题规则使用“同学”“主动”等泛词，具体主题标签过强。 | 只保留关键词索引，删除机制或频率解读。 |
| QA-005 | MAJOR | A4 原规格计算正确，但合理替代参与编码使结果减弱。 | A4 降为 `weak signal`，不得概括为中介参与—压力关系。 |
| QA-006 | MINOR | codebook 的母题文字与项目文字未分开。 | 由最终问卷补入母题，保留导出表头为 `source_column`。 |
| QA-007 | MINOR | 构念报告误写不存在的 `n_scored` 字段。 | 改为 `scored_n`。 |
| QA-008 | MINOR | 旧 validation 未检查限选、题组缺失、互斥和替代编码。 | 新增第二轮量化验证。 |

机械复核确认：160 个导出位置未错位；250 个主要矩阵/Q5.5 计数单元正确；A1 在完整个案、替代门槛、替代聚合和 leave-one-out 下方向稳定。
"""
    qualitative = """# Reviewer B：质性证据复核（公开安全版）

判定：**PASS_WITH_ISSUES**；无 blocker。84/84 条 canonical 引语逐字存在、均来自 Participant 行；所有证据最高为中等置信度。

| issue_id | severity | 问题与证据 | 修改建议 |
|---|---|---|---|
| QL-001 | MINOR | 受限案例有少量机器断句片段截在句中，注释使用了下一行意义。 | 延伸至紧邻补句并重验逐字。 |
| QL-002 | MINOR | 少数主码不符合 codebook 纳入条件。 | 重编码正式课程陌生、自信变化、一般建议和幸运归因。 |
| QL-003 | MINOR | 不同内容域、不同阶段或限选未勾选被误标为 convergence/divergence。 | 只在同构念、重叠时段、相反方向时判 divergence。 |
| QL-004 | MINOR | 少数报告把压缩释义放入引号。 | 引号只放逐字文本，其他明确标为释义。 |
| QL-005 | MINOR | “三个个案共同显示任务—关系交叉场景”覆盖过强。 | 改为一个案例直接支持、其余案例仅部分支持。 |
| QL-006 | NOTE | 旧自动验证只能查逐字和枚举，不能查语义错分。 | 第二轮区分机械验证与人工语义复核。 |
| QL-007 | NOTE | 多个候选过程码尚未系统回填 master。 | 已应用码转 ACTIVE；未回填者继续标 PROPOSED 并禁止频率解读。 |

审查未发现伪造引语、超出资料质量的 HIGH 置信度、用代码次数代替主题强度，或把三个个案推广到完整样本。
"""
    integration = """# Reviewer C：混合方法与论证复核（公开安全版）

判定：**PASS_WITH_ISSUES**；无 blocker。

| issue_id | severity | 问题与证据 | 修改建议 |
|---|---|---|---|
| MM-001 | MAJOR | Q3.3 原题是复合“可以信任并谈心”，旧报告缩成“可信任”后又把二者拆开。 | 恢复完整题意；保留 P01 同题 divergence；不得分别估计信任与谈心。 |
| MM-002 | MAJOR | 75 条 alignment 的关系分类未稳定满足同构念、时段重叠、方向相反。 | 全量二次裁决并形成 divergence inventory。 |
| MM-003 | MINOR | 旧 joint display 的宽主题只有单一标签，正文却声称多种关系。 | 拆成“主题 × 关系类型”，规格敏感性不再标为资料 divergence。 |
| MM-004 | MINOR | “回答如何形成”“支撑归属”等措辞隐含生成性。 | 改为回顾性叙述配置并存，并列竞争解释。 |
| MM-005 | NOTE | 人物一一绑定的“三条路径”容易固化为类型。 | 改用配置矩阵和 leave-one-case-out 依赖检查。 |

四层证据区分、非代表性边界、替代解释、负例和反本质主义总体良好；主要问题集中在复合题意与关系类型粒度。
"""
    reproducibility = """# Reviewer D：隐私与可复现性复核（公开安全版）

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
"""
    for name, text in {
        "quantitative_audit_v2.md": quantitative,
        "qualitative_audit_v2.md": qualitative,
        "integration_audit_v2.md": integration,
        "reproducibility_privacy_audit_v2.md": reproducibility,
    }.items():
        (REVIEWS / name).write_text(text, encoding="utf-8")


def write_joint_display() -> pd.DataFrame:
    rows = [
        {
            "analytic_topic": "同伴边界—归属",
            "survey_evidence": "A1在替代计分和leave-one-out下保持负向；后期成员感整体较高。",
            "interview_subsample_position": "个案位置覆盖样本IQR内及低于IQR的归属位置；不代表抽样分层。",
            "linked_case_evidence": "不同回顾性关系配置与相近边界回答并存。",
            "relationship_type": "EXPANSION",
            "integrated_interpretation": "问卷描述排序关系，访谈把成员感、求助、亲密和群体门槛区分开。",
            "alternative_explanations": "题项门槛、回忆、语言、班级机会和一般转校陌生感。",
            "limitations": "A1为事后资格口径下的探索性相关，不识别方向。",
            "source_files": "exploratory_associations.csv; exploratory_extension_v2.csv; restricted alignment adjudication",
        },
        {
            "analytic_topic": "复合信任谈心题",
            "survey_evidence": "35/35对“至少一位可以信任并谈心的同学”给出正向回答。",
            "interview_subsample_position": "P01学校归属位置低于样本IQR。",
            "linked_case_evidence": "P01访谈否认有能够交心的朋友。",
            "relationship_type": "DIVERGENCE",
            "integrated_interpretation": "保留为同题直接分歧；不能把问卷拆成信任和谈心两个比例。",
            "alternative_explanations": "时间点、个人门槛、问卷反应压缩或访谈回忆。",
            "limitations": "单案分歧不能重估完整样本。",
            "source_files": "survey_item_statistics.csv; P01 restricted alignment",
        },
        {
            "analytic_topic": "学术任务与规则",
            "survey_evidence": "初期具体任务困难与后期较高规则理解回答并存。",
            "interview_subsample_position": "三案学业困难位置不一，其中受限案例处于样本较低位置。",
            "linked_case_evidence": "规则知道、任务耗时、语言负担和参与位置可不同步。",
            "relationship_type": "EXPANSION",
            "integrated_interpretation": "“能完成”“不耗时”“懂规则”和“能进入互动”不是同一结果。",
            "alternative_explanations": "科目、教师、年级、后期熟练度回投及工具适配。",
            "limitations": "回顾性叙述不是观察到的学习路径。",
            "source_files": "survey_item_statistics.csv; restricted alignment adjudication",
        },
        {
            "analytic_topic": "初期任务困难",
            "survey_evidence": "若干任务题在完整样本中较常被评为困难。",
            "interview_subsample_position": "受限案例问卷组合位置较低。",
            "linked_case_evidence": "受限案例对相同任务内容叙述了更强摩擦。",
            "relationship_type": "DIVERGENCE",
            "integrated_interpretation": "保留强度分歧；不裁定问卷或访谈更真实。",
            "alternative_explanations": "量表压缩、问题理解、时点、回忆和显著事件选择。",
            "limitations": "公开层不连接案例代号、背景或行号。",
            "source_files": "restricted third-case alignment; exploratory_extension_v2.csv",
        },
        {
            "analytic_topic": "支持来源",
            "survey_evidence": "Q5.4全有效回答与限选合规子集均由两类同伴来源居前。",
            "interview_subsample_position": "个案未满足支持位置存在差异。",
            "linked_case_evidence": "三案均叙述可定位的非正式同伴帮助。",
            "relationship_type": "CONVERGENCE",
            "integrated_interpretation": "两类资料共同支持同伴是可见支持来源，但不证明支持效果。",
            "alternative_explanations": "表单超限、选项分类、支持者个体投入和学校安排。",
            "limitations": "Q5.4是endorsement，不能恢复严格“最大三项”含义。",
            "source_files": "exploratory_extension_v2.csv; restricted case evidence",
        },
        {
            "analytic_topic": "支持状态与可接受性",
            "survey_evidence": "Q5.5区分帮助较大、帮助有限和未获得但希望。",
            "interview_subsample_position": "P01未满足支持高于样本IQR；P02位于IQR内。",
            "linked_case_evidence": "零散帮助、介入时机、家庭资源和支持可见性影响回顾评价。",
            "relationship_type": "EXPANSION",
            "integrated_interpretation": "获得状态、主观有效性、时机和可接受性应分开。",
            "alternative_explanations": "正式/非正式支持理解、长期回忆和访谈覆盖。",
            "limitations": "探索性配置不能识别支持造成何种结果。",
            "source_files": "support_gap_analysis.csv; exploratory_extension_v2.csv; restricted case evidence",
        },
        {
            "analytic_topic": "文化中介行动",
            "survey_evidence": "问卷中解释差异的正向回答较多。",
            "interview_subsample_position": "三案不是统计代表性子样本。",
            "linked_case_evidence": "只有受限案例出现有限的明确学校差异解释证据。",
            "relationship_type": "EXPANSION",
            "integrated_interpretation": "具体事件扩展问卷概念，但不足以定义稳定角色。",
            "alternative_explanations": "一般经验分享、朋友好奇或访谈未追问。",
            "limitations": "A4已降为weak signal；事件不进入主体主发现。",
            "source_files": "exploratory_extension_v2.csv; restricted brokerage evidence",
        },
        {
            "analytic_topic": "文化中介负担",
            "survey_evidence": "A4原单项相关对合理参与编码不稳。",
            "interview_subsample_position": "个案访谈覆盖有限。",
            "linked_case_evidence": "P01/P02没有本人实施中介的可定位事件。",
            "relationship_type": "SILENCE",
            "integrated_interpretation": "访谈沉默不能否定问卷，但不支持稳定中介—负担机制。",
            "alternative_explanations": "提纲未追问、概念理解不同。",
            "limitations": "只作为weak signal和未来研究。",
            "source_files": "exploratory_extension_v2.csv; restricted alignment adjudication",
        },
        {
            "analytic_topic": "数字平台组合",
            "survey_evidence": "成对回顾显示旧平台保留与WhatsApp/Instagram后期采用并存。",
            "interview_subsample_position": "三案问卷均报告一定平台分工，但不是代表性配置。",
            "linked_case_evidence": "三份访谈均无平台—受众—功能可核对事件链。",
            "relationship_type": "SILENCE",
            "integrated_interpretation": "问卷支持媒体组合和自报功能，访谈不能确认机制。",
            "alternative_explanations": "访谈未系统追问、平台生态随年份改变。",
            "limitations": "平台选择不是身份、归属或融入代理。",
            "source_files": "exploratory_extension_v2.csv; restricted alignment adjudication",
        },
    ]
    display = pd.DataFrame(rows, columns=JOINT_FIELDS)
    display.to_csv(TABLES / "joint_display.csv", index=False, encoding="utf-8-sig")
    display.to_csv(
        ROUND2_RUN / "public_safe_joint_display_v2.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return display


def write_safe_qualitative_reports() -> None:
    cross_case = """# 链接个案质性综合（第二轮公开安全版）

完整三案编码、逐字引语、行号、样本位置和配置矩阵保存在受限分析层。本公开衍生版不显示受限第三案例的匿名代号、行号或背景组合。

独立复核确认 84/84 条 canonical 引语逐字存在且来自参与者行；少量机器断句范围已补齐，少数主码已按 codebook 重编码。75 条问卷—访谈对照已按“同构念、时段重叠、方向相反”三条件全量复核，关系计数变为 EXPANSION 34、CONVERGENCE 21、SILENCE 11、DIVERGENCE 9。

最重要的修订是：Q3.3 的原题为复合“至少一位可以信任并谈心的同学”。P01 问卷正向回答与访谈否认有能够交心的朋友构成未解决的直接分歧，不能再用“信任与谈心是两个层次”消解；这一层次区分只能作为访谈提出的测量建议，不能从完整问卷分别估计。

将人物命名的路径改为配置矩阵后，三案共同支持的是：支持来源、正式度、时机与可见性需分开；成员感、复合信任谈心题、求助、亲密和稳定群体门槛不能互换。任务、语言与关系进入的完整同场景事件链只由受限案例直接支持，P01/P02 分别提供任务或同伴侧面，因此降为单案依赖的探索性配置。三份访谈仍没有平台—受众—功能链；有限的差异解释证据也不足以定义稳定文化中介角色。

允许提出的结论仅为三个回顾性个案配置及其反例，不作频率、饱和、代表性、因果或固定类型判断。
"""
    integrated = """# 混合方法整合发现（第二轮公开安全版）

整合保持四层证据：完整问卷样本、访谈对象样本内位置、个案内问卷—访谈对照、跨案配置。`joint_display.csv` 已按“主题 × 关系类型”重建，不再用单一 dominant label 覆盖同一主题中的 expansion、divergence 或 silence。

完整样本的直接描述保持稳定：初期同伴/任务摩擦与后期较高成员感、复合信任谈心题和规则理解回答并存。A1 对替代计分与逐一删除回答方向较稳，但仍只是事后资格口径下的探索性排序关系。A4 对中介参与替代编码不稳，降为 weak signal。

三案不被用来说明问卷回答“如何形成”，而只为其提供回顾性情境。明确保留的分歧包括 P01 的复合信任谈心题与访谈否认交心、P02 的插班年级表述，以及受限案例若干同内容任务题的强度差异。不同内容域、不同阶段、限选未勾选或支持强度条件不再误标为 divergence。

支持整合改为三层：Q5.4 是因表单未执行限选而得到的 endorsement；Q5.5 分开“帮助较大”“帮助有限”“未获得但希望”；访谈只提出时机、正式度、资源和可见性的探索性解释。平台整合使用同一个体的 retained/adopted/stopped/neither，并保持访谈机制沉默。

文献只用于解释和提出替代机制，不替代参与者证据。现有资料不支持文化本质主义、缺陷视角、平台融入代理、稳定中介角色或支持的因果效果。
"""
    (REPORTS / "cross_case_analysis.md").write_text(cross_case, encoding="utf-8")
    (REPORTS / "integrated_findings.md").write_text(integrated, encoding="utf-8")
    (REPORTS / "draft_report.md").write_text(
        "# 历史初稿访问说明\n\n完整第一轮初稿已保存在本轮受限归档和 `analysis-v2` Git tag；当前路径不再公开参与者级组合证据。请使用 `final_report_v2.md`。\n",
        encoding="utf-8",
    )


def write_revision_log() -> None:
    entries = [
        ("QA-001", "限选题按设计上限解释", "8/14/9份超限", "新增逐题质量标记、endorsement与合规子集", "prepare_data.py; exploratory_extension_v2.csv", "revised"),
        ("QA-002", "Q5.4普通选项分母35", "题组特殊回答未传播", "分母改为34，计数23/19不变", "analyze_survey.py; exploratory_extension_v2.csv", "revised"),
        ("QA-003", "未检查Q5.3互斥组合", "存在少量冲突", "保留原值并标记；不猜测", "prepare_data.py; data_quality_report.md", "revised"),
        ("QA-004", "开放题泛词主题频率", "同学/主动造成误标", "降为关键词索引，删除机制频率措辞", "analyze_survey.py; survey_open_text_summary.csv", "revised"),
        ("QA-005", "A4与A1并列主要信号", "替代参与编码不稳", "A4降为weak signal，仅留限制", "exploratory_extension_v2.py; association_robustness_v2.csv", "revised"),
        ("QA-006", "codebook母题与项目相同", "160行语义层未分", "补入canonical母题、保留source_column", "prepare_data.py; survey_codebook.csv", "revised"),
        ("QA-007", "构念报告写n_scored", "实际字段scored_n", "修正字段名", "analyze_survey.py; construct_assessment.md", "revised"),
        ("QA-008", "旧量化validation覆盖窄", "关键问题在全PASS下存在", "新增限选、分母、互斥、替代规格检查", "validate_round2.py", "revised"),
        ("QL-001", "少量受限片段截断", "机器断句下一行补完意义", "扩展行范围并重验逐字", "revise_qualitative_v2.py; coded_segments_master_v2.csv", "revised"),
        ("QL-002", "少数primary code不符定义", "正式课程、自信、建议、幸运归因误码", "重编码并检查未知码为零", "revise_qualitative_v2.py", "revised"),
        ("QL-003/MM-002", "部分假divergence/convergence", "内容域/时段/限选不可比", "75条三条件全量裁决；最终DIVERGENCE=9", "alignment_adjudication_v2.csv", "revised"),
        ("QL-004", "压缩释义放入引号", "报告文本非逐字", "公开报告只保留明确释义", "write_round2_reports.py", "revised"),
        ("QL-005", "三案共同任务—关系机制", "完整事件链只由单案直接支持", "降为单案依赖的探索性配置", "leave_one_case_out_themes_v2.csv", "revised"),
        ("QL-006", "自动验证冒充语义复核", "旧脚本只能机械查引语", "v2报告分开机械与人工语义检查", "validate_round2.py", "revised"),
        ("QL-007", "候选码似已全部应用", "多数PROPOSED未回填", "已用渐进码转ACTIVE，其余明确候选", "qualitative_codebook.csv", "revised"),
        ("MM-001", "可信任题被拆义", "原题是信任并谈心复合陈述", "恢复完整标签，P01保留直接分歧", "final_report_v2.md; joint_display.csv", "revised"),
        ("MM-003", "joint display宽主题单标签", "正文与表关系类型不一致", "按主题×关系类型重建", "write_round2_reports.py; joint_display.csv", "revised"),
        ("MM-004", "形成/支撑等隐性生成措辞", "超出回顾性横断设计", "改为回顾性配置并存", "final_report_v2.md", "revised"),
        ("MM-005", "人物绑定三条路径", "任一案例移除即丢失一路", "改为配置矩阵并做leave-one-case-out", "case_configuration_matrix_v2.csv", "revised"),
        ("RP-001", "其他报告仍连接受限案例", "旧final之外路径未切断", "完整证据受限；公开衍生版去连接键", "write_round2_reports.py", "revised"),
        ("RP-002", "公开稀有质量小格", "旧报告精确披露", "新版概括为少量/资料形式不一", "final_report_v2.md; validation_report_v2.md", "revised"),
        ("RP-003", "隐私验证假阴性", "旧48项全PASS仍漏问题", "新增明确allowlist与跨版本检查", "validate_round2.py", "revised"),
        ("RP-004", "旧summary Git状态滞后", "记录早于tag终点", "v2 summary记录本轮起点和analysis-v3", "pipeline_summary_v2.md", "revised"),
        ("RP-005", "复现边界未分层", "冻结解释判断被写成算法再生", "新增target_mode并扩充目标", "verify_reproducibility.py", "revised"),
        ("RP-006", "v2交付未入Git allowlist", "默认ignore", "只放行公开安全第二轮交付", ".gitignore; validate_round2.py", "revised"),
        ("EXT-001", "仅有平台边际变化", "同一回答者可配对", "新增retained/adopted/stopped/neither", "exploratory_extension_v2.csv", "added"),
        ("EXT-002", "只报告未满足支持", "Q5.5可比较三状态", "新增帮助较大/有限/未满足对照", "exploratory_extension_v2.csv", "added"),
        ("EXT-003", "未系统定位访谈案例", "构念位置可计算", "三案受限精确定位；公开只给宽位置", "linked_case_position_v2.csv", "added"),
        ("EXT-004", "A1稳健性未给", "四规格及LOO方向一致", "升级为plausible exploratory，不作因果", "association_robustness_v2.csv", "added"),
        ("DEL-001", "A4一般文化中介结论", "合理替代编码不稳", "从主体发现删除", "final_report_v2.md", "removed"),
        ("DEL-002", "平台采用代表融入/身份", "问卷和访谈均不支持", "删除，不进入发现表", "exploratory_extension_v2.md", "removed"),
    ]
    table = "\n".join(
        f"| {issue} | {original} | {review} | {action} | `{evidence}` | {status} |"
        for issue, original, review, action, evidence, status in entries
    )
    report = f"""# 第二轮修订日志

| issue/claim | 原结论或问题 | reviewer核查 | 实际修改 | 证据/脚本 | 最终状态 |
|---|---|---|---|---|---|
{table}

## 第一版结论处置总览

- retained：35/35 合资格、0 排除、旧口径 11 份重分类；三份访谈唯一链接；主要矩阵描述；非代表性、回顾性和非因果边界。
- revised：复合信任谈心题、Q5.4 分母与限选含义、开放题索引、joint display、divergence 清单、跨案配置和公开隐私层。
- removed：A4 作为主体主要发现、三案共同任务—关系机制、泛关键词主题频率、平台采用作为融入代理。
- added：案例样本内位置、支持三状态、Q5.4合规子集、个体内平台转换、A1/A4稳健性和单案依赖检查。
"""
    (REPORTS / "revision_log_v2.md").write_text(report, encoding="utf-8")


def write_final_report() -> None:
    survey = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    extension = pd.read_csv(TABLES / "exploratory_extension_v2.csv", dtype=str, keep_default_na=False)
    assert len(survey) == 35 and survey["eligible"].eq("TRUE").all()
    assert not extension.astype(str).agg(" ".join, axis=1).str.contains(r"\bP03\b").any()
    report = """# 内地—香港插班经历者的学校适应、同伴关系与数字生活

## 报告状态

这是独立复核与补充探索后的第二轮报告。第一轮版本保存在 `analysis-v2` Git tag 和本轮受限归档；当前 `final_report.md` 与 `final_report_v2.md` 内容一致。所有新发现按 `robust finding`、`plausible exploratory finding` 或 `weak signal` 分级；不支持的解释已删除。

## 摘要

研究使用 35 份回顾性问卷及其中三个唯一链接访谈，探索内地—香港插班经历中的同伴边界、归属、身份协商、学术规则与辅助性数字平台实践。当前资格口径纳入迁居与跨境往返、较低年级插班及不能确认内地连续就读两年者；同意与成年仍为伦理门槛。35 份全部合资格、排除 0，旧口径排除的 11 份保留为可审计重分类。

第二轮确认大多数矩阵计数和主要描述正确，但修复了多选限额未执行、Q5.4 分母、复合“信任并谈心”题被拆义、若干假 divergence、开放题泛关键词、joint display 粒度和公开隐私覆盖。A1 在替代计分与逐一删除回答时方向稳定，仍只列为 `plausible exploratory finding`；A4 对合理替代编码不稳，降为 `weak signal`。新增支持三状态与同一个体的平台转换分析。访谈提出的支持时机、可见性和关系门槛只作为回顾性探索配置，不被当作因果机制或完整样本代表。

## 1. 设计、样本与资格

这是非概率、一次性、回顾性的链接混合方法研究。问卷“初期”和“后期”题并非同一量尺的实际纵向测量；访谈对象选择理由未记录。研究问题聚焦：（1）同伴边界、归属、身份协商和有限的文化中介经验；（2）课堂、作业、评价与未明说规则；数字平台为补充问题。

资格扩展发生在第一版结果可见后，因此增加分析自由度。首次插班年级、内地就学年限和迁居/跨境方式只作背景，不用于排除。V1/V2 不构成资格组比较。

## 2. 清洗、质量与问卷映射

原问卷为 35 行、160 个导出字段，全部映射至代码本。第二轮把 `question_text` 恢复为母题、`item_text` 保留具体项目、`source_column` 保留导出表头。`BLANK`、`NOT_APPLICABLE`、`CANNOT_REMEMBER`、`UNWILLING_TO_ANSWER`、`INVALID_RESPONSE` 始终分开。

问卷平台未执行若干限选：Q2.10 有 8/35 超过两项，Q3.2 有 14/35 超过三项，Q5.4 有 9/35 超过三项。记录不因单题超限被整份删除；原勾选保留并加质量标记。Q5.3 另有少量互斥组合，只标记、不猜测。共享网络、异常短时长和资料形式差异均只作质量警告，精确稀有小格保留在受限层。

Q2.11 的时点措辞冲突，Q3.1 一项和后期微博列缺失，均未重建。开放题只生成关键词定位索引，不再从“同学”“主动”等泛词推断主题频率或机制。

## 3. 问卷—访谈链接与证据质量

三份访谈均按文件名约定数字标记唯一匹配到合资格问卷记录；无歧义、重复或未解决映射。资料形式和核验状态不一，所有质性证据最高为中等置信度。84/84 条 canonical 引语逐字存在于参与者行；第二轮补齐少量机器断句上下文并修正少数代码。
公开报告不显示受限问卷序号、内部行 ID、受限第三案例匿名代号、行号或背景组合。完整链接、位置、编码和逐行裁决仅供授权审计。

## 4. 完整问卷样本

### 4.1 同伴边界、归属与身份

插班初期，语言/幽默进入障碍“经常/非常经常”为 5/31（16.1%），地方知识障碍为 14/35（40.0%），因担忧而减少参与为 11/33（33.3%）。后期 30/33（90.9%）认同自己是学校或班级一员；35/35 对“至少有一位可以信任并谈心的同学”给出正向回答。

最后一项是复合陈述，不能拆成“信任”和“谈心”的两个总体比例。调整表达、解释差异、解释疲惫和双重边缘感也均是独立单项，不合成固定文化类型。

### 4.2 学术适应与规则

初期“比较/非常困难”较多的项目为小组项目 23/34、繁体字 23/32、粤语课堂 22/34、混合评价 22/35、口头汇报 18/33 和答题格式 16/34；理解未明说规则为 10/35。后期 32/34 认同理解评价方式，30/34 认同能区分规则不熟悉与能力不足。题意和时点不同，不能计算改善幅度或归因于个人能力。

### 4.3 支持

排除 Q5.4 题组特殊回答后，香港本地同学为 23/34、具有内地经历的同学为 19/34，是最常被勾选的帮助来源。由于表单没有执行“最多三项”，这只是 endorsement；在严格符合上限的 25 份子集中，两者仍居前（17/25、12/25），属于 `plausible exploratory finding`，不是支持效果。

Q5.5 的三状态对照属于样本内 `robust finding`：朋辈伙伴支持中 17/32 报告“帮助较大”、9/32“帮助有限”；情绪/反排斥支持中 11/30“帮助较大”、5/30“帮助有限”、5/30“未获得但希望”。不同支持项目的有效分母不同，完整表见 `exploratory_extension_v2.csv`。

### 4.4 数字平台

同一个体的两段回顾显示：微信 26/35 保留、6/35 停用；WhatsApp 26/35 后期采用；Instagram 22/35 后期采用。该 `robust finding` 比边际百分点更准确地显示旧平台持续与新平台加入并存。Q6.5 还记录分别维持关系、不同表达、校内信息、旧网络情绪支持和多个平台角色等自报功能。

这些是媒体组合和题项自报，不是文化融入、政治身份、归属或平台效果。后期微博列缺失，不能当作无人使用。

### 4.5 探索性关联与稳健性

A1（初期同伴边界—后期学校归属）原规格 n=30、ρ=-0.499、BH-FDR q=0.029。完整个案、60%门槛、80%中位数和 leave-one-out 的方向均保持，四个规格 ρ 为 -0.604 至 -0.478。它被保留为 `plausible exploratory finding`，但资格口径事后扩展、样本非概率、时点不等价且方向未知，不构成因果或总体结论。

A4 原单项规格 n=32、ρ=-0.430、q=0.035，但两种合理的文化中介参与编码使 ρ 减弱至 -0.363 和 -0.233，V1 也未通过 FDR，故降为 `weak signal`，不进入主体发现。A2、A3、A5 原规格均未通过 FDR；只保留完整表和限制，不作“无关系”证明。

## 5. 铍接个案在样本中的位置

P01 的同伴边界与学业困难位于样本 IQR 内，学校归属和规则理解低于 IQR，未满足支持数高于 IQR。P02 的五项探索指标均位于样本 IQR 内。受限第三案例的精确位置不公开；其较低问卷学业困难位置与访谈多项具体摩擦并存。

这些是当前 35 份样本内的宽位置，不是访谈者具有代表性、典型性或统计抽样地位的证据。

## 6. 问卷—访谈关系重新裁决

75 条对照全部增加同构念、时段重叠、方向相反三项判断。修订后为 EXPANSION 34、CONVERGENCE 21、SILENCE 11、DIVERGENCE 9。这些是证据关系计数，不是主题或参与者频率。

明确保留的分歧包括：

- P01 在问卷中认可复合“信任并谈心”陈述，访谈却否认有能够交心的朋友；这是未解决的同题 divergence。
- P02 的首次插班年级在问卷与访谈中不一致；文件名唯一映射不因此改写。
- 受限第三案例若干同内容任务题的问卷强度与访谈摩擦叙述不一致。

英文材料—英文口语、初期—后来、限选未勾选、一般制度—评价规则、希望关注—不希望显眼特殊关照等改为 expansion 或 silence。可能解释包括时段、内容域、量表压缩、回忆、限选、访谈提示和转写质量；不自动判断哪一来源更真实。

## 7. 跨案配置、负例与替代解释

人物绑定的“三条路径”已改写为“初期接口—进入安排—支持配置—后期关系层次—教育路径”的回顾性配置矩阵。

可作为 `plausible exploratory finding` 的是：

- 支持的来源、正式度、到达时机、资源条件与可见性必须分开；零散帮助不等于系统支持，较晚介入可能仍留缺口，显眼关照也可能带来压力。
- 成员感、复合信任谈心题、求助可用性、深层亲密和稳定群体门槛不等价；逐一移除任一案例后，这一分析区分仍有其他案例支持。
- 相似问卷位置可与不同回顾性配置并存，但不能说这些配置“形成”了问卷回答。

任务、语言与关系进入的完整同场景事件链只由受限案例直接支持；P01/P02 分别提供任务或同伴侧面，因此只保留为单案依赖的探索性配置，不再写成三案共同机制。少参与未必是排斥，功能帮助未必等于深层亲密，离开香港学校也未必等于此前适应失败。

文化中介方面只有有限的明确学校差异解释证据，属于 `weak signal`；没有证据定义稳定角色、网络桥接位置或一般收益/负担。三份访谈均缺少平台—受众—功能链；这是对访谈覆盖的可靠 silence，不是现实中平台没有作用。

## 8. 文献、解释边界与局限

冻结文献包只提供背景和比较框架。当前材料与“语言熟练不等于群体承认”“归属与排斥不同”“支持功能依情境变化”等判断相容，但不能用文献填补参与者证据。现有资料不支持“内地应试—香港全人”的二元本质化，也不能从跨境方式、平台或教育路径推断身份。

主要局限：

1. 资格口径在第一版结果可见后扩展，增加分析自由度。
2. 35 份问卷为非概率小样本；三份访谈选择理由未知，不能代表完整样本或支持饱和。
3. 问卷与访谈均为回顾性自报，初期/后期题不等价；不能识别因果、变化或机制。
4. 自编指标不是验证量表；关联受缺失、规格、混杂和小样本影响。
5. 资料形式、访谈提示和转写核验状态不一；受限案例跨越较长教育阶段，工具适配有限。
6. 多选限额未被表单执行；若干导出列缺失或措辞冲突。
7. 隐私抑制减少公开细节；完整证据只在受限层审计。

## 9. 可复现性与交付

原始资料未修改。数值清洗、表格、案例位置、稳健性和公开报告可由 `scripts/` 再生；质性编码和解释性判断则是冻结分析输入经独立语义复核、修订和提升，不能描述为算法重新发现。第二轮审计见 `outputs/reviews/`，补充发现见 `exploratory_extension_v2.md`，逐项处置见 `revision_log_v2.md`，验证见 `validation_report_v2.md`。
"""
    report = report.replace("## 5. 铍接个案", "## 5. 链接个案")
    (REPORTS / "final_report_v2.md").write_text(report, encoding="utf-8")
    (REPORTS / "final_report.md").write_text(report, encoding="utf-8")


def write_manifest() -> None:
    manifest = """# Agent 运行清单

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
"""
    (REPORTS / "agent_run_manifest.md").write_text(manifest, encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    preserve_first_round()
    write_public_reviews()
    write_joint_display()
    write_safe_qualitative_reports()
    write_revision_log()
    write_final_report()
    write_manifest()
    print("round2 public reports generated")


if __name__ == "__main__":
    main()
