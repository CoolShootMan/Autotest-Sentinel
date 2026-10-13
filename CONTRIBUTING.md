# Contributing

Conventions for this repository. Applies to everyone working on `bosinc/Pear-automation-test`.

## Commit messages

Write commit messages in **English**, following [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

| Type | Use for |
|---|---|
| `feat` | a new feature |
| `fix` | a bug fix |
| `chore` | tooling, deps, config — no production code change |
| `docs` | documentation only |
| `refactor` | code change that neither fixes a bug nor adds a feature |
| `test` | adding or fixing tests |
| `ci` | CI configuration |

Rules:

- Subject: imperative mood, lower-case, **no trailing period**, ~72 chars or less.
- Optional body: explain **what** and **why**, not how. Wrap at 72 chars.
- Reference the ticket when there is one, e.g. `fix(ui): correct CTA locator (KAT-12345)`.

## Pull requests

`main` receives changes through pull requests only — direct pushes are not counted as PRs.

```bash
# 1) branch off an up-to-date main
git switch main && py -3.9 tools/gh_push.py --fetch && git merge origin/main --no-edit
git switch -c feat/<ticket>-<slug>

# 2) commit (English message, per above)
git commit -F .git/COMMIT_MSG.txt

# 3) open the PR (pushes the branch, prints the PR URL)
py -3.9 tools/gh_pr.py --push --title "feat(xxx): ..." --body "..."

# 4) merge with a merge commit
py -3.9 tools/gh_pr.py --merge --pr <N>
```

- **PR titles are also written in English.**
- Merge with a **merge commit**. Do **not** rebase or squash branches that others may have pulled.

## History

- **Never rewrite or force-push `main`.** Always merge.
- Commit messages are part of a commit's identity (SHA). Editing one rewrites every later commit and breaks everyone's clone.
- If a rewrite is ever unavoidable: get the owner's sign-off first, push a **backup branch** holding the old tip, then use `--force-with-lease` (never a bare `--force`), and verify the tree is byte-identical (`git rev-parse <old>^{tree} <new>^{tree}`).
  ```bash
  py -3.9 tools/gh_push.py --branch <backup-branch>        # push old tip first
  py -3.9 tools/gh_push.py --branch main --force           # force-with-lease under the hood
  ```

## Repository hygiene

- Do **not** delete `data/` wholesale. `.gitignore` deliberately keeps
  `data/verify/<KEY>/{report.md,path_map.md,ones_cases*.json,case_diff.*}` tracked — it is business data, not scratch.
- Generated artifacts (`allure-results/`, `allure-report/`, `report/`, `step_captures/`, `recordings/`, `log/`) stay untracked.
- `allure/` is the **Allure CLI dependency** (used by `main.py` and CI) — do not remove it as "generated output".
- Credentials and login state (`*cookie*.json`, tokens) must never be committed.

## Documentation

- Root README is bilingual: `README.md` (**English** — the file GitHub renders by default) and
  `README.zh-CN.md` (Chinese). Keep both in sync, and keep the language switch line at the top of each.
