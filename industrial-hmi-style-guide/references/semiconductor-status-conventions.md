# Semiconductor Equipment Status Conventions (SEMI E90 / E84)

This file bridges the general High Performance HMI / ISA-101 color-and-hierarchy principles
(see the other reference files) with the state models semiconductor equipment engineers
already work with in SECS/GEM backend code (E90 substrate tracking, E84 handoff handshake).
The goal is that the HMI's visual state names line up 1:1 with the state names already used in
equipment control software, so there's no "translation layer" between what the PLC/EFEM
controller reports and what's drawn on screen.

This is a **practical convention**, not a reproduction of SEMI's copyrighted standard text —
always verify exact state names/transitions against your organization's licensed SEMI E90/E84
documents.

## SEMI E90 — Substrate (wafer) tracking state → color mapping

E90 tracks a substrate with separate state models. Common GEM300 names (verify against your
licensed E90): transport `AT_SOURCE` / `AT_WORK` / `AT_DESTINATION`; processing
`NEEDS_PROCESSING`, `IN_PROCESS`, `PROCESSED`, `ABORTED`, `STOPPED`, `REJECTED`, `LOST`,
`SKIPPED`; ID verification `ID_NOT_CONFIRMED`, `WAITING_FOR_HOST`, `CONFIRMED`,
`CONFIRMATION_FAILED`. Implementations add their own names (e.g. `NotAcquired`, `InCarrier`);
map every model's states onto the same few rows by operator consequence:

| Substrate state category | Suggested color treatment | Why |
|---|---|---|
| Not yet confirmed / waiting for host (`WAITING_FOR_HOST`, `ID_NOT_CONFIRMED`; e.g. `NotAcquired`) | Neutral gray, low visual weight | Nothing to act on yet — treat like "normal/idle," not alarm-adjacent. |
| At rest in a carrier (`AT_SOURCE`, `AT_DESTINATION`; e.g. `InCarrier`) | Neutral gray | Static/at-rest state. |
| In process / in transit (`IN_PROCESS`, `NEEDS_PROCESSING`, `AT_WORK`) | Cool live-data color (dark blue/green), same convention as any other "live" value | Signals "this is actively changing," consistent with the general live-data color rule. |
| ID confirmation failed (`CONFIRMATION_FAILED`) | Amber/yellow, with the reason as text | The host rejected the substrate ID: someone has to look, but nothing is damaged. |
| Processed / complete (`Processed`) | Muted green, used sparingly | Completion state — don't make it loud; it's good news, not urgent news. |
| Aborted / Stopped / Rejected | Amber/yellow | Requires operator awareness/action but isn't necessarily an equipment-damage emergency — matches ISA-18.2 "medium/high" tier, not "critical" by default. |
| Lost / Skipped | Red, full saturation, likely paired with an actual E90-triggered alarm | A lost substrate is a serious event (potential wafer damage, mapping mismatch) — treat as alarm-tier, not just a status label. |

Practical rule: **substrate state color should follow the same palette rules as everything
else on the HMI** — reserve full-saturation red for states that are genuinely alarm-worthy
(Lost, Skipped, certain Aborted cases), and keep routine in-flow states in the muted/cool
palette so a wafer map full of "InProcess" substrates doesn't look like a wall of alarms.

## SEMI E84 — Carrier handoff handshake status

E84 governs the handshake between an AMHS/OHT vehicle (or operator) and the equipment's load
port during carrier (FOUP) transfer. On an EFEM/load-port HMI screen, this is usually shown as
a small state indicator per load port rather than a full alarm banner, since most of the
sequence is normal, expected traffic — not something requiring operator action.

| Handshake phase (conceptual) | Suggested treatment |
|---|---|
| Idle / no transfer in progress | Neutral gray — this is the "nothing happening" baseline state. |
| Transfer request active / in progress (valid, transfer request, busy-style states) | Cool live-indicator color, static — no pulsing: motion is reserved for things that need action (see `color-visual-language.md` rule 4). If the phase matters, show which E84 signal is active as text or a step indicator. |
| Transfer complete | Brief, muted confirmation (done color or a checkmark for ~2 s, no flashing), then return to idle gray — don't leave "complete" as a permanently colored state or it accumulates visual noise across ports. |
| Handshake timeout / error (e.g. no response within the E84 time window) | This should escalate into the real ISA-18.2 alarm system (see `alarm-management-isa18-2.md`), not just a colored icon on the load port — a timed-out handoff is exactly the kind of thing that needs an acknowledgeable alarm, an audible cue, and a place in the alarm summary list, not just a red icon operators might not be looking at. |

## General principle for mapping SECS/GEM-style state machines to HMI color

1. **Group states by operator consequence, not by how many distinct states the state machine
   has.** A state machine might have 8–10 named states; the HMI palette should still only use
   the handful of color tiers from `color-visual-language.md` (normal/gray, live/cool color,
   good-but-quiet/green, needs-attention/amber, alarm/red).
2. **Anything that would also fire a SECS/GEM alarm ID should look like an alarm on screen**,
   using the ISA-18.2 conventions — don't invent a separate, inconsistent "equipment fault"
   color scheme that competes with the alarm banner's colors.
3. **Keep the mapping in one place in code** (e.g. a `SubstrateStateColor` or
   `E84StateColor` enum/dict next to your existing SECS/GEM state enums), so when the state
   machine changes, the HMI color mapping is a one-line update, not a search-and-replace across
   widget code.
