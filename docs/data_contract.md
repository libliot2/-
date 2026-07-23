# Data Contract

## 1. Purpose

This document defines the canonical data structures used by the automated analysis pipeline.

All agents must use these schemas. Do not create incompatible alternatives without recording the change in `notes/analysis_decisions.md`.

---

## 2. Canonical locations

### Raw data

```text
data/raw/survey/
data/raw/interviews/
```

Raw files are immutable.

### Processed data

```text
data/processed/
```

### Generated results

```text
outputs/tables/
outputs/qualitative/
outputs/reports/
outputs/agent_runs/
```

### Canonical master files

Only the Main Agent may update:

```text
data/processed/survey_codebook.csv
data/processed/survey_clean.csv
data/processed/interview_survey_map.csv
data/processed/qualitative_codebook.csv
outputs/qualitative/coded_segments_master.csv
outputs/tables/joint_display.csv
outputs/reports/final_report.md
outputs/reports/validation_report.md
notes/analysis_decisions.md
```

---

## 3. Missing-value contract

The following meanings must remain distinct:

```text
BLANK
NOT_APPLICABLE
CANNOT_REMEMBER
UNWILLING_TO_ANSWER
INVALID_RESPONSE
```

Do not collapse them into one generic missing value in the canonical processed data.

Analysis-specific scripts may derive a temporary analytic missing value, but the original category must remain recoverable.

---

## 4. Survey codebook schema

File:

```text
data/processed/survey_codebook.csv
```

Required fields:

```text
variable_name
question_id
question_text
item_text
response_type
allowed_values
special_missing_codes
source_column
analysis_role
notes
```

### Field definitions

- `variable_name`: stable machine-readable name.
- `question_id`: questionnaire identifier such as `Q3.1_1`.
- `question_text`: parent question text.
- `item_text`: matrix item or option text, when applicable.
- `response_type`: one of `screening`, `single_choice`, `multiple_choice`, `matrix`, `numeric`, `open_text`, `metadata`.
- `allowed_values`: valid response values.
- `special_missing_codes`: applicable special missing categories.
- `source_column`: original spreadsheet column.
- `analysis_role`: construct or analytic purpose.
- `notes`: uncertainty, recoding rule, or warning.

---

## 5. Clean survey schema

File:

```text
data/processed/survey_clean.csv
```

Rules:

1. preserve one row per raw submission;
2. include a stable internal `survey_row_id`;
3. preserve the questionnaire sequence/index value;
4. retain eligibility fields and exclusion reason;
5. preserve original open-text responses;
6. use standardised variable names;
7. keep raw special-response meaning recoverable;
8. do not expose questionnaire sequence numbers in public outputs.

Minimum administrative fields:

```text
survey_row_id
questionnaire_sequence
eligible
exclusion_reason
duplicate_flag
data_quality_flag
```

---

## 6. Interview filename linkage

The questionnaire sequence number is encoded in the interview filename.

Preferred filename form:

```text
interview_q012.md
interview_q027.md
interview_q041.md
```

The parser should extract the integer following `q`.

If filenames use another convention, the parser may use a documented alternative rule.

Do not guess when:

- more than one plausible numeric token exists;
- no exact survey match exists;
- more than one survey record matches.

---

## 7. Interview-survey mapping schema

File:

```text
data/processed/interview_survey_map.csv
```

Required fields:

```text
participant_id
interview_filename
questionnaire_sequence
survey_row_id
mapping_status
mapping_notes
```

Allowed `mapping_status` values:

```text
MATCHED
UNRESOLVED
AMBIGUOUS
DUPLICATE
INELIGIBLE
```

Rules:

- `participant_id` uses anonymous IDs such as `P01`.
- `questionnaire_sequence` is restricted internal linkage data.
- public reports must not reproduce questionnaire sequence numbers.
- linked-case analysis may proceed only for `MATCHED` and eligible records.

---

## 8. Linked case profile

Files:

```text
data/processed/linked_cases/P01_profile.md
```

Required sections:

```text
Participant ID
Linkage status
Survey background
Core questionnaire responses
Survey open-text responses
Derived exploratory indicators
Position relative to full sample
Interview source
Selection rationale
Data-quality or interpretation warnings
```

Rules:

