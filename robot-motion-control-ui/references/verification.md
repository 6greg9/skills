# Verification

Use this reference to test domain math, interaction semantics, protocol behavior, and presentation independently before combining them.

## Contents

- Test the pure domain model
- Exercise every jog termination
- Fault-inject the command protocol
- Verify the operator contract
- Degrade telemetry presentation
- Integrate in layers
- Apply minimum acceptance scenarios

## Test the Pure Domain Model

Cover:

- transform composition/inversion and point/pose round trips;
- quaternion normalization, `q`/`-q` equivalence, Euler convention, and wrap boundaries;
- joint wrap/multi-turn behavior and unit conversions;
- FK provenance and invalid input;
- IK with multiple branches, unreachable targets, singularities, near limits, and collision rejection;
- frame/tool/workpiece revision invalidation;
- eligibility reason aggregation and precedence;
- legal and illegal command/jog state transitions;
- idempotent duplicate events and rejected stale/out-of-order regressions;
- telemetry freshness across sequence gaps, clock jumps, and controller session changes.

Use explicit tolerances tied to the robot/controller contract. Do not choose precision from display decimal places.

## Test Every Jog Termination Path

For each mouse, pen, touch, key, or pendant input that is supported, verify stop behavior for:

- normal release inside and outside the control;
- pointer capture loss and pointer cancellation;
- app deactivation, page visibility loss, focus loss, route change, component disposal, and client crash;
- Escape and explicit stop;
- selected axis, motion mode, frame, TCP, workpiece, step, or speed-context change;
- permission loss, control-owner replacement, or lease expiry;
- interlock, limit, collision, protective stop, drive fault, or operating-mode change;
- stale telemetry, transport failure, and controller restart.

Assert both UI state and the controller request trace. Verify the controller watchdog stops motion when no release/stop message arrives.

## Test the Command Protocol

Exercise:

- acknowledgement before/after intermediate telemetry;
- reject before execution;
- queued, executing, held, resumed, completed, canceled, and faulted outcomes;
- lost request, lost acknowledgement, lost terminal event, and client timeout;
- duplicate submission with the same idempotency key;
- duplicate and out-of-order lifecycle events;
- disconnect while submitting, executing, canceling, or stopping;
- reconnect to the same controller session and to a new boot/session;
- reconciliation where the controller says completed, active, absent, or unknown;
- no automatic replay or resume after ambiguity;
- command timeout followed by an accidental or deliberate retry with the same/different idempotency key;
- controller restart plus late events from the prior session/boot.

Completion must require authoritative controller evidence. If pose tolerance is displayed, test it as an observation separate from command completion.

## Test the Operator Contract

Build a mode/authority/permission/interlock matrix. For every cell, verify:

- the control is correctly enabled or disabled;
- every blocker is visible and understandable;
- a state change during submission is rejected safely by controller validation;
- forbidden operations cannot be invoked through alternate inputs, shortcuts, or stale screens;
- control acquisition, expiry, replacement, logout, and release are visible;
- external enabling-device state is not conflated with an on-screen hold gesture.

Check keyboard order, accessible names, non-color status cues, focus visibility, target sizes, and announcements for blocking/fault state changes. Avoid global shortcuts that can start motion while focus is ambiguous.

## Test Telemetry Presentation

Simulate normal rate, jitter, bursts, dropped samples, reordering, duplicates, partial fields, clock drift/jumps, stale data, disconnect, and resynchronization.

Assert that:

- freshness uses the intended clock and threshold;
- derived joint/pose values come from a coherent snapshot;
- stale values remain labeled as historical rather than current;
- unknown values never render as zero, clear, or safe;
- transport reconnection alone does not enable motion;
- a controller boot/session change invalidates transient state and pending previews;
- a fresh heartbeat cannot mask stale pose, mode, safety, tool, or external-equipment signals.

## Integrate in Layers

Use, in order:

1. pure math and transition tests;
2. UI adapter/component tests with a deterministic clock and fake controller;
3. protocol integration tests against the supported controller API or simulator;
4. fault injection for latency, loss, restart, and conflicting ownership;
5. hardware-in-the-loop tests at constrained speed and in an approved test setup;
6. controls/functional-safety review for claims that depend on certified behavior.

Record robot/controller versions, configuration, tool/payload, frames, limit sets, safety configuration, and test environment. Never treat simulator-only results as proof of physical stopping distance, collision coverage, or safety performance.

## Minimum Acceptance Scenarios

- Joint jog begins only with valid authority and ends on every termination path.
- Cartesian jog visibly binds direction to a frame and rotation to a TCP.
- A frame/TCP revision change invalidates a preview and active gesture.
- A multi-solution IK target requires an explicit, stable branch choice.
- Lost acknowledgement produces uncertainty and reconciliation, not blind retry.
- Disconnect during motion disables new intent and never reports a guessed terminal result.
- Reconnect requires fresh coherent state and explicit re-arming.
- An interlock or protective stop remains visible above routine command progress.
- Effective speed/limit constraints are attributed rather than silently clamped.
- Teach stores provenance and never moves the robot implicitly.
- Competing clients and local takeover produce one visible control owner and terminate displaced intent.
- Reset/guard restoration while an input remains held never restarts motion.
- Arm standstill does not hide continuing tool, external-axis, stored-energy, or process hazards.
