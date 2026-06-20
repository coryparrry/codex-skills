# Triage Review Comments

> *"Stop manually sorting PR feedback. Let the skill classify it for you."*

I built this because every time I submitted a PR and the reviews came back, I'd spend time manually reading through each comment, figuring out what was a real blocker versus noise, and deciding what to do about it. CodeRabbit, Cursor, and human reviewers all produce different formats and different signal-to-noise ratios — and I was doing the same triage dance every time. I realized I didn't actually have to.

This skill loads the full PR review context, builds a complete inventory, deduplicates by underlying issue, classifies everything into four buckets, resolves inline threads that are already fixed, tracks real deferred work in Linear, and recommends prevention tests so the same issues don't come back.

---

## What it does

- Builds a complete inventory of every review comment: open inline threads, resolved threads, general comments, and standalone review findings
- Strips out boilerplate, walkthrough notes, and automation banners that contain no actionable finding
- Deduplicates comments that describe the same underlying issue
- Classifies every actionable comment into one of four buckets:
  - **Fix now** — reachable, meaningful, should block merge
  - **Fix if cheap** — probably valid, limited impact, low-risk to take now
  - **Defer** — real work but better as follow-up
  - **Ignore** — duplicate, stale, speculative, style-only, or already fixed
- Resolves fixed inline review threads on GitHub when the current code clearly addresses them
- Files real deferred items as Linear issues under the correct project
- Recommends the smallest practical prevention test or check for every real issue

## What it doesn't do

- Apply fixes automatically (it classifies and recommends, you decide)
- Resolve general PR conversation comments (GitHub doesn't treat those as resolvable threads)
- Replace your judgment on whether a `Defer` item is worth tracking
- Work without PR review context to load

## How it works

```
triage-review-comments
  ├─ Load PR review context (inline threads, general comments, reviews)
  ├─ Strip boilerplate and non-actionable content
  ├─ Deduplicate by underlying issue
  ├─ Classify each comment → Fix now / Fix if cheap / Defer / Ignore
  ├─ Resolve fixed inline threads on GitHub
  ├─ File deferred items in Linear
  ├─ Recommend prevention tests for real issues
  └─ Return full inventory, buckets, and next steps
```

The skill treats every review comment as a hypothesis that must be checked against the actual code — nothing gets classified on trust alone.

## Installation

```bash
git clone https://github.com/coryparrry/codex-skills.git
cd codex-skills

# Install the skill
mkdir -p ~/.codex/skills
cp -R skills/triage-review-comments ~/.codex/skills/triage-review-comments
```

Then restart Codex. No dependencies, no agent profiles to install.

---

## Usage

Invoke the skill by name when you have an open PR with review comments:

```text
Use triage-review-comments to triage the review comments on this PR.
```

Or more casually:

```text
triage-review-comments
```

**Good fits:**

- A PR just came back from review with comments from multiple sources (human, CodeRabbit, Cursor)
- You want a single triage pass that separates blockers from noise before you start fixing
- You want prevention tests recommended alongside every real issue
- You want fixed threads resolved on GitHub and deferred work tracked in Linear in one pass

**Not a fit:**

- A PR with zero review comments (nothing to triage)
- A review that's entirely style nits you've already decided to ignore
- You want the skill to apply the fixes for you (it classifies, you implement)

---

## Layout

```text
skills/triage-review-comments/
  SKILL.md                    — the skill Codex loads
  agents/                     — agent metadata
  references/                 — full triage rubric and output shape
```

---

## License

MIT — see [LICENSE](../LICENSE).
