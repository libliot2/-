#!/usr/bin/env python3
"""Validate and promote the reconciled open-text analysis proposals."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "outputs/agent_runs/20260724_open_text_v5/open_text_synthesis"
)

THEME_BASIS = {
    "焦点事件主要指向进入": "EVENT_DIRECTION=ENTRY",
    "焦点事件主要指向距离": "EVENT_DIRECTION=DISTANCE",
    "进入与距离在同一回答中并存": "EVENT_DIRECTION=MIXED",
    "同伴主动邀请": "OTC02",
    "共同任务提供关系入口": "OTC06",
    "触发事件后关系延伸到日常": "OTC12",
    "日常陪伴或共同活动": "OTC05",
    "同伴调整语速或解释表达": "OTC07",
    "直接听说语言门槛": "OTC08",
    "本地共同参照或笑点缺口": "OTC09",
    "初期独处或处于关系外围": "OTC14",
    "自由分组或既有朋友圈形成门槛": "ANY_OF:OTC01|OTC15",
    "既有优势或贡献获得角色与认可": "ANY_OF:OTC10|OTC11",
    "同伴解释任务或课堂规则": "OTC21",
    "教师主动确认或非正式倾听": "ANY_OF:OTC03|OTC04",
    "课外或体育活动入口": "OTC16",
    "担心语言表现或群体尴尬而收缩参与": "OTC20",
    "观点在合作中被认真听取": "OTC22",
    "被惦记带来情绪舒缓": "OTC18",
    "笼统社会进入但过程不可分类": "OTC17",
    "线上班群作为线下关系的后续延伸": "OTC13",
    "直接表达被接纳或班级成员感": "OTC45",
    "需要适应时间或缓冲": "OTC27",
    "反对能力、性格或融入意愿的缺陷化判断": "OTC28",
    "课程内容、教材或进度衔接": "OTC29",
    "作业、评分、课堂或活动规则说明": "OTC30",
    "语言、术语或表达支持": "OTC31",
    "同伴主动搭话、分享或邀约": "OTC32",
    "学校安排朋辈结对或桥梁": "OTC25",
    "个别化评估与按需支持": "OTC24",
    "情绪支持或关注情绪变化": "OTC26",
    "主动询问或持续关注适应": "OTC23",
    "多领域适应与复合压力": "OTC34",
    "沉默或迟疑不应被解释为拒绝参与": "OTC35",
    "入学前或初期导向": "OTC37",
    "语言协助需要灵活且避免过度迁就": "OTC38",
    "包容差异与平等沟通": "OTC36",
    "教师安排分组": "OTC33",
    "提升自信并承认不同能力": "OTC39",
    "维持旧关系构成额外负担": "OTC41",
    "明确肯定既有支持": "OTC42",
    "线上学习群组入门": "OTC43",
    "规则未提前说明": "OTC46",
    "补齐已落下的课业": "OTC40",
    "支持内容不明确或无法进一步分类": "OTC44",
}


def codes(value: str) -> set[str]:
    return {part.strip() for part in str(value).split(";") if part.strip()}


def theme_count(coded: pd.DataFrame, question_id: str, basis: str) -> int:
    rows = coded[coded["question_id"].eq(question_id)].copy()
    if basis.startswith("EVENT_DIRECTION="):
        value = basis.split("=", 1)[1]
        rows = rows[rows["event_direction"].eq(value)]
    elif basis.startswith("ANY_OF:"):
        candidates = set(basis.removeprefix("ANY_OF:").split("|"))
        rows = rows[rows["final_codes"].map(lambda value: bool(codes(value) & candidates))]
    else:
        rows = rows[rows["final_codes"].map(lambda value: basis in codes(value))]
    return int(rows["public_respondent_id"].nunique())


def main() -> None:
    source_files = {
        "codebook": SOURCE / "proposed_open_text_codebook.csv",
        "coded": SOURCE / "proposed_coded_responses.csv",
        "themes": SOURCE / "proposed_theme_summary.csv",
        "reconciliation": SOURCE / "coding_reconciliation.md",
        "q81": SOURCE / "q81_analysis_draft.md",
        "q82": SOURCE / "q82_analysis_draft.md",
    }
    missing = [name for name, path in source_files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing synthesis proposals: {missing}")

    codebook = pd.read_csv(source_files["codebook"], keep_default_na=False)
    coded = pd.read_csv(source_files["coded"], keep_default_na=False)
    themes = pd.read_csv(source_files["themes"], keep_default_na=False)
    if len(codebook) != 46 or len(coded) != 52:
        raise ValueError(
            f"Unexpected synthesis sizes: codebook={len(codebook)}, coded={len(coded)}"
        )
    if coded["question_id"].value_counts().to_dict() != {"Q8.1": 26, "Q8.2": 26}:
        raise ValueError("Expected 26 reconciled responses for each question")
    unknown_themes = sorted(set(themes["theme"]) - set(THEME_BASIS))
    if unknown_themes:
        raise ValueError(f"Theme counting bases missing: {unknown_themes}")

    themes.insert(
        themes.columns.get_loc("theme") + 1,
        "counting_basis",
        themes["theme"].map(THEME_BASIS),
    )
    mismatches = []
    for row in themes.itertuples(index=False):
        observed = theme_count(coded, row.question_id, row.counting_basis)
        if observed != int(row.unique_respondents):
            mismatches.append(
                f"{row.question_id}:{row.theme}:{observed}!={row.unique_respondents}"
            )
    if mismatches:
        raise ValueError(f"Theme count mismatches: {mismatches}")

    (ROOT / "data/processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs/open_text").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs/tables").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        source_files["codebook"], ROOT / "data/processed/open_text_codebook.csv"
    )
    shutil.copyfile(
        source_files["coded"], ROOT / "outputs/open_text/open_text_coded_responses.csv"
    )
    shutil.copyfile(
        source_files["reconciliation"],
        ROOT / "outputs/open_text/coding_reconciliation.md",
    )
    shutil.copyfile(
        source_files["q81"],
        ROOT / "outputs/open_text/q81_critical_incident_analysis.md",
    )
    shutil.copyfile(
        source_files["q82"],
        ROOT / "outputs/open_text/q82_support_needs_analysis.md",
    )
    themes.to_csv(
        ROOT / "outputs/tables/open_text_theme_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    print(
        "promoted "
        f"codes={len(codebook)} coded_responses={len(coded)} themes={len(themes)}"
    )


if __name__ == "__main__":
    main()
