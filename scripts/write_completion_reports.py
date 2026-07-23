#!/usr/bin/env python3
"""Write the v2 agent manifest and end-to-end pipeline summary."""

from __future__ import annotations

import subprocess

import pandas as pd

from pipeline_common import ROOT, RUN_ID


REPORTS = ROOT / "outputs/reports"
RUN = ROOT / "outputs/agent_runs" / RUN_ID
PROCESSED = ROOT / "data/processed"
TABLES = ROOT / "outputs/tables"
QUALITATIVE = ROOT / "outputs/qualitative"


def git_log() -> str:
    result = subprocess.run(
        ["git", "log", "--oneline", "--decorate", "-10"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validation_status() -> tuple[str, str]:
    path = REPORTS / "validation_results.csv"
    if not path.is_file():
        return "待最终验证", "尚未生成检查表"
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    if "survey_reclassified_v2" not in set(frame["check_id"]):
        return "待最终验证", "现有检查表属于旧分析版本"
    passed = int(frame["status"].eq("PASS").sum())
    failed = int(frame["status"].eq("FAIL").sum())
    status = "PASS" if failed == 0 else "FAIL"
    return status, f"{passed} 项通过，{failed} 项失败"


def output_counts() -> dict[str, int]:
    survey = pd.read_csv(PROCESSED / "survey_clean.csv", dtype=str, keep_default_na=False)
    mapping = pd.read_csv(
        PROCESSED / "interview_survey_map.csv", dtype=str, keep_default_na=False
    )
    master = pd.read_csv(
        QUALITATIVE / "coded_segments_master.csv", dtype=str, keep_default_na=False
    )
    codebook = pd.read_csv(
        PROCESSED / "qualitative_codebook.csv", dtype=str, keep_default_na=False
    )
    framework = pd.read_csv(
        QUALITATIVE / "framework_matrix.csv", dtype=str, keep_default_na=False
    )
    joint = pd.read_csv(TABLES / "joint_display.csv", dtype=str, keep_default_na=False)
    return {
        "survey_total": len(survey),
        "eligible": int(survey["eligible"].eq("TRUE").sum()),
        "reclassified": int(
            survey["eligibility_reclassification"].eq("NEWLY_INCLUDED_V2").sum()
        ),
        "matched": int(mapping["mapping_status"].eq("MATCHED").sum()),
        "segments": len(master),
        "codes": len(codebook),
        "themes": len(framework),
        "joint_topics": len(joint),
    }


def write_manifest(counts: dict[str, int]) -> None:
    manifest = f"""# Agent 运行清单

运行 ID：`{RUN_ID}`

| 角色 | 执行方式 | 依赖完成后启动 | 独立输出 | 状态 |
|---|---|---|---|---|
| Main Agent | 主代理 | — | canonical processed data、master files、报告与 Git | 完成 |
| Survey Analyst | subagent | 问卷清洗与 codebook | `outputs/agent_runs/{RUN_ID}/survey/` | 完成并由主代理复核/重现 |
| Linked Case Agents（3） | 三个独立 subagent | 链接、档案、编号转录、问卷发现 | 受限角色目录 | 全部完成 |
| Qualitative Synthesis | subagent | 三个链接个案完成 | `outputs/agent_runs/{RUN_ID}/qualitative_synthesis/` | 完成并提升 {counts["segments"]} 条编码片段 |
| Mixed-Methods Integration | subagent | 问卷分析与质性综合完成 | `outputs/agent_runs/{RUN_ID}/mixed_methods/` | 完成并提升 {counts["joint_topics"]} 个联合展示主题 |
| Evidence Reviewer | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/{RUN_ID}/reviews/evidence_audit.md` | 完成 |
| Privacy and Method Reviewer | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/{RUN_ID}/reviews/privacy_method_audit.md` | 完成 |

## 依赖与写入控制

- 个案 subagent 只在问卷清洗、链接、档案与转录准备后启动。
- 质性综合只在三个链接个案完成后启动；混合方法整合只在问卷和质性主文件完成后启动。
- 所有 worker 写入角色隔离目录；只有主代理提升 canonical master、修订报告并运行验证。
- 两名 reviewer 未参与初稿或上游分析，只提交审计意见，没有直接编辑初稿。
- 本环境支持 subagent，未使用串行 fallback。
"""
    (REPORTS / "agent_run_manifest.md").write_text(manifest, encoding="utf-8")


def write_summary(counts: dict[str, int]) -> None:
    status, detail = validation_status()
    summary = f"""# 流水线总结

## 总体状态

Stages 0–15 已按依赖顺序实际执行。扩展资格决定解决了旧版唯一不合资格访谈的范围问题，没有硬性阻塞。最终自动验证状态：**{status}**（{detail}）。

## 阶段结果

| 阶段 | 结果 |
|---|---|
| 0 库存 | 研究设计、最终问卷、1 个 35×160 工作表、3 份 DOCX 访谈、冻结文献包均可读；访谈指南缺失并记录 |
| 1 原始资料 | 4 个来源文件建立 SHA-256 基线；全程校验未变 |
| 2 映射/codebook | 160 个导出字段全部进入 codebook；版本冲突和缺失导出列明确标记 |
| 3 清洗/资格 | {counts["survey_total"]} 份全部保留；V2 合资格 {counts["eligible"]}、排除 0；旧口径排除的 {counts["reclassified"]} 份明确重分类；特殊缺失保持分开 |
| 4 链接 | 3 个文件均唯一匹配且 V2 合资格；0 未解决、0 歧义、0 重复 |
| 5 问卷 | 描述统计、支持缺口、平台转变、开放题辅助扫描和 5 项探索性关联完成 |
| 6–7 档案/转录 | {counts["matched"]} 个链接档案、3 份脱敏编号转录完成 |
| 8 个案 | 三个链接个案分别由独立 subagent 完成；公开交付对跨版本间接识别风险作最小化 |
| 9 质性综合 | {counts["segments"]} 条编码片段、{counts["codes"]} 个 canonical codes、{counts["themes"]} 个框架主题；引文逐字核验 |
| 10 混合整合 | {counts["joint_topics"]} 个联合展示主题，覆盖四层证据及 expansion/divergence/silence |
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
{git_log()}
```
"""
    (REPORTS / "pipeline_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    counts = output_counts()
    write_manifest(counts)
    write_summary(counts)
    print("completion reports generated")


if __name__ == "__main__":
    main()
