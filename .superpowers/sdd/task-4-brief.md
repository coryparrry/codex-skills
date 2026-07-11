### Task 4: Dry-Run The Invocation Contract Without Changing A Repo

**Files:**
- Check: `~/.codex/skills/Knowledge-setup/SKILL.md`

**Interfaces:**
- Consumes: installed skill instructions.
- Produces: confidence that a future invocation will modify only the three context-layer files.

- [ ] **Step 1: Read the skill as Codex would**

```bash
sed -n '1,260p' "$HOME/.codex/skills/Knowledge-setup/SKILL.md"
```

Expected: The skill gives a complete adoption workflow without referencing missing files, scripts, generated tooling, or background automation.

- [ ] **Step 2: Confirm the future invocation wording**

Use this manual trigger from any target repo:

```text
Use $Knowledge-setup in this repo
```

Expected: The skill activates as a manual one-command repo initialization workflow. It does not run automatically on arbitrary folders.
