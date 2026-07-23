# 第二轮流水线总结

## 总体状态

第二轮“独立复核与补充探索”已完成，没有从头无条件重复质性判断。四份独立审查均为 `PASS_WITH_ISSUES`、无 blocker；审查封闭后才由主agent实施补充探索、代码修复、表格再生和报告改写。

自动验证：**PASS**（46 项通过，0 项失败）。版本化复现：46 项通过，0 项失败，其中明确区分 `REGENERATED` 与 `FROZEN_ANALYTIC_INPUT_PROMOTED`。

## 数据、映射与角色

- 问卷：原始 35 份；V2 合资格 35、排除 0；旧口径 11 份重分类。
- 多选质量：Q2.10、Q3.2、Q5.4 的限选超限已逐题标记；不删除整份问卷。Q5.4 改用有效 n=34 的 endorsement，并补 n=25 合规子集。
- 链接：3 份访谈均唯一 `MATCHED`，无歧义、重复或未解决映射。
- 角色：Reviewer A/B/C 由三个独立 subagent 并行执行；Reviewer D 由主agent在不修改 canonical 的审查阶段独立完成；随后只有主agent更新 canonical 和最终报告。未使用串行 fallback。

## 第一版主要问题与实际修复

1. 发现并修复多选限额、题组特殊缺失传播、互斥组合和 codebook 母题语义。
2. 把 Q3.3 恢复为复合“信任并谈心”题，保留 P01 的直接分歧。
3. 75 条 alignment 全量重裁决为 EXPANSION 34、CONVERGENCE 21、SILENCE 11、DIVERGENCE 9。
4. 修复少量上下文截断和主码；84/84 引语仍逐字通过。
5. joint display 改为主题 × 关系类型；人物路径改为配置矩阵与单案依赖检查。
6. A4 降为 weak signal；开放题泛关键词不再解释为主题频率。
7. 公开层切断受限第三案例跨版本连接，并抑制稀有质量小格。

## 补充探索

公开表共 110 行：

- `robust finding`：Q5.5 三状态直接分布、同一个体的平台 retained/adopted/stopped/neither、平台功能题项，以及访谈平台机制沉默。
- `plausible exploratory finding`：三案样本内宽位置、Q5.4合规子集、A1替代计分、支持配置和关系层次。
- `weak signal`：A4及文化中介稳定角色，只留在稳健性/局限。
- `unsupported`：平台代表融入、支持造成归属、单一稳定路径等已删除，未进入发现表。

## 验证与隐私

- 原始 4 个来源文件 SHA-256 与基线一致。
- 35/35 资格、0 排除、11 重分类和三条唯一链接一致。
- 84 条引语逐字且说话人正确；人工语义审查问题全部在 revision log 闭环。
- 当前公开 allowlist 不含问卷序号、内部 row ID、受限第三案例代号/行号、直接标识或 n<3 数值。
- 第一轮报告由 `analysis-v2` tag 与本轮受限归档保留；当前公开报告为第二轮安全衍生版。

## Git 与版本

- 本轮起始 commit：`b737ae6d7cfe29a5b69576cde8d3e51d2953673e`
- 生成本总结时的 HEAD：`b737ae6d7cfe29a5b69576cde8d3e51d2953673e`
- 既有标签：`analysis-v1`、`analysis-v2`
- 完成标签：`analysis-v3`（在最终验证通过且工作树提交后由主agent创建）
- 分支：`main`
- merge conflict：无

最终完成 commit 由 annotated tag `analysis-v3` 唯一解析；为避免提交哈希自指，本文件不硬编码尚未产生的完成提交值。
