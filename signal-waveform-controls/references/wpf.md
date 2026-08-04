# WPF Adapter

Use WPF as the shell and adapter around domain-owned acquisition, storage, reduction, interaction, and measurement services.

## Divide Responsibilities

Keep in view models/application services:

- acquisition identity/configuration and connection status;
- committed channel visibility, scale/offset, trigger, cursors, and regions;
- measurement definitions/results and export commands;
- live/frozen/review mode and undoable settings.

Keep in the viewer/controller:

- chart surface/series instances;
- pointer capture, hover, and gesture sessions;
- visible render buffers and frame caches;
- coalesced invalidation and device resources.

Do not expose one `ObservableCollection` item per sample. Append arrays/ranges or publish buffer revisions in bounded batches.

## Keep Ingestion off the Dispatcher

Receive, validate, calibrate, store, and reduce chunks away from the UI thread. Marshal only a lightweight consistent snapshot or batched append to the Dispatcher. Coalesce updates at the target display cadence; do not queue one Dispatcher operation per device callback.

Define ownership if native, pooled, or pinned buffers cross threads. Never mutate a buffer while the chart may read it.

## Select and Wrap the Chart Engine

Evaluate the current repository dependency first. For demanding live/dense plots, benchmark high-performance WPF engines such as SciChart and comparable options. Verify:

- batched append and bounded FIFO behavior;
- min/max or custom reduction;
- gap/NaN and digital-step semantics;
- synchronized panes and cursors;
- custom annotations/trigger handles;
- export and per-monitor DPI behavior;
- licensing and deployment.

Keep chart `DataSeries`, modifiers, and annotations behind an adapter. Store exact timestamps and samples in domain services. Convert timestamps to relative doubles or the engine's proven high-precision axis representation.

## Integrate MVVM Without Frame Churn

Bind committed configuration and semantic status. Do not two-way bind high-rate sample buffers, hover coordinates, or every preview point through the entire view-model graph.

Publish a throttled live readout when panels require it. Commit cursor/trigger/region changes once per gesture. Keep device range/coupling distinct from visual y-axis scale.

Use a controlled rendering/invalidation loop appropriate to the selected engine. Clean up render callbacks, event handlers, workers, and chart resources when the view unloads or the document changes.

## Verify WPF Risks

- Verify Dispatcher backlog under burst acquisition.
- Verify monitor/DPI changes, layout resizing, and logical/device coordinates.
- Verify routed mouse/stylus/touch events and lost capture.
- Verify unload/reload does not duplicate subscriptions.
- Verify the selected engine's resampling preserves single-sample spikes and gaps.
- Verify export contains the intended cursors, trigger, units, status, and source context.
