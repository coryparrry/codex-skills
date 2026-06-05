# Model-Switch Fallback

Load this reference only if custom agents are not configured or not callable and a built-in subagent/model-override route is unavailable.

Tell the user the exact model-switch action instead of continuing expensively.

Examples:

```text
To conserve limits for this routine task, switch this Codex thread to gpt-5.4-mini with /model gpt-5.4-mini, then continue.
```

```text
For this targeted implementation, use codex -m gpt-5.3-codex from a fresh thread, or configure a codex_worker custom agent.
```

Do not claim the default model for cloud tasks can be changed unless the current Codex documentation and product surface explicitly support it.
