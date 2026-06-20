# Worked Example

## Review Claim

> `ProjectAccess.swift` checks that a user belongs to the same workspace, but it does not check `project:read`. A user in the workspace may be able to read a private project they do not have permission for.

## Code Verification

Current code:

```swift
guard session.workspaceID == project.workspaceID else {
    throw AccessError.notFound
}
return project
```

Evidence:
- The route reads a private project.
- The only guard is same-workspace membership.
- There is no project-level permission check before returning the project.
- A same-workspace user without `project:read` is a reachable caller if workspace membership and project access are separate concepts.

False-positive check:
- Not stale: current code still returns the project immediately after the workspace check.
- Not guarded elsewhere: no project-level permission guard appears before the return.
- Not preference-only: the comment identifies a concrete authorization boundary.
- Permission model checked: project-level permissions are a real concept in this app. If that cannot be proven from current code, this becomes `Ignore` as a false positive.

## Bucket

`Fix now`

Reason: reachable authorization boundary bug. Same-workspace membership is not equivalent to private-project read permission.

Confidence: high, after confirming the app has separate project-level permissions.

If not fixed: private project contents may be exposed to users who only share the workspace.

## Fix Packet

- `Bug`: private project read path checks workspace membership but not project read permission.
- `Trigger`: same-workspace user requests a private project without `project:read`.
- `Patch scope`: project lookup/access service or route guard around `ProjectAccess.swift`.
- `Prevention first`: authorization regression test for same-workspace/no-project-read denial.
- `Fix shape`: require both same workspace and project read permission before returning project data.
- `Validation`: run the focused auth/access test target or repo test command that covers project access.
- `Risk`: over-tightening could block legitimate project readers; include allowed-user test too.

## Prevention Recommendation

Add a focused authorization test:

```text
given user is in workspace
and project is private
and user lacks project:read
when user requests project details
then access is denied
```

Also add the positive case for a user with `project:read` so the fix does not break legitimate access.
