# 开放题第五轮共享架构

## 证据层

1. 完整问卷封闭题：35份有效问卷；
2. 完整问卷开放题子样本：Q8.1与Q8.2各自的可分析回答者；
3. 三份链接访谈：只作个案内三源对照及过程扩展；
4. 文献背景：只作解释资源。

不得跨层替代证据。开放题“主动提及人数”不是经历率；未提及或空白不表示没有经历。

## ID与隐私

- `internal_response_id`、`survey_row_id`、问卷序号、参与者ID和原文只在受限文件中出现。
- `public_text_id`格式为`OT-Rxx-Q81`或`OT-Rxx-Q82`，`public_respondent_id`格式为`Rxx`；`Rxx`由内部行ID的加盐哈希排序产生，与问卷序号及原始行序无关。同一回答者的两题共享`Rxx`。
- 公开摘录必须逐字、去识别且不拼接；改写内容只能标为“释义”。

## 独立编码文件

两名编码代理的`coded_responses.csv`统一包含：

```text
internal_response_id
public_text_id
question_id
analyzable
semantic_summary
proposed_codes
event_direction
scene
actors
actions
emotion_or_evaluation
immediate_outcome
later_impact
turning_point
negative_or_contrasting_case
exact_excerpt
researcher_inference
alternative_explanation
confidence
```

- 多代码用`;`分隔；`confidence`仅允许`HIGH`、`MEDIUM`、`LOW`。
- `semantic_summary`是分析概括，不得加引号。
- 没有适用代码时保留该行，并写明理由。
- Agent A的代码须从文本生成；Agent B可使用现有代码本与理论，但必须保留`UNCLASSIFIABLE`或新代码。

Agent A的`proposed_codes.csv`与正式代码本字段一致：

```text
code_id,code_name,definition,include_when,exclude_when,example_excerpt,example_text_id,
inductive_or_deductive,related_research_question,related_theory,status,notes
```

公开代码本的`example_excerpt`只能使用正式逐回答文件中已批准为
`VERBATIM_SAFE`的连续子串，并在`example_text_id`记录来源；没有安全例句时两栏均留空。

Agent B的`framework_fit.csv`包含：

```text
framework,question_id,evidence_text_ids,fit,what_it_explains,
what_it_misses,rival_explanation,overinterpretation_risk
```

`fit`只允许`strong fit`、`moderate fit`、`weak fit`、`not supported`。

## 正式逐回答编码

`outputs/open_text/open_text_coded_responses.csv`至少包含：

```text
internal_response_id
public_text_id
public_respondent_id
question_id
original_response
analyzable
exclusion_or_warning
final_codes
event_direction
scene
actors
actions
emotion_or_evaluation
immediate_outcome
later_impact
turning_point
support_target
support_type
unmet_need
agency_expectation
negative_or_contrasting_case
deidentified_excerpt
excerpt_status
analytic_summary
theoretical_interpretation
researcher_inference
alternative_explanation
coding_confidence
review_status
```

`excerpt_status`只允许`VERBATIM_SAFE`、`PARAPHRASE_ONLY`、`NO_PUBLIC_EXCERPT`。

## 计数与整合

- 主题计数单位是`public_respondent_id`，同一问题、同一主题每人最多一次。
- Q8.1和Q8.2分别使用各自可分析回答数作分母。
- 开放—封闭对照和开放题—访谈对照只允许
  `CONVERGENCE`、`EXPANSION`、`DIVERGENCE`、`SILENCE`。
- `DIVERGENCE`须同时满足构念相同、时间范围重叠和方向相反；限选题未勾选不视为否定。
- 每条整合判断必须记录原变量、证据ID、解释、替代解释和置信度。

开放题—封闭题对照文件统一包含：

```text
public_text_id
public_respondent_id
question_id
open_text_codes
closed_question_id
closed_variable
closed_response
relationship_type
alignment_rationale
alternative_explanation
confidence
review_status
```

开放题—访谈对照文件统一包含：

```text
public_text_id
linked_interview_participant
question_id
open_text_summary
closed_question_id
closed_evidence
transcript_file
transcript_line_start
transcript_line_end
transcript_evidence_summary
relationship_type
alignment_rationale
alternative_explanation
confidence
review_status
```

- 每条可分析开放回答至少有一条与相关封闭题的语义对照，不以全变量机械配对代替判断。
- 三名链接访谈者的两道开放题共6条回答均须进入三源对照。
- `confidence`仅允许`HIGH`、`MEDIUM`、`LOW`；`review_status`记录主agent是否核验。
- 最终文件的`review_status`只允许`MAIN_AGENT_VERIFIED`或`REVIEWER_RESOLVED`，不得残留`AGENT_PROPOSED`或仅有综合代理裁决状态。
- `event_direction=MIXED`只表示同一回答含有两个方向；须另用代码区分“持续并存”和“先有距离后转为进入”。

## 结论登记的开放题证据层

`findings_register.csv`使用`survey open-text sub-sample`指Q8.1或Q8.2的26名自选作答者；它不能替换`complete survey sample`。同时使用35份封闭题与开放题时须并列两个范围。
