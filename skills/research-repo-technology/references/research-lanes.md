# Research lane design

Use this menu to create independent lanes from the repository's actual gaps. Select only lanes that fit the product; do not run every lane mechanically.

## Core lanes

| Lane | Question | Required evidence |
| --- | --- | --- |
| Architecture and workflows | Where do ownership, state, or data-flow boundaries constrain the product? | Exact source paths, workflow trace, tests, mismatch with architecture prose |
| Performance and reliability | What workloads, recovery paths, or scaling limits are weak? | Benchmarks or receipts, algorithms, queues/caches, failure tests, measurable bottleneck |
| Privacy and security | Which recommendations preserve or weaken the product's boundaries? | Data classes, retention, privileges, network access, threat surface, repository policy |
| Protocols and integrations | Which standards or adapters remove bespoke machinery or unlock workflows? | Current protocol code, official specification, compatibility and versioning risks |
| Product and native UX | Which capability delivers meaningful user value within the product's interaction model? | Current UI/control source, platform constraints, user workflow, accessibility evidence |
| External technology | Which maintained projects solve one verified gap? | Source, tests, releases, issues, licence, dependencies, exact reusable unit |
| Strategic differentiation | What should this product build because its constraint combination is unusual? | Unmet need, rejected existing options, differentiating value, bounded validation path |
| Adversarial rejection | Which attractive recommendations fail under real constraints? | Counterevidence on fit, cost, privacy, performance, licence, maintenance, or scope |

## Lane prompt contract

Give every subagent:

- the exact repository path and the relevant local scope;
- the read-only boundary;
- one concrete question derived from an observed gap;
- the files or workflows to inspect first without limiting later discovery;
- the requirement to inspect external projects beyond the README;
- the required output: repository evidence, external primary evidence, recommendation, risks, confidence, and rejected alternatives;
- a prohibition on edits, installs, task updates, deployments, and unsupported claims.

Keep independent lanes isolated during the divergent pass. Do not give them another lane's conclusions. After clusters emerge, send focused evidence lanes to test the strongest ideas rather than asking for more unbounded brainstorming.

## Root-agent responsibilities

Keep these with the root agent:

- live repository baseline and Git-state verification;
- cross-lane comparison and contradiction resolution;
- verification of material external claims;
- adopt/adapt/build/reject decisions;
- final ranking, proof-of-concept design, and closeout.

Continue local inspection while lanes run. Use bounded waits, then synthesize available evidence if a lane stalls. Disclose incomplete lanes instead of treating silence as confirmation.

Define the stopping rule before dispatch. A lane is complete when it has enough primary repository and external evidence to distinguish the credible choices, not when it has found every adjacent project.
