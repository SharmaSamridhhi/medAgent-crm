# Git Workflow (Strict)

These rules are mandatory for every spec and epic in this project. They apply
to every working session, including fresh sessions started for a new spec.

## 0. Two modes

There are two valid ways to move work through this repo. Which one is active
is a project-level decision the user makes explicitly — default to **Mode A**
unless the user has told you to switch to **Mode B** (they did, given this
project's 36-hour time-box — see `CLAUDE.md`).

- **Mode A — per-spec branch, agent never commits.** One branch per spec,
  agent stages changes and stops; the user commits/pushes/merges. This is
  the default and is fully specified in sections 1–6 below.
- **Mode B — per-epic branch, agent commits atomically per spec.** One
  branch per *epic*, with each child spec landing as its own atomic commit
  on that branch, authored by the agent. Still never push, merge, or open a
  PR — only the "never commit" rule is lifted, and only because the user
  said so. See section 7.

If the user hasn't said which mode applies, ask rather than assume — the two
modes produce very different-looking history.

## 1. Branching (Mode A — per spec)

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
- Epics are tracking documents only in Mode A. They are never branched or
  implemented directly — only their child specs get branches.
- Never branch from another feature branch. Always branch from `main`, even
  if the dependency spec's branch hasn't been merged yet — if a dependency
  isn't merged, the spec is not ready to start (see
  [[03-development-workflow]]).
- One spec per branch. Do not combine multiple specs into one branch, and do
  not let unrelated changes creep into a spec's branch.

## 2. Status lifecycle

Each spec file has a `Status` field: `To Do` → `In Progress` → `Done`. This
applies identically in both modes.

- The moment work begins on a spec, update its `Status` to `In Progress` in
  the spec's markdown file. This is just a file edit on the branch like any
  other change.
- When all acceptance criteria are met and the code is ready for review,
  update `Status` to `Done` in the spec file **and** update the corresponding
  row in `specs/README.md`.
- Status edits live in the same branch/working tree as the implementation —
  do not create a separate branch or commit just for a status change (in
  Mode B, fold the status edit into that spec's own atomic commit).

## 3. Commits, staging, and pushing — hard boundary (Mode A)

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

## 4. Suggested commit message format

```
MEDGENT-XXX: <short summary of what the spec delivers>
```

In Mode A, propose this message in your handoff summary so the user can
copy it — you do not run the commit yourself. In Mode B, use this exact
format as the message of that spec's atomic commit (you author it).

## 5. Dependency ordering

- Before starting a spec, check its `Depends on` field against
  `specs/README.md`. All listed dependencies must show `Status: Done` **and**
  be merged into `main` (verify with `git log main` / `git branch -r`, not
  just the spec file, since the spec file on a stale local `main` may be
  outdated — re-run `git pull origin main` first). In Mode B, a dependency
  satisfied by an earlier commit on the *same* epic branch also counts —
  it doesn't need to be on `main` yet.
- If a dependency isn't actually merged/committed yet, tell the user before
  starting rather than building on top of nothing.

## 6. Scope discipline per branch

- Touch only the files needed for the spec's acceptance criteria, plus the
  spec's own status field and its `specs/README.md` row.
- If you discover unrelated work that should happen (a bug, missing spec,
  scope gap), do not fold it into the current branch — flag it to the user
  and, if agreed, it becomes a new spec.

## 7. Mode B — per-epic branch, atomic per-spec commits

Only active when the user has explicitly said to batch an epic this way
(as opposed to Mode A being silently assumed).

- Branch per epic, from latest `main`, named after the epic file:
  `EPIC-XX-short-slug` (e.g. `EPIC-03-ai-agent`, matching
  `specs/epics/EPIC-03-ai-agent.md`).
- Within that branch, implement the epic's child specs **in their
  dependency order**, one at a time. For each spec: mark it `In Progress`,
  implement it fully (including its own tests, per
  [[02-code-quality]]), verify it works, mark it `Done`, update
  `specs/README.md`'s row for it, then make **one atomic commit** covering
  exactly that spec's changes (code + its own status/index updates) using
  the message format in section 4.
- Do not squash multiple specs into one commit, and do not split one spec's
  work across multiple commits — one spec, one commit, in order.
- Once every spec in the epic is `Done` and committed, make one final
  commit updating the epic file's own `Status` to `Done` (e.g.
  `docs: mark EPIC-XX done`).
- Still never `git push`, never open/merge a PR, never touch `main` beyond
  `pull`. When the branch is ready, stop and tell the user it's ready —
  they decide when to push and open the PR, same as Mode A.
- If a spec inside the epic turns out to depend on something outside the
  epic that isn't on `main` yet, stop and flag it rather than guessing.

### Checkpoint exception for specs needing a real external integration

If a spec's acceptance criteria can only be genuinely verified against a
live external service the user controls (an API key/account only they can
provision — e.g. MEDGENT-009's Groq integration), don't commit it purely
on the strength of mocked tests. Implement it, run it live once against
the real credential (already in the user's local, gitignored `.env` —
never ask them to paste a live key into chat), show them the result, and
only commit once they've confirmed it actually works. Every other spec in
the epic still follows the normal Mode B flow (implement → verify →
commit → move on) without waiting for a checkpoint.
