---
name: precision-imaging-controls
description: Design, implement, refactor, or review precise static imaging editors and optional calibrated-measurement extensions for microscope, machine-vision, inspection, scientific, medical, and large-image applications. Use when selecting imaging libraries or rendering backends, working on coordinate transforms, zoom/pan/rotate/focus interaction, annotations, ROI editing, overlays, crosshairs, rulers, masks, feature points, snapping, hit testing, or high-precision pointer input, or adding calibrated physical measurements, image-to-world or stage mapping, reportable measurements, accuracy or uncertainty claims, or inspection pass/fail in WPF, web frontends, PySide6/Qt, or another UI framework.
---

# Precision Imaging Controls

Build precision imaging interaction as a framework-neutral domain system with thin platform adapters. Preserve numerical correctness, predictable input behavior, and render performance before styling the controls.

## Route the Work

Read only the references needed for the request:

- Always read [core-model.md](references/core-model.md) before designing or changing image/view coordinates, ROI semantics, or persisted geometry.
- Read [metrology.md](references/metrology.md) only when the request requires physical units, calibration, image-to-world or stage mappings, reportable measurements, accuracy or uncertainty claims, or inspection pass/fail decisions. Keep pixel-only annotation and ROI work on the core path.
- Read [interaction-tools.md](references/interaction-tools.md) for tools, selection, handles, snapping, constraints, pointer gestures, editing, or undo/redo.
- Read [rendering-performance.md](references/rendering-performance.md) for overlays, masks, large images, DPI, rendering architecture, or performance.
- Read [library-selection.md](references/library-selection.md) before selecting, replacing, or building rendering, scene-graph, tiling, interaction, or image-processing infrastructure.
- Read exactly one primary platform guide when the stack is known: [wpf.md](references/wpf.md), [web.md](references/web.md), or [pyside6.md](references/pyside6.md). Read multiple only when designing a shared library or comparing implementations.
- For React work, read [react.md](references/react.md) after [web.md](references/web.md). For Vue work, read [vue.md](references/vue.md) after [web.md](references/web.md). Keep geometry and tool semantics in the shared core. When the metrology branch is active, keep its semantics behind that seam rather than duplicating them in framework components.
- For WPF viewer, ROI, annotation-editor, pixel-inspection, or bitmap-export work, read [wpf-case-studies.md](references/wpf-case-studies.md) after [wpf.md](references/wpf.md). Extract the demonstrated technique, then apply this skill's coordinate, interaction, and verification invariants instead of copying an experimental architecture.
- Read [verification.md](references/verification.md) before implementing tests, diagnosing precision defects, or declaring an implementation complete.

## Follow the Design Workflow

### 1. Discover the Existing Contract

Inspect the repository, current rendering stack, data models, tests, and documented conventions before proposing architecture. Determine:

- image dimensions, pixel format, tiling, and expected maximum size;
- whether the work is pixel-only or activates the optional metrology branch;
- required tools and whether their geometry must persist or export;
- mouse, pen, touch, keyboard, and accessibility expectations;
- framework and rendering backend constraints;
- latency, DPI, and zoom-range targets.

State assumptions when the repository cannot answer them. Do not invent storage formats or performance thresholds. When the metrology branch is active, apply its additional discovery rules before making calibration or accuracy claims.

### 2. Select Infrastructure Deliberately

Audit existing dependencies before adding or building infrastructure. Prefer a mature rendering, scene-graph, tiling, interaction, or image-processing library when it satisfies the verified precision, input, extensibility, and performance requirements. Reuse proven layers, transforms, event routing, pointer capture, hit testing, caching, and large-image navigation rather than recreating them without a demonstrated need.

Keep persisted geometry, tool sessions, and undo history independent of the selected library. Treat library nodes as rendering and interaction projections, not as the authoritative domain model. When the metrology branch is active, keep calibration and derived results independent too. Replace or bypass only the layer that fails a measured requirement; do not build a custom scene graph merely for architectural purity.

