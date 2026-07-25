#!/usr/bin/env python3
"""Run dependency-free structural checks against both scaffold layouts."""

from __future__ import annotations

import tempfile
from pathlib import Path

from scaffold_project import scaffold


def require(path: Path) -> None:
    if not path.is_file():
        raise AssertionError(f"expected generated file: {path}")


def validate_layout(root: Path, name: str, layout: str) -> None:
    app_root = root if layout == "standalone" else root / "apps" / name
    package_name = name.replace("-", "_")
    package_root = app_root / "src" / package_name
    for path in (
        root / "pyproject.toml",
        app_root / "pyproject.toml",
        app_root / "README.md",
        app_root / "scripts" / "audit_package.py",
        app_root / "scripts" / "compile_ui.py",
        app_root / "scripts" / "package_app.py",
        package_root / "views" / "dashboard_page.ui",
        package_root / "views" / "main_window.ui",
        package_root / "views" / "settings_page.ui",
        package_root / "views" / "view_dashboard_page.py",
        package_root / "views" / "view_main_window.py",
        package_root / "views" / "view_settings_page.py",
        app_root / "tests" / "test_main_window.py",
        app_root / "tests" / "test_package_audit.py",
        app_root / "packaging" / f"{name}.spec",
    ):
        require(path)
    if "__PACKAGE_NAME__" in (app_root / "pyproject.toml").read_text(encoding="utf-8"):
        raise AssertionError("template token remained in generated pyproject.toml")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="pyside6-skill-test-") as temp:
        parent = Path(temp)
        for layout in ("standalone", "workspace"):
            name = f"sample-{layout}"
            root = scaffold(name, parent, layout, f"Sample {layout.title()}")
            validate_layout(root, name, layout)

        try:
            scaffold("Invalid_Name", parent, "standalone")
        except ValueError:
            pass
        else:
            raise AssertionError("invalid project name was accepted")

        existing = parent / "already-there"
        existing.mkdir()
        try:
            scaffold("already-there", parent, "standalone")
        except FileExistsError:
            pass
        else:
            raise AssertionError("existing target was overwritten")

    print("Scaffold structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
