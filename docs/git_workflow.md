# Git Workflow

## 1. Purpose

Git is used for provenance, reproducibility, and recovery.

The pipeline must manage Git automatically. The user should not be required to create branches, commit files, merge subagent work, or resolve routine conflicts.

---

## 2. Initialisation

When first invoked:

1. if the current directory is not a Git repository, run `git init`;
2. use or create the `main` branch;
3. configure repository-local Git identity only if no usable identity exists;
4. create or update `.gitignore`;
5. create a baseline commit before generating analysis outputs.

Recommended baseline commit:

```text
chore: initialise research analysis repository
```

Recommended `.gitignore` entries:

```gitignore
__pycache__/
*.pyc
.venv/
venv/
.ipynb_checkpoints/
.DS_Store
Thumbs.db
~$*.xlsx
~$*.docx
.vscode/
.idea/
outputs/tmp/
data/processed/tmp/
```

Do not ignore `data/raw/` unless the project explicitly decides not to track raw data.

---

## 3. Working model

Run the pipeline on the current branch.

Do not require a feature branch unless the environment needs isolated worktrees for subagents.

If subagents use branches or worktrees:

- the Main Agent owns integration;
- worker agents must not require user-side merges;
- outputs should first be written under separate `outputs/agent_runs/<run_id>/` directories;
- only the Main Agent updates canonical files.

---

## 4. Automatic commits

Commit completed and internally consistent stages automatically.

Recommended sequence:

```text
chore: initialise research analysis repository
data: map and clean questionnaire responses
analysis: generate questionnaire findings
data: link survey records and interview transcripts
analysis: complete linked case analysis
analysis: integrate mixed-methods findings
docs: generate final research report
chore: validate and finalise analysis pipeline
```

Before every commit:

1. verify `data/raw/` is unchanged;
2. verify the stage outputs exist;
3. run relevant validation checks;
4. do not commit a failed stage as completed.

A stage with warnings may be committed when the warning is explicit and the outputs remain valid.

---

## 5. Raw-data protection

Before every commit, compare current raw-file checksums with:

```text
outputs/reports/raw_file_checksums.csv
```

If a raw file changed:

1. stop committing affected work;
2. restore the original raw file when the intended baseline is unambiguous;
3. record the incident in `outputs/reports/pipeline_summary.md`;
4. rerun affected stages.

Do not silently accept raw-data changes.

---

## 6. Merge and conflict handling

If an automatic merge conflict occurs:

1. preserve all source outputs;
2. resolve the conflict only when the canonical result is unambiguous;
3. do not discard either agent’s evidence;
4. when unresolved, write:

```text
outputs/reports/merge_conflict_report.md
```

5. continue with unaffected stages;
6. list unresolved conflicts in the final pipeline summary.

Canonical master files may be updated only by the Main Agent.

---

## 7. Finalisation

At the end of a successful run:

1. run full automated validation;
2. commit all valid outputs;
3. leave the working tree clean;
4. create an annotated tag.

Recommended tag:

```text
analysis-v1
```

Recommended command semantics:

```text
git tag -a analysis-v1 -m "Completed automated mixed-methods analysis"
```

If the tag already exists, create the next version, such as `analysis-v2`.

Record in:

```text
outputs/reports/pipeline_summary.md
```

- baseline commit hash;
- stage commit hashes;
- final commit hash;
- final tag;
- worktree or branch usage;
- merge conflicts;
- uncommitted or skipped files.

---

## 8. Failure behaviour

Do not create a “completed” commit or final tag when:

- required files are unreadable;
- linkage is irreconcilably ambiguous;
- validation fails on core sample counts;
- raw files were modified and cannot be restored;
- final claims cannot be traced to evidence.

In partial runs:

1. commit only valid completed stages;
2. use a commit message that clearly indicates partial status;
3. do not create the final analysis tag;
4. record what remains incomplete.

---

## 9. User interaction

Do not ask the user to run routine Git commands.

Only request user intervention when:

- repository permissions prevent Git operations;
- Git identity cannot be configured safely;
- an external authentication step is required;
- a merge conflict requires substantive research judgment;
- restoring the intended raw-data baseline is ambiguous.
