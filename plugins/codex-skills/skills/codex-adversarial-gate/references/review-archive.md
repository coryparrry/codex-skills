# Review Archive Protocol

Read this whenever a plan review, completion review, or completion critic review finishes.

## Archive Location

Save exact review outputs under:

```text
<repo>/docs/Adversarial Reviews/
```

Use this exact folder name and capitalization.

## Safety Boundary

Reviewer and critic roles should remain read-only. The implementing Codex thread archives the exact output after receiving it. Do not make a reviewer writable just to create archive files.

The archive write is allowed after the review output is produced. It records evidence; it must not modify implementation files or generated artifacts under review.

## What To Archive

Archive every:

- plan reviewer output;
- completion reviewer output;
- completion critic output;
- rerun output after fixes or critic dissent.

The archive file must include:

- review kind: `plan`, `completion`, or `critic`;
- phase/slice or plan name;
- reviewer role or label;
- verdict/disposition;
- timestamp;
- repo-relative archive path;
- exact review body, unedited except for a short metadata header;
- implementer resolution when known.

If the review output contains a secret or credential, stop and report it instead of archiving. Do not redact silently unless the owner explicitly instructs it.

## Preferred Script

Use the bundled helper when Python 3 is available:

```bash
python3 "<path-to-skill>/scripts/archive_adversarial_review.py" \
  --repo "<repo-root>" \
  --kind completion \
  --phase "task parser" \
  --reviewer task_completion_adversarial_reviewer \
  --verdict PASS \
  --review-file "./review.md"
```

The script creates `docs/Adversarial Reviews/` and prints the archive path.

Use `--stdin` to read the review from standard input:

```bash
printf '%s\n' "$REVIEW_TEXT" | python3 "<path-to-skill>/scripts/archive_adversarial_review.py" \
  --repo "<repo-root>" \
  --kind critic \
  --phase "task parser" \
  --reviewer task_completion_review_critic \
  --verdict AGREE_PASS \
  --stdin
```

## Manual Fallback

If the script cannot run:

1. Create `<repo>/docs/Adversarial Reviews/`.
2. Create a filename with UTC timestamp, review kind, phase slug, and verdict, for example:
   `2026-06-14T121500Z-completion-task-parser-pass.md`.
3. Add a short metadata header.
4. Paste the exact review output below `## Review`.
5. Record the archive path in the plan or implementation report.

## Final Report Table Columns

Every implementation closeout report must include:

| Phase/slice | Reviewer verdict | Reviewer archive | Critic verdict | Critic archive | Disagreement class | Evidence checked | Fixes or evidence required | Final status |
|---|---|---|---|---|---|---|---|---|
