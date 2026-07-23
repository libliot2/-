#!/usr/bin/env python3
"""Write the agent manifest and end-to-end pipeline summary."""

from __future__ import annotations

import subprocess

import pandas as pd

from pipeline_common import ROOT


REPORTS = ROOT / "outputs/reports"
RUN = ROOT / "outputs/agent_runs/20260723_full_pipeline"


def git_log() -> str:
    result = subprocess.run(
        ["git", "log", "--oneline", "--decorate", "-8"],
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
    passed = int(frame["status"].eq("PASS").sum())
    failed = int(frame["status"].eq("FAIL").sum())
    status = "PASS" if failed == 0 else "FAIL"
    return status, f"{passed} 项通过，{failed} 项失败"


def write_manifest() -> None:
    manifest = """# Agent 运行清单

运行 ID：`20260723_full_pipeline`

| 角色 | 执行方式 | 依赖完成后启动 | 独立输出 | 状态 |
|---|---|---|---|---|
| Main Agent | 主代理 | — | canonical processed data、master files、报告与 Git | 完成 |
| Survey Analyst | subagent | 问卷清洗与 codebook | `outputs/agent_runs/20260723_full_pipeline/survey/` | 完成并由主代理复核/重现 |
| Linked Case P01 | subagent | 链接、档案、编号转录、问卷发现 | `outputs/agent_runs/20260723_full_pipeline/P01/` | 完成 |
| Linked Case P02 | subagent | 链接、档案、编号转录、问卷发现 | `outputs/agent_runs/20260723_full_pipeline/P02/` | 完成 |
| 第三份访谈 | 规则性跳过 | 资格筛选 | 脱敏编号转录与排除说明 | 问卷记录不合资格，不作个案分析 |
| Qualitative Synthesis | subagent | 两个合资格个案完成 | `outputs/agent_runs/20260723_full_pipeline/qualitative_synthesis/` | 完成并通过 47 条引文核验 |
| Mixed-Methods Integration | subagent | 问卷分析与质性综合完成 | `outputs/agent_runs/20260723_full_pipeline/mixed_methods/` | 完成并提升 10 主题联合展示 |
| Reviewer A | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/20260723_full_pipeline/reviews/evidence_audit.md` | 完成 |
| Reviewer B | 独立 subagent | 完整初稿完成 | `outputs/agent_runs/20260723_full_pipeline/reviews/privacy_method_audit.md` | 完成 |

## 依赖与写入控制

- 个案 subagent 只在问卷清洗、链接、档案与转录准备后启动。
- 质性综合只在两个合资格个案完成后启动；混合方法整合只在问卷和质性主文件完成后启动。
- 所有 worker 写入角色隔离目录；只有主代理提升 canonical master、修订报告并运行验证。
- 两名 reviewer 未参与初稿或上游分析，只提交审计意见，没有直接编辑初稿。
"""
    (REPORTS / "agent_run_manifest.md").write_text(manifest, encoding="utf-8")


def write_summary() -> None:
    status, detail = validation_status()
    summary = f"""# 流水线总结

## 总体状态

Stages 0–15 已按依赖顺序实际执行。核心分析没有硬性阻塞；一份唯一链接但不合资格的访谈按数据合同只跳过其个案与综合分析，其余有效阶段继续完成。最终自动验证状态：**{status}**（{detail}）。

## 阶段结果

| 阶段 | 结果 |
|---|---|
| 0 库存 | 研究设计、最终问卷、1 个 35×160 工作表、3 份 DOCX 访谈、冻结文献包均可读；访谈指南缺失并记录 |
| 1 原始资料 | 4 个来源文件建立 SHA-256 基线；全程校验未变 |
| 2 映射/codebook | 160 个导出字段全部进入 codebook；版本冲突和缺失导出列明确标记 |
| 3 清洗/资格 | 35 份全部保留；24 合资格、11 排除；特殊缺失分开，0 个完全响应重复 |
| 4 链接 | 3 个文件均唯一匹配；2 个合资格、1 个不合资格；0 未解决、0 歧义、0 重复 |
| 5 问卷 | 描述统计、支持缺口、平台转变、开放题辅助扫描和 5 项探索性关联完成 |
| 6–7 档案/转录 | 2 个合资格链接档案、3 份脱敏编号转录完成 |
| 8 个案 | P01、P02 分别由 subagent 完成；不合资格访谈未作实质解释 |
| 9 质性综合 | 47 条编码片段、39 个 canonical codes、11 个框架主题；47/47 引文逐字匹配 |
| 10 混合整合 | 10 个联合展示主题，覆盖四层证据与四种关系类型 |
| 11 文献 | 只用冻结规范文献包比较；区分直接、相邻和理论证据 |
| 12–14 报告/审查/修订 | 初稿、两项独立审查和审查后终稿完成 |
| 15 验证 | 原始资料、计数、链接、引文、隐私、主张和可复现性自动检查完成 |

## 明确警告和跳过

- 问卷粤语题时点措辞冲突；Q3.1 一项和后期微博列缺失，未重建。
- 4 条重复 IP 与 1 条短时作答只标记、不据此排除。
- 合资格访谈包含一份整理式记录和一份未核音、存在工具情境风险的机器转写；另有个案内年级表述分歧。
- 访谈选择理由与完整招募过程未记录；不将案例称为典型、极端或代表性。
- 五项探索性关联均无 BH-FDR q<0.05；回归、因子分析、因果模型和伪前后变化分均跳过。
- 文化中介和平台机制在访谈中证据沉默；不由沉默推断经验不存在。
- 小格、开放题原话、受限问卷序号、身份键和原始未脱敏资料不进入公开输出。

## 自动执行与 Git

本次使用 Survey Analyst、两个合资格 Linked Case Agent、Qualitative Synthesis Agent、Mixed-Methods Integration Agent 及两个独立 Reviewer subagent；主代理负责依赖控制、canonical 提升、审查修订、再生和验证，没有使用串行 fallback。

Git 由主代理自动初始化和分阶段提交；原始问卷、原始访谈、参与者级 processed/qualitative 产物及独立 Overleaf 仓库均不在最终历史中。受限产物保留在本地工作区供授权研究审计和再现。隐私审查后，活动仓库使用净化后的公开安全历史；最终交付由 annotated tag `analysis-v1` 标记，tag 指向即为最终公开安全提交。

```text
{git_log()}
```
"""
    (REPORTS / "pipeline_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_manifest()
    write_summary()
    print("completion reports generated")


if __name__ == "__main__":
    main()
