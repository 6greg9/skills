# PyInstaller packaging profiles

## Choose a profile

Use `minimal` by default for the generated Widgets-only application. It retains Qt Core, Gui, Widgets, the Windows platform plugin, Python/Shiboken runtimes, config, and QSS resources. It rejects QML, Quick, PDF, OpenGL, SVG, VirtualKeyboard, Qt Network, translations, extra Qt plugins, and Designer/generated UI source files in the runtime bundle.

Use `full` only after the application intentionally imports one of those Qt modules or needs extra image, input, TLS, platform, or localization plugins. The full profile lets PyInstaller's PySide6 hooks collect their normal runtime set, but still omits `.ui` source files because the application imports generated UI classes.

## Build and verify

Run the generated packaging wrapper from the app root:

```text
uv run python scripts/package_app.py --profile minimal
```

The wrapper performs a clean PyInstaller build, audits the runtime tree, and launches the packaged executable in hidden smoke-test mode. It fails if a minimal bundle contains forbidden Qt modules/plugins or if the executable does not exit cleanly.

For a workspace, run from the workspace root:

```text
uv run --package <project-name> python apps/<project-name>/scripts/package_app.py --profile minimal
```

Use `--profile full` for a deliberately feature-rich Qt application. Use `--no-smoke` only in an environment that cannot start executables; report that packaged startup was not verified.

## Evolve the package safely

- Add a Qt feature to application imports first, then choose `full` until a tested narrower profile explicitly retains its modules and plugins.
- Keep config and QSS in `datas`; do not add `.ui` or `*_ui.py` as data when generated modules are imported normally.
- Rebuild with `--clean`; never optimize by manually deleting files from `dist`.
- Run the audit and packaged smoke test after every exclusion change on the oldest supported Windows target.
- Treat size limits as regression signals, not proof that the bundle is complete.
