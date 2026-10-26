---
name: tkinter-mvvm-async
description: Architecture and verification rules for non-trivial tkinter/ttk desktop apps, especially equipment-side tools talking to PLCs, SECS/GEM hosts or E84 load ports - MVVM without a framework (Observable, Command, binders), threads and asyncio next to the Tk main loop (UiDispatcher, comms loop on its own thread), Tk 8.6 to 9.0 compatibility, theming ttk from the Equipment HMI design-system tokens, and rendering every screen to PNG to check layout and compare with mockups. Bundles tested templates (observable.py, mvvm.py, comms_runtime.py, theme.py) and tools (check_view_rules, snap_view, compare_mockup). Use whenever writing, refactoring, reviewing or debugging tkinter code beyond a toy script, including UI freezes, 'main thread is not in main loop' errors, widgets updated from worker threads, PLC or serial polling in a GUI, ttk styling, Tk 9 upgrades or PyInstaller builds with Tk, even if MVVM or asyncio is not mentioned.
---

# tkinter MVVM + async + Tk 9

Opinionated rules for maintainable tkinter apps, especially equipment-side tools that talk to
PLCs and SECS hosts. Colors, alarm presentation and screen hierarchy for equipment HMIs come
from the `industrial-hmi-style-guide` skill and the Equipment HMI design system (Part 5); this
skill covers how that look is applied in tkinter, not which colors to choose.

## Start from the bundled files

Everything below is implemented in this skill's folder and tested on Windows with
Python 3.12 / Tk 8.6.12 and Python 3.15 / Tk 9.0.3 (2026-10). Copy the files into the project
instead of retyping code: retyped copies drift and lose the fixes recorded in their comments.

| Skill file | Copy to | What it is |
|---|---|---|
| `templates/observable.py` | `app/observable.py` | `Observable`, `Command`, `computed` (no tkinter) |
| `templates/mvvm.py` | `app/mvvm.py` | `UiDispatcher`, `Bindings`, `bind_*` binders; re-exports the three above |
| `templates/comms_runtime.py` | `app/comms_runtime.py` | asyncio loop on its own thread (Model B) |
| `templates/theme.py` | `app/theme.py` | tokens.json to ttk styles, named fonts, `blink()`, `rounded_rect()` |
| `assets/tokens.baseline.json` | `app/design/tokens.json` | fallback only; get the current tokens from the Design System (Part 5) |
| `scripts/check_view_rules.py`, `scripts/snap_view.py`, `scripts/compare_mockup.py` | `tools/` | layering check, PNG renders, mockup side-by-side |
| `examples/loadport.py`, `examples/loadport_themed.py` | (reference) | one complete screen module, unthemed and themed |

Adjust the `app` package name if the project uses another layout. Read a template before
changing its behaviour; the comments explain the non-obvious choices.

---

## Part 1 — Architecture & binding

```
Model / Service   PLC driver, SECS handler, DB, file I/O.   No tkinter import. May run on any thread.
ViewModel         State + commands (app.observable only).   Exposes Observable[T] and Command.
Binder            Glue: Observable <-> widget.              Only place that touches both sides.
View              Layout only (plain-Python ttk.Frame).     No business logic, no I/O.
```

- **ViewModels never import tkinter**, not even indirectly through `app.mvvm` or `app.theme`.
  That keeps them unit-testable without a display and reusable under PySide6;
  `check_view_rules.py --viewmodels` enforces it.
- **Only the Tk main thread touches widgets or `tk.Variable`.** Every cross-thread update goes
  through `UiDispatcher` (Part 2).
- Derived state ("can load" = carrier present AND E84 ready AND no alarm) lives in the VM as
  `computed(...)`, never in widget callbacks, so it has one definition and can be tested.

What the templates provide:

- `Observable(value)`: thread-safe holder; setting `.value` notifies subscribers on the setting
  thread; equal values are ignored, which also breaks two-way binding loops.
  `subscribe(cb, immediate=True)` returns a disposer.
- `computed(fn, *sources)`, and `Command(execute, can_execute)` which only runs while
  `can_execute.value` is true.
- `UiDispatcher(root)`: `post(fn, *args)` (FIFO) and `post_latest(key, fn, *args)` (newest per
  key per pump) from any thread; `close()` before `root.destroy()`. A failing callback is
  logged and the pump keeps running.
