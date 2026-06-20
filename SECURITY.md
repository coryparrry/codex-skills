# Security Policy

## Supported Versions

This repository currently supports the latest version on the default branch.

## Reporting A Vulnerability

Please do not include secrets, tokens, private paths, or sensitive logs in public issues.

If GitHub private vulnerability reporting is enabled for this repository, use it. If it is not enabled, open a minimal public issue asking for a private contact path and omit sensitive details.

## Sensitive Data Handling

The archive helper stores exact review output. Before archiving, check that the review text does not contain:

- API keys or tokens;
- credentials;
- private filesystem paths;
- private diagnostics;
- confidential customer or project data.

If review output contains sensitive material, stop and report it instead of archiving. Do not silently redact unless the repository owner explicitly asks for that.

## Security-Sensitive Changes

Changes touching reviewer permissions, archive behavior, fallback prompts, or custom agent sandbox settings should receive extra scrutiny. The reviewer and critic roles should remain read-only.
