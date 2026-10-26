# Color & Visual Language (High Performance HMI / ISA-101)

Based on ASM Consortium "High Performance HMI" methodology (Hollifield et al.) and the
ISA-101 framework it fed into. ISA-101 itself does not lock in exact hex values — it mandates
that a site/product define, document, and consistently apply a level-based palette. The values
below are a commonly used, defensible baseline to start from.

## The core inversion

Traditional/legacy SCADA style: bright primary colors everywhere (red pipes, green pipes,
yellow equipment, blue tanks) used decoratively to distinguish equipment types. This is the
anti-pattern High Performance HMI exists to fix — full-screen saturated color becomes
"wallpaper" the operator's eye stops registering, so when something is actually critical,
it doesn't stand out.

High Performance HMI style: the *default* rendering of a normally-operating process is close
to monochrome. Color is spent only where it carries meaning the operator must act on.

## Baseline palette

| Purpose | Color | Approx. RGB / hex | Notes |
|---|---|---|---|
| Screen background | Medium-light gray | `RGB(192,192,192)` / `#C0C0C0` (or a slightly darker `#B8B8B8`–`#D0D0D0` band) | Not black, not white. Black causes eye fatigue over long shifts and worsens color contrast; white causes glare under control-room lighting. |
| Equipment outline / normal state | Dark gray / near-black lines | `#404040`–`#000000` | Static piping/equipment shapes, unpowered/idle state. |
| Static labels, tag names | Dark gray/black text | `#202020` | Should not compete visually with live data. |
| Live/dynamic process values | Cool, low-saturation color | Dark blue `#1F3A5F` or dark green `#1F4D3A` | Distinguishes "this number is live" from static text, without being alarm-loud. |
| Operator input fields / setpoints | Distinct muted color (often cyan or tan) | e.g. `#4A7A8C` | Signals "you can change this," separate from read-only live data. |
| Equipment running / active | Sparse, muted green | Use *sparingly* — some site style guides avoid green entirely to keep it fully reserved for alarms-clear state | — |
| Alarm colors | Bright, fully saturated, reserved exclusively for alarms | See `alarm-management-isa18-2.md` | Never reuse an alarm color for anything else on the same screen. |

## Rules that matter more than the exact hex values

1. **Alarm colors are never reused for anything else.** If red means "alarm," nothing
   non-alarm on the screen may be red — not a logo, not a decorative border, not a "danger"
   label on a button that isn't actually an alarm.
2. **One documented palette, applied consistently across every screen.** Ad hoc color choices
   per-screen or per-developer are the single biggest cause of HMI inconsistency complaints.
   In code, this means a centralized theme/token file, not inline hex values scattered through
   widget code.
3. **Reserve full saturation for exceptions.** At normal control-room viewing distance, a fully
   saturated color covering a small fraction of the screen is immediately detected; the same
   color covering most of the screen is not. Keep saturated color's *screen area* small even
   when you do use it.
4. **Animation/flashing is reserved for "needs immediate action."** Don't use blinking for
   decorative emphasis. When something does flash, keep the object legible in both animation
   states (alternate between two visible shades, not visible/invisible) and give the operator a
   way to stop the flashing once acknowledged. Text itself should not flash; flash a border or
   adjacent indicator instead.
5. **Don't make things invisible.** Hiding an object based on state (rather than dimming/
   graying it) causes confusion later when a different user role sees it appear. Use visual
   weight (contrast, saturation) to de-emphasize, not disappearance.
6. **Font: consistent sans-serif, sized for the viewing distance**, not decorative/branded
   fonts. Legibility at a glance beats visual branding on an HMI.
7. **3D bevels, gradients, drop shadows, skeuomorphic textures are anti-patterns**, not
   polish, in this domain. They increase visual noise without adding information and are one
   of the most common "modern-app" instincts to actively resist here.

## Quick self-check when reviewing a screen

- Would a colorblind operator (about 1 in 12 men has some form of color vision deficiency) still
  be able to tell normal from alarm state? (Pair color with shape/position/text, not color alone.)
- If I squint at this screen, does the abnormal thing jump out, or does everything look equally
  "busy"?
- Could I remove color from 80% of this screen and lose zero information? (If yes, you likely
  already have decorative color to remove.)