Record the evaluated candidates, representative workload, decision, tradeoffs, and exit strategy. Verify current official documentation, maintenance, licensing, and framework compatibility before recommending a new dependency.

### 3. Establish the Invariants

Define the image, view, and device coordinate spaces explicitly. Keep persisted core geometry in stable image coordinates using floating-point values. Keep viewport coordinates transient. Centralize forward and inverse viewport transforms and define pixel-center, axis direction, and rotation conventions. Let the optional metrology branch add named physical frames without changing the editor's source of truth.

Separate these concerns:

- image geometry;
- viewport navigation;
- tool interaction state;
- hit testing and snapping;
- rendering and visual styling;
- persistence and undo history.

Keep calibrated measurement as a separate optional module. Expose its interface only when the product actually needs physical or reportable results.

### 4. Design a Deep Control Boundary

Prefer a small public interface backed by substantial internal behavior. A typical boundary exposes:

- viewport state and coordinate conversion;
- immutable or transactionally edited annotation/ROI models;
- tool activation plus `begin`, `update`, `commit`, and `cancel`;
- selection and semantic hit-test results;
- render snapshots or layer invalidation;
- commands/events for committed domain changes.

Keep raw framework events, visual nodes, and device pixels behind an adapter. Do not leak them into persisted models.

### 5. Implement a Vertical Slice

Build the smallest end-to-end slice that proves the architecture:

1. Render one image.
2. Support cursor-anchored zoom and pan.
3. Add one line or rectangular ROI annotation.
4. Select and drag an endpoint handle.
5. Cancel an edit and undo a committed edit.
6. Verify round-trip transforms plus geometry save/load.

Generalize additional tool types only after the slice works. Share tool lifecycle and geometry primitives; do not force every tool into one oversized class.

When the metrology branch is active, extend this proven slice through the calibrated-measurement slice in [metrology.md](references/metrology.md).

### 6. Make Precision Visible

Expose the behavior users need to trust:

- keep handles and labels legible at every zoom;
- distinguish preview, selected, invalid, locked, and committed states;
- show snap targets and active constraints;
- show image-space coordinates without implying a physical unit;
- keep crosshairs and geometry previews responsive during pointer movement;
- cancel safely on Escape, capture loss, deactivation, or invalid geometry.

### 7. Verify Before Handoff

Test numerical invariants separately from UI events. Then test the platform adapter, rendering, and representative end-to-end gestures. Exercise non-100% DPI, extreme zoom, rotation, out-of-bounds input, pointer cancellation, degenerate geometry, and a realistically large image.

If implementing code, run the repository's relevant checks and report what was and was not verified. If only designing, deliver an acceptance matrix that makes the design testable.

## Produce Decision-Ready Output

For a design task, include:

- image/view/device coordinate conventions;
- transform ownership and equations;
- domain model and tool lifecycle;
- layer/rendering plan;
- input arbitration and cancellation rules;
- undo/persistence boundary;
- framework mapping;
- precision, performance, and accessibility acceptance criteria.

When the metrology branch is active, also include the additional decisions required by [metrology.md](references/metrology.md).

For an implementation task, encode those decisions in focused types and tests. Prefer names from the imaging domain such as `ViewportTransform`, `Annotation`, `RegionOfInterest`, `ToolSession`, `HitTarget`, and `SnapCandidate`.

## Guardrails

- Do not persist screen, canvas, DIP, or device-pixel coordinates.
- Do not round during transforms or geometry edits; quantize only at explicit I/O boundaries.
- Do not calculate hit tolerance in image units without accounting for zoom and anisotropy.
- Keep pixel-only work pixel-only; activate the metrology branch before introducing physical units.
- Do not bake annotations into source pixels unless destructive export is explicitly requested.
- Do not send every pointer move through application-wide reactive state or undo history.
- Do not let a framework widget become the only source of truth for domain geometry.
- Do not build a custom scene graph, hit-testing engine, or image tiler before evaluating the existing stack and suitable mature libraries.
- Do not let a third-party node model or serializer dictate the persisted domain schema.
