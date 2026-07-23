# AGENTS.md

## Project

This repository contains an exploratory linked mixed-methods study of
Mainland-to-Hong Kong secondary-school transfer students.

The primary research topics are:

1. peer boundaries, belonging, identity negotiation, and cultural brokerage;
2. academic norms, assessment practices, and hidden curriculum.

Digital-platform practices are supplementary.

## Canonical documents

Read before analysis:

1. `docs/research_design.md`
2. `docs/analysis_pipeline.md`
3. `docs/data_contract.md`
4. `research_materials/questionnaire.md`
5. `research_materials/interview_guide.md`, if present
6. `docs/literature_context/research_context.md`, if present
7. `notes/analysis_decisions.md`, if present

The most recent explicit entry in `notes/analysis_decisions.md` takes
precedence over older project documents.

## Core rules

- Never modify files under `data/raw/`.
- Save processed data under `data/processed/`.
- Save reproducible scripts under `scripts/`.
- Save generated outputs under `outputs/`.
- Do not invent data, quotations, participant details, statistics, or sources.
- Keep blank, not applicable, cannot remember, and unwilling to answer distinct.
- All claims must be traceable to survey tables or transcript line ranges.
- Do not use causal language for retrospective cross-sectional data.
- Do not generalise three interviews to the full sample.
- Literature provides context, not evidence about current participants.

## Linked design

Interviewees were selected from the questionnaire sample.

The questionnaire sequence number is encoded in each interview filename.
Follow the mapping and validation rules in `docs/data_contract.md`.

The required order is:

1. clean and analyse the complete questionnaire sample;
2. link interview files to questionnaire records;
3. construct linked case profiles;
4. analyse the linked cases;
5. conduct cross-case synthesis;
6. integrate case findings with complete-sample survey findings.

Never guess an ambiguous mapping.

## Multi-agent workflow

Use subagents when supported.

The main agent must define shared schemas before delegation. Then use:

- one Survey Analyst;
- one Linked Case Agent per interviewee;
- one Qualitative Synthesis Agent;
- one Mixed-Methods Integration Agent;
- one Evidence Reviewer;
- one Privacy and Method Reviewer.

Dependent stages must wait for their inputs. Worker agents must use separate
output directories. Only the main agent may update canonical files and the
final report.

If subagents are unavailable, run the same roles sequentially and record the
fallback.

## Pipeline

Execute `docs/analysis_pipeline.md` end to end.

Do not stop after producing a plan or inventory when the required data are
readable. Skip only analyses that are methodologically unsupported and record
the reason.

## Git

Manage Git automatically according to `docs/git_workflow.md`.

Do not require the user to create branches, commit files, or merge subagent
work. Before every commit, verify that `data/raw/` is unchanged.

## Completion

Produce at minimum:

- `outputs/reports/final_report.md`
- `outputs/reports/validation_report.md`
- `outputs/reports/pipeline_summary.md`
- `outputs/reports/agent_run_manifest.md`

Stop the full pipeline only when missing, unreadable, unsafe, or irreconcilably
ambiguous data make valid analysis impossible.