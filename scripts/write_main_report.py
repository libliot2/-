#!/usr/bin/env python3
"""Generate the reproducible Chinese v2 draft or reviewed final report."""

from __future__ import annotations

import argparse

import pandas as pd

from pipeline_common import ROOT, RUN_ID


REPORTS = ROOT / "outputs/reports"
TABLES = ROOT / "outputs/tables"
PROCESSED = ROOT / "data/processed"
QUALITATIVE = ROOT / "outputs/qualitative"
RUN = ROOT / "outputs/agent_runs" / RUN_ID


def check_inputs(final: bool) -> dict[str, int]:
    survey = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    mapping = pd.read_csv(
        PROCESSED / "interview_survey_map.csv", dtype=str, keep_default_na=False
    )
    joint = pd.read_csv(TABLES / "joint_display.csv", dtype=str, keep_default_na=False)
    associations = pd.read_csv(TABLES / "exploratory_associations.csv")
    master = pd.read_csv(
        QUALITATIVE / "coded_segments_master.csv", dtype=str, keep_default_na=False
    )
    counts = {
        "total": len(survey),
        "eligible": int(survey["eligible"].eq("TRUE").sum()),
        "excluded": int(survey["eligible"].eq("FALSE").sum()),
        "reclassified": int(
            survey["eligibility_reclassification"].eq("NEWLY_INCLUDED_V2").sum()
        ),
        "linked": int(mapping["mapping_status"].eq("MATCHED").sum()),
        "segments": len(master),
        "topics": len(joint),
    }
    assert (
        counts["total"],
        counts["eligible"],
        counts["excluded"],
        counts["reclassified"],
    ) == (35, 35, 0, 11)
    assert counts["linked"] == 3
    assert set(mapping["mapping_status"]) == {"MATCHED"}
    assert set(master["participant_id"]) == {"P01", "P02", "P03"}
    assert len(joint) >= 4
    retained = set(associations.loc[associations["bh_fdr_q"] < 0.05, "analysis_id"])
    assert len(associations) == 5 and retained == {"A1", "A4"}
    if final:
        assert (RUN / "reviews/evidence_audit.md").is_file()
        assert (RUN / "reviews/privacy_method_audit.md").is_file()
    return counts


