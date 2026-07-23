#!/usr/bin/env python3
"""Write the v2 main-agent disposition of both independent audits."""

from __future__ import annotations

from pipeline_common import ROOT, RUN_ID


RUN = ROOT / "outputs/agent_runs" / RUN_ID / "reviews"
REPORT = ROOT / "outputs/reports/review_resolution.md"


TEXT = """# 独立审查问题处理记录

## 审查范围

主代理逐项核对 Evidence Reviewer 与 Privacy and Method Reviewer 的审计。两名 reviewer 均未直接编辑初稿、canonical 数据或生成脚本。以下问题均已在生成脚本、公开产物或受限/公开分层中处理。

## Evidence Reviewer

| 编号 | 处理 | 结果 |
|---|---|---|
| EV-01 关联不确定性报告不对称 | 接受 | A2、A3、A5 补齐 bootstrap 95% CI 和置换 p；五项分析使用一致字段。 |
| EV-02 “邀请”证据范围 | 接受 | P02 公开释义改为“主动答疑和接近”，并补入支持主动接近的行号。 |
| EV-03 未定义的质性强度标签 | 接受 | “高摩擦”统一改为“多项具体摩擦叙述”，避免没有阈值的高低标签。 |
| EV-04 V2 文献等级适用范围 | 接受 | 明确旧 A/B/C 未按 V2 重分级；DP002 的跨境个案在 V2 下新具直接相关性，但不代表跨境学生。 |

## Privacy and Method Reviewer

| 编号 | 处理 | 结果 |
|---|---|---|
| PM-01 跨版本间接识别链 | 接受并作为发布门槛 | 公开终稿不再把第三个案与匿名代号、旧资格、背景—资源组合、样本位置或行号相连；其完整证据保留在受限层。公开 canonical codebook 删除退休/合并审计行，并清空归纳码的个案例证。 |
| PM-02 公开小格不一致 | 接受 | 旧资格原因只列类别不拆小格；质量警告改为“少量”；平台的小于 3 边际人数不公开；稀有程序事件不与公开个案代号连接。 |
| PM-03 资格决定时序不足 | 接受 | 研究设计、决策记录和终稿明确：人口口径在 V1 分析、审查与结果可见后改变，理由是概念范围扩大，不是资料质量纠错或显著性筛选。A1/A4 明确标为须独立复核的事后探索信号。 |
| PM-04 个别因果动词 | 接受 | 改为参与者回顾中的同时出现和关联表述；不把任务、支持或边界写成效果。 |
| PM-05 旧人口措辞残留 | 接受 | 研究设计统一为“内地—香港学校插班经历者”，并把局限改为小样本与路径异质性。 |

## 复核结果

Evidence Reviewer 核验了 35/35 样本、11 份重分类、三个唯一链接、全部已报告问卷统计和 84 条逐字编码；没有 BLOCKER 或 MAJOR。Privacy and Method Reviewer 的一个发布 BLOCKER 已通过公开最小化、代码本净化和 Git 分层解除；其余问题全部落实。

最终发布仍以自动验证、可复现性检查、公开文件隐私扫描、Git index 扫描和所有 refs 的对象路径扫描为准。受限 participant-level 数据、agent 产物、joint display、编号转录和逐字编码不得进入 Git。
"""


def main() -> None:
    for name in ["evidence_audit.md", "privacy_method_audit.md"]:
        if not (RUN / name).is_file():
            raise FileNotFoundError(RUN / name)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(TEXT, encoding="utf-8")
    print("review resolution generated")


if __name__ == "__main__":
    main()
