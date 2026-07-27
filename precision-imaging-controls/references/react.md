# React Adapter

Apply React as the application-shell and committed-state adapter around the framework-neutral imaging controller. Keep React rendering pure and keep high-frequency interaction out of the component tree unless it must affect ordinary UI.

## Place State by Responsibility

Keep in React state, context, or the application's established store:

- document and source-image identity;
- committed annotations and ROIs, plus optional extension snapshots when active;
- active tool and durable tool settings;
- selected domain IDs when panels or commands consume them;
- display settings, status, and accessible derived text required by active branches;
- committed undo/redo availability.

Keep in an imperative controller or `useRef`:

- renderer, Stage, scene, and third-party class instances;
- active pointer IDs and capture ownership;
- hover target and gesture-local tool session;
- transient preview geometry;
- pending animation-frame handle and render caches.

Use `useSyncExternalStore` only when React must subscribe to a controller-owned external store. Return cached, immutable snapshots and stable subscribe functions. Prefer ordinary React state for state that naturally belongs to the component tree.

## Build an Idempotent Lifecycle

Create or attach the controller after the host element exists. Keep setup and cleanup symmetrical:

- remove every event listener and observer;
- release pointer capture owned by the controller;
- cancel animation frames, workers, decode jobs, and tool sessions;
- destroy renderer- or GPU-owned resources;
- make cleanup safe when invoked more than once.

Verify development Strict Mode. Do not suppress its extra setup/cleanup cycle to hide leaks or duplicate subscriptions. Keep render free of side effects and avoid reading mutable refs as rendered state.

Prevent stale event behavior. Dispatch semantic samples into the controller or read an explicit current snapshot; do not let a long-lived pointer handler capture obsolete tool, viewport, or optional-extension values.

## Integrate React-Konva Deliberately

Use `react-konva` components to project a committed scene when their reconciliation cost fits the measured workload. Use refs only for imperative capabilities such as Stage access, focus, export, or Transformer attachment.

- Use stable domain IDs as React keys.
- Keep Konva node properties subordinate to the domain snapshot.
- Commit one semantic change on `dragend` or `transformend`.
- Convert node geometry back through the authoritative coordinate adapter.
- Normalize Transformer scale into the domain geometry when appropriate; do not persist `scaleX`/`scaleY` accidentally.
- Restore or rerender the node from the committed domain result.
- Keep non-interactive layers out of hit processing when supported.

Do not mirror every Konva attribute into separate React state. Do not use direct node mutation as a second model.

## Control High-Frequency Updates

Send pointer movement directly to the controller and coalesce preview rendering with `requestAnimationFrame`. Publish to React only at a controlled frame rate when an external label or panel must display live feedback.

Commit once per completed gesture. Do not:

- call application-store setters for every raw pointer event;
- append undo commands during drag updates;
- recreate the renderer, tool controller, or transform service on every render;
- rebuild all annotation props because only hover or one preview changed.

Use memoization only after establishing stable ownership and profiling actual rerender cost.

## Handle Routing and SSR

Treat Canvas, Konva, WebGL, ResizeObserver, and browser input as client-only infrastructure. In an SSR framework, create an explicit client boundary and initialize the viewer after mount. Avoid server/client markup that depends on measured viewport dimensions.

Keep routing, document loading, and viewer teardown coordinated so late tiles, workers, or callbacks cannot update a replaced document.

## Verify the Adapter

Test:

- one controller instance per mounted viewer under development Strict Mode;
- complete teardown and remount;
- fresh tool, viewport, and active-extension state in long-lived event handlers;
- one domain commit and one undo entry per gesture;
- no React-wide rerender storm during pointer movement;
- Transformer scale normalization and coordinate conversion;
- client-only loading and resize behavior in the chosen application framework.
