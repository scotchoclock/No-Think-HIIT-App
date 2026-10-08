# Git for a PM, using this repo as the lab

## What matters for a PM

You will not be judged on rebasing. You will be judged on whether you can:

1. Read history to answer "when did this change, and why?" without asking an engineer.
2. Write work as small, well-labelled changes that others can review.
3. Run a backlog, release notes and roadmap in GitHub (Issues, Projects, Releases), where engineering already lives.

Everything below builds those three skills. Git (the tool on your machine) and GitHub (the website that hosts a copy) are different things.

## The mental model: four places

```
working folder  --git add-->  staging area  --git commit-->  local history  --git push-->  GitHub
(your files)                  (next snapshot)                 (.git folder)                (remote "origin")
```

- A **commit** is a labelled snapshot of the whole project, not a diff. It has an author, a time, a message and a parent.
- **Staging** lets you choose what goes in the next snapshot. That is how you keep one commit to one idea.
- **Nothing is on GitHub until you push.** Commits are local until then.

## Setup (once)

Check Git exists in PowerShell: `git --version`. If not: `winget install --id Git.Git -e`, then reopen PowerShell.

```powershell
git config --global user.name "Taylor Sharpe"
git config --global user.email "scotchoclock@users.noreply.github.com"
cd "C:\Users\sharp\No Think HIIT"
git status
```

If Git says "dubious ownership", run the `safe.directory` command it prints. The repo was created by a different user account than your Windows login.

## First push

The repo already has 9 commits locally. Publish them:

```powershell
git push -u origin main
```

A browser window opens for GitHub sign-in (Git Credential Manager). Sign in there. Never paste a password or token into a file or chat. If GitHub reports the remote already has commits (for example an auto-created README), run `git pull --rebase origin main` and push again.

## Week 1: read history (no risk, high payoff)

Run each command and read the output before moving on.

```powershell
git log --oneline                      # the story of the project
git log --stat -3                      # which files each recent commit touched
git show 1470e55                    # one commit in full: message plus code changes
git diff 22e1b61 1470e55 --stat        # v39 -> v42, files changed
git diff 22e1b61 1470e55 -- app/index.html   # the actual code changes
git log -S"LEAD_IN" --oneline -- app/index.html   # which commit first added LEAD_IN
git blame -L 300,310 app/index.html    # who/when for lines 300-310
```

Exercise: find the commit that introduced the 3-second lead-in without opening the app. `git log -S` is the "when did this feature appear" tool you will use most as a PM.

## Week 2: make changes the safe way (branches)

A **branch** is a parallel line of work. `main` stays working; experiments live elsewhere.

```powershell
git switch -c shorter-circuit-break
# edit app/index.html line ~307: CIRCUIT_BREAK = 90  ->  60
git diff                               # review before saving
git add app/index.html
git commit -m "Shorten circuit break from 90s to 60s"
git switch main                        # the change disappears from your folder
git switch shorter-circuit-break       # and comes back
```

Decide: keep it (`git switch main; git merge shorter-circuit-break`) or throw it away (`git switch main; git branch -D shorter-circuit-break`). Either is fine. The point is that trying things costs nothing.

Undo cheat sheet:

| Situation | Command |
|---|---|
| Edited a file, want the last commit's version back | `git restore <file>` |
| Staged the wrong file | `git restore --staged <file>` |
| Bad commit already pushed | `git revert <hash>` (adds an undo commit; safe) |
| Bad commit not pushed, fix the message | `git commit --amend` |

Avoid `git reset --hard` and `git push --force` until you know exactly what they destroy.

## Week 3: GitHub as your PM workspace

On https://github.com/scotchoclock/No-Think-HIIT-App:

1. **Issues = backlog.** Create one per item, with a user-visible title and acceptance criteria. Seed it with the open items: render the new countdown clips, wire in per-circuit break lines, verify music mixing on Android and iPhone, handle the silent-switch limitation.
2. **Projects = board.** Create a board with Todo / Doing / Done and add the issues.
3. **Pull requests = review.** Push a branch, open a PR, write what changed and why, and put `Closes #12` in the description. Merging closes the issue automatically. Even solo, PRs give you a written record, and it is the workflow every engineering team uses.
4. **Tags and Releases = release notes.** Mark shipped versions:

```powershell
git tag -a v42 1470e55 -m "Music mixing, unique moves"
git tag -a v41 3e0cf71 -m "Lead-in and leveling"
git tag -a v40 6496ced -m "Count cutoff fix"
git tag -a v39 22e1b61 -m "Voice overhaul"
git push --tags
```

Then on GitHub: Releases > Draft a new release > pick a tag > "Generate release notes". Your commit messages become the changelog, which is why they matter.

## Week 4: collaboration habits

- **Commit message format:** a short imperative title (about 60 characters), blank line, then why. Prefix with the artifact version while versions map to commits.
- **One idea per commit.** If the message needs "and", split it.
- **Pull before you push** when anyone else touches the repo: `git pull --rebase`.
- **Never commit secrets.** API keys live in environment variables. If one is ever committed, rotate the key at the provider first; deleting the file does not remove it from history.
- **Do not commit large generated files.** That is why `.gitignore` excludes the videos and audio (about 700 MB; GitHub rejects files over 100 MB).
- Add a `CHANGELOG.md` or use Releases, not both.

## Working with Claude on this repo

Ask for the work in Git terms and you practice the vocabulary on real changes:

- "Make this change on a branch and show me the diff before committing."
- "Commit the app change and the voice scripts separately."
- "Write the release notes for v43 from the git log since v42."
- "Open issues for the feedback items I listed."

Review `git diff` yourself before approving a commit. Reading diffs is the skill that transfers to every engineering conversation.

## Command reference

| Goal | Command |
|---|---|
| Where am I, what changed | `git status` |
| See unstaged / staged changes | `git diff` / `git diff --staged` |
| Stage / commit | `git add <file>` / `git commit -m "..."` |
| History | `git log --oneline --graph --all` |
| New / switch branch | `git switch -c <name>` / `git switch <name>` |
| Download remote changes | `git pull --rebase` |
| Publish | `git push` |
| Who changed this line | `git blame <file>` |
| When did this text appear | `git log -S"text"` |
