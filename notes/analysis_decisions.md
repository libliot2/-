# Analysis Decisions

## 2026-07-23 — Repository and source-location decisions

- The working directory was not a Git repository. A new analysis repository is
  initialised here in accordance with `docs/git_workflow.md`.
- `6a58bbb68d0662ee12b5ab75/` is a separate Overleaf Git checkout containing
  manuscript material; it is outside this analysis pipeline and is excluded
  from the analysis repository.
- The final questionnaire is present as
  `research_materials/内地迁居香港高年级插班学生的学校适应、同伴关系与数字生活调查.md`;
  this file is used in place of the absent alias
  `research_materials/questionnaire.md`.
- Survey data are present as the sole workbook under `data/raw/`, rather than
  the preferred `data/raw/survey/` subdirectory. Public audit outputs use the
  alias `SURVEY_SOURCE.xlsx` instead of the source basename.
- Interview source files are present at `data/interview/`, rather than the
  preferred `data/raw/interviews/` subdirectory. They are treated as immutable
  raw sources and included in baseline and final checksum validation without
  copying or modifying them.
- Unredacted survey and interview sources are excluded from Git to avoid
  committing potentially identifying research data. Their integrity is tracked
  through `outputs/reports/raw_file_checksums.csv`.
- Transcript-specific location terms needed for reproducible redaction are kept
  in a restricted local term file. Speaker roles are inferred from label
  recurrence and turn counts, so no speaker name or platform handle is
  hard-coded in committed scripts.

## 2026-07-23 — Survey mapping and eligibility decisions

- The workbook export contains 160 columns and 35 submissions. Administrative
  identifiers and quasi-identifiers (user ID, exact timestamp, source detail,
  IP, and remarks) are used only for restricted quality checks and excluded
  from `survey_clean.csv`.
- Eligibility requires consent, at least two continuous Mainland school years,
  actual residence migration to Hong Kong, first local-school transfer at S2
  or above, and age 18 or older. No quality flag alone causes exclusion.
- Q2.11 has conflicting time wording: the final questionnaire says
  "before coming to Hong Kong" while the export says "initial transfer
  period". It is retained as a timing-uncertain background item and excluded
  from temporal comparisons.
- Missing export columns (Q3.1 item 6, later-period Weibo, and several
  "unwilling to answer" multiple-choice flags) are not reconstructed.
- Public-facing linkage reports suppress questionnaire sequence numbers even
  though the internal mapping table retains them. This resolves the apparent
  tension between linkage auditing and the stricter public-output privacy rule.
- Two interview files link uniquely to eligible survey records. The third links
  uniquely to an ineligible record whose first Hong Kong local-school entry was
  below S2. Its transcript is prepared for audit, but it is excluded from
  linked-case interpretation and cross-case synthesis.
- Agent run ID: `20260723_full_pipeline`.

## 2026-07-23 — Survey-analysis decisions

- Four item groups are retained only as exploratory descriptive indicators:
  peer-cultural boundary, later school belonging, initial academic-adaptation
  difficulty, and later academic-rule understanding. A participant score
  requires at least 80% non-special item responses. Internal-consistency
  diagnostics do not validate these self-designed groups.
- Brokerage participation, brokerage burden, and platform function are not
  combined into scores because their items describe conceptually different
  dimensions.
- Counts of Q5.5 support statuses require at least seven valid responses across
  the eight support items. Special missing and not-applicable values remain
  missing and never contribute an implicit zero. This 80% rule was adopted
  after independent evidence review and all A3-dependent outputs were rerun.
- Five research-question-driven Spearman associations were specified. Their
  uncertainty was assessed by bootstrap confidence intervals and permutation
  tests, followed by BH-FDR correction. None had q<0.05; all remain descriptive
  prompts for interpretation rather than confirmed statistical relationships.
- Regression, factor analysis, causal contrasts, and non-equivalent
  initial-versus-later change scores are skipped as unsupported.

## 2026-07-23 — Linked-case and qualitative decisions

- Only the two eligible anonymous cases enter linked-case and cross-case
  analysis. The remaining uniquely linked but ineligible interview remains in
  restricted transcript-preparation and linkage audit outputs only.
- P01 is a summary-style interview record, so only its lines labelled
  `Participant` may be quoted and no coded segment exceeds medium confidence.
  P02 is an unverified machine transcript and likewise has a maximum of medium
  confidence.
- P02's interview preamble records that the interviewer initially loaded an
  incorrect questionnaire. The filename-based unique linkage is preserved,
  while all content dependent on prompted questionnaire recall is treated
  cautiously.
- P02's survey entry grade and interview self-report conflict. Neither value is
  overwritten, and the discrepancy remains an explicit divergence.
- The canonical qualitative synthesis retains five proposed process codes:
  `SUPPORT_SAFETY_CIRCLE_TRADEOFF`, `GRADUAL_ADAPTATION_PATH`,
  `PEER_COMMUNICATION_PROXY`, `POST_EXIT_TIE_RECONFIGURATION`, and
  `NON_INTRUSIVE_SUPPORT_PREFERENCE`. Narrower or potentially psychological
  labels were merged into broader descriptive codes.
- Cultural brokerage and platform-role claims remain survey-supported but
  interview-silent. Interview silence is not interpreted as evidence that the
  experience did not occur.
