# 协作说明

感谢参与本项目。提交修改前，请先阅读：

1. `AGENTS.md`
2. `docs/research_design.md`
3. `docs/analysis_pipeline.md`
4. `docs/data_contract.md`
5. `notes/analysis_decisions.md`

## 工作原则

- 不修改或提交`data/raw/`和`data/interview/`。
- 不提交参与者级处理资料、逐行访谈、连接键或稀有背景组合。
- 数字结论须回到生成表，质性结论须在受限环境回到原文行段。
- 严格区分完整问卷、访谈子样本、个案内链接、跨案解释和文献背景。
- 不把回顾性横截面资料写成因果或总体结论。
- 保留空白、不适用、不能记起、不愿回答和无效回答的区别。
- 不覆盖v1—v3历史报告或既有审查记录。

## 提交流程

1. 在当前`main`基础上修改。
2. 将脚本、处理数据和生成成果分别放入规范目录。
3. 运行公开仓库检查：

   ```bash
   python3 scripts/validate_github_repository.py
   ```

4. 如果拥有完整受限环境，再运行：

   ```bash
   python3 scripts/validate_final_delivery.py
   python3 scripts/verify_reproducibility.py
   ```

5. 确认`git diff -- data/raw data/interview`为空。
6. Pull Request须说明证据来源、受影响结论、验证结果和隐私影响。

发现疑似资料泄露时，不要在Issue或Pull Request中粘贴样本内容；请按
`SECURITY.md`处理。
