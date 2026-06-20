# Contributing

Thanks for improving `codex-adversarial-gate`.

## Development Principles

- Preserve the reviewer-plus-critic gate.
- Keep custom agent names stable unless there is a migration path.
- Keep reviewer and critic agents read-only.
- Do not add private workflow assumptions, personal paths, secrets, or organization-specific jargon.
- Prefer references and templates over bloating `SKILL.md`.

## Project Layout

| Path | Purpose |
|---|---|
| `skills/codex-adversarial-gate/SKILL.md` | Skill entrypoint |
| `skills/codex-adversarial-gate/agents/*.toml` | Bundled custom agents |
| `skills/codex-adversarial-gate/references/` | Detailed workflow and rubric docs |
| `skills/codex-adversarial-gate/templates/` | Snippets copied into plans or closeout packets |
| `skills/codex-adversarial-gate/scripts/` | Package installer, archive helper, and smoke test |
| `scripts/` | Repo-level install wrapper and install tests |
| `docs/` | User-facing docs and captured learnings |

## Before You Commit

Run:

```bash
bash -n scripts/install.sh
bash -n skills/codex-adversarial-gate/scripts/install.sh
bash scripts/test_install.sh
python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 -m py_compile \
  skills/codex-adversarial-gate/scripts/archive_adversarial_review.py \
  skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
git diff --check
```

Check custom agent TOMLs with Python 3.11+:

```bash
python3 - <<'PY'
from pathlib import Path
import tomllib

for path in sorted(Path("skills/codex-adversarial-gate/agents").glob("*.toml")):
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    for key in ("name", "description", "developer_instructions"):
        assert data.get(key), f"{path}: missing {key}"
    print(f"{path}: {data['name']}")
PY
```

Run the Codex skill validator if available:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py skills/codex-adversarial-gate
```

## Documentation Changes

When changing workflow behavior, update all relevant surfaces:

- `skills/codex-adversarial-gate/SKILL.md`
- `skills/codex-adversarial-gate/references/`
- `skills/codex-adversarial-gate/templates/`
- `skills/codex-adversarial-gate/agents/*.toml`
- `skills/codex-adversarial-gate/scripts/install.sh`
- `scripts/install.sh`
- `docs/reference.md`
- `docs/usage.md`

## Pull Request Checklist

- [ ] The skill still routes to the bundled custom agents.
- [ ] Fallback prompts do not allow same-context self-review.
- [ ] Review archive behavior is documented and tested.
- [ ] No private paths, credentials, or local workflow assumptions were introduced.
- [ ] Validation commands pass.
