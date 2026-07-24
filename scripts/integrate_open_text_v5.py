#!/usr/bin/env python3
"""Integrate reconciled open-text findings into canonical public evidence tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "outputs/final"


REGISTER_UPDATES = {
    "F105": {
        "finding_statement": (
            "Q8.1的26名作答者中，15名主动提到同伴邀请、14名提到共同任务、"
            "10名提到触发事件后的关系延伸；邀请、在组、延伸与归属不能合并，也不能写成因果链。"
        ),
        "survey_evidence": (
            "outputs/tables/open_text_theme_summary.csv；"
            "outputs/open_text/q81_critical_incident_analysis.md"
        ),
        "evidence_scope": (
            "survey open-text sub-sample; within-case linked evidence; "
            "cross-case interpretation"
        ),
        "changed_across_versions": "yes",
        "reviewer_comments": "开放题把原先单案依赖的进入场景扩展到26名作答者，但相似叙述与自选回答限制机制解释。",
        "final_confidence": "moderate",
        "final_status": "revised",
        "notes": "主动提及不是经历率；共同任务、邀请、关系延伸和成员感分别编码。",
    },
    "F108": {
        "evidence_scope": (
            "survey open-text sub-sample; within-case linked evidence; "
            "cross-case interpretation"
        ),
        "survey_evidence": (
            "outputs/reports/open_text_qualitative_synthesis.md；"
            "data/processed/open_text_codebook.csv"
        ),
        "reviewer_comments": "开放题没有直接跨群体解释或连接行为，进一步支持删除稳定文化中介角色。",
        "notes": "问卷高自报、网络位置、一次帮助和持续中介行为不可互换。",
    },
    "F204": {
        "finding_statement": (
            "封闭题中10/35对未明说规则报告较高困难；Q8.2仅1/26名作答者明确提到规则事前未知。"
            "一般任务、内容衔接、明示评分和纪律不能都归入hidden curriculum。"
        ),
        "survey_evidence": (
            "outputs/tables/survey_item_statistics.csv；"
            "outputs/tables/open_text_theme_summary.csv；"
            "outputs/open_text/q82_support_needs_analysis.md"
        ),
        "evidence_scope": (
            "complete survey sample; survey open-text sub-sample; "
            "within-case linked evidence"
        ),
        "changed_across_versions": "yes",
        "reviewer_comments": "开放题语义复核提供更严格的未预告规则阈值。",
        "notes": "1/26是主动提及，不是隐性规则经历率。",
    },
    "F207": {
        "finding_statement": (
            "支持的来源、时机、可见性和需求匹配可能影响主观可用性；Q8.2同时显示语言支持偏好不统一，"
            "且提出建议不等于实际缺口。"
        ),
        "survey_evidence": (
            "outputs/tables/support_gap_analysis.csv；"
            "outputs/open_text/q82_support_needs_analysis.md"
        ),
        "evidence_scope": (
            "survey open-text sub-sample; within-case linked evidence; "
            "cross-case interpretation"
        ),
        "changed_across_versions": "yes",
        "reviewer_comments": "两条相反语言调整偏好与两条既有支持肯定限制统一支持处方。",
        "notes": "机制仍为探索性；开放题通常不能单独判定已获/有限/未获。",
    },
    "F304": {
        "finding_statement": (
            "三份访谈没有形成完整数字事件链；开放题仅有1条线下关系后加入班群和1条线上学习群组入门建议，"
            "不能补足平台机制。"
        ),
        "survey_evidence": (
            "outputs/tables/open_text_theme_summary.csv；"
            "outputs/reports/open_text_qualitative_synthesis.md"
        ),
        "evidence_scope": (
            "survey open-text sub-sample; interview sub-sample; "
            "cross-case interpretation"
        ),
        "changed_across_versions": "yes",
        "reviewer_comments": "开放题数字材料稀少且功能不同，平台作用仍只作情境。",
        "notes": "未主动提及不表示平台无作用；访谈提纲缺失。",
    },
    "F402": {
        "finding_statement": (
            "Q8.1和Q8.2各26份有效回答已全部逐条语义编码；主题按题目内独立回答者去重，"
            "只报告主动提及，不再用关键词命中解释主题发生率。"
        ),
        "evidence_scope": "survey open-text sub-sample",
        "survey_evidence": (
            "data/processed/open_text_codebook.csv；"
            "outputs/tables/open_text_theme_summary.csv；"
            "outputs/reports/open_text_qualitative_synthesis.md"
        ),
        "changed_across_versions": "yes",
        "reviewer_comments": "第五轮用双路径独立编码和协调取代关键词辅助分析。",
        "notes": "52条文本、47个正式代码；9名两题均无实质文本不等于没有经历。",
    },
}

NEW_FINDINGS = [
    {
        "finding_id": "F110",
        "research_question": "RQ1",
        "finding_statement": (
            "Q8.1的26名作答者中，焦点方向为进入16名、距离4名、混合6名；"
            "混合中持续并存5名、先有距离后转为进入1名。语言门槛5名与本地共同参照缺口11名应分开。"
        ),
        "evidence_scope": "survey open-text sub-sample",
        "survey_evidence": (
            "outputs/tables/open_text_theme_summary.csv；"
            "outputs/open_text/q81_critical_incident_analysis.md"
        ),
        "interview_evidence": "outputs/reports/open_text_linked_case_analysis.md",
        "literature_support": "DP005；TM005-TM008",
        "first_appeared_version": "v5-open-text",
        "changed_across_versions": "added",
        "reviewer_comments": "混合方向须拆成持续并存5名与顺序反转1名；主动提及不是经历率。",
        "final_confidence": "moderate",
        "final_status": "retained",
        "notes": "混合方向中5条为持续并存，1条为先有距离后转为进入。",
    },
    {
        "finding_id": "F211",
        "research_question": "RQ2",
        "finding_statement": (
            "Q8.2的26名作答者中，适应时间与语言/术语支持各12名、课程衔接11名、"
            "同伴主动接触8名、规则说明6名；8名反对缺陷化判断。"
        ),
        "evidence_scope": "survey open-text sub-sample",
        "survey_evidence": (
            "outputs/tables/open_text_theme_summary.csv；"
            "outputs/open_text/q82_support_needs_analysis.md"
        ),
        "interview_evidence": "outputs/reports/open_text_linked_case_analysis.md",
        "literature_support": "DP001-DP005；DP011；TM005-TM008",
        "first_appeared_version": "v5-open-text",
        "changed_across_versions": "added",
        "reviewer_comments": "支持期望不等于实际缺口；主题相互重叠，人数不可相加。",
        "final_confidence": "moderate",
        "final_status": "retained",
        "notes": "主动提及只适用于26名Q8.2作答者。",
    },
    {
        "finding_id": "F404",
        "research_question": "INTEGRATION",
        "finding_statement": (
            "开放题构成独立事件/需要证据层：覆盖多于3份访谈但少于35份封闭问卷，"
            "深度低于访谈；它可扩展和解释封闭题，不能替代总体分布或访谈过程。"
        ),
        "evidence_scope": "survey open-text sub-sample; within-case linked evidence",
        "survey_evidence": (
            "outputs/reports/open_closed_integration.md；"
            "outputs/reports/open_text_qualitative_synthesis.md"
        ),
        "interview_evidence": "outputs/reports/open_text_linked_case_analysis.md",
        "literature_support": "不适用",
        "first_appeared_version": "v5-open-text",
        "changed_across_versions": "added",
        "reviewer_comments": "必须保留封闭题、开放题、链接访谈和文献四层角色。",
        "final_confidence": "high",
        "final_status": "retained",
        "notes": "未提及和未作答不解释为没有经历。",
    },
]


MATRIX_NEW = [
    {
        "research_question": "RQ1",
        "subtheme": "开放题关键事件",
        "survey_evidence": (
            "Q8.1作答者26名：焦点进入16、距离4、混合6（持续并存5、顺序反转1）；"
            "同伴邀请15、共同任务14、关系延伸10；语言门槛5、本地参照缺口11"
        ),
        "linked_case_evidence": "三名链接个案的开放题—封闭题—访谈对照见受限alignment及公开链接个案报告",
        "literature_relation": "边界工作与多维归属可组织材料；不支持稳定文化中介",
        "confidence": "moderate",
        "final_interpretation": "进入与距离可持续并存或顺序反转；邀请、在组、延伸和成员感必须分开。",
        "limitation": "26名自选作答者；主动提及不是经历率；相似叙述可能受题干塑形。",
    },
    {
        "research_question": "RQ2",
        "subtheme": "开放题支持期待",
        "survey_evidence": (
            "Q8.2作答者26名：适应时间12、语言/术语12、课程衔接11、同伴接触8、"
            "规则说明6、反缺陷化8"
        ),
        "linked_case_evidence": "三源对照用于区分简短建议、封闭支持状态与访谈中的具体过程",
        "literature_relation": "学术社会化与学习者身份贴合；hidden curriculum仅1条直接开放证据",
        "confidence": "moderate",
        "final_interpretation": "需求跨制度与关系领域；支持偏好不一，建议不等于缺口。",
        "limitation": "主题重叠不可相加；开放题不能估计支持效果或总体需要率。",
    },
    {
        "research_question": "RQ3",
        "subtheme": "开放题数字材料",
        "survey_evidence": "Q8.1仅1名提到线下关系后加入班群；Q8.2仅1名提出线上学习群组入门",
        "linked_case_evidence": "三份链接访谈仍无完整平台—关系事件链",
        "literature_relation": "媒体组合只作提问框架，开放题不支持平台身份或平台效果",
        "confidence": "moderate",
        "final_interpretation": "数字材料更接近关系延伸和信息接口，不能说明平台造成融入。",
        "limitation": "主动提及极少不等于平台无作用；问题未系统追问数字实践。",
    },
]


JOINT_NEW = [
    {
        "analytic_topic": "开放题关键事件—封闭题边界与归属",
        "survey_evidence": "Q8.1作答者26名：进入16、距离4、混合6（持续并存5、顺序反转1）；邀请15、共同任务14；语言门槛5、本地参照缺口11。",
        "interview_subsample_position": "三名链接个案只作个案内三源对照，不代表26名开放题作答者或35份问卷。",
        "linked_case_evidence": "开放题概括焦点，访谈可补人物、时序和关系层次，也可能保留不同叙述。",
        "relationship_type": "EXPANSION; DIVERGENCE; CONVERGENCE; SILENCE",
        "integrated_interpretation": "相同封闭题位置可对应不同事件；进入与距离、成员感与具体边界可共存。",
        "alternative_explanations": "一般新生陌生、班级网络、任务结构、兴趣、题干塑形与回忆。",
        "limitations": "主动提及不是经历率；开放题比访谈短且无追问。",
        "source_files": "open_text_theme_summary.csv; open_closed_alignment.csv; open_text_interview_alignment.csv",
    },
    {
        "analytic_topic": "开放题支持期待—封闭题支持状态",
        "survey_evidence": "Q8.2作答者26名：时间12、语言/术语12、课程11、同伴接触8、规则6、反缺陷化8。",
        "interview_subsample_position": "三名链接个案只用于核对建议与个人已获/有限/未获支持叙述。",
        "linked_case_evidence": "访谈可补支持来源、可见性、时机和接受方式；未提及不等于未获得。",
        "relationship_type": "EXPANSION; CONVERGENCE; SILENCE",
        "integrated_interpretation": "规范性建议不等于实际缺口；语言和支持偏好不统一。",
        "alternative_explanations": "一般倡议、当前与回顾时点、需求严重度、学校资源及个体偏好。",
        "limitations": "主题重叠不可相加；开放题不能估计支持效果。",
        "source_files": "support_gap_analysis.csv; open_text_theme_summary.csv; open_closed_alignment.csv",
    },
    {
        "analytic_topic": "开放题数字材料—平台功能",
        "survey_evidence": "开放题仅见1条线下关系后班群延伸及1条线上群组入门建议。",
        "interview_subsample_position": "三案无连续平台构念位置，也无完整数字事件链。",
        "linked_case_evidence": "开放题和访谈没有共同支持平台造成关系进入。",
        "relationship_type": "EXPANSION; SILENCE",
        "integrated_interpretation": "数字材料可作关系延伸或信息接口，不能把平台使用解释为文化融入。",
        "alternative_explanations": "学校通信规范、任务后便利、既有关系、未系统追问。",
        "limitations": "极少主动提及不是没有作用的证据。",
        "source_files": "platform_transition_analysis.csv; open_text_theme_summary.csv; open_text_linked_case_analysis.md",
    },
]


def main() -> None:
    register_path = FINAL / "findings_register.csv"
    register = pd.read_csv(register_path, keep_default_na=False)
    for finding_id, updates in REGISTER_UPDATES.items():
        matches = register["finding_id"].eq(finding_id)
        if matches.sum() != 1:
            raise ValueError(f"Expected one {finding_id}, got {matches.sum()}")
        for column, value in updates.items():
            register.loc[matches, column] = value
    new_ids = {row["finding_id"] for row in NEW_FINDINGS}
    register = register[~register["finding_id"].isin(new_ids)]
    register = pd.concat([register, pd.DataFrame(NEW_FINDINGS)], ignore_index=True)
    register["_group"] = register["finding_id"].str.extract(r"F(\d+)")[0].astype(int)
    register = register.sort_values("_group").drop(columns="_group")
    register.to_csv(register_path, index=False, encoding="utf-8-sig")

    matrix_path = FINAL / "research_question_evidence_matrix.csv"
    matrix = pd.read_csv(matrix_path, keep_default_na=False)
    new_keys = {(row["research_question"], row["subtheme"]) for row in MATRIX_NEW}
    matrix = matrix[
        ~matrix.apply(
            lambda row: (row["research_question"], row["subtheme"]) in new_keys, axis=1
        )
    ]
    matrix = pd.concat([matrix, pd.DataFrame(MATRIX_NEW)], ignore_index=True)
    rq_order = {"RQ1": 1, "RQ2": 2, "RQ3": 3}
    matrix["_order"] = matrix["research_question"].map(rq_order)
    matrix = matrix.sort_values(["_order"], kind="stable").drop(columns="_order")
    matrix.to_csv(matrix_path, index=False, encoding="utf-8-sig")

    joint_path = ROOT / "outputs/tables/joint_display.csv"
    joint = pd.read_csv(joint_path, keep_default_na=False)
    topics = {row["analytic_topic"] for row in JOINT_NEW}
    joint = joint[~joint["analytic_topic"].isin(topics)]
    joint = pd.concat([joint, pd.DataFrame(JOINT_NEW)], ignore_index=True)
    for column in joint.select_dtypes(include="object").columns:
        joint[column] = (
            joint[column]
            .str.replace(r"\bP01\b", "一个链接个案", regex=True)
            .str.replace(r"\bP02\b", "另一个链接个案", regex=True)
            .str.replace(r"\bP03\b", "第三个链接个案", regex=True)
        )
    joint.to_csv(joint_path, index=False, encoding="utf-8-sig")
    print(
        f"integrated findings={len(register)} matrix={len(matrix)} joint_display={len(joint)}"
    )


if __name__ == "__main__":
    main()
