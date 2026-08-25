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

### Marketplace release evidence

The release-contract workflow emits a machine-readable marketplace receipt for pull requests and pushes to `main`. A pull-request receipt proves that the repository candidate has consistent manifests, marketplace metadata, skill mirrors, and catalogue entries. Its `tested_commit` is the exact checkout tested by CI; for a pull request, GitHub may make that a synthetic merge commit, so the receipt also records the optional source `pull_request_head_commit`. A `main` receipt binds the evidence to the exact merged Git commit and ref. Neither receipt updates Codex on a developer Mac or proves that its local marketplace and plugin cache are current.

After a shipped plugin change is merged, refresh and verify the local installation separately:

```bash
codex plugin marketplace upgrade codex-skills
codex plugin remove codex-skills@codex-skills
codex plugin add codex-skills@codex-skills --json
codex plugin list --marketplace codex-skills --available --json
```

Confirm the installed manifest and cache provenance point to the merged `main` snapshot, then start a new Codex task.

Verify that the previous plugin cache is absent after removal, that the newly installed cache points to the merged snapshot, and that no standalone `${CODEX_HOME:-$HOME/.codex}/skills/` copy is masking the marketplace installation.

The marketplace plugin exposes:

- `appstore-readiness-audit`
- `codex-routing`
- `continue-deep-research`
- `deep-code-review`
- `git-clean-merged-branch`
- `research-repo-technology`
- `swift-code-review`
- `triage-review-comments`

## Load Through an Agent Plugins v1 Client

Build the portable package into a new output directory:

```bash
python3 scripts/build_agent_plugin.py --output dist/codex-skills
```

The builder copies the Agent Plugins 1.0.0 manifest, the `skills/` directory, the license, and `mcp.json` when present. It leaves out `.codex-plugin/`, Codex agent profiles, and interface assets. The output path must not already exist.

Load `dist/codex-skills/` using the client's directory-based plugin flow. The Agent Plugins specification defines the package format, not a shared install command or marketplace protocol, so the final install step depends on the client.

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
npx skills add coryparrry/codex-skills --global --agent codex --skill codex-routing
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
- [App Store Readiness Audit](app-review/appstore-readiness-audit.md)
- [Codex Routing](orchestration/codex-routing.md)
- [Deep Code Review](code-review/deep-code-review.md)
- [Git Clean Merged Branch](git-workflow/git-clean-merged-branch.md)
- [Triage Review Comments](code-review/triage-review-comments.md)
- [Continue Deep Research](research/continue-deep-research.md)
- [Repository Technology Research](research/research-repo-technology.md)
- [Swift Code Review](code-review/swift-code-review.md)
