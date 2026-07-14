# Git Workflow (Strict)

These rules are mandatory for every spec and epic in this project. They apply
to every working session, including fresh sessions started for a new spec.

## 1. Branching

- Every spec is implemented on its own branch, checked out from the latest
  `main`:
  ```
  git fetch origin
  git checkout main
  git pull origin main
  git checkout -b MEDGENT-XXX-short-kebab-title
  ```
- Branch name format is fixed: `MEDGENT-XXX-branch-name`, where `XXX` is the
  zero-padded spec number (e.g. `MEDGENT-007`) and `branch-name` is a short
  kebab-case slug matching the spec title (e.g.
  `MEDGENT-007-interaction-crud-api`).
- Epics are tracking documents only. They are never branched or implemented
  directly — only their child specs get branches.
- Never branch from another feature branch. Always branch from `main`, even
  if the dependency spec's branch hasn't been merged yet — if a dependency
  isn't merged, the spec is not ready to start (see
  [[03-development-workflow]]).
- One spec per branch. Do not combine multiple specs into one branch, and do
  not let unrelated changes creep into a spec's branch.

## 2. Status lifecycle

Each spec file has a `Status` field: `To Do` → `In Progress` → `Done`.

- The moment work begins on a spec, update its `Status` to `In Progress` in
  the spec's markdown file. This is just a file edit on the branch like any
  other change.
- When all acceptance criteria are met and the code is ready for review,
  update `Status` to `Done` in the spec file **and** update the corresponding
  row in `specs/README.md`.
- Status edits live in the same branch/working tree as the implementation —
  do not create a separate branch or commit just for a status change.

## 3. Commits, staging, and pushing — hard boundary

- **Never run `git commit`.** Stage changes with `git add` once the spec is
  complete and marked `Done`, then stop and tell the user the spec is ready
  for review. Committing, writing the commit message, pushing, opening the
  PR, and merging are entirely the user's responsibility.
- **Never run `git push`.**
- **Never open, merge, or close a pull request.**
- **Never merge, rebase, or reset `main`.** Treat `main` as read-only except
  for `git pull`.
- If asked to "finish up" a spec, the correct end state is: working tree has
  the finished, staged changes; spec status says `Done`; nothing has been
  committed.

## 4. Suggested commit message format (for the user, not for you to apply)

```
MEDGENT-XXX: <short summary of what the spec delivers>
```

You may propose this message in your handoff summary so the user can copy it,
but you do not run the commit yourself.

## 5. Dependency ordering

- Before starting a spec, check its `Depends on` field against
  `specs/README.md`. All listed dependencies must show `Status: Done` **and**
  be merged into `main` (verify with `git log main` / `git branch -r`, not
  just the spec file, since the spec file on a stale local `main` may be
  outdated — re-run `git pull origin main` first).
- If a dependency isn't actually merged yet, tell the user before starting
  rather than building on an unmerged branch.

## 6. Scope discipline per branch

- Touch only the files needed for the spec's acceptance criteria, plus the
  spec's own status field and its `specs/README.md` row.
- If you discover unrelated work that should happen (a bug, missing spec,
  scope gap), do not fold it into the current branch — flag it to the user
  and, if agreed, it becomes a new spec.
