# Frames, Kinematics, and Poses

Use this reference to define the mathematical and UI contract for robot motion.

## Contents

- Name and compose frames
- Define pose and joint representation
- Distinguish motion modes
- Bound FK and IK
- Represent constraints
- Enforce invariants

## Name Every Space

Use an unambiguous transform notation. For example, let `T_A_B` map coordinates expressed in frame `B` into frame `A`:

`p_A = T_A_B * p_B`

Document multiplication order and test it. Distinguish:

- `world`: cell or installation frame;
- `base`: robot kinematic root;
- `tool`: flange-mounted tool frame;
- `TCP`: active tool center point used for commanded pose;
- `workpiece`: task/user/object frame;
- joint configuration: one value per joint, not a Cartesian frame.

Treat names as labels, not identity. Represent a frame/tool/workpiece with a stable ID plus revision. Preserve calibration/model provenance where available. A command must carry or resolve the exact revision it was previewed against; reject or re-preview after a relevant revision changes.

## Compose Explicitly

Centralize transform composition and inversion. Do not reproduce transform math in widgets. Define which component owns:

- static cell and robot-base transforms;
- dynamic FK from joints to flange;
- flange-to-tool and tool-to-TCP calibration;
- workpiece localization;
- camera/image calibration when vision is present.

Keep the robot motion model separate from image/view coordinates. Connect them through named, calibrated transforms with validity metadata.

## Define Pose Representation

Keep canonical orientation as a normalized quaternion or rotation matrix. Euler/RPY values are a display and entry representation only. Always state:

- position and angle units;
- handedness and positive-axis directions;
- Euler axis order;
- intrinsic or extrinsic rotations;
- quaternion component order;
- normalization and near-zero handling.

Treat `q` and `-q` as the same orientation. Avoid discontinuous display jumps by unwrapping Euler values only in the presentation layer. Do not persist an unwrapped display angle as a new physical orientation.

For joint state, preserve joint type, unit, permitted wrap/multi-turn semantics, and controller-reported actual position. Apply a documented model-specific rule before normalizing a rotary joint to a range such as `[-180 deg, 180 deg)`.

## Distinguish Motion Modes

Joint mode commands a named joint direction or joint target. Label axes with joint names and units.

Cartesian mode commands a TCP translation/rotation or Cartesian target. Make both of these explicit:

- reference frame in which direction, twist, increment, or target is expressed;
- TCP/tool whose pose and rotation center are controlled.

Changing reference frame alters the meaning of Cartesian direction. Changing TCP can alter both displayed pose and swept path. End the current jog session and require a new preview/command after either change.

Do not conflate motion representation with controller operating mode:

- Joint versus Cartesian describes motion coordinates.
- Continuous versus incremental describes interaction.
- Manual/Teach/Auto/Remote describes controller operation and authorization.

## Bound FK and IK

Let an approved kinematics component own FK and IK. Include robot model revision, tool/TCP, external-axis state, and relevant calibration in every result.

For FK:

- report the source joint sequence/time;
- derive related Cartesian displays from the same atomic joint snapshot;
- mark the pose invalid if required joints are missing, stale, or unhomed.

For IK, return structured candidates rather than one unexplained pose:

- joint solution;
- branch/configuration identity;
- distance from current joints;
- reachability and residual error;
- singularity or conditioning metric;
- joint and coupled-limit margins;
- collision-check status and provenance;
- warnings and rejection reasons.

Keep the current or explicitly selected branch stable across nearby previews. Require a new confirmation when the chosen branch changes materially. Do not use the nearest solution as the only safety or process criterion.

## Represent Constraints

Keep constraint sources distinct:

- safety-rated limits enforced by a safety system;
- controller joint, velocity, acceleration, torque, and workspace limits;
- software-configured soft limits;
- task/process envelopes;
- advisory UI thresholds.

Show which constraint limited or rejected a request. Model directional inhibition so a blocked direction can still permit a validated retreat direction. Do not silently clamp position, increment, or speed. Near singularities, expose Cartesian-to-joint speed amplification and let the controller enforce valid motion.

Treat a valid IK endpoint as insufficient evidence for a valid path. Preserve the collision model, payload, tool, zones, and trajectory-check provenance used for a preview; invalidate the preview when any dependency changes.

## Required Invariants

- Transform round trips are stable within a declared tolerance.
- Pose display and command serialization use the same documented convention.
- A Cartesian command always resolves a reference frame and TCP.
- A derived pose carries the joint snapshot and model revision that produced it.
- A taught pose preserves whether it is joint-space or Cartesian plus all context required to reproduce its meaning.
- A frame/tool/workpiece revision change invalidates dependent previews and pending edits.
- Unknown, unhomed, or stale kinematic input never appears as a valid zero pose.
