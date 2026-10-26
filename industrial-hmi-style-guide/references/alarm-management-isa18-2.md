# Alarm Management (ISA-18.2 / IEC 62682)

ISA-18.2 (also published as IEC 62682) defines a full lifecycle for alarm management:
philosophy → identification → rationalization → detailed design → implementation → operation →
maintenance/monitoring → audit. For HMI design work you'll mostly touch the "detailed design"
layer — priority-to-color mapping and on-screen behavior — but it's worth knowing the bigger
lifecycle exists so alarm design isn't treated as an afterthought bolted onto a finished screen.

## What counts as an alarm

ISA-18.2's core definition: an alarm is a notification that requires **operator action**. If
nothing needs to be done in response, it is not an alarm — it's a status/event log entry.
Conflating "interesting to log" with "alarm" is the most common root cause of alarm floods.

## Priority levels

ISA-18.2 recommends **no more than 3–4 distinct alarm priorities**, and recommends that no more
than ~5% of configured alarms be "high" priority (if everything is high priority, nothing is).
A typical 4-level mapping:

| Priority | Typical color | Meaning | Audible |
|---|---|---|---|
| Critical / Emergency | Red, full saturation | Immediate safety/equipment-damage risk, immediate response required | Distinct, urgent tone |
| High | Red or amber (site-dependent) | Prompt response required, real consequence if ignored | Distinct tone |
| Medium/Low | Yellow | Response required but not urgent | Softer tone or none |
| Advisory/Informational | Cyan/blue or white | For awareness, does not require action (arguably shouldn't be a true "alarm" at all) | None |

Notes:
- Priority should be based on **consequence severity and required response time**, decided
  during rationalization — not assigned based on "whatever colors the SCADA package has
  available."
- Some site style guides reserve red *exclusively* for the highest priority and never use it
  for anything lower, to preserve maximum contrast for the alarms that matter most.
- Magenta/purple is sometimes reserved separately for "bad quality / instrument fault" (i.e.
  the sensor itself is unreliable) so it isn't confused with a real process alarm.

## On-screen alarm states and behavior

An alarm typically needs to represent more than one binary state — at minimum:

- **Unacknowledged + active** — the loudest visual state (often blinking + full color).
- **Acknowledged + active** — operator has seen it, condition still exists (often solid color,
  no longer blinking).
- **Unacknowledged + cleared** — condition resolved but operator hasn't acknowledged yet
  (still needs a distinct visual treatment so it isn't lost).
- **Normal** — no visual weight at all.

Encode state using **both color and shape/pattern/blink**, not color alone — colorblind
operators (about 1 in 12 men) must still be able to distinguish states. Blinking should stop
being necessary to distinguish state once acknowledged; use it only for "needs attention now."

## Alarm banner / summary list UI rules

- Sort by priority first (highest at top), then time — an operator scanning top-to-bottom
  should see the worst thing first.
- Give each priority level a unique, consistent color used *nowhere else* on that screen.
- Keep the color palette in the alarm list small (3–4 colors max) — more than that slows down
  operator discrimination speed rather than adding information.
- Show the expected operator action alongside the alarm text where feasible (short, specific:
  "Close V-12" not just "High Level").
- Support alarm suppression states (shelved / out-of-service / suppressed-by-design) visibly
  distinct from "normal" — a suppressed alarm should not look identical to "nothing wrong,"
  or operators lose track of what's intentionally silenced vs. actually fine.

## Common failure modes to avoid

- **Alarm flood**: one root cause triggering dozens of alarms (e.g. every downstream sensor
  reacting to one upstream fault) with no correlation/suppression logic.
- **Chattering**: an alarm rapidly toggling active/clear because it has no deadband or
  time-delay around the setpoint — add hysteresis/on-delay so real state changes are
  distinguished from noise.
- **Color abuse**: reusing an alarm color for a non-alarm purpose elsewhere on the same screen,
  which trains operators to ignore it.
- **Standing alarms**: an alarm that's been active so long / so often that operators mentally
  filter it out — a signal the priority or setpoint needs re-rationalizing, not a normal state
  to design around.
