# Vue Adapter

Apply Vue as the application-shell and committed-state adapter around the framework-neutral imaging controller. Keep high-frequency renderer state outside deep reactivity.

## Place State by Responsibility

Keep in component state or the application's established store such as Pinia:

- document and source-image identity;
- committed annotations and ROIs, plus optional extension snapshots when active;
- active tool and durable tool settings;
- selected domain IDs used by panels and commands;
- display settings, status, and accessible derived text required by active branches;
- committed undo/redo availability.

Keep in an imperative controller:

- renderer, Stage, scene, and third-party class instances;
- active pointer IDs and capture ownership;
- hover target and gesture-local tool session;
- transient preview geometry;
- pending animation-frame handle and render caches.

Hold external controller instances in `shallowRef`; use `markRaw` only where a third-party instance must be embedded in another state object. Do not allow deep reactive proxies to wrap scene-graph, renderer, matrix, image-buffer, or GPU-resource objects.

## Build a Scoped Lifecycle

Create or attach the controller in `onMounted` after the host exists. In `onBeforeUnmount`:

- remove every event listener and observer;
- release owned pointer capture;
- stop watchers and external subscriptions;
- cancel animation frames, workers, decode jobs, and tool sessions;
- destroy renderer- or GPU-owned resources.

Make teardown safe if navigation, conditional rendering, or an error removes the viewer during an active gesture.

Keep watcher scope narrow. Watch document IDs, immutable root snapshots, or explicit revisions instead of deep-watching every annotation point. Replace a `shallowRef` root to publish a new committed snapshot.

## Integrate Vue-Konva Deliberately

Use `vue-konva` components and config objects to project a committed scene when their update cost fits the measured workload. Access `getNode()` through component refs only for supported imperative operations such as Stage access or Transformer attachment.

- Use stable domain IDs as Vue keys.
- Keep Konva config subordinate to the domain snapshot.
- Commit one semantic change on `dragend` or `transformend`.
- Convert node geometry through the authoritative coordinate adapter.
- Normalize Transformer scale into domain geometry when appropriate.
- Restore or rerender from the committed domain result.
- Avoid recreating large config trees for hover-only or preview-only changes.

Do not persist Konva nodes, Vue proxies, or config objects as domain geometry. Do not emit third-party nodes as application events.

## Control High-Frequency Updates

Send pointer movement directly to the controller and coalesce preview drawing with `requestAnimationFrame`. Emit a semantic `commit` event or invoke one store action when the gesture completes.

Publish live values to Vue at a controlled frame rate only when ordinary UI needs them. Avoid:

- mutating Pinia for every raw pointer event;
- deep-watching large annotation arrays;
- serializing reactive geometry during a drag;
- creating undo entries before commit;
- synchronizing the same transient state in both the controller and Vue.

Use shallow immutable snapshots or explicit revision counters for large collections when component updates are required.

## Handle Routing and SSR

Treat Canvas, Konva, WebGL, ResizeObserver, and browser input as client-only infrastructure. In Nuxt or another SSR environment, create a client boundary and initialize after mount. Do not derive server markup from unavailable viewport measurements.

Coordinate route changes and document replacement with controller teardown. Reject late tile, worker, or feature-detection results that belong to an obsolete document revision.

## Verify the Adapter

Test:

- mount, unmount, remount, and conditional viewer removal;
- third-party instances remain raw rather than deeply proxied;
- watcher/subscription cleanup;
- one domain commit and one undo entry per gesture;
- no Pinia or component-wide update storm during pointer movement;
- Transformer scale normalization and coordinate conversion;
- client-only loading and resize behavior in the chosen application framework.