- distinguish direct responses from derived indicators;
- do not use “high” or “low” without a documented threshold;
- do not include direct identifiers;
- questionnaire sequence belongs only in a restricted internal section.

---

## 9. Numbered transcript format

Files:

```text
data/processed/interviews/interview_P01_numbered.md
```

Recommended format:

```text
[L0001] Interviewer: ...
[L0002] Participant: ...
```

Rules:

- line numbers must remain stable after creation;
- preserve original wording;
- mark redactions explicitly, for example `[学校名称已隐去]`;
- do not silently paraphrase;
- use the numbered transcript as the canonical source for qualitative citations.

---

## 10. Qualitative codebook schema

File:

```text
data/processed/qualitative_codebook.csv
```

Required fields:

```text
code_id
code_name
parent_code
definition
include_when
exclude_when
example
source
status
notes
```

Allowed `source` values:

```text
DEDUCTIVE
INDUCTIVE
MIXED
```

Allowed `status` values:

```text
ACTIVE
MERGED
RETIRED
PROPOSED
```

Suggested top-level domains:

- migration background and prior resources;
- educational-system discontinuity;
- peer-cultural boundaries;
- adaptation strategies and agency;
- cultural brokerage;
- digital-platform practices;
- support resources;
- belonging and identity outcomes;
- contradictions and negative cases.

---

## 11. Coded segment schema

Worker-agent files:

```text
outputs/agent_runs/<run_id>/P01/coded_segments.csv
```

Canonical merged file:

```text
outputs/qualitative/coded_segments_master.csv
```

Required fields:

```text
participant_id
source_file
line_start
line_end
exact_quote
primary_code
secondary_code
time_period
analytic_note
alternative_explanation
confidence
```

Allowed `confidence` values:

```text
HIGH
MEDIUM
LOW
```

Rules:

- `exact_quote` must be verbatim;
- `line_start` and `line_end` must locate the quotation;
- do not infer absence because a topic was not mentioned;
- allow multiple codes when justified;
- code frequency is not equivalent to importance.

---

## 12. Survey-interview alignment schema

File:

```text
outputs/agent_runs/<run_id>/P01/survey_interview_alignment.csv
```

Required fields:

```text
participant_id
survey_variable
survey_response
interview_line_start
interview_line_end
interview_evidence
relationship_type
interpretation
alternative_explanation
confidence
```

Allowed `relationship_type` values:

```text
CONVERGENCE
EXPANSION
DIVERGENCE
SILENCE
```

Definitions:

- `CONVERGENCE`: survey and interview support a similar interpretation.
- `EXPANSION`: interview explains or deepens the survey response.
- `DIVERGENCE`: survey and interview point in different directions.
- `SILENCE`: one source contains relevant evidence and the other does not.

---

## 13. Framework matrix schema

File:

```text
outputs/qualitative/framework_matrix.csv
```

Required fields:

```text
theme
P01_summary
P01_evidence
P02_summary
P02_evidence
P03_summary
P03_evidence
shared_pattern
difference_or_negative_case
alternative_explanation
```

Do not convert three cases into prevalence claims.

---

## 14. Joint display schema

File:

```text
outputs/tables/joint_display.csv
```

Required fields:

```text
analytic_topic
survey_evidence
interview_subsample_position
linked_case_evidence
relationship_type
integrated_interpretation
alternative_explanations
limitations
source_files
```

Allowed `relationship_type` values:

```text
CONVERGENCE
EXPANSION
DIVERGENCE
SILENCE
```

---

## 15. Evidence traceability

Every quantitative claim must identify:

- source table;
- valid sample size;
- variable or question;
- statistic.

Every qualitative claim must identify:

- participant ID;
- transcript file;
- line range;
- exact quotation or clearly marked paraphrase.

Every literature comparison must identify:

- canonical literature record or citation;
- evidence level when available;
- whether it is direct, adjacent, or theoretical evidence.

Unsupported claims must be removed or weakened.

---

## 16. Public-output restrictions

Public-facing outputs must not contain:

- questionnaire sequence numbers;
- direct identifiers;
- identity keys;
- unredacted transcripts;
- private messages or screenshots;
- rare identifying combinations;
- small-cell details that create disclosure risk.

The internal linkage table is restricted and must not be reproduced in public reports.
