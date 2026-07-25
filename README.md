# Personal Codex Skills

Curated skills maintained for use with Codex.

## Included skills

- `cross-session-workflow` — establishes durable project workflow files for work that spans multiple Codex sessions.
- `wpf-materialdesign-mvvm` — scaffolds or refactors a WPF application into a MaterialDesignInXaml MVVM shell.

## Install

Copy a skill directory into your local Codex skills directory:

```powershell
Copy-Item -Recurse .\cross-session-workflow "$env:USERPROFILE\.codex\skills\"
```

Restart Codex after adding or updating a skill.

## Contributing

Each skill lives in its own directory and includes a `SKILL.md` file. Add or edit skills locally, then commit and push the changed directory.
