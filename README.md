# Personal Codex Skills

Curated skills maintained for use with Codex.

## Included skills

- `cross-session-workflow` — establishes durable project workflow files for work that spans multiple Codex sessions.
- `create-pyside6-widget-project` — creates uv-managed PySide6 Widget application scaffolds with Qt Designer, lightweight MVVM pages, tests, and PyInstaller packaging.
- `robot-motion-control-ui` — designs explicit, testable robot motion controls for frames, jogging, command lifecycles, telemetry, and safety-state presentation.
- `signal-waveform-controls` — designs faithful live and historical waveform interaction, triggering, measurement, spectrum analysis, and high-rate rendering.
- `precision-imaging-controls` — designs precise, cross-platform imaging interaction, measurement, annotation, ROI, rendering, and input controls.
- `wpf-design-taste` — guides polished, non-generic WPF interface design, redesign, theming, and visual verification.
- `wpf-industrial-brutalist-ui` — designs rigid, high-contrast WPF interfaces for engineering tools, workstations, and telemetry.
- `wpf-materialdesign-mvvm` — scaffolds or refactors a WPF application into a MaterialDesignInXaml MVVM shell.
- `wpf-minimalist-ui` — designs restrained, editorial, information-first WPF interfaces with minimal visual chrome.

## Claude skills

These skills were written for Claude (Claude Code and claude.ai). They have a `SKILL.md` with `name` and `description` frontmatter, and no `agents/openai.yaml`.

- `cppsharp` — generates C# (P/Invoke) or C++/CLI bindings from C/C++ headers with CppSharp, and fixes common generation, build, and runtime errors.
- `ste100-writing` — explains, writes, rewrites, and checks English in ASD-STE100 Simplified Technical English, with a heuristic checker script.
- `tkinter-mvvm-async` — architecture and verification rules for tkinter/ttk desktop apps: MVVM, threads and asyncio, Tk 8.6 to 9.0 compatibility, ttk theming, and screen rendering checks.
- `go-templ-htmx` — conventions for server-rendered Go web UIs with net/http, templ, and htmx 2.x.
- `fastapi-htmx-jinja` — conventions for server-rendered FastAPI web UIs with Jinja2, jinja2-fragments, and htmx 2.x.
- `industrial-hmi-style-guide` — reference for industrial and semiconductor equipment HMI screens: ISA-101, ISA-18.2, and SEMI E90/E84 status conventions.
- `html-drawio-wireframe` — low-fidelity wireframes as one HTML file per screen (mobile and desktop, every state, numbered notes), checked by script and exported to draw.io, with annotations read back from draw.io.

## Install

Copy a skill directory into your local Codex skills directory:

```powershell
Copy-Item -Recurse .\cross-session-workflow "$env:USERPROFILE\.codex\skills\"
```

Restart Codex after adding or updating a skill.

For Claude Code, copy a skill directory into `~/.claude/skills/` instead:

```powershell
Copy-Item -Recurse .\ste100-writing "$env:USERPROFILE\.claude\skills\"
```

For claude.ai, zip the skill directory (the skill folder must be at the top of the zip) and upload it in Settings → Capabilities → Skills.

## Contributing

Each skill lives in its own directory and includes a `SKILL.md` file. Add or edit skills locally, then commit and push the changed directory.
