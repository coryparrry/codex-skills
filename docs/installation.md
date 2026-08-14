# Install Codex Skills

This guide explains how to install one skill or the full bundle.

## Before You Start

You need Codex with local skills enabled and `skills` CLI support through `npx`.

## Install Through Codex Marketplace

1. Open **Plugins** in the Codex app.
2. Click **Add marketplace**.
3. Add `https://github.com/coryparrry/codex-skills` as the marketplace source.
4. Open **Codex Skills** and click the plus button or **Add to Codex**.

After installation, Codex lists the plugin with installed plugins rather than in the marketplace's available-only results. Start a new task after installing or updating so the task loads the current plugin version and skills.

The marketplace plugin exposes:

- `appstore-readiness-audit`
- `continue-deep-research`
- `deep-code-review`
- `engineering-advisor`
- `git-clean-merged-branch`
- `research-repo-technology`
- `swift-code-review`
- `triage-review-comments`

## Install in Cursor

The Cursor package contains skills only; it does not add MCP servers, hooks, rules, or background processes.

To use the version in a trusted local checkout:

1. Do not use **Add** > **From Local Repo**. That flow is for a Cursor marketplace, while this package is an Agent Plugin loaded directly from Cursor's local-plugin directory.
2. Copy the package into Cursor's durable local-plugin directory:

   ```bash
   mkdir -p ~/.cursor/plugins/local
   ditto "$(pwd)/plugins/cursor-skills" ~/.cursor/plugins/local/cursor-skills
   ```

3. Quit and reopen Cursor, or run **Developer: Reload Window**.
4. Open **Customize** > **Skills** and invoke a skill such as `/deep-code-review`.

Cursor reads the Agent Plugin manifest from `plugins/cursor-skills/plugin.json`; its skills live immediately below `plugins/cursor-skills/skills/`.

The public Cursor Marketplace requires a separate submission and manual review. After this package is merged to the default branch, submit `https://github.com/coryparrry/codex-skills` at [Cursor Marketplace publishing](https://cursor.com/marketplace/publish). Until Cursor approves it, use the local-plugin flow above.

## Install Through skills.sh

Install the full bundle:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

Install one skill:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill appstore-readiness-audit
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill deep-code-review
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill git-clean-merged-branch
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill engineering-advisor
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill triage-review-comments
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill continue-deep-research
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill research-repo-technology
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill swift-code-review
```

Global Codex skill copies are stored under `${CODEX_HOME:-$HOME/.codex}/skills/`.

## Install From A Trusted Local Checkout

From a trusted local checkout:

```bash
bash scripts/install.sh
```

The installer copies each top-level skill from `skills/` into `${CODEX_HOME:-$HOME/.codex}/skills/`. It refuses curl-style execution because installation requires a trusted local checkout.

Restart Codex if an installed skill does not appear.

## Common Problems

If Codex does not show an installed skill, restart Codex and verify that its `SKILL.md` is under the expected directory.

If the marketplace itself does not appear, verify that `.agents/plugins/marketplace.json` and `plugins/codex-skills/.codex-plugin/plugin.json` exist on the repository's default branch, then remove and re-add the marketplace. If the marketplace appears but reports an older installed version, upgrade the marketplace snapshot, remove the installed plugin, reinstall it, and start a new task.

If Cursor does not load the local package, remove a stale **Cursor Skills** entry from **Customize** > **Plugins**, confirm `~/.cursor/plugins/local/cursor-skills/plugin.json` exists, then fully quit and reopen Cursor. Do not install this repository through **Add** > **From Local Repo**.

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [App Store Readiness Audit](appstore-readiness-audit.md)
- [Deep Code Review](deep-code-review.md)
- [Engineering Advisor](engineering-advisor.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
- [Continue Deep Research](continue-deep-research.md)
- [Repository Technology Research](research-repo-technology.md)
- [Swift Code Review](swift-code-review.md)
