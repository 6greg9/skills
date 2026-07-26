# Safety, Telemetry, and Access

Use this reference to derive UI state from authoritative controller facts without overstating guarantees.

## Contents

- Separate safety and stop meanings
- Derive eligibility from reason codes
- Model mode, authority, and permission
- Track telemetry provenance and freshness
- Present stale/unknown state and status precedence
- Reset, limit, and collision behavior

## Separate Safety from Presentation

Identify the subsystem authoritative for every safety-relevant signal and stop action. The UI may observe and request; it is safety-rated only when the certified architecture says so.

Scope the control contract to the whole robot application/cell: robot arm, external axes, gripper/load, tooling, conveyor, and process energy such as spindle, laser, welding, pneumatic, or hydraulic hazards. `Robot stopped` is not evidence that the cell is safe.

Keep these concepts distinct:

- application hold or pause;
- controller controlled stop;
- program cancel/abort;
- protective stop;
- safety stop;
- emergency stop;
- drive power/servo state;
- fault reset and safety reset.

Use controller-specific wording where meanings differ. Never place unlike actions behind one generic `Stop` label. Make the normal motion-stop action consistently reachable, but do not depict an application-layer button as a substitute for a physical emergency-stop device.

Keep physical evidence distinct: stop requested, stop acknowledged, decelerating, measured zero velocity, monitored standstill, torque removed, brake verified, and energy isolated. Report only facts provided by their authoritative subsystem.

## Build Motion Eligibility from Reasons

Compute eligibility as data, not scattered widget conditions:

`eligible = mode_ok AND authority_ok AND permission_ok AND telemetry_live AND drives_ready AND enabling_ok AND interlocks_clear AND limits_ok AND collision_ok AND no_active_conflict`

Preserve every failed predicate as a reason code with source and remediation hint. Show all relevant blockers even if only one determines the disabled state. Re-evaluate from an atomic snapshot before submission; the controller must validate again.

Apply this eligibility gate to new motion. Keep the controller-defined stop path idempotent and callable when ordinary motion authorization, telemetry freshness, or UI state is degraded.

Examples include:

- wrong operating mode;
- another station owns control;
- session or lease expired;
- insufficient role;
- external enabling device not active;
- guards, doors, zones, or process interlocks open;
- drives not enabled or robot unhomed;
- protective stop, safety stop, emergency stop, or unresolved fault;
- near/at joint or workspace limit;
- collision monitor unavailable, predicted collision, or detected contact;
- telemetry stale or controller disconnected;
- incompatible command already active.

## Model Mode, Authority, and Permission Separately

Represent:

- controller operating mode, such as Manual/Teach/Auto/Remote;
- control authority/ownership, including station, user, lease, and expiry;
- role permission, such as view, jog, teach, execute, edit configuration, or reset;
- external enabling-device state;
- safety and process interlocks.

Do not infer one from another. A user may have permission without owning control; owning control does not make the current mode eligible; an enabled UI session does not satisfy an external enabling device.

Make authority acquisition/release explicit. Warn before taking control when supported. Expiry, replacement by another owner, logout, or controller session change must invalidate active interaction state.

Treat frame/TCP, payload, limit, bypass/override, and safety-configuration changes as separately permissioned, versioned, and auditable operations. Give overrides a named scope, mode, owner, and expiry; keep their annunciation persistent.

## Carry Telemetry Provenance

For each atomic telemetry snapshot, retain:

- controller session/boot ID;
- sequence number or revision;
- controller source timestamp;
- local monotonic receive time;
- schema/model revision;
- validity/quality bits;
- required fields from the same coherent sample or declared aggregation window.

Use monotonic receive age to drive local freshness. Use controller time for ordering only when clock synchronization and reset behavior are understood. Detect duplicates, gaps, reordering, session changes, and impossible field combinations.

Define product-specific states such as:

- `live`: within the verified motion-enable freshness bound;
- `degraded`: delayed, gapped, partial, or lower quality but still useful for observation;
- `stale`: too old or incomplete for motion authorization;
- `disconnected`: transport/session unavailable;
- `resynchronizing`: connected but controller truth not yet reconciled.

Keep thresholds configurable and justified by controller update rate, transport behavior, UI scheduling, and watchdog contract. Avoid one magic timeout for every signal.

Track freshness per required signal/source. A fresh gateway heartbeat does not make pose, mode, safety controller, tool, or external equipment data fresh. Show the health of independent communication legs when the architecture exposes them.

## Present Stale and Unknown State

When telemetry becomes stale:

- freeze the last sample only as a visibly labeled historical value;
- show age and quality near the affected data;
- stop accepting new motion and end transient jog intent;
- distinguish `unknown` from `false`, `off`, `clear`, and numeric zero;
- keep the last controller command evidence without inventing a terminal state.

On reconnect, do not flash normal/live from transport connectivity alone. Enter `resynchronizing` until mode, ownership, safety/interlocks, active command, and a coherent fresh robot state have been reconciled.

## Prioritize Status Presentation

Keep a persistent status region visible during motion control. Present at least:

- safety stop/emergency/protective-stop state;
- connection and telemetry freshness;
- controller mode and drive readiness;
- control owner/lease and operator permission;
- enabling-device and interlock state;
- limit/collision status;
- active command and stop/cancel progress.

Use a deterministic severity/precedence policy so critical blockers cannot be visually displaced by success toasts or routine progress. Do not collapse multiple simultaneous blockers into the most convenient message. Pair color with text, shape/icon, and accessible announcements.

## Reset Carefully

Treat reset or fault acknowledgement as a distinct permissioned command, not a local dismissal:

- show exactly which condition is eligible for reset;
- require controller acknowledgement and resulting state evidence;
- never imply that reset removes the physical cause;
- do not automatically resume the interrupted motion;
- log actor, station, command ID, controller result, and relevant state revision where auditability is required.

Keep fault acknowledgement, fault clear, safety reset, re-arm, drive enable, and deliberate restart as separate transitions. Restoring a guard, releasing a stop, or clearing an interlock may permit a new start; it must not cause one.

## Collision and Limit Honesty

Distinguish configured limits, proximity warnings, controller rejection, predicted collision, detected contact, and protective stop. Display the provenance and coverage of any collision result. `No collision detected` is not equivalent to `safe` when geometry, payload, tools, zones, or telemetry are missing or stale.

Treat UI visualization and offline simulation as advisory unless explicitly part of the approved control/safety system. The controller remains responsible for enforcing motion validity at execution time.
