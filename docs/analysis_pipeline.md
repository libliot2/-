# Analysis Pipeline

## 1. Purpose

This document defines the end-to-end automated pipeline for the linked survey-interview study.

The design is not based on two independent datasets. The interview participants were selected from the questionnaire sample. The pipeline must therefore:

1. analyse the complete questionnaire sample;
2. link each interview file to its questionnaire record;
3. construct linked survey-interview cases;
4. analyse the linked cases;
5. compare cases;
6. integrate the case findings with the complete-sample survey findings.

Run the pipeline automatically when the required files are readable. Skip only analyses that are unsupported by the data and record why.

---

## 2. Multi-agent workflow

Use subagents when supported. If subagents are unavailable, execute the same roles sequentially and record the fallback in `outputs/reports/pipeline_summary.md`.

### Roles

- **Main Agent**: defines shared schemas, controls stage dependencies, integrates outputs, and writes the final report.
- **Survey Analyst**: cleans and analyses the complete questionnaire sample.
- **Linked Case Agent P01/P02/P03**: analyses one linked questionnaire-interview case.
- **Qualitative Synthesis Agent**: compares the linked cases and reconciles codes.
- **Mixed-Methods Integration Agent**: integrates complete-sample and linked-case evidence.
- **Evidence Reviewer**: audits numbers, quotations, mappings, and evidential support.
- **Privacy and Method Reviewer**: audits disclosure risk, overclaiming, conceptual bias, and method–conclusion fit.

### Orchestration rules

1. The Main Agent must define the survey codebook, linkage table schema, and qualitative coding schema before delegation.
2. Dependent stages must wait for their inputs.
3. Worker agents must write to separate directories under:

```text
outputs/agent_runs/<run_id>/
```

4. Only the Main Agent may update canonical master files and final reports.
5. Reviewer agents must not edit the draft directly.
6. The Main Agent must apply valid review findings before final delivery.
7. Do not run multiple agents to write competing full reports.

---

## 3. Stage 0: repository inventory

Inspect the repository and verify the presence of:

- `docs/research_design.md`
- `research_materials/questionnaire.md`
- survey export under `data/raw/survey/`
- interview files under `data/raw/interviews/`
- `research_materials/interview_guide.md`, if available
- literature context under `docs/literature_context/`, if available
- `notes/analysis_decisions.md`, if available

Report:

- available and missing files;
- file sizes and formats;
- survey workbook sheet names;
- survey row and column counts;
- apparent number of submissions;
- interview file count;
- transcript encoding and format;
- whether transcripts appear anonymised;
- warnings and missing prerequisites.

Create:

```text
outputs/reports/repository_inventory.md
```

Do not stop after inventory unless missing or unreadable files make valid analysis impossible.

---

## 4. Stage 1: preserve raw data

Compute checksums for all files under `data/raw/`.

Create:

```text
outputs/reports/raw_file_checksums.csv
```

Fields:

```text
relative_path
file_size
modified_time
hash_algorithm
file_hash
```

These checksums are the baseline for later validation. Never modify raw files.

---

## 5. Stage 2: questionnaire mapping and codebook

Read the final questionnaire and inspect the survey export.

Map each spreadsheet column to the corresponding questionnaire item.

Identify:

- questionnaire sequence/index column;
- platform metadata;
- screening items;
- demographic items;
- single-choice items;
- multiple-choice items;
- matrix items;
- numeric items;
- open-text items.

Create:

```text
data/processed/survey_codebook.csv
outputs/reports/survey_mapping_report.md
```

Suggested codebook fields are defined in `docs/data_contract.md`.

Do not guess uncertain mappings. Mark them as unresolved.

---

## 6. Stage 3: survey cleaning and eligibility filtering

Create a processed copy while preserving every raw row.

Tasks:

1. standardise variable names;
2. normalise whitespace and obvious formatting problems;
3. preserve distinct special-response categories;
4. check malformed values;
5. check possible duplicates where defensible;
6. apply eligibility criteria from the questionnaire and research design;
7. document every exclusion reason;
8. expand multiple-choice items into binary variables when useful;
9. preserve original open-text responses.

Create:

```text
data/processed/survey_clean.csv
outputs/tables/sample_flow.csv
outputs/reports/data_quality_report.md
```

The report must include:

- total submissions;
- eligible sample;
- exclusions by reason;
- missingness by item;
- malformed or impossible values;
- duplicate checks;
- unresolved issues.

---

## 7. Stage 4: interview-survey linkage

The questionnaire sequence number is encoded in each interview filename.

For each interview file:

1. extract the sequence number using the filename convention;
2. match it to the survey sequence/index column;
3. assign an anonymous participant ID;
4. verify a unique match;
5. verify the linked record satisfies eligibility criteria;
6. record unresolved or ambiguous cases.

Create:

```text
data/processed/interview_survey_map.csv
outputs/reports/linkage_report.md
```