- Binders returning disposers for a `Bindings(view)` bag that disposes on the view's
  `<Destroy>`: `bind_text`, `bind_enabled`, `bind_style` (state to ttk style), `bind_entry`
  (two-way), `bind_grid_visible`, `bind_command`.

When writing a new binder:
- Use `trace_add` / `trace_remove` / `trace_info` only; `trace_variable`, `trace_vdelete` and
  `trace_vinfo` raise `TclError` on Tk 9.
- `textvariable` exists only on some widgets; state, style, visibility and images go through
  `configure`, posted via the dispatcher.
- Bind `<Destroy>` with `add="+"` so other handlers survive.
- Never echo a view-originated change back through the dispatcher: the echo arrives one pump
  later and overwrites newer keystrokes (see `bind_entry`).

If the VM needs time or combination logic (debounce, throttle, combine_latest), RxPY can
replace the hand-rolled Observable: read `references/rxpy.md`.

---

## Part 2 — Concurrency

**The one hard rule:** widgets and `tk.Variable` are touched only from the thread that created
the `Tk()` root. Everything else is a way to obey that rule: `UiDispatcher.post` for updates
from other threads, `post_latest` for high-rate signals (a 10 ms PLC poll would otherwise
flood the UI).

| Model | Use for | Avoid for |
|---|---|---|
| A. Single-thread asyncio, Tk pumped with `root.update()` | small tools and test utilities where a few seconds of freeze is harmless | anything with protocol timers (E84 TP1-TP6, SECS T3/T5-T8, linktest) |
| **B. Tk main thread + comms asyncio loop on a worker thread** (default for equipment) | PLC polling, SECS/GEM, E84 handshakes, anything time-critical | - |
| C. Plain worker threads + dispatcher | legacy blocking drivers, simple polling | many concurrent protocols (use B) |

Model A stops every coroutine while Windows drags or resizes the window, while `messagebox`,
`filedialog` or `wait_window` run, and during any CPU-heavy callback, which is why protocol
timers never live there. Model A code and the full list of freezes: `references/concurrency.md`.

Model B (`templates/comms_runtime.py`, wiring example in `references/concurrency.md`):
- **comms to UI**: VM `Observable` set on the comms thread, binders post to the Tk thread.
- **UI to comms**: `Command.execute` calls `runtime.submit(coro)`. For a result use
  `future.add_done_callback(lambda f: ui.post(handle, f))`; the callback runs on the comms
  thread, so it may only `post`.
- **Shutdown** on `WM_DELETE_WINDOW`: `runtime.stop()`, then `ui.close()`, then
  `root.destroy()`. Destroying Tk first makes pending posts hit dead widgets.
- **Blocking libraries** (pyserial, sync pymodbus, vendor DLLs via ctypes, sync DB drivers):
  `await asyncio.to_thread(fn, ...)`; the await resumes on the comms thread, so still post to
  the UI. CPU-heavy work (image processing, big log parsing): `ProcessPoolExecutor`.

---

## Part 3 — Tk 9 compatibility

