# Design system, ttk styles and mockup comparison

Design System: "Equipment HMI (tkinter)", https://claude.ai/artifact/8ku5sZX7PdGESW8ychz21Z

## Files

| File | Where it comes from | Where it goes |
|---|---|---|
| `tokens.json` | the Design System's `project/tokens.json` (Artifact `read` by path, or download from the page); `assets/tokens.baseline.json` in this skill only as a fallback | `app/design/tokens.json`, committed |
| `theme.py` | this skill's `templates/theme.py` (same code as the Design System's `project/tkinter/theme.py`; if they differ, use the newer and tell the user) | `app/theme.py` |
| `compare_mockup.py` | this skill's `scripts/compare_mockup.py` | `tools/compare_mockup.py` |
| mockup PNGs | exported from the Design canvas, one per screen state, at the panel resolution | `design/mockups/<screen>__<scenario>.png` |

When tokens change in the Design System, re-export `tokens.json` and commit it; never edit
colors in `theme.py`. If neither the skill's `templates/theme.py` nor the Design System is
reachable, ask the user for `theme.py` rather than rewriting it.

## Applying the theme

```python
from app.theme import apply_theme
root.theme = apply_theme(root, "app/design/tokens.json")   # once, before building views
view = LoadPortView(root, root.theme)
```

`apply_theme` switches ttk to `clam` (the only built-in theme that honours field, border and
background colors on every OS), creates named fonts `hmi.<style>` from the type styles,
re-points `TkDefaultFont` / `TkTextFont` / `TkHeadingFont` / `TkFixedFont`, and defines these
styles:

| Need | Style / lookup |
|---|---|
| Static label, title, section, caption | `TLabel`, `Title.TLabel`, `Section.TLabel`, `Caption.TLabel` |
| Live value, key figure, setpoint value, ID | `Live.TLabel`, `LiveLarge.TLabel`, `Setpoint.TLabel`, `Id.TLabel` |
| Running / complete text, used sparingly | `Running.TLabel` |
| Panel (raised ground, 1px border, title inside) | `ttk.Frame(style="Panel.TFrame", padding=theme.px("space-3"))` + `Panel.Section.TLabel`; nested frames `PanelBody.TFrame`; labels inside use `Panel.<style>` |
| Setpoint input | `ttk.Entry(style="Setpoint.TEntry", font=theme.font("value"))`; Entry/Combobox/Spinbox fonts come from the widget, not the style |
| Alarm fills | `AlarmCritical/AlarmHigh/AlarmMedium/AlarmAdvisory/BadQuality/Shelved.TLabel` |
| Unacknowledged alarm | `blink(lbl, ("AlarmCriticalUnackA.TLabel", "AlarmCriticalUnackB.TLabel"), theme.ms("blink-period"))` returns `stop()` for acknowledge |
| Equipment state | `StateIdle/StateActive/StateDone/StateAttention/StateAlarm.TLabel`; SEMI E90 mapping in `E90_STATE_STYLE`; bind with `bind_style` |
| Canvas drawing | `theme.color("state-active")`, `rounded_rect(cv, x0, y0, x1, y1, theme.px("radius-sm"), fill=..., outline=theme.color("outline"))` |
| Spacing / durations | `theme.px("space-3")`, `theme.ms("confirm-hold")` |

Rules:
- Views never contain hex codes, font tuples or pixel paddings; only style names and `theme.*`
  lookups. Add a style to `theme.py`'s tables instead of configuring one inline.
- Font sizes are pixels from the tokens, applied as **negative** Tk sizes (`-14`), so the app
  matches the mockup regardless of Tk's point/DPI conversion.
- Prefer `Panel.TFrame` over `ttk.Labelframe`: Labelframe draws its title on the border, which
  does not match the design system's panel.
- Every alarm or state fill carries a text label (`P1`, `P2`, `Lost`, `SHELVED`), never color
  alone: `alarm-critical` and `alarm-high` are close in lightness.

## Feasibility tiers (guidance, not bans)

| Tier | Mockup uses | tkinter cost |
|---|---|---|
| 1 Native | flat fills, 1px borders, system fonts at token sizes, grid layout, tables, tabs, progress | style names from `theme.py`, no extra code |
| 2 Canvas / images | rounded tiles and pills, lamps, wafer maps, equipment diagrams, gauges, icons, blinking | `tk.Canvas` + `rounded_rect`, PNG icons, `blink()`: some code per widget, fully doable |
| 3 Expensive | translucency, blur, real shadows, gradients, fonts not installed on the tool PC, CSS transitions | pre-rendered images or drop it; mostly HMI anti-patterns anyway |

When a mockup uses Tier 3, raise it with the user before building: suggest the Tier 1/2
equivalent, or a pre-rendered image if the effect matters.

## Mockup and tkinter comparison

1. Export each agreed mockup state from the Design canvas to
   `design/mockups/<screen>__<scenario>.png` at the panel resolution. Scenario names must match
   the screen module's `preview()` scenarios.
2. Render the tkinter screen at the same size:
   `python tools/snap_view.py app.screens.<screen> --sizes <WxH>` (the theme is applied
   automatically from `app/design/tokens.json`).
3. `python tools/compare_mockup.py` writes
   `shots/compare/<screen>__<scenario>__<WxH>__compare.png` (mockup left, tkinter right), flags
   size mismatches, and lists states that exist on only one side.
4. Open every compare image. **Bugs:** different structure or order, a missing element, a wrong
   color token, wrong enabled/disabled state, clipped text, a title outside its panel.
   **Expected:** font rasterization and fallback fonts on Linux CI, +-1-2px spacing, widgets
   shrinking to content where the mockup had a fixed width (fix only if the width matters).
5. Fix the tkinter side unless the mockup is not buildable at reasonable cost (Tier 3); then
   say so and propose updating the mockup or the Design System instead.