def report_text(final: bool) -> str:
    c = check_inputs(final)
    status_note = (
        "本版本已根据独立证据审查和隐私—方法审查逐项核验并修订；审查不改写原始资料。"
        if final
        else "本版本是供独立证据审查和隐私—方法审查使用的完整初稿。"
    )
    return f"""# 内地—香港插班经历者的学校适应、同伴关系与数字生活

## 报告状态

{status_note}

## 摘要

本研究以 {c["eligible"]} 份回顾性问卷和其中三个唯一链接访谈，探索内地—香港学校插班经历中的同伴边界、学校归属、身份协商、文化中介与学术规则学习。V2 在 V1 分析、独立审查和结果查看完成后，按研究者对目标人口的概念修订扩大资格：跨境往返、较低年级插班、插班节点填“其他”及不能确认内地连续就学两年者均纳入；同意和成年仍为伦理门槛。原 35 份提交全部合资格，旧口径排除的 11 份被显式重分类而非静默改写。

问卷中，地方知识边界、具体语言/任务困难与后期较高归属回答并存。三个链接个案进一步显示：同伴支持可能是关系、语言与规则学习的共同入口，但功能性帮助、成员感、稳定群体和深度友谊并不等同；相似问卷回答可由不同过程形成，较低困难回答也可与多项具体摩擦叙述并存。数字平台的分工主要由问卷支持，访谈不足以验证机制。初期同伴边界与后期归属（A1）以及解释两地差异与解释疲惫（A4）只在 V2 中出现 FDR 校正后 q<0.05；这是结果可见后改变人口口径所得的探索性信号，须由预先固定口径的新样本独立复核。

## 1. 研究目的与资格口径

研究对象是自报曾从中国内地学校转入香港学校、参加研究时已成年并明确同意的参与者。首次插班年级、内地连续就学年限以及实际迁居或跨境往返均作为异质性背景，不再用于排除。

这项资格变更发生在资料收集及 V1 完整分析、独立审查和结果查看之后，理由是目标人口的概念范围扩大，而不是资料质量纠错或按显著性筛选样本。原问卷筛选题、原回答和 V1 tag 全部保留；`legacy_eligible_v1` 与重分类字段使 V1/V2 可审计。研究主问题是：（1）同伴边界、归属、身份协商与文化中介怎样相互联系；（2）参与者如何学习课堂、作业、评价及未明说规则。数字平台是关系维持、关系进入和信息获取的辅助问题。

## 2. 样本、清洗与资格流程

原始问卷共有 {c["total"]} 份提交；V2 合资格 {c["eligible"]} 份、排除 {c["excluded"]} 份，旧口径排除而本次重分类纳入 {c["reclassified"]} 份。旧理由涉及插班年级或类别、居住/跨境方式及内地就学年限确认，且原因可重叠；为避免公开小格披露，不在本报告拆分人数。它们在 V2 均只是背景差异。完整流程见受限 `sample_flow.csv` 和 `data_quality_report.md`。

现有数据包未提供足以确认具体招募方式的完整记录，因此按非概率样本处理。背景分布见 `sample_characteristics.csv`；公开输出抑制 n<3 的稀有类别，不组合披露个体背景。

## 3. 问卷—访谈链接

三份访谈文件的约定数字标记均可唯一提取，并在问卷序号列中唯一匹配；V2 下三份均合资格。没有未解决、歧义或重复映射。受限问卷序号和完整三案证据链只存在内部资料，不在本报告公开。

其中一份机器转写记录访谈员现场调出了错误问卷，且首次插班年级的问卷与访谈表述不一致。文件名映射仍满足预设唯一链接规则；内容分歧原样保留，未用访谈反向改写链接。详见 `linkage_report.md`。

## 4. 方法

### 4.1 问卷

原工作簿有 35 行、160 个导出字段。脚本逐列映射最终问卷，保留一行一提交并区分 `BLANK`、`NOT_APPLICABLE`、`CANNOT_REMEMBER`、`UNWILLING_TO_ANSWER` 和 `INVALID_RESPONSE`。平台身份键、精确时间、IP 与备注不进入分析表。

分析以有效 n、频数、比例、中位数和 IQR 为主。四个题组只作探索性描述指标，每人至少 80% 题项有效才计分；Cronbach α 只作内部一致性诊断，不证明量表效度。五项 Spearman 关联使用 50,000 次双侧 Monte Carlo 置换、10,000 次 bootstrap 和统一 BH-FDR 校正。未运行回归、因子分析、因果模型，也未把不等价的初期—后期题项做成变化分。

### 4.2 链接个案与质性综合

问卷清洗、链接、档案和编号转录完成后，三个独立 Linked Case Agent 分别比较问卷与访谈的 convergence、expansion、divergence 和 silence。一份资料是整理式记录，只有 `Participant` 行可作逐字证据；另两份是未经录音核对的机器转写。所有个案证据最高为中等置信度。

质性综合保留参与者、稳定行号、逐字引文、替代解释和负例；{c["segments"]} 条 canonical 编码片段可回溯至 `coded_segments_master.csv` 和编号转录。三个个案不用于频率估计、统计代表性或主题饱和主张。

### 4.3 混合方法与文献

整合依次比较完整问卷、访谈对象在样本中的位置、个案内对照及跨个案路径。`joint_display.csv` 的 {c["topics"]} 个主题逐项保留关系类型、替代解释、限制与来源。文献比较只使用冻结证据包；原证据等级依较窄旧人口定义建立，V2 后只能谨慎映射，文献不替代当前参与者资料。

## 5. 数据质量

没有发现闭合题与开放题完整响应向量完全相同的提交。少量记录触发共享网络或异常短作答时长的质量标记；共享网络、设备与不同作答速度均可能解释，故只标记而不排除。

最终问卷与导出有少量版本差异：粤语题的时间措辞冲突，只作“时点不确定”背景；Q3.1 一项和后期微博列未导出，未重建为零。两道开放题各有 26/35 份非空回答，公开结果仅作多标签关键词辅助扫描，不逐字刊载。完整缺失与异常见 `data_quality_report.md`。

## 6. 完整问卷样本发现

### 6.1 同伴边界、归属与网络

插班初期，语言/幽默进入障碍“经常/非常经常”为 5/31（16.1%），地方知识障碍为 14/35（40.0%），因担忧而减少参与为 11/33（33.3%）。后期 35/35 认同至少有一位可信任同学，30/33（90.9%）认同自己是学校或班级一员。不同时间框架的回答可以并存，不是等价前后改善。

后期网络以“同时维持几个不同背景朋友圈”为 16/35（45.7%）最多，其次是依课程、兴趣和场景进入不同群体 8/35（22.9%）及主要与内地背景同学交往 7/35（20.0%）。网络类别不等于关系深度或归属程度。来源：`survey_item_statistics.csv`、`sample_characteristics.csv`。

### 6.2 身份协商与文化中介

调整表达获得 31/31 正向回答，解释两地差异为 29/34；解释者疲惫为 9/32，双重边缘感的正向回答为 15/32。它们是不同单项，不合成为“文化中介量表”，也不构成固定身份类型。来源：`survey_item_statistics.csv`。

### 6.3 学术适应与规则

插班初期，“比较/非常困难”较多的项目为小组项目 23/34、繁体字 23/32、粤语课堂 22/34、混合评价 22/35、口头汇报 18/33 和答题格式 16/34；理解未明说规则为 10/35。后期 32/34 认同理解评价方式，30/34 认同能区分规则不熟悉与能力不足。题目内容与时点不同，不能计算进步幅度或把困难归为个人能力缺陷。来源：`survey_item_statistics.csv`。

### 6.4 支持与支持缺口

被选为主要帮助最多的是香港本地同学 23/35 和具有内地经历的同学 19/35。未满足需求最高的是情绪/反排斥支持 5/30，其次是英文支持 4/33 和家长制度说明 4/29。支持来源、获得状态、实际帮助和希望获得须分开理解；这些计数不估计总体需求率或支持效果。来源：`support_gap_analysis.csv`。

### 6.5 数字平台

两个回顾时点的边际选择人数为：微信/朋友圈 32/35 与 27/35，WhatsApp 0/35 与 26/35；Instagram 后期为 23/35，插班前的小格按公开规则抑制。它们说明样本层面的媒体组合分布改变并持续共存，不是同一个体的保留或替代率。后期微博列缺失，平台选择也不是文化、政治身份或融入的代理。来源：`platform_transition_analysis.csv`。

### 6.6 探索性关联与 V1/V2 敏感性

- A1（初期同伴边界—后期归属）：n=30，ρ=-0.499，bootstrap 95% CI [-0.772, -0.171]，置换 p=0.0058，q=0.0291。
- A2（初期学业困难—后期规则理解）：n=31，ρ=0.359，bootstrap 95% CI [-0.061, 0.719]，置换 p=0.0474，q=0.0790。
- A3（支持项目数—归属）：n=29，ρ=0.315，bootstrap 95% CI [-0.146, 0.711]，置换 p=0.0974，q=0.1218。
- A4（解释差异—解释疲惫）：n=32，ρ=-0.430，bootstrap 95% CI [-0.704, -0.083]，置换 p=0.0141，q=0.0353。
- A5（平台分工—同伴网络）：n=30，ρ=-0.035，bootstrap 95% CI [-0.395, 0.348]，置换 p=0.9886，q=0.9886。

V1 的五项 q 均不低于 0.05；在 V1 结果可见后扩大到 V2，A1/A4 才低于 0.05。这个变化与研究者分析自由度、样本从 24 增至 35、排序结构、有效 n、缺失模式和随机波动同时存在，不能当作资格组检验或确认性发现。A1 不证明边界导致归属降低，A4 的负相关也不证明解释行为具有保护作用。完整结果见 `exploratory_associations.csv`，版本对照可由 `analysis-v1` 与当前脚本重现。

## 7. 三个链接个案

### 7.1 P01：规则学习、同背景支持与亲密门槛

P01 释义显示，参与者把英语口语任务中从害怕开口到更主动表达的回顾，与后来理解“敢说”也属于评价要求联系起来（P01，L0010）。内地背景同伴初期提供翻译、学校规则、地方信息及关系入口，后期同一网络成为相对安全圈，并与拓展本地关系动力下降同时出现（P01，L0016–L0018）。这只是回顾性权衡，不证明支持造成隔离。

问卷认可有可信任同学，访谈却报告缺少“交心”朋友；问卷认为英文材料/口头汇报较不困难，访谈又强调口语障碍（P01，L0021、L0010）。可信任与深度亲密、材料与口语、初期与整个就学期并非同一概念，因此两类资料同时保留。

### 7.2 P02：少数密友、沟通代理与支持强度

P02 释义显示，会一种地区粤语仍可能遇到香港粤语接口；同学主动答疑和接近，少数密友提供可用关系，并在参与者难以开口时代为沟通（P02，L0024、L0041–L0044、L0085–L0093、L0207–L0212、L0246）。朋友替其沟通是支持接受，不是 P02 主动文化中介。

参与者对学校严格节奏的不适、返回内地以及后来更愿意主动表达可以同时成立（P02，L0123–L0148）。访谈还区分希望获得关注与不希望被过度、显眼地特殊关照（P02，L0239–L0248）。长期回忆和机器转写均限制裁定；稀有程序问题只在总体方法限制中披露，不与公开个案代号连接。

### 7.3 第三个链接个案的公开最小化

第三个案的完整问卷—访谈分析、逐字引文和行号已经在受限证据层完成并通过验证，但旧版公开历史与新版资格决定可能形成跨版本间接识别链。因此，本报告不复述其匿名代号、背景—资源组合、样本位置或行号。它只以两个经概括的主题进入下文综合：一个受限个案的较低问卷困难回答与多项具体摩擦叙述并存；另有一个有限的一对一差异解释事件，但不足以定义稳定文化中介角色。完整证据仅供获授权审计。

## 8. 跨个案发现

三个个案共同显示，小组任务既是学术要求，也可能成为语言、地方知识与关系进入的交叉场景；但进入路径不同。P01 主要通过同背景支持和任务试错，P02 依赖即时答疑、少数密友与沟通代理；第三案的具体路径因跨版本再识别风险只保留在受限综合。

归属须拆成成员感、可求助性、稳定群体和深度亲密：P01 有功能性支持却缺少交心感，P02 以少数密友支撑正向归属；受限第三案也显示核心友谊与稳定群体自评可以不同。参与较少不等于排斥，离开香港学校也不自动等于适应失败。

三案还提供两类测量负例：相似的正向归属回答可对应不同关系结构；一个受限个案的较低困难回答与多项具体摩擦叙述并存。文化中介只有一个受限个案出现有限的一对一解释事件；P01/P02 没有足够主动中介证据。三案访谈均不足以说明平台—受众—功能机制。完整可追溯资料见受限 `cross_case_analysis.md`。

## 9. 混合方法整合

完整问卷说明本样本中边界、归属、任务困难、支持状态和平台组合的分布；链接个案解释这些回答可能如何形成，也暴露问卷无法裁定的时间、门槛和测量差异。主要关系是：

1. **边界—归属（convergence/expansion/divergence）：** A1 给出当前样本的负向排序关系；三案同时说明早期障碍、后期成员感、少数亲密关系和具体距离感可以并存。
2. **学术规则（expansion/divergence）：** 问卷显示具体初期困难与后期规则理解；P01 提供任务试错链，P02 保留严格印象与过程回忆不足；一个受限个案呈现较低困难回答与多项具体摩擦叙述。
3. **支持（convergence/expansion）：** 问卷显示同伴常被选为主要帮助；访谈把支持展开为不同来源、功能、到达时机和可接受的可见性，而非单一“支持剂量”。
4. **身份与文化中介（expansion/silence）：** 问卷给出表达调整和解释行为分布；只有一个案例出现有限具体解释事件，另外两案不足以验证稳定角色。
5. **平台（silence）：** 问卷支持平台组合和关系分工，访谈没有足够机制事件，因此不声称平台促进归属。

各主题的替代解释、限制与来源见 `joint_display.csv` 和 `integrated_findings.md`。

## 10. 文献比较

冻结文献包中的原 A/B/C 等级按旧人口口径建立，不能直接作为 V2 整体的人口贴近度。DP001/DP002 只能支持可分离的相近个案；DP002 的一个跨境个案在 V2 下新具直接相关性，但不足以代表跨境学生。当前资料与“语言熟练不等于被群体承认”“归属与排斥不是同一指标”“支持功能依来源和情境变化”等判断相容，并以任务分组、支持时机、资源可得性和关系门槛加以扩展。

教育制度、文化中介与 polymedia 文献提供比较框架，却不能替代参与者证据。现有资料不支持“内地应试—香港全人”的二元本质化比较，也不能由跨境/迁居方式、平台选择或返回内地推断身份。逐条证据等级与关系分类见 `literature_comparison.md`。

## 11. 矛盾、负例与替代解释

- V1/V2 的统计判定改变，说明资格口径与小样本排序会影响结果稳定性。
- 初期边界与后期归属并存，不是同一量尺的前后变化。
- 可信任同学、成员感、稳定群体和“交心”门槛可能不一致。
- 参与较少可能同时涉及语言、个人选择、通勤/家庭安排、费用、任务形式与班级机会，不能自动归为排斥。
- 问卷“困难”可能表示能否完成，访谈则描述耗时、不适或参与位置；一个受限个案出现两类回答并存，长期回忆与工具措辞均可解释。
- 学校类型、教学语言、插班年级、自由分组、班级构成、教师介入时机、家庭资源与偶然座位安排都是可行替代解释。

## 12. 局限

1. 资格口径在 V1 结果可见后扩展，增加研究者分析自由度；工具原设计仍带有高年级迁居假设，V2 人口异质性更大。
2. 35 份问卷是非概率小样本，不能估计香港目标人口比例；V1/V2 不是资格组比较。
3. 问卷为一次性回顾性自报，初期与后期题项不等价；方向、变化及机制不能识别。
4. 自编题组不是验证量表；A1/A4 的 q<0.05 仍受事后口径、小样本和未测混杂限制。
5. 只有三个链接个案，选择理由未记录，不能声称代表性、频率或饱和。
6. 一份访谈是整理记录，两份是未核音机器转写；一份还存在错误问卷提示和年级分歧。
7. 工具版本差异使一题时点不确定，且若干导出列缺失。
8. 公开报告抑制小格、组合背景和开放题原话；保护隐私的同时减少外部可见细节。
9. 冻结文献的证据等级依据旧人口口径，邻近或理论研究只能用于比较。

## 13. 谨慎启示

资料提出可供后续评估的设计线索：入学初期明确说明课堂、评价与分组规则；为粤语/英语、繁体字、小组任务和口头汇报提供低门槛、可选择且不过度突出个人的支持；自由分组时设置可进入的伙伴或分组机制；区分关系入口、可求助同伴、成员感和深度友谊；评估家庭无法购买额外支持时的替代方案。

这些不是已验证干预建议。后续研究宜预先固定资格口径，分层记录插班年级与跨境/迁居路径，采用更大样本和前瞻重复测量，使用适配不同年龄的题项，并在同意下核对完整录音转录及专门追问平台—受众—功能和中介事件。

## 14. 可复现性

原始资料未修改；四个来源文件的哈希基线和最终校验一致。脚本位于 `scripts/`，角色隔离结果位于 `outputs/agent_runs/{RUN_ID}/`，受限 processed/qualitative 产物只保存在本地。量化主张回溯至 `sample_flow.csv`、`survey_item_statistics.csv`、`support_gap_analysis.csv`、`platform_transition_analysis.csv` 和 `exploratory_associations.csv`；质性主张回溯至 `coded_segments_master.csv` 与编号转录；整合主张回溯至 `joint_display.csv`。最终自动检查见 `validation_report.md`。
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true", help="Write reviewed final report")
    args = parser.parse_args()
    REPORTS.mkdir(parents=True, exist_ok=True)
    if args.final and (TABLES / "exploratory_extension_v2.csv").is_file():
        from write_round2_reports import write_final_report

        write_final_report()
        print(f"wrote {REPORTS / 'final_report.md'} from round2 reviewed inputs")
        return
    output = REPORTS / ("final_report.md" if args.final else "draft_report.md")
    output.write_text(report_text(args.final), encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
