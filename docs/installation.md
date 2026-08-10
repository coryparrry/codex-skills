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
- `engineering-advisor`
- `git-clean-merged-branch`
- `research-repo-technology`
- `swift-code-review`
- `triage-review-comments`

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

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [App Store Readiness Audit](appstore-readiness-audit.md)
- [Engineering Advisor](engineering-advisor.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
- [Continue Deep Research](continue-deep-research.md)
- [Repository Technology Research](research-repo-technology.md)
- [Swift Code Review](swift-code-review.md)