Do not guess ambiguous mappings. Do not expose questionnaire sequence numbers in public-facing outputs.

---

## 8. Stage 5: complete-sample survey analysis

Run one Survey Analyst.

### 8.1 Sample description

Analyse:

- current status;
- current residence;
- gender;
- school-entry year;
- time in Hong Kong schools;
- school transfers;
- school type;
- language of instruction;
- prior schooling region;
- migration reasons;
- Cantonese before arrival;
- language use during the later school period.

Create:

```text
outputs/tables/sample_characteristics.csv
outputs/reports/sample_description.md
```

### 8.2 Item-level thematic analysis

Analyse:

1. initial peer-cultural boundaries;
2. later school belonging;
3. identity negotiation and cultural brokerage;
4. initial educational adaptation difficulties;
5. later academic-rule understanding;
6. support resources and unmet needs;
7. digital-platform use and change;
8. later peer-network structure;
9. open-ended survey responses.

Create:

```text
outputs/tables/survey_item_statistics.csv
outputs/tables/support_gap_analysis.csv
outputs/tables/platform_transition_analysis.csv
outputs/reports/survey_findings.md
```

Report:

- valid n;
- frequencies and percentages;
- medians and interquartile ranges;
- special-response counts;
- effect sizes and uncertainty where appropriate.

### 8.3 Exploratory constructs

Only construct composite indicators when:

- items are conceptually coherent;
- response directions are consistent;
- missingness is manageable;
- sample size is adequate.

Possible exploratory groupings:

- peer-cultural boundary;
- school belonging;
- educational adaptation difficulty;
- academic-rule understanding;
- cultural-brokerage participation;
- cultural-brokerage pressure;
- platform functional differentiation.

Create:

```text
outputs/tables/exploratory_constructs.csv
outputs/reports/construct_assessment.md
```

Do not call these validated scales.

### 8.4 Exploratory associations

Select a small number of analyses tied directly to the research questions.

Possible relationships:

- peer-cultural boundaries and school belonging;
- initial educational difficulty and later rule understanding;
- support resources and school belonging;
- prior Cantonese and language-related peer barriers;
- cultural-brokerage participation and pressure;
- platform differentiation and peer-network structure.

Prefer methods suited to sample size and variable type, such as:

- Spearman correlation;
- Fisher’s exact test;
- Mann–Whitney test;
- permutation or exact methods.

Create:

```text
outputs/tables/exploratory_associations.csv
outputs/reports/exploratory_analysis.md
```

Skip unsupported tests and explain why. Use association language, not causal language.

---

## 9. Stage 6: linked case profiles

Create one profile per successfully linked interviewee.

Each profile should contain:

- anonymous participant ID;
- restricted internal questionnaire sequence;
- background variables;
- responses to core questionnaire themes;
- survey open-text responses;
- position relative to the full sample;
- interview file;
- documented selection rationale, if available;
- unresolved linkage or data-quality issues.

Create:

```text
data/processed/linked_cases/P01_profile.md
data/processed/linked_cases/P02_profile.md
data/processed/linked_cases/P03_profile.md
```

Distinguish:

- direct survey responses;
- derived exploratory indicators;
- comparisons with the full sample;
- unavailable information.

Do not label a participant “high” or “low” without a documented rule.

---

## 10. Stage 7: transcript preparation

For each transcript:

1. create an analysis-ready copy;
2. preserve original wording;
3. standardise speaker labels;
4. add stable line or paragraph numbers;
5. mask direct identifiers;
6. record uncertain redactions.

Create:

```text
data/processed/interviews/interview_P01_numbered.md
data/processed/interviews/interview_P02_numbered.md
data/processed/interviews/interview_P03_numbered.md
outputs/reports/transcript_preparation_report.md
```

Do not silently rewrite participant speech.

---

## 11. Stage 8: parallel linked-case analysis

After survey cleaning, linkage, profiles, and transcript preparation are complete, run one Linked Case Agent per participant.

Each agent must read:

- the participant’s linked profile;
- the participant’s numbered transcript;
- `docs/research_design.md`;
- the shared qualitative schema;
- the survey findings summary;
- literature context only when needed.

Each case analysis must answer:

1. What is the participant’s adaptation trajectory?
2. Which interview passages explain questionnaire responses?
3. Where do survey and interview data converge?
4. Where do they diverge?
5. Could divergence reflect timing, interpretation, recall, or wording?
6. What were the main turning points?
7. What support was useful, absent, or ineffective?
8. How did peer boundaries, academic rules, identity, and platforms interact?
9. What alternative non-cultural explanations are plausible?
10. What does the interview add beyond the questionnaire?

Each agent creates:

```text
outputs/agent_runs/<run_id>/P01/case_memo.md
outputs/agent_runs/<run_id>/P01/coded_segments.csv
outputs/agent_runs/<run_id>/P01/survey_interview_alignment.csv
outputs/agent_runs/<run_id>/P01/suggested_new_codes.csv
```

