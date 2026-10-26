# Navigation / Display Hierarchy (ISA-101 Level 1-4)

ISA-101 defines HMI screens as a hierarchy providing **progressive exposure of detail**,
specifically to avoid the "flat pile of equally-important screens" pattern that results from
just digitizing a stack of P&IDs (one screen per drawing, all reachable in one click, none of
them prioritized).

## The four levels

| Level | Name | Purpose | Typical audience/use |
|---|---|---|---|
| **1** | Process/Tool Area Overview | Big-picture, whole span-of-control at a glance. Shows overall health/KPIs, not control interactions. | Good candidate for a wall/overview display; not where operators click to control equipment. |
| **2** | Unit/Process Operation | One functional unit (e.g. one tool, one process module, one conveyor line) — most-used screen for day-to-day monitoring and control. | The operator's "home" screen for their area of responsibility. |
| **3** | Sub-unit / Equipment Detail | Zoomed into one piece of equipment or subsystem within the unit — more parameters, more control points. | Used when investigating or adjusting something specific flagged from Level 2. |
| **4** | Diagnostic / Support Detail | Deep diagnostic data, raw I/O, engineering-only parameters, detailed trends. Not for routine operation. | Engineers/maintenance, not routine operator use. |

## Design rules that follow from this

- **Fixed, small, predictable navigation depth.** An operator should be able to reach any
  relevant screen from the overview in a small, consistent number of steps — not an
  unpredictable maze. If reaching a common screen takes 5+ clicks, the hierarchy needs
  rework, not a shortcut hack.
- **Level 1 shows status, not controls.** Keep interactive control elements (start/stop,
  setpoint entry) out of the top-level overview — it exists to answer "is everything OK,"
  not to be a control surface. Mixing the two invites accidental interaction with the wrong
  equipment from an overview screen.
- **Consistent layout scaffolding across all screens at the same level** — same location for
  navigation, alarm banner, and system status regardless of which Level-2/3 screen is showing,
  so operators build muscle memory instead of re-learning layout per screen.
- **Alarm banner and navigation are persistent**, not per-screen — an alarm should be visible
  and actionable no matter which level/screen the operator is currently viewing.
- **Trends over snapshots.** Where feasible, show a short trend/sparkline alongside a live
  value rather than only the instantaneous number — operators infer direction and rate of
  change much faster from a trend than from watching a number change.
- **Contextualize values in place.** Show expected range/setpoint/deviation on the same
  faceplate as the live value, rather than requiring a separate trip to a detail screen just to
  know whether "72" is fine or alarming.

## Applying this to equipment/tool HMI (not just plant-wide process)

For a single piece of equipment (e.g. one semiconductor tool) rather than a whole plant, the
same 4-level idea compresses but the *principle* — overview → operation → detail → diagnostic —
still holds:

- Level 1 → whole-tool status (state machine summary, alarm summary, throughput).
- Level 2 → per-module/per-chamber operation screen (the screen an operator actually lives on).
- Level 3 → component detail within a module (e.g. one robot arm, one load port).
- Level 4 → raw I/O, PLC register view, engineering diagnostics — gated behind an
  engineer/maintenance role, not exposed on the default operator navigation path.
