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

## 2026-07-23 — Expanded eligibility decision (analysis v2)

- The investigator explicitly broadened the target from the earlier
  high-grade, resident-migrant definition to all respondents with a
  Mainland-to-Hong Kong school-transfer experience.
- The former thresholds of at least two confirmed Mainland school years,
  actual residence migration to Hong Kong, and first transfer at S2 or above
  are now background descriptors rather than exclusion rules.
- Cross-border commuters, respondents uncertain about two continuous
  Mainland school years, lower-grade transfer entrants, and the response
  category “other” are included.
- Consent and adult status remain ethical gates. All 35 submissions satisfy
  both, so analysis v2 uses 35/35 records. Eleven records formerly excluded in
  analysis v1 are explicitly marked as reclassified, not silently relabelled.
- This population-definition change was made after the complete v1 analysis,
  independent reviews, and tagged results were available. It reflects the
  investigator's conceptual expansion of the target population, not a data-
  quality correction or a significance-driven screening decision. V1/V2
  differences are therefore reported as post-hoc specification sensitivity.
- All three uniquely linked interview files now map to eligible survey records
  and must receive linked-case analysis. Analysis v1 and tag `analysis-v1`
  remain preserved for provenance; the expanded analysis uses run ID
  `20260723_expanded_eligibility` and will be tagged separately.

## 2026-07-23 — Independent review and extension decisions (analysis v3)

- The four independent second-round audits were closed before canonical
  revision. Reviewer A/B/C used separate subagents; Reviewer D was performed
  by the main agent without editing first-round outputs during the audit.
- Multiple-choice export values remain recoverable. Exceeding a questionnaire
  selection limit creates a question-specific quality flag, not whole-record
  exclusion. Q5.4 is reported as endorsement with group-level special missing
  propagated to its denominator, plus a limit-compliant sensitivity subset.
- Q3.3 item 2 is a composite statement about at least one peer who can be
  trusted and confided in. It must not be shortened to trust alone or split
  into separate full-sample trust and confiding percentages.
- A survey–interview relationship is labelled `DIVERGENCE` only when the
  comparison concerns the same construct, has an overlapping timeframe, and
  points in opposite directions. All 75 alignments receive an explicit
  second-round adjudication; capped-choice non-selection is not a negative
  response.
- New findings use exactly four possible grades. `robust finding` is a
  reproducible description of the current dataset, not population
  generalisability; `plausible exploratory finding` is traceable but has live
  competing explanations; `weak signal` appears only in robustness,
  limitations, or future research; `unsupported` interpretations are removed
  rather than retained in the finding table.
- A1 is retained as a plausible exploratory association because its direction
  survives specified scoring and leave-one-out checks. A4 is a weak signal
  because reasonable brokerage-participation encodings materially reduce it.
  Neither association supports causal or population claims.
- Full third-case positions, line references, configurations, and revised
  alignments remain restricted. Current public derivatives omit its anonymous
  ID, line ranges, rare background/resource combinations, and unsuppressed
  cells below three. First-round files remain recoverable from `analysis-v2`
  and a restricted preservation directory.
- Reproducibility is reported in two modes: deterministic regeneration, and
  promotion of frozen interpretive inputs after explicit semantic review.
  The latter is not described as algorithmically rediscovering qualitative
  judgements.
- Second-round run ID:
  `20260723_independent_review_extension_v2`. The next completion tag is
  `analysis-v3`.
