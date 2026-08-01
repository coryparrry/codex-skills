# Install Codex Skills

This guide explains how to install one skill or the full bundle.

## Before You Start

You need Codex with local skills enabled and `skills` CLI support through `npx`.

## Install Through Codex Marketplace

1. Open **Plugins** in the Codex app.
2. Click **Add marketplace**.
3. Add `https://github.com/coryparrry/codex-skills` as the marketplace source.
4. Open **Codex Skills** and click the plus button or **Add to Codex**.

The marketplace plugin exposes `git-clean-merged-branch` and `triage-review-comments`.

## Install Through skills.sh

Install the full bundle:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill '*'
```

Install one skill:

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill git-clean-merged-branch
```

```bash
npx skills add coryparrry/codex-skills --global --agent codex --skill triage-review-comments
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

If the marketplace plugin does not appear, verify that `.agents/plugins/marketplace.json` and `plugins/codex-skills/.codex-plugin/plugin.json` exist, then remove and re-add the marketplace.

## Related Docs

- [Usage Guide](usage.md)
- [Reference](reference.md)
- [Git Clean Merged Branch](git-clean-merged-branch.md)
- [Triage Review Comments](triage-review-comments.md)
