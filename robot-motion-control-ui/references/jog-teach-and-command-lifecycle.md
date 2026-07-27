# Jog, Teach, and Command Lifecycle

Use this reference to make transient gestures and durable controller commands explicit.

## Contents

- Model jog sessions and hold-to-run
- Keep external enabling-device semantics honest
- Apply speed and increments
- Track command records and states
- Reconcile after connection loss
- Teach without implicit motion

## Model a Jog as a Session

Represent continuous jogging as a session, not repeated button clicks:

`idle -> arming -> requested -> active -> stopping -> terminal`

Allow `faulted` or `uncertain` from any nonterminal state. Give every session a unique client ID, selected axis/direction, motion context snapshot, requested speed, start time, and last controller observation.

Start only after eligibility is evaluated from a coherent control snapshot. Distinguish:

- press/request emitted;
- controller acknowledgement;
- controller reports motion active;
- release/stop requested;
- controller reports motion stopped.

The UI may show these phases, but must not imply motion before controller evidence.

## Define Hold-to-Run Precisely

Use pointer or key press to request the session and release to request its stop. Also stop or invalidate the session on:

- pointer cancellation or capture loss;
- window/app deactivation, page visibility loss, or relevant focus loss;
- route/navigation or component disposal;
- Escape or an explicit motion-stop action;
- mode, frame, TCP, workpiece, increment, or selected-axis change;
- loss of control authority or permission;
- interlock, limit, collision, protective-stop, or controller fault;
- stale telemetry, session/boot change, or connection loss.

Capture the pointer when the platform supports it, but never rely on capture or release delivery as the safety mechanism. Use a controller-supported hold-to-run primitive, bounded-duration velocity command, heartbeat, or watchdog. Define its timeout from the controller contract, not UI intuition.

Do not restart when a pointer re-enters the control. Require a new intentional press after any terminal or uncertain outcome.

Accept one input identity per session. Suppress browser key-repeat, duplicate pointer-down, multi-pointer ambiguity, and simultaneous opposite directions. Route stop requests as idempotent, high-priority operations that are never delayed behind motion queues, rate limiting, ordinary authorization loss, or stale-view validation.

## Keep Deadman Semantics Honest

Reserve `deadman` or `enabling device` for the external device and controller/safety-system signal. A typical multi-position enabling device may permit motion only in its enabled position and stop on release or over-travel, but use the actual device contract.

Display external enabling-device state separately from an on-screen hold gesture. The UI gesture can be one required condition; it is not a substitute for certified hardware or controller logic.

## Handle Speed and Increments

Show requested speed override and controller-reported effective speed separately. Define whether speed is latched at jog start or may change during motion. If dynamic changes are supported, route them through an acknowledged controller operation.

For incremental jog:

- show the exact step and unit next to the control;
- snapshot step, frame, TCP, and direction per command;
- disable rapid unintended accumulation unless the controller contract explicitly supports queued increments;
- show queued/executing state so repeated presses have visible consequences.

Never silently clamp speed or step. Report the applied limit and source.

## Use a Command Record

Store one record per submitted command with:

- unique, stable `clientCommandId`;
- controller command/correlation ID when acknowledged;
- robot/cell identity, controller session/boot identity, command kind, and immutable motion-context snapshot;
- payload, tool, configuration, limit-profile, and other execution-critical revisions;
- submit time, acknowledgement observation, execution observations, and terminal observation;
- latest sequence/revision;
- rejection, fault, cancellation, or stop reason;
- outcome certainty and telemetry/session provenance.

Use idempotency when the controller supports it. Never generate a new ID merely to retry an ambiguous request.

## Model Command States

Adapt names to the controller while preserving these distinctions:

| State | Meaning |
| --- | --- |
| `draft` | Local intent, not submitted |
| `submitting` | Send attempted; receipt not yet known |
| `acknowledged` | Controller accepted responsibility; execution may not have begun |
| `queued` | Accepted and waiting |
| `executing` | Controller reports active execution |
| `held` | Execution retained but not progressing |
| `completed` | Controller reports successful terminal outcome |
| `rejected` | Controller refused before execution |
| `canceling` | Cancellation requested; terminal result pending |
| `canceled` | Controller reports canceled terminal outcome |
| `stopped` | Controller reports an interrupted command reached its defined stopped terminal outcome |
| `faulted` | Controller reports failed terminal outcome |
| `uncertain` | Observation was lost, so the outcome is unknown |

Terminal states come from authoritative controller reconciliation, not from animations, elapsed time, or pose proximity. Treat client timeout as an observation failure that may lead to `uncertain`, not as `rejected`, `canceled`, or `faulted`.

Accept duplicate and out-of-order events idempotently. Reject regressions unless a controller session/boot change requires full reconciliation.

Define what `completed` means for each command kind: trajectory terminal, within target tolerance, settled, program terminal, or process complete. Show position/tolerance as observation rather than silently substituting it for controller completion.

## Reconcile After Connection Loss

On disconnect:

- stop issuing new motion;
- attempt the controller-defined stop/watchdog path where possible;
- mark affected nonterminal commands `uncertain`;
- retain their identifiers and last evidence;
- never auto-resume or replay.

After reconnect, establish controller session identity, fetch current mode/authority/safety state, active commands, and terminal command results. Reconcile by controller ID or idempotency key. Require a fresh operator action before motion is re-enabled.

## Teach Without Moving Implicitly

Treat `teach` as capture/store, not execute. Show:

- source telemetry sequence/time and freshness;
- joint or Cartesian representation;
- frame, TCP, workpiece, model, and calibration revisions;
- name/version and overwrite target;
- precision/rounding applied at persistence;
- warnings for limits, singularity, unhomed axes, or incomplete collision checking.

Preview and confirm overwrites. Saving a taught pose must not move the robot. Executing or moving to a taught pose is a separate, authorized command with its own preview and lifecycle.
