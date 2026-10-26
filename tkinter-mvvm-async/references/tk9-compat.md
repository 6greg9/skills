# Tk 9 compatibility

## Status (2026-10; re-check for new Python releases)

Verified on Windows on 2026-10-14 with uv-managed CPython (python-build-standalone):

| Python | Tcl/Tk |
|---|---|
| 3.12.13, 3.13.14 | 8.6.12 |
| 3.14.6 | 8.6.14 |
| 3.15.0b3 | 9.0.3 |

Reported, not re-verified here:
- python.org **macOS** installer 3.14.5+ bundles Tcl/Tk 9.0.3; Homebrew `python-tk@3.14` builds
  against Tcl/Tk 9.0.
- uv-managed CPython 3.13.14 on **Linux** ships Tcl/Tk 9.0.3, so a Linux CI job can run Tk 9
  while Windows developers and targets still run 8.6.
- Python 3.15 moves the official **Windows** installer to Tk 9.0 (consistent with the uv build
  above); beta-period breakage was reported.
- Linux distro Pythons follow the distro's `tk` package.

The easiest Tk 9 environment on Windows is `uv python install 3.15` + `uv venv --python 3.15`;
on Linux CI, a uv-managed Python under `xvfb-run`.

Check at runtime:

```python
import tkinter
print(tkinter.TkVersion, tkinter.Tcl().call("info", "patchlevel"))
```

## Write code that runs on both 8.6 and 9.0

| Pattern | 8.6 | 9.0 | Do this |
|---|---|---|---|
| `var.trace_variable / trace_vdelete / trace_vinfo` | works (deprecated) | **raises** `TclError: bad option "variable": must be add, info, or remove` (verified 9.0.3; Python 3.15 also warns) | `trace_add / trace_remove / trace_info` |
| `ttk.Combobox.current()` on empty combobox | `-1` | raw Tk returns `""`; tkinter still returns `-1` (verified) | fine via tkinter; don't call the raw Tk command yourself |
| Raw `root.tk.call(...)` returning ints/lists | 8.6 semantics | some return types changed | wrap in `root.tk.splitlist` / explicit conversion; avoid raw calls where tkinter has an API |
| Binary Tcl extensions (tkdnd, tktable, tktreectrl, ...) | 8.6 builds | **must be rebuilt for Tcl 9** | prefer pure-Python widgets; pin and test extension versions |
| Pure-Tcl ttk themes (`.tcl` + images) | fine | usually fine, verify | test the theme package on a Tk 9 build before upgrading |
| Freezing (PyInstaller, Nuitka, cx_Freeze) | stable | Tcl 9 library layout differs (zipfs); older freezer hooks may not find `tk.tcl` | upgrade the freezer, test the frozen build on the target OS |

The bundled templates (`observable.py`, `mvvm.py`, `comms_runtime.py`, `theme.py`) pass the same
test suite on 8.6.12 and 9.0.3.

## Migration checklist

- [ ] `grep -rn "trace_variable\|trace_vdelete\|trace_vinfo"` returns nothing.
- [ ] No hard-coded Tcl version paths (`tcl8.6`, `tk8.6`) in code, spec files or env vars
      (`TCL_LIBRARY`, `TK_LIBRARY`).
- [ ] Third-party Tcl/Tk extensions inventoried; each confirmed on Tk 9 or replaced.
- [ ] CI runs the app's smoke test on an 8.6 build and a 9.0 build.
- [ ] Frozen executable tested on a clean target machine.
- [ ] Fonts, DPI scaling and widget sizes re-checked with `snap_view.py`; don't assume
      pixel-identical layout across Tk versions.

## Platform hygiene (both versions)

```python
import sys
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)   # call BEFORE tk.Tk()
    except (AttributeError, OSError):
        pass
```

- Without DPI awareness Windows bitmap-scales the window at 125-200% (blurry text), and screen
  grabs no longer line up with `winfo_*` coordinates; `snap_view.py` sets it for that reason.
- Use `ttk` widgets consistently; mixing classic `tk` widgets breaks theming.
- Set fonts once on the named fonts (`TkDefaultFont`, `TkTextFont`, `TkHeadingFont`,
  `TkFixedFont`), not per widget; `apply_theme` does this from the tokens. Copy a font's
  `configure()` options, not `actual()`: `actual()` reports whole points and turns a 14px font
  into 10pt.
