# Vue Adapter

Use Vue for the application shell and committed waveform configuration. Keep sample buffers, renderer instances, and high-frequency interaction outside deep reactivity.

## Place State Deliberately

Keep in component state or the established store such as Pinia:

- acquisition/document identity and semantic status;
- channel visibility, committed scale/offset, and display settings;
- committed trigger, cursors, and analysis regions;
- measurement results, errors, and accessible text;
- live/frozen/review mode and commands.

Keep in an imperative controller:

- chart/renderer/worker instances;
- typed sample buffers, watermarks, and render envelopes;
- active pointer, hover, and gesture preview;
- animation-frame handle and caches.

Hold external controllers and third-party chart instances in `shallowRef`; use `markRaw` only where an instance must live inside another state object. Do not deep-proxy typed arrays, scene graphs, workers, matrices, or GPU resources.

## Build a Scoped Lifecycle

Create the controller in `onMounted` after the host exists. In `onBeforeUnmount`, remove listeners/observers, stop watchers/subscriptions, cancel frames/jobs/tool sessions, terminate workers, and destroy chart/GPU resources.

Watch acquisition IDs, immutable root snapshots, or explicit revisions. Do not deep-watch every sample or annotation point. Replace a shallow root or publish a bounded semantic snapshot when ordinary UI must update.

## Wrap Vue Chart Components

Use declarative chart/config components for committed structure only when their update cost fits. Use refs for supported imperative append, resize, cursor, or export operations.

Emit semantic trigger/cursor/region commits, not third-party nodes or reactive proxies. Never mirror high-rate buffers into Pinia or component props. Keep the chart adapter replaceable and domain-owned history authoritative.

## Handle SSR and Routing

Create a client boundary in Nuxt or another SSR environment. Initialize Canvas/WebGL, observers, and Workers after mount. On route or acquisition changes, invalidate late worker/device callbacks by revision and tear down the old controller.

## Verify Vue Risks

- Verify third-party instances and large buffers are not deeply proxied.
- Verify no deep-watch or Pinia update storm during streaming.
- Verify watcher/subscription cleanup after conditional removal and remount.
- Verify one semantic commit and undo record per gesture.
- Verify workers, contexts, and buffers are released on teardown.
