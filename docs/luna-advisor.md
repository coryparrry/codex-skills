# Luna Advisor

`luna-advisor` keeps Luna as the main implementation agent and asks one
read-only Sol subagent for a bounded execution packet only when a task exceeds
a clear Luna-only lane. Luna checks the active model first. Clear, local,
reversible work with strong objective checks stays Luna-only. Ambiguity,
cross-cutting or unfamiliar behavior, subtle debugging, weak verification,
meaningful security or reliability consequences, an expensive mistake, or an
explicit request for Sol triggers the advisor. Sol Low is limited to one
narrow choice with known scope, complete evidence, deterministic checks, and
no material design or system-boundary judgment. Sol Medium covers the other
triggered cases.

The skill cannot change the active root model. If the current model is not
Luna, the workflow stops and reports the mismatch. Sol does not edit files,
delegate, stage, commit, push, open pull requests, or mutate external systems.

## Use it

Install the skill from the Codex Skills marketplace or skills.sh, then ask:

```text
Use $luna-advisor to have Luna get one bounded Sol execution packet before implementing this change.
```

Before the Sol call, Luna supplies the trigger, requested outcome, verified
current behavior, exact candidate scope, preserved behavior and user
constraints, known unknowns, validation commands, and authority boundaries.
Sol must return a complete packet with the decision, exact scope, ordered
steps, constraints, validation, success evidence, stop triggers, and
unresolved user decisions.

Luna does not implement an incomplete packet. It uses one bounded follow-up on
the same Sol advisor when required. If implementation contradicts the packet,
Luna stops and sends the raw evidence back to that advisor instead of silently
expanding scope or starting an advice loop. If Sol identifies unresolved
product intent or authorization, Luna asks the user.

The routing reflects the current model roles and prompting guidance in the
[GPT-5.6 Luna model guide](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[GPT-5.6 Sol model guide](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
and [latest-model prompting guide](https://developers.openai.com/api/docs/guides/latest-model).

## Related files

- [Usage Guide](usage.md)
- [Installation](installation.md)
- [Reference](reference.md)
