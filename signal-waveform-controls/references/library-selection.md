# Plotting Library Selection

## Contents

- Default policy
- Evaluation scorecard
- Platform candidates
- Benchmark workload
- Ownership boundary

## Apply the Default Policy

Inspect and reuse suitable repository infrastructure first. Prefer a mature chart engine over a custom renderer when it meets measured requirements. Verify current official documentation, maintenance, licensing, deployment, and platform support before recommending a dependency.

Separate responsibilities when no single library fits:

- sample storage and acquisition;
- view-dependent reduction;
- trace rendering;
- cursors, triggers, regions, and annotations;
- measurement and FFT computation;
- export and accessibility.

## Use an Evaluation Scorecard

| Criterion | Evidence to require |
|---|---|
| Streaming API | Batched append/update without full-series replacement |
| Data ownership | Raw buffers can remain outside chart nodes |
| Fidelity | Peak/gap/digital-transition semantics are controllable |
| Time precision | Relative axes and exact label reconstruction are possible |
| Interaction | Custom cursors, trigger handles, regions, hit testing, and cancellation |
| Multi-pane | Shared time range and cursor synchronization without screen-coordinate hacks |
| Throughput | Target channels, visible points, update cadence, and history measured |
| Threading | Acquisition/processing can stay off the UI thread |
| Export | Required image/vector/data output includes overlays and provenance |
| Operations | License, bundle, deployment, support, and versioning are acceptable |
| Testability | Math/state can be tested without an actual render surface |

Reject a candidate that silently owns the only copy of data or exposes only already-decimated values for analysis.

## Evaluate Platform Candidates

For WPF high-density/live requirements, evaluate maintained high-performance engines such as SciChart and comparable commercial options against the actual workload. For moderate historical plots, evaluate lighter general chart libraries only after proving append, cursor, gap, and reduction behavior.

For Web aligned time-series data, evaluate lightweight Canvas engines such as uPlot. Its columnar/aligned-x model is a fit constraint, not merely an API detail. Evaluate WebGL/WebGPU engines for denser traces, spectrograms, or higher refresh requirements. Treat dashboard-oriented libraries as candidates only when oscilloscope-style interaction and faithful reduction can be implemented cleanly.

For PySide6, evaluate pyqtgraph for live scientific plotting and verify its clipping/downsampling mode against spike and gap requirements. Evaluate Qt Graphs/Charts for simpler native views. Use Matplotlib primarily for analysis/publication workflows unless the target interaction profile proves acceptable.

Do not encode a library choice as a domain invariant. Re-check official capabilities and versions at implementation time.

## Benchmark a Representative Workload

Include:

- realistic number and types of channels;
- uniform/irregular timing, gaps, and quality flags;
- sustained plus burst append rates;
- live-follow and frozen navigation;
- narrow impulses, square transitions, noise, and long flat regions;
- cursor, trigger, region, and synchronized-pane interaction;
- expected history, visible span, pixel size, and device scale;
- export if required.

Measure append cost, UI-thread time, reduction latency, frame time, pointer latency, allocations, CPU/GPU, and memory. Inspect visual correctness, not only FPS.

## Keep an Exit Strategy

Wrap the chosen library behind a waveform renderer/interaction adapter. Retain domain-owned `WaveformStore`, `TimeViewport`, tools, and measurement services. Record unsupported requirements and the seam for replacing only rendering, reduction, or annotations.

Build custom infrastructure only after a prototype demonstrates a material failure in available options. Implement the smallest missing layer and keep a deterministic reference path for correctness tests.
