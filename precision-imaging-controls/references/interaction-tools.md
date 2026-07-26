# Interaction and Tool Architecture

## Contents

- Input normalization
- Tool lifecycle
- Selection and hit testing
- Snapping and constraints
- Gesture arbitration
- History and persistence
- Tool families

## Normalize Input

Translate framework events into semantic samples before tool logic:

```text
PointerSample
  pointer_id
  device_kind: mouse | pen | touch
  view_position
  image_position
  buttons
  modifiers
  pressure/tilt when relevant
  timestamp
```

Keep double-click, drag thresholds, wheel normalization, pointer capture, and platform key mapping in the adapter. Pass semantic commands such as `Cancel`, `DeleteSelection`, `Nudge`, `Constrain`, and `FinishPath` into tools.

Coalesce high-frequency moves for rendering when helpful, but never reorder `down`, `up`, `cancel`, or capture-loss transitions.

## Use an Explicit Tool Lifecycle

Give each active tool a small state machine. Use states that match the behavior rather than a single global boolean collection.

```text
inactive -> ready -> creating -> preview
                    |           |
                    +-> commit <-+
                    +-> cancel

ready -> editing-handle -> commit | cancel
ready -> moving-selection -> commit | cancel
```

Expose a common lifecycle:

- `activate(context)` and `deactivate(reason)`;
- `begin(sample, hit)`;
- `update(sample)`;
- `commit(sample?)`;
- `cancel(reason)`;
- `build_preview()` or a read-only preview snapshot.

Make `cancel` idempotent. Restore the pre-gesture model on cancellation. Treat Escape, capture loss, window deactivation, tool switching, model deletion, and invalid transforms as explicit cancellation paths.

Keep gesture-local mutable state in a `ToolSession`. Publish a domain change only on commit unless live collaboration explicitly requires intermediate operations.

## Separate Selection from Hit Testing

Return semantic hit targets rather than UI elements:

```text
HitTarget
  annotation_id
  part: body | vertex | edge | rotation-handle | label
  index
  distance_in_view
  priority
```

Hit test in this order unless the product specifies otherwise:

1. active selection handles;
2. editable vertices or endpoints;
3. labels or special controls;
4. annotation strokes/fills;
5. image/background.

Use view-space distance for usability. Use a spatial index in image space only to reduce candidates, then rank precise hits in view space. Resolve overlaps deterministically and support cycling when dense annotations make one choice ambiguous.

Keep visual handle size and pointer hit radius separate. Increase hit radius for touch without making the handle visually oversized.

## Compose Snapping and Constraints

Model snapping as candidate generation plus ranking:

```text
SnapProvider -> zero or more SnapCandidate
SnapCandidate
  proposed image point
  target identity and kind
  view-space distance
  confidence
  visual guide
```

Combine providers for pixels, grid intersections, existing vertices, edges, detected features, axes, and guides. Rank within a view-space threshold. Add hysteresis so the active snap does not flicker between nearby targets.

Apply constraints deliberately:

- angle increments;
- horizontal/vertical;
- fixed length or aspect ratio;
- containment within an image or parent ROI;
- symmetric resize;
- minimum geometry size.

Document precedence. A robust default is:

1. create an unconstrained proposal;
2. apply the active geometric constraint;
3. find snap candidates consistent with it;
4. retain the prior snap within a release threshold;
5. show the chosen guide.

Never silently modify committed geometry without visible feedback.

## Arbitrate Gestures

Define priority instead of letting event-handler order decide:

- a handle drag owns the pointer once begun;
- Space or a configured navigation chord may temporarily pan;
- wheel/trackpad zoom targets the cursor unless the product specifies otherwise;
- a second touch pointer may promote an eligible gesture to pan/zoom/rotate;
- drawing tools either reject multi-touch or suspend predictably;
- mouse right-click opens context actions only if it did not perform another gesture.

Capture the initiating pointer during drags. Release capture on commit and every cancellation path. Keep keyboard focus policy explicit so shortcuts work without stealing text-entry input.

## Make History Transactional

Open one edit transaction at gesture start:

```text
before model -> live preview -> after model
```

Commit one undoable command on successful completion. Discard the transaction on cancel. Coalesce keyboard nudges or repeated wheel adjustments only within a documented time and target boundary.

Persist domain models, not tool sessions, selection handles, hover state, or render caches. Version serialized geometry and record its image-coordinate convention. Let optional modules persist their own provenance outside the core geometry schema.

## Reuse Tool Families

Share lifecycle and primitives while preserving tool-specific rules:

- point/feature marker;
- line, polyline, and profile;
- angle and multi-segment angle;
- rectangle, rotated rectangle, ellipse, and polygon ROI;
- freehand path or brush mask;
- crosshair, ruler, axes, and scale bar;
- text/callout annotation;
- focus region or autofocus target.

Define geometry adapters for control points, bounds, hit parts, constraints, and rendering snapshots. Avoid one base class that accumulates flags for every possible tool.
