---
name: create-pyside6-widget-project
description: Create complete uv-managed PySide6 desktop project scaffolds with a Sidebar and Stacked Content shell, Qt Designer .ui files, generated Ui_ classes, hand-written View_ classes, lightweight MVVM pages, tests, resources, and optimized PyInstaller packaging. Use when Codex needs to start a standalone src-layout PySide6 app or an apps/app-name uv workspace, establish UI/View/page naming and inheritance conventions, add stacked navigation pages, or add a Qt Designer form that must follow those conventions. Do not use for QML, Qt Quick, WebEngine, FastAPI, or database scaffolds.
---

# Create a PySide6 Widget Project

Create the project with the bundled deterministic Sidebar + Stacked Content scaffold, then use `uv` to materialize and verify it. Treat every `*_ui.py` file as generated code.

## Create the scaffold

1. Resolve a kebab-case project name, destination parent directory, layout (`standalone` or `workspace`), and optional display name from the request. Ask only when one of these choices materially remains unknown.
2. Refuse to overwrite an existing target directory. Do not add a force option.
3. Run:

   ```text
   python <skill-dir>/scripts/scaffold_project.py <project-name> --destination <parent> --layout <standalone|workspace> [--display-name <title>]
   ```

4. Treat the project root as `<parent>/<project-name>`. For workspace mode, treat `apps/<project-name>` as the app root.

## Materialize and verify

Run these commands from the generated project root.

For standalone mode:

```text
uv sync
uv run python scripts/compile_ui.py
uv run pytest
uv build
uv lock
```

For workspace mode:

```text
uv sync
uv run --package <project-name> python apps/<project-name>/scripts/compile_ui.py
uv run --package <project-name> pytest apps/<project-name>/tests
uv build --package <project-name>
uv lock
```

Build, audit, and smoke-test the desktop executable when requested or when validating the scaffold. Read [references/packaging.md](references/packaging.md) before changing packaging profiles or exclusions.

```text
uv run python scripts/package_app.py --profile minimal
```

For workspace mode, prefix the command with `--package <project-name>` and run `apps/<project-name>/scripts/package_app.py`. Keep `minimal` as the default for Widgets-only projects; use `full` only when the app intentionally needs QML, Quick, PDF, OpenGL, SVG, VirtualKeyboard, Qt Network, translations, or additional Qt plugins.

If dependency resolution or download is unavailable, leave the complete scaffold in place and report the first failed command plus the exact recovery command. Never hand-edit the missing `*_ui.py`; generate it after the environment becomes available.

On Windows, if `uv` reports that its default cache path cannot be initialized, retry the same command as `uv --cache-dir "$env:TEMP/codex-uv-cache" ...`. Do not delete or replace the user's default cache without explicit permission.

## Extend the UI

Read [references/ui-conventions.md](references/ui-conventions.md) before adding or renaming a form or stacked page. Author widgets only in Qt Designer `.ui` files, then run `scripts/compile_ui.py`. Keep `View_MainWindow` as the navigation/composition shell, give every visible page its own `.ui` and `View_` class, and keep state and business behavior in Model/ViewModel/Service layers.

## Report completion

State the generated layout and absolute path, list verification commands that passed, report packaged size/profile when packaging ran, and call out any dependency or packaging command that could not be completed. Do not claim success when UI compilation, tests, package audit, or requested smoke testing were skipped.
