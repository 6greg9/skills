# Web Frontend Mapping

Use browser APIs as an adapter around the framework-neutral imaging model.

## Select the Surface by Workload

Audit the repository first, then verify current official documentation, maintenance, licensing, bundle impact, and browser support before adding a dependency.

| Workload | Prefer evaluating | Main caution |
|---|---|---|
| Annotation, ROI, dragging, handles, layered Canvas editing | Konva.js | Keep Konva nodes and serialization subordinate to the domain model; profile dense scenes |
| Editor-like object controls, serialization, and SVG interchange | Fabric.js | Validate precision, custom interaction rules, and schema independence |
| GPU rendering, dense graphics, masks, or high frame rates | PixiJS | Expect to implement more interaction and editor semantics |
| Very large tiled or pyramid images | OpenSeadragon | Use its image-specific coordinate APIs and add a controlled annotation layer |
| Modest interactive vector count and strong DOM accessibility | SVG | Avoid a DOM node per dense feature |
| Specialized rendering or minimal dependencies | Canvas 2D, WebGL, or WebGPU directly | Custom event, scene, hit-test, and lifecycle code needs explicit justification |

Combine a tiled-image viewer with Konva, SVG, Canvas, or another overlay only when one component owns the viewport transform, animation, input arbitration, and redraw clock. Test alignment through zoom, rotation, resize, fullscreen, and device-pixel-ratio changes.

Do not choose a DOM node per feature for dense contours or annotations. Keep semantic models in application state and render scalable snapshots.

## Handle Coordinates and DPI

Treat CSS pixels as view coordinates. Size the backing store to `cssSize × devicePixelRatio`, then normalize drawing so domain code still receives CSS-pixel positions.

Use `getBoundingClientRect()` to normalize pointer coordinates. Account for CSS transforms explicitly or prohibit them at the viewport boundary. Centralize transforms with `DOMMatrix`, typed arrays, or one tested matrix abstraction.

Use `ResizeObserver` to update the viewport. Recreate size-dependent buffers when CSS size or device-pixel ratio changes.

## Map Input

- Prefer Pointer Events for mouse, pen, and touch.
- Call `setPointerCapture(pointerId)` for owned drags and handle `lostpointercapture`.
- Set an intentional `touch-action` policy on the interactive surface.
- Normalize wheel delta modes before zooming.
- Prevent browser scrolling only for gestures the viewport actually owns.
- Use `requestAnimationFrame` to coalesce previews; do not commit global reactive state for every `pointermove`.

Track active pointers by ID. Promote to a multi-pointer navigation gesture only through an explicit transition, and define what happens to an in-progress drawing tool.

Keep keyboard shortcuts scoped to the focused viewport and ignore them while users edit text unless explicitly supported.

## Keep Framework Boundaries Without Frame Churn

Use the framework for document state, tool settings, panels, accessibility, and committed changes. Use an imperative renderer/controller for high-frequency pointer previews and image frames. Bridge them with stable snapshots and semantic events.

For React, load the React adapter guidance routed from `SKILL.md`. For Vue, load the Vue adapter guidance. Apply the same boundary to another reactive framework unless its lifecycle requires a different adapter.

Avoid:

- rebuilding the whole scene graph for every pointer sample;
- keeping a mutable canvas context as the domain model;
- deriving persisted geometry from DOM bounding boxes;
- mixing CSS zoom with the imaging transform.

Use workers and `OffscreenCanvas` only when profiling shows main-thread contention and the transfer/coordination cost is justified.

## Verify Browser-Specific Risks

- Verify page zoom and non-integer device-pixel ratios.
- Verify touch scrolling, pinch behavior, and pointer cancellation.
- Verify trackpad and mouse-wheel normalization across target browsers.
- Verify context loss for GPU renderers and recover cached resources.
- Verify resizing and fullscreen transitions preserve the image point or fit policy promised to users.
- Provide accessible names, live values required by active tools, and keyboard-operable alternatives for essential canvas-only actions.
