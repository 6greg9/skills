#!/usr/bin/env python3
"""Create a safe PySide6 Widgets project from the bundled template assets."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tempfile
from pathlib import Path


PROJECT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
TOKEN_PATTERN = re.compile(r"__[A-Z][A-Z0-9_]*__")
SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = SKILL_ROOT / "assets"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a uv-managed PySide6 Widgets project."
    )
    parser.add_argument("project_name", help="kebab-case project and app name")
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.cwd(),
        help="parent directory in which to create the project",
    )
    parser.add_argument(
        "--layout",
        choices=("standalone", "workspace"),
        required=True,
        help="generated uv project layout",
    )
    parser.add_argument(
        "--display-name",
        help="human-facing application title; defaults to title-cased project name",
    )
    return parser.parse_args()


def validate_inputs(project_name: str, display_name: str) -> None:
    if not PROJECT_NAME_PATTERN.fullmatch(project_name):
        raise ValueError(
            "project name must be kebab-case and match "
            "^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
        )
    if not display_name.strip():
        raise ValueError("display name must not be empty")
    if "\n" in display_name or "\r" in display_name:
        raise ValueError("display name must be a single line")


def replacements(project_name: str, display_name: str) -> dict[str, str]:
    package_name = project_name.replace("-", "_")
    return {
        "__PROJECT_NAME__": project_name,
        "__PACKAGE_NAME__": package_name,
        "__DISPLAY_NAME__": display_name,
        "__DISPLAY_NAME_XML__": html.escape(display_name, quote=True),
        "__DISPLAY_NAME_PY__": repr(display_name),
        "__DISPLAY_NAME_TOML__": json.dumps(display_name, ensure_ascii=False),
    }


def render_text(text: str, values: dict[str, str], source: Path) -> str:
    for token, value in values.items():
        text = text.replace(token, value)
    unresolved = sorted(set(TOKEN_PATTERN.findall(text)))
    if unresolved:
        raise ValueError(f"unresolved template tokens in {source}: {unresolved}")
    return text


def render_relative_path(relative: Path, values: dict[str, str]) -> Path:
    rendered_parts: list[str] = []
    for part in relative.parts:
        rendered = part
        for token, value in values.items():
            rendered = rendered.replace(token, value)
        if rendered.endswith(".tmpl"):
            rendered = rendered[:-5]
        rendered_parts.append(rendered)
    return Path(*rendered_parts)


def render_tree(source_root: Path, target_root: Path, values: dict[str, str]) -> None:
    if not source_root.is_dir():
        raise FileNotFoundError(f"template asset directory is missing: {source_root}")
    for source in sorted(source_root.rglob("*")):
        if source.is_dir():
            continue
        relative = render_relative_path(source.relative_to(source_root), values)
        target = target_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_text(encoding="utf-8")
        target.write_text(
            render_text(content, values, source), encoding="utf-8", newline="\n"
        )


def scaffold(
    project_name: str,
    destination: Path,
    layout: str,
    display_name: str | None = None,
) -> Path:
    title = display_name if display_name is not None else project_name.replace("-", " ").title()
    validate_inputs(project_name, title)
    destination = destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / project_name
    if target.exists():
        raise FileExistsError(f"target already exists; refusing to overwrite: {target}")

    values = replacements(project_name, title)
    staging_parent = Path(tempfile.mkdtemp(prefix=f".{project_name}-", dir=destination))
    staging_root = staging_parent / project_name
    try:
        staging_root.mkdir()
        if layout == "standalone":
            render_tree(ASSETS_ROOT / "app-template", staging_root, values)
        elif layout == "workspace":
            render_tree(ASSETS_ROOT / "workspace-root-template", staging_root, values)
            render_tree(
                ASSETS_ROOT / "app-template",
                staging_root / "apps" / project_name,
                values,
            )
        else:
            raise ValueError(f"unsupported layout: {layout}")
        staging_root.replace(target)
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)
    return target


def main() -> int:
    args = parse_args()
    try:
        target = scaffold(
            project_name=args.project_name,
            destination=args.destination,
            layout=args.layout,
            display_name=args.display_name,
        )
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2

    app_root = target if args.layout == "standalone" else target / "apps" / args.project_name
    print(f"Created {args.layout} project: {target}")
    print(f"Application root: {app_root}")
    print("Next: run uv sync, compile the UI, then run pytest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
