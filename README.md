# Personal Codex Skills

Curated skills maintained for use with Codex.

## Included skills

- `cross-session-workflow` — establishes durable project workflow files for work that spans multiple Codex sessions.
- `create-pyside6-widget-project` — creates uv-managed PySide6 Widget application scaffolds with Qt Designer, lightweight MVVM pages, tests, and PyInstaller packaging.
- `robot-motion-control-ui` — designs explicit, testable robot motion controls for frames, jogging, command lifecycles, telemetry, and safety-state presentation.
- `precision-imaging-controls` — designs precise, cross-platform imaging interaction, measurement, annotation, ROI, rendering, and input controls.
- `wpf-design-taste` — guides polished, non-generic WPF interface design, redesign, theming, and visual verification.
- `wpf-industrial-brutalist-ui` — designs rigid, high-contrast WPF interfaces for engineering tools, workstations, and telemetry.
- `wpf-materialdesign-mvvm` — scaffolds or refactors a WPF application into a MaterialDesignInXaml MVVM shell.
- `wpf-minimalist-ui` — designs restrained, editorial, information-first WPF interfaces with minimal visual chrome.

## Install

Copy a skill directory into your local Codex skills directory:

```powershell
Copy-Item -Recurse .\cross-session-workflow "$env:USERPROFILE\.codex\skills\"
```

Restart Codex after adding or updating a skill.

## Contributing

Each skill lives in its own directory and includes a `SKILL.md` file. Add or edit skills locally, then commit and push the changed directory.
