# Web Adapter

Use the browser framework as the shell around domain-owned signal storage, reduction, tools, and measurements.

## Build a Browser Data Pipeline

Use typed arrays or another contiguous representation for samples. Batch ingestion and avoid object-per-sample allocation. Move decode, reduction, or FFT work to a Worker when profiling shows main-thread contention; include acquisition/source revisions in every message and reject stale results.

Use transferable buffers when ownership transfer fits. Use shared memory only with an explicit synchronization protocol and deployment-compatible isolation headers. Do not introduce it merely to avoid designing bounded batches.

Convert exact timestamps to relative numeric coordinates near the viewport before charting. Keep the exact epoch/index/ticks for labels and export.

## Schedule Rendering

Use `requestAnimationFrame` or the chosen engine's bounded render loop. Let ingestion continue independently and display the newest consistent watermark. Pause or reduce visual updates when hidden while preserving the declared acquisition/storage behavior.

Use Canvas 2D for suitable trace loads, WebGL/WebGPU for measured high-density needs, and DOM/SVG for limited accessible overlays. Size backing surfaces using device-pixel ratio while using CSS pixels for interaction.

Evaluate `OffscreenCanvas` only after profiling and verifying library/browser support, text/export needs, and worker lifecycle complexity.

## Map Input

- Use Pointer Events for mouse, pen, and touch.
- Capture owned drags and handle `lostpointercapture`.
- Define `touch-action` and wheel normalization deliberately.
- Keep cursor/trigger/region hit radii in CSS pixels.
- Scope keyboard shortcuts to the focused viewer and preserve text-entry behavior.

Prevent default browser scrolling only for gestures the viewer owns. Coalesce pointer previews and commit semantic settings once per completed gesture.

## Select the Engine

Evaluate aligned Canvas time-series engines such as uPlot when its data-shape and interaction constraints fit. Evaluate WebGL/WebGPU engines for denser traces, spectrograms, or higher refresh. Evaluate dashboard chart libraries only against the full waveform benchmark and required custom tools.

Wrap the engine. Do not make its arrays, series, annotations, or timestamps the persisted domain model. Verify gaps, digital steps, reduction, multi-pane synchronization, export, accessibility, and device-pixel-ratio behavior.

## Handle Browser Lifecycle

Treat the viewer as client-only in SSR applications. Initialize after mount and tear down observers, pointer listeners, animation frames, workers, GPU resources, and subscriptions on unmount/navigation.

Handle ResizeObserver, page visibility, fullscreen, device-pixel-ratio changes, GPU context/device loss, and late worker results. Never append an obsolete document/acquisition result to the current view.

## Verify Browser Risks

- Verify tab throttling and return-to-visible reconciliation.
- Verify touch/trackpad/pointer cancellation across target browsers.
- Verify page zoom and non-integer device-pixel ratios.
- Verify memory remains bounded after long streaming sessions.
- Verify worker termination and transfer ownership.
- Provide accessible live/frozen status, channel names, measurements, and keyboard alternatives outside the canvas.