Use equivalent paths for other participants.

Every coded segment must follow `docs/data_contract.md`.

---

## 12. Stage 9: qualitative synthesis

After all Linked Case Agents finish, run one Qualitative Synthesis Agent.

Tasks:

1. compare the case memos;
2. reconcile suggested codes;
3. identify shared processes and contrasting pathways;
4. distinguish similar survey profiles with different explanations;
5. distinguish different survey profiles produced by similar events;
6. identify turning points, negative cases, and contradictions;
7. preserve participant IDs and transcript line ranges;
8. avoid prevalence claims from three cases.

Create:

```text
data/processed/qualitative_codebook.csv
outputs/qualitative/framework_matrix.csv
outputs/qualitative/coded_segments_master.csv
outputs/reports/cross_case_analysis.md
```

---

## 13. Stage 10: mixed-methods integration

After survey analysis and qualitative synthesis are complete, run one Mixed-Methods Integration Agent.

Integrate at four levels:

1. complete questionnaire sample;
2. position of interviewees within that sample;
3. within-case survey-interview alignment;
4. cross-case qualitative comparison.

For each major topic, identify:

- survey evidence;
- linked-case evidence;
- relationship type;
- integrated interpretation;
- alternative explanations;
- limitations.

Relationship types:

- **convergence**
- **expansion**
- **divergence**
- **silence**

Create:

```text
outputs/tables/joint_display.csv
outputs/reports/integrated_findings.md
```

Do not treat the interviewees as statistically representative of the full sample.

---

## 14. Stage 11: literature comparison

Use canonical literature context to compare, not replace, current findings.

For each major finding:

1. state what current data show;
2. identify relevant prior findings;
3. distinguish direct Hong Kong evidence from adjacent or theoretical evidence;
4. classify the relationship as supporting, extending, complicating, or differing;
5. avoid importing literature claims into the sample.

Create:

```text
outputs/reports/literature_comparison.md
```

---

## 15. Stage 12: draft report

The Main Agent creates:

```text
outputs/reports/draft_report.md
```

Recommended structure:

1. research purpose;
2. sample and recruitment;
3. questionnaire-interview linkage;
4. methods;
5. data quality;
6. complete-sample survey findings;
7. linked case profiles;
8. cross-case findings;
9. mixed-methods integration;
10. literature comparison;
11. contradictions and negative cases;
12. limitations;
13. cautious implications;
14. reproducibility note.

Use Chinese unless instructed otherwise.

---

## 16. Stage 13: independent review

Run two reviewer subagents in parallel.

### Evidence Reviewer

Audit:

- survey counts;
- eligibility and exclusions;
- linkage mappings;
- quotations and line ranges;
- claims against evidence;
- causal or prevalence overstatement;
- literature support;
- consistency between report, tables, and figures.

Create:

```text
outputs/agent_runs/<run_id>/reviews/evidence_audit.md
```

### Privacy and Method Reviewer

Audit:

- direct and indirect identifiers;
- exposed questionnaire sequence numbers;
- small-cell disclosure risk;
- overgeneralisation from the interview sub-sample;
- misuse of exploratory constructs;
- cultural essentialism;
- unsupported identity or psychological inference;
- fit between methods and conclusions;
- whether alternative explanations were considered.

Create:

```text
outputs/agent_runs/<run_id>/reviews/privacy_method_audit.md
```

Reviewers must not edit the draft directly.

---

## 17. Stage 14: final revision

The Main Agent must:

1. read both review reports;
2. verify each issue;
3. revise, weaken, or remove unsupported claims;
4. regenerate affected tables when needed;
5. ensure public outputs hide questionnaire sequence numbers;
6. produce:

```text
outputs/reports/final_report.md
```

The report must distinguish:

- complete-sample findings;
- interview-sub-sample findings;
- within-case linked findings;
- cross-case interpretations;
- literature-based interpretation.

---

## 18. Stage 15: validation and completion

Run automated checks for:

- unchanged raw-file checksums;
- reproducible processed outputs;
- consistent sample counts;
- traceable exclusions;
- unique and valid linkage mappings;
- verbatim quotations in source transcripts;
- qualitative claims linked to participant and line range;
- quantitative claims linked to generated tables;
- absence of unsupported causal language;
- absence of direct or indirect identifiers;
- absence of questionnaire sequence numbers in public outputs;
- complete reporting of warnings and skipped analyses.

Create:

```text
outputs/reports/validation_report.md
outputs/reports/pipeline_summary.md
outputs/reports/agent_run_manifest.md
```

If a claim fails validation, remove or weaken it automatically.

Stop the full pipeline only when missing, unreadable, unsafe, or irreconcilably ambiguous data make valid analysis impossible.
