---
name: industrial-hmi-style-guide
description: Reference guide for industrial and semiconductor equipment HMI screens (人機介面, 機台畫面) - High Performance HMI / ISA-101 grayscale color language, ISA-18.2 alarm priorities, colors and blinking, the ISA-101 display hierarchy (Levels 1-4), and SEMI E90 substrate / E84 load-port handoff status conventions. Use whenever designing, reviewing, styling or coding an equipment, SCADA, PLC operator panel or semiconductor tool HMI in any toolkit (tkinter, PySide6/Qt, WPF, web/htmx, WinCC, Ignition), including choosing status or alarm colors, alarm banners and lists, screen navigation structure, wafer, load-port or EFEM state display, or feedback that a screen looks too much like a toy or consumer app. Also when the user mentions ISA-101, ISA-18.2, IEC 62682, High Performance HMI, Hollifield, ASM Consortium, SEMI E90/E84/E95, or asks for an HMI style guide.
---

# Industrial HMI Style Guide

A reference for designing HMI screens that follow established industrial/process-automation
design standards rather than generic consumer-app aesthetics. This skill is a **reference**,
not a code generator — read the relevant file(s) below, then apply the principles in the
actual UI code (tkinter, PySide6, WPF, web, Ignition, WinCC, etc.).

## When to go deeper

Load the reference file(s) that match what the user is actually doing. Don't load all of them
for a simple question — pick what's relevant.

| Situation | Read |
|---|---|
| Choosing background/foreground colors, "why does my HMI look like a toy", general visual style | `references/color-visual-language.md` |
| Alarm banners, alarm list, alarm colors, alarm priority, blinking/flashing rules | `references/alarm-management-isa18-2.md` |
| Screen navigation structure, how many screens, overview vs detail screens, menu depth | `references/navigation-hierarchy-isa101.md` |
| Semiconductor equipment status display (wafer/substrate state, load port, EFEM, carrier state) | `references/semiconductor-status-conventions.md` |

## Core principle (read this even if you don't open the reference files)

Industrial HMI design inverts the intuition most software/app designers start with:

- **Color is scarce, not decorative.** The default palette is grayscale/muted. Color is
  reserved almost exclusively for things the operator must act on (alarms) or things
  that carry live process meaning (live values vs. static labels). If everything is
  colorful, nothing stands out when something is actually wrong.
- **"Boring" is a feature, not a bug.** A screen that looks flat and gray in normal
  operation is doing its job — it means nothing needs attention right now. Read
  `color-visual-language.md` before "improving" a gray HMI with brighter colors, gradients,
  3D bevels, or skeuomorphic textures — those are anti-patterns in this domain even though
  they read as "polish" in consumer UI design.
- **Hierarchy of screens matters as much as any single screen.** Operators should be able to
  go from a plant/tool-wide overview down to component-level detail in a small, fixed number
  of predictable steps — not a flat pile of equally-important screens.
- **Alarms are a distinct subsystem with its own rules**, not "red text when something is
  bad." Priority, color, and flashing behavior are governed by ISA-18.2, and getting this
  wrong (alarm floods, color abuse, no acknowledge state) is the single most common cause of
  operator error during abnormal situations.

## Use the project's palette first

- If the project already has a documented palette or design tokens — for example the
  "Equipment HMI" design system (`tokens.json`, derived from this guide) — use its names and
  values. The hex values in the reference files are the baseline those tokens came from, not a
  second source of truth to mix in.
- No palette yet: start from the baseline in `references/color-visual-language.md`, put it in
  one token/theme file, and tell the user it is a baseline to adapt and sign off for their site.

## Applying this when writing code

1. Confirm the color/status semantics first (which states map to which colors) using
   `color-visual-language.md` and, if alarms are involved, `alarm-management-isa18-2.md`.
2. Apply them as a small, centralized theme/token module, never as hex values inline in each
   widget — this mirrors how a real site "HMI style guide" document is used and keeps the
   palette auditable in one place:
   - tkinter/ttk: follow the `tkinter-mvvm-async` skill (`theme.py` turns `tokens.json` into
     styles such as `AlarmHigh.TLabel`, `StateActive.TLabel`).
   - Web (htmx with Jinja or templ): CSS custom properties generated from the same tokens
     (`--alarm-high`) and one class per state (`.state-active`), no inline styles.
   - PySide6/Qt, WPF: a stylesheet / resource dictionary generated from the tokens, with a
     dynamic property or style per state.
3. For semiconductor-specific screens (EFEM, load port, sorter, wafer map), map states with
   `semiconductor-status-conventions.md` in one table next to the SECS/GEM state enums, so the
   HMI names line up with the backend's.
4. Pair every color with text or shape (priority label `P1`/`P2`, the state name), so the
   screen still works for color-blind operators and in grayscale screenshots.

## Reviewing an existing screen

Quick pass; the reference files have the reasoning behind each point:

- Squint test: in normal operation is the screen calm and gray, and does the abnormal thing
  jump out?
- Is any alarm color used for something that is not that alarm (logo, "danger" button, chart
  series, decorative border)?
- More than 3–4 alarm priorities/colors, no distinct unacknowledged vs. acknowledged state, or
  shelved alarms that look like "normal"?
- Anything blinking other than an unacknowledged alarm, or blinking text?
- Gradients, bevels, drop shadows or decorative color?
- Color as the only encoding anywhere?
- Navigation: is every routine screen reachable in a few predictable steps, with the alarm
  banner in the same place on every screen?

Report each finding as: the issue → why it matters to the operator → the concrete fix (token
or style name to use).

## Important caveat

None of the underlying standards (ISA-101, ISA-18.2, SEMI E95) mandate exact hex codes — they
mandate structure, semantics, and a documented, consistently-applied palette. The specific RGB
values in the reference files are a defensible, commonly-used starting baseline (consistent
with published High Performance HMI / ASM Consortium guidance), not a copy of a copyrighted
proprietary style guide. Always tell the user this is a baseline to adapt and formally sign off
on for their own site/product, not a value to blindly hardcode as "the standard."
