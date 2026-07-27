# Library Selection and Reuse

## Contents

- Default policy
- Capability boundaries
- Evaluation scorecard
- Composition rules
- Custom implementation threshold
- Decision record

## Apply the Default Policy

Inspect the repository and reuse its suitable infrastructure first. Prefer a maintained library over custom infrastructure when it meets the verified requirements. Do not add a second scene graph, transform authority, gesture system, or image cache merely because it is more familiar.

Evaluate libraries by responsibility rather than searching for one product that does everything:

- tiled image loading and level-of-detail navigation;
- scene graph and overlay rendering;
- pointer events, capture, dragging, and gesture recognition;
- editable handles and object controls;
- image decoding, processing, and GPU effects;
- spatial indexing and geometry operations;
- serialization or interoperability.

Keep the domain model independent even when a library covers several responsibilities.

## Reuse Capabilities, Not Authority

Reuse mature implementations of:

- layers, clipping, transforms, and invalidation;
- event routing, pointer capture, drag thresholds, and multi-pointer tracking;
- scene traversal and coarse hit testing;
- tile scheduling, cache eviction, and GPU resource management;
- path tessellation, text layout, filters, and export adapters.

Retain application authority over:

- coordinate-space and pixel-center conventions;
- persisted annotations and ROIs;
- semantic hit priority, snapping, and constraints;
- tool lifecycle, cancellation, and undo transactions;
- optional domain modules and their provenance or claims when those branches are active.

Treat library objects as adapters, projections, or caches. Rebuild them from the domain model when necessary.

## Use an Evaluation Scorecard

Test candidates against a representative vertical slice rather than feature-list claims.

| Criterion | Evidence to require |
|---|---|
| Coordinate control | Forward/inverse transforms remain explicit and testable |
| Precision | No forced integer geometry or hidden destructive transforms |
| Hit testing | Custom view-space tolerance, priority, and handles are possible |
| Input lifecycle | Capture, cancellation, pen/touch, and multi-pointer rules are controllable |
| Visual semantics | Screen-constant strokes, handles, labels, and custom overlays are possible |
| Workload | Target image size, object count, update rate, and zoom range are measured |
| Extensibility | Custom shapes, render passes, tools, and export paths have supported seams |
| Domain separation | Geometry and history can remain independent of library nodes/serialization |
| Operations | Maintenance, license, bundle/deployment impact, and platform support are acceptable |
| Testability | Geometry and tool state can be tested without a real render surface |

Profile with realistic bit depth, tiles, masks, annotation counts, and pointer-update rates. Do not select by popularity or a trivial demo alone.

## Compose Libraries Carefully

Combine specialized libraries when their ownership boundaries remain clear—for example, a tiled-image viewer beneath an annotation scene. Assign exactly one authority for:

- viewport transform;
- animation timing;
- pointer/gesture ownership;
- device-pixel scaling;
- redraw scheduling;
- visible bounds.

Synchronize other layers from that authority and verify alignment during zoom, rotation, resize, fullscreen, and DPI changes. Avoid stacking libraries whose transforms or event systems cannot be controlled deterministically.

## Justify Custom Infrastructure

Build a custom component only when evidence shows that available options fail a material requirement, such as:

- unsupported image size, bit depth, latency, or GPU pipeline;
- insufficient coordinate precision or transform control;
- inaccessible hit testing, gesture cancellation, or screen-constant adorners;
- unacceptable memory, bundle, deployment, licensing, or maintenance constraints;
- required device or native integration unavailable through existing libraries.

Implement only the missing layer when possible. Preserve replaceable interfaces and comparison benchmarks.

## Record the Decision

Capture:

- existing infrastructure inspected;
- candidates and versions evaluated against current official documentation;
- representative dataset and interaction;
- accepted and rejected requirements;
- chosen ownership boundaries;
- benchmark or prototype evidence;
- fallback and replacement strategy.

Revisit the decision when workload, rendering backend, supported devices, or product requirements change.