Official builds are moving from Tk 8.6 to 9.0 at different times per platform (Python 3.15's
Windows build ships 9.0.3, while uv's 3.12-3.14 Windows builds still ship 8.6). Write code that
runs on both:

- Only `trace_add` / `trace_remove` / `trace_info`.
- Prefer tkinter APIs over raw `root.tk.call(...)`: some raw return types changed (raw
  `ttk::combobox current` returns `""` on Tk 9; `Combobox.current()` still returns -1).
- Binary Tcl extensions (tkdnd, tktable, ...) must be rebuilt for Tcl 9; no hard-coded
  `tcl8.6` / `tk8.6` paths; upgrade and re-test freezers (PyInstaller, Nuitka, cx_Freeze).
- Check at runtime: `tkinter.TkVersion`, `tkinter.Tcl().call("info", "patchlevel")`.

Per-platform status, the full pattern table, the migration checklist and platform hygiene
(DPI awareness, fonts): `references/tk9-compat.md`.

---

## Part 4 — Screen modules and visual verification

An agent writing tkinter cannot see its result, and the usual failures (clipped text,
misaligned columns, controls squeezed at small resolutions, wrong enabled state) never show up
in a traceback. So: no visual designer, plain-Python views, and every screen rendered to PNG
and looked at before reporting done.

### Screen module convention

One screen = one module under `app/screens/` with exactly four parts (see `examples/loadport.py`):

1. **View class** (`ttk.Frame` subclass): layout only. Widgets are attributes with role
   prefixes (`ent_`, `lbl_`, `btn_`, `cmb_`, `tree_`, `frm_`). No VM reference, no logic.
2. **VM shape**: the observables and commands the binder needs. The real VM may live in
   `app/viewmodels/`; a screen module never imports the Model/comms layer.
3. **Binder** `bind_<screen>(view, vm, ui) -> Bindings`.
4. **`preview(master, ui) -> (widget, {scenario_name: callable})`** building a fresh view + VM
   with fake data (no hardware) and named scenarios that set VM state.

Layout: `grid` with `columnconfigure(..., weight=)` for anything that stretches, `place()` only
for overlays; size text widgets in characters, never pixels. Scenarios cover at least `empty`,
normal operation, busy/disabled, alarm/error, and `long_text` (longest IDs and state names,
translated strings if the UI is multilingual).

### Agent loop after any View or binder change

1. `python tools/check_view_rules.py app/screens --viewmodels app/viewmodels` must print
   `view rules OK`.
2. Render at the target panel resolution **and** the smallest supported one:
   `python tools/snap_view.py app.screens.<name> --sizes 1280x800,1024x768`
   (headless Linux: prefix `xvfb-run -a -s "-screen 0 1920x1080x24"`). It applies
   `app/design/tokens.json` first when present, keeps the window topmost, and is DPI-aware on
   Windows so grabs stay aligned at 125-200% display scaling.
3. **Open every PNG** and check: labels and inputs aligned per column; nothing clipped or
   overlapping; enabled/disabled state matches the scenario; stretchable areas stretch;
   alarm/error states visually distinct (per `industrial-hmi-style-guide`).
4. Fix every `WARN clipped:` line (requested width larger than allocated, almost always cut-off
   text) or state why it is acceptable.
5. Repeat until clean; show the user the final PNGs of the changed scenarios.

Fonts and DPI on Linux CI differ from a Windows target: CI renders catch layout logic errors;
do a final pass on the target OS at its DPI setting before release.

---

## Part 5 — Design system to tokens to ttk

The look lives in the Claude Design **Design System "Equipment HMI (tkinter)"**
(https://claude.ai/artifact/8ku5sZX7PdGESW8ychz21Z), not in Python. Its `project/tokens.json`
is the single source for colors, type, spacing, radii, border widths and timings; mockups and
the tkinter app both read it.

- Put the current tokens at `app/design/tokens.json`: Artifact `read` with path
  `project/tokens.json`, or download from the page. Use `assets/tokens.baseline.json` only when
  the Design System is unreachable, and tell the user it may be out of date.
- At startup, before building views: `root.theme = apply_theme(root, "app/design/tokens.json")`.
  Views receive the theme (`LoadPortView(master, theme)`); `snap_view.py` sets `root.theme` the
  same way, so `preview()` can pass it on.
- Views contain no hex codes, font tuples or pixel paddings: only style names (`Live.TLabel`,
  `Panel.TFrame`, `AlarmHigh.TLabel`, `StateActive.TLabel`, ...) and `theme.px()`, `font()`,
  `color()`, `ms()` lookups. A missing style is added to `theme.py`'s tables, not configured
  inline, so the palette stays auditable in one place.
- States map to styles in one table next to the state enum, bound with `bind_style`
  (`E90_STATE_STYLE` in `theme.py` for SEMI E90).
- Font sizes are token pixels applied as negative Tk sizes (`-14`), so the app matches the
  mockup regardless of DPI.

Style catalogue, feasibility tiers for mockup effects, and the mockup comparison workflow
(`compare_mockup.py`): `references/design-system.md`. Worked themed screen:
`examples/loadport_themed.py`.

---

## Review checklist

- [ ] `check_view_rules.py` passes: views layout-only, ViewModels import only `app.observable`
- [ ] No widget, `tk.Variable` or `root.after` access from non-Tk threads except via `UiDispatcher`
- [ ] No `time.sleep` in Tk callbacks; protocol timers live in the comms loop, never in `after()`
- [ ] High-rate signals use `post_latest` (or Rx throttling); subscriptions disposed via `Bindings`
- [ ] Shutdown order: comms stopped, dispatcher closed, then Tk destroyed
- [ ] Only `trace_add/remove/info`; no `tcl8.6` paths; extensions and freezer checked on Tk 9
- [ ] Every changed screen rendered at target and smallest size, PNGs opened, no unexplained `WARN clipped`
- [ ] Themed apps: no hex codes, font tuples or pixel paddings in views; states to styles through one table
