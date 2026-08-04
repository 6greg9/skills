# React Adapter

Use React for the application shell and committed waveform configuration. Keep the acquisition/render hot path in an imperative controller.

## Place State Deliberately

Keep in React state or the established store:

- acquisition/document identity and semantic status;
- channel visibility, committed scale/offset, and display settings;
- committed trigger, cursors, and analysis regions;
- measurement results, errors, and accessible text;
- live/frozen/review mode and commands.

Keep in `useRef` or the controller:

- chart/renderer/worker instances;
- sample buffers, watermarks, and render envelopes;
- active pointer, hover, and gesture preview;
- animation-frame handle and caches.

Do not call React setters per sample, chunk, or raw pointer move. If React must observe an external store, use a stable subscription and immutable/cached snapshots rather than exposing mutable buffers.

## Build an Idempotent Lifecycle

Create the controller after the host exists. Make setup/cleanup symmetrical and safe under development Strict Mode:

- unsubscribe from acquisition/store events;
- remove observers and pointer handlers;
- cancel frames, workers, reduction, and FFT jobs;
- release owned buffers and GPU/chart resources;
- cancel active tool sessions.

Keep render pure. Prevent long-lived handlers from capturing stale acquisition, calibration, trigger, or viewport state; dispatch into the controller or read an explicit current snapshot.

## Wrap React Chart Components

Use declarative chart components for committed structure only when reconciliation cost fits. Keep high-rate data append and preview rendering behind a stable adapter/ref when the library supports it.

Use stable domain IDs as keys. Commit trigger/cursor/region edits once at gesture end. Never treat component props, chart nodes, or a library's internal store as the authoritative sample history.

Memoize only after stabilizing ownership and measuring rerender cost. A memoized component does not fix full-array replacement or an unbounded external queue.

## Handle SSR and Routing

Create a client boundary for Canvas/WebGL, browser observers, and Workers. Avoid server markup that depends on measured plot dimensions. On route or acquisition replacement, invalidate late callbacks by document/acquisition revision before tearing down the old controller.

## Verify React Risks

- Verify one controller/subscription set per mounted viewer under Strict Mode.
- Verify no application-wide rerender storm during streaming or pointer movement.
- Verify current settings in long-lived handlers.
- Verify one semantic commit and undo record per gesture.
- Verify unmount/remount releases workers, chart contexts, and buffers.
