---
description: Generate commit message and commit
---

Please follow these steps:

1. Run `git status` and `git diff` to view changes
2. Analyze the changes and determine if they should be split into multiple commits (e.g., separate by feature, type, or scope)
3. For each commit, generate a commit message following the Conventional Commits specification
4. Format: `type(scope): description`
   - type: 
        - feat: Commits that add, adjust or remove a new feature to the API or UI
        - fix: Commits that fix an API or UI bug of a preceded feat commit
        - refactor Commits that rewrite or restructure code without altering API or UI behavior
        - perf Commits are special type of refactor commits that specifically improve performance
        - style Commits that address code style (e.g., white-space, formatting, missing semi-colons) and do not - affect application behavior
        - test Commits that add missing tests or correct existing ones
        - docs Commits that exclusively affect documentation
        - build Commits that affect build-related components such as build tools, dependencies, project     version, ...
        - ops: Commits that affect operational aspects like infrastructure (IaC), deployment scripts, CI/CD pipelines, backups, monitoring, or recovery procedures, ...
        - chore: Commits that represent tasks like initial commit, modifying .gitignore, ...
   - The description should clearly explain "what was done" and "why"
5. Ask me to confirm each commit one by one
6. Display the remaining number of commits after each commit

Do not commit directly; let me confirm each message first.

**Important:** Do NOT add any auto-generated footers like "Generated with Claude Code" or "Co-Authored-By" to commit messages.