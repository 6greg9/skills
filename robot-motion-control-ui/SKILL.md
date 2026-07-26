---
name: robot-motion-control-ui
description: Robot motion control UI design, implementation, refactoring, review, and testing for teach pendants, setup panels, and supervisory controls. Use when a task involves (1) Joint/Cartesian motion, frames, poses, or FK/IK; (2) jog, hold-to-run/deadman, teach, speed, or limits; (3) command acknowledgement, execution, completion, cancellation, or fault states; or (4) telemetry freshness, connection loss, operating modes, authority, permissions, interlocks, collision, or safety-stop presentation.
---

# Robot Motion Control UI

Build a **control contract**, not a collection of enabled buttons. Keep motion intent, coordinate context, command ownership, controller execution, observation freshness, and safety eligibility as separate, inspectable facts.

## Route the Work

Load each applicable branch before making design or code decisions:

- Read [frames-kinematics-and-poses.md](references/frames-kinematics-and-poses.md) for Joint/Cartesian behavior, frames, pose entry/display, FK/IK, singularities, or motion limits.
- Read [jog-teach-and-command-lifecycle.md](references/jog-teach-and-command-lifecycle.md) for jog controls, speed/step behavior, external enabling devices, teach actions, command submission, progress, stop/cancel, or reconnect recovery.
- Read [safety-telemetry-and-access.md](references/safety-telemetry-and-access.md) for motion enablement, stop/reset controls, telemetry, connections, operating modes, authority, permissions, interlocks, limits, collision, or safety-state presentation.
- Read [verification.md](references/verification.md) before implementing tests, diagnosing a robot-control defect, or completing an implementation/review.
- For a camera or precision image viewport, use `precision-imaging-controls` for image/view transforms and ROI interaction. Keep robot and image coordinates separate behind named calibrated transforms.

## Build the Control Contract

### 1. Establish Authoritative Facts

Inspect the repository, robot/controller API, state schemas, tests, and documented safety architecture. Record:

- robot/cell identity, topology, external axes, tools/process equipment, kinematic model, homing, and units;
- ownership of transforms, FK, IK, trajectory generation, collision checking, and each limit;
- supported motion forms and the controller primitive used for each;
- frame/tool/TCP/workpiece identity, revision, and calibration provenance;
- controller modes, control ownership/lease, roles, interlocks, and external enabling devices;
- command identifiers, idempotency, acknowledgement, execution, terminal states, and reconciliation;
- telemetry provenance, update rates, freshness budgets, session/boot identity, and watchdog behavior;
- the authority and physical meaning of every hold, stop, cancel, reset, and restart action.

Resolve facts from implementation or authoritative documentation. Mark unresolved items as assumptions; verify current authoritative standards when compliance or safety-rated behavior is in scope.

**Complete when:** every motion or safety-relevant value/action has an authoritative source, freshness/validity rule, and unknown-state behavior, or is explicitly listed as unresolved.

### 2. Model Orthogonal State

Define these truth domains independently:

- **Intent:** operator request.
- **Eligibility:** current permission to request motion plus every blocking reason.
- **Transport:** delivery/acknowledgement certainty.
- **Execution:** controller-observed command lifecycle.
- **Observation:** measured state with provenance and freshness.
- **Safety:** controller/safety-system facts and their scope.

Define one immutable `MotionContext` snapshot per command containing:

- Joint/Cartesian and continuous/incremental selection;
- selected axis/direction or target;
- reference frame, tool/TCP, and workpiece IDs/revisions;
- pose/units convention;
- requested speed/step plus applied controller constraints;
- operating mode, authority, permission, model/configuration, and limit context.

Use focused types such as `FrameRef`, `Pose`, `JointState`, `KinematicSolution`, `MotionEligibility`, `JogSession`, `CommandRecord`, `TelemetrySnapshot`, `ControlAuthority`, `InterlockReason`, `SafetyState`, and an atomic `RobotControlSnapshot`. Keep framework events and controller protocol details behind adapters.

**Complete when:** an acknowledged command, observed motion, stale sample, client timeout, controller fault, and safety stop cannot collapse into the same state or boolean; every command is interpretable without mutable UI selection.

### 3. Prove a Vertical Slice

Implement one constrained Joint jog path before broadening the feature set:

1. Display an atomic joint sample and derived pose with visible freshness.
2. Select Joint mode, axis, direction, and low requested speed.
3. Acquire authority and expose every motion blocker.
4. Begin one hold-to-run `JogSession`.
5. Correlate request, acknowledgement, execution, stop request, and controller terminal evidence.
6. Terminate local intent on every release, cancellation, loss-of-context, stale/disconnected, authority, interlock, and fault path specified by the loaded references.
7. Reconnect through reconciliation and a fresh operator press; preserve ambiguous outcomes rather than replaying them.

Keep controller or approved motion services authoritative for execution and safety enforcement. Treat UI kinematics and collision views as advisory unless the certified architecture establishes otherwise.

**Complete when:** deterministic tests can drive every start/stop/uncertain transition, and loss of any UI release event is bounded by the controller-side jog/watchdog contract.

### 4. Make Consequences Persistent

Keep these visible whenever motion can be requested:

- connection and telemetry age/quality;
- operating mode, control owner/lease, and operator permission;
- Joint/Cartesian and continuous/incremental selection;
- reference frame, tool/TCP, and workpiece;
- requested versus controller-effective speed/step/limits;
- external enabling device, interlocks, limit direction, collision, and stop state;
- active command with acknowledgement, execution, stop/cancel, and terminal reason.

Use a deterministic precedence policy for simultaneous states. Pair color with text/icon/shape and accessible announcements. Derive disabled controls from structured reason codes and show the relevant blockers.

**Complete when:** the operator can answer "what will move, relative to which frame/TCP, how fast, who controls it, is the data live, what blocks it, what is executing, and what stop state is physically known?" without opening a secondary screen.

### 5. Verify and Hand Off

Apply every applicable invariant and scenario in [verification.md](references/verification.md). Test pure math/transitions, UI input adapters, protocol integration, connection/fault injection, and the available simulator or hardware path in that order.

For design/review work, deliver a testable contract containing frame/pose conventions, state machines, eligibility reasons, jog/watchdog behavior, command/reconnect semantics, stop taxonomy, status layout, and an acceptance matrix. For implementation work, encode the same contract in domain types, transition tests, protocol adapters, and UI behavior.

Report verified behavior separately from assumptions requiring controller, controls-engineering, or functional-safety confirmation. UI tests establish application behavior, not a safety rating.

**Complete when:** every applicable reference rule is accounted for in the design/code/tests, all available relevant checks pass, and every unverified safety-dependent assumption is named with its required owner/evidence.
