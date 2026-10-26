---
name: signal-waveform-controls
description: Design, implement, refactor, review, or test precise waveform and signal-analysis UI controls for oscilloscopes, DAQ systems, sensor monitoring, vibration, audio, power, scientific instruments, and industrial telemetry. Use for live or historical traces, timebases, multi-channel panes, triggers, cursors, regions, amplitude/time/frequency measurements, FFT or spectrum views, ring buffers, gaps and quality flags, high-rate streaming, peak-preserving decimation, synchronized zoom/pan, or WPF, web, React, Vue, and PySide6 plotting-library selection and integration.
---

# Signal Waveform Controls

Build waveform interaction around acquisition truth, explicit time semantics, faithful visual reduction, and reproducible measurements. Treat the chart as a projection of signal data, not as the data model.

## Route the Work

Read only the references required by the request:

- Always read [signal-model.md](references/signal-model.md) before designing timestamps, channels, samples, gaps, units, derived signals, persistence, or export.
- Read [acquisition-trigger-streaming.md](references/acquisition-trigger-streaming.md) for live acquisition, buffering, trigger behavior, backpressure, reconnects, freeze/review, or dropped samples.
- Read [rendering-decimation.md](references/rendering-decimation.md) for high-rate rendering, level of detail, peak preservation, multi-pane synchronization, DPI, GPU use, or performance.
- Read [measurements-spectrum.md](references/measurements-spectrum.md) for cursors, statistics, period/frequency, FFT, PSD, filtering, or reportable results.
- Read [interaction-tools.md](references/interaction-tools.md) for zoom, pan, cursor/region editing, trigger handles, hit testing, keyboard/touch input, or undoable configuration changes.
- Read [library-selection.md](references/library-selection.md) before choosing, replacing, or building a charting/rendering engine.
- Read one primary platform guide when the stack is known: [wpf.md](references/wpf.md), [web.md](references/web.md), or [pyside6.md](references/pyside6.md).
- For React, read [react.md](references/react.md) after [web.md](references/web.md). For Vue, read [vue.md](references/vue.md) after [web.md](references/web.md).
- Read [verification.md](references/verification.md) before implementing tests, diagnosing a fidelity/performance defect, or declaring work complete.

## Follow the Design Workflow

### 1. Discover the Acquisition Contract

Inspect the repository, device/protocol APIs, data formats, chart dependencies, tests, and documented requirements. Establish:

- channel count, signal type, unit, calibration, resolution, and valid range;
- uniform or irregular sampling, sample rate, clock source, timestamp epoch, drift, and synchronization;
- chunk size, sustained and burst throughput, history length, retention, and export needs;
- missing, invalid, late, duplicated, or reordered sample semantics;
- live, triggered, frozen, historical, comparison, and playback modes;
- hardware versus software trigger ownership and pre/post-trigger guarantees;
- required time/amplitude measurements and spectral definitions;
- visible latency, refresh-rate, memory, DPI, accessibility, and supported-device targets.

State assumptions when the repository cannot answer them. Do not invent sample rates, clock accuracy, trigger guarantees, or real-time claims.

### 2. Establish Signal Truth

Keep raw acquisition data and metadata independent of the chart. Model channel identity, acquisition/session identity, sequence, time mapping, units, quality, discontinuities, and calibration explicitly. Preserve an immutable or append-only raw path; derive display reductions and measurements from declared source revisions.

Use relative time near the visible origin for floating-point rendering. Retain integer ticks, sample indices, or another exact representation for long absolute timelines. Never force nanosecond-scale absolute timestamps through a plain floating-point chart axis without a precision analysis.

Separate:

- acquisition and transport state;
- raw and calibrated samples;
- display reduction and exact analysis data;
- viewport state and channel layout;
- trigger configuration and observed trigger events;
- interaction previews and committed settings;
- measurement definitions and computed results.

### 3. Select Infrastructure Deliberately

Audit existing dependencies first. Prefer a mature plotting engine when it satisfies the verified streaming, gap, reduction, cursor, export, licensing, and platform requirements. Benchmark the intended channel count, data density, update cadence, and interaction—not a vendor demo.

Keep sample storage, time mapping, trigger semantics, measurements, and history independent of chart-series objects. Treat plot nodes and library annotations as render adapters. Build custom rendering only when measured requirements justify the missing layer.

### 4. Design a Deep Viewer Boundary

Expose a small semantic interface around substantial internal behavior. A typical boundary handles:

- append/reconcile `SampleChunk` values by acquisition and sequence;
- switch among live-follow, frozen review, historical, and triggered capture;
- set a `TimeViewport` and synchronized pane ranges;
- configure visible channels, scales, offsets, and styles;
- edit triggers, cursors, and analysis regions through begin/update/commit/cancel;
- request measurements against a named raw/derived data revision;
- publish render snapshots, quality/freshness state, and committed semantic events.

Keep UI events, chart nodes, worker messages, and device protocol details behind adapters.

### 5. Prove a Vertical Slice

Build one end-to-end slice before generalizing:

1. Generate or ingest a uniformly sampled sine wave containing a narrow pulse, a gap, and sequence metadata.
2. Append chunks into a bounded store without blocking the UI thread.
3. Render a live-follow trace using a peak-preserving reduction.
4. Freeze the display while ingestion continues, then pan and zoom into exact samples.
5. Add two time cursors and report `Δt` plus the guarded reciprocal frequency.
6. Arm one edge trigger and retain the declared pre/post-trigger window.
7. Reconnect with a new acquisition identity and show the discontinuity instead of joining sessions.
8. Verify the pulse, gap, cursor result, trigger index, and bounded memory behavior.

### 6. Make Trust Visible

Continuously distinguish:

- live-follow, frozen, stopped, triggered, historical, and disconnected states;
- newest data time, visible window, latency, and freshness;
- raw, calibrated, filtered, and display-reduced traces;
- valid samples, gaps, saturation, clipping, overrange, and other quality states;
- hardware trigger configuration, armed/waiting state, and observed trigger position;
- cursor source channel, region, unit, and analysis revision;
- requested versus effective sample rate, timebase, and channel scaling when they differ.

Use text/icon/shape in addition to color. Keep controls operable by keyboard and expose essential values outside a canvas-only surface.

### 7. Verify Before Handoff

Test data and math independently from rendering. Then test ingestion, state transitions, reduction fidelity, interaction adapters, library integration, and end-to-end gestures. Include synthetic signals with known answers and adversarial patterns that expose aliasing, hidden spikes, timestamp precision loss, and gaps.

Report the exact dataset, rates, hardware, render size, device scale, and measurement conventions behind any correctness or performance claim.

## Produce Decision-Ready Output

For design/review work, include:

- signal/time/quality model and acquisition state machine;
- buffering, retention, backpressure, and reconnect policy;
- raw versus render versus analysis data flow;
- reduction/LOD algorithm and fidelity guarantees;
- trigger, cursor, region, measurement, and spectrum semantics;
- chart-library boundary and platform mapping;
- performance, accessibility, export, and verification criteria.

For implementation work, encode those decisions in focused types and deterministic tests. Prefer names such as `SignalChannel`, `AcquisitionId`, `SampleChunk`, `TimeMapping`, `QualitySpan`, `WaveformStore`, `TimeViewport`, `TriggerConfig`, `CursorSet`, `AnalysisRegion`, `MeasurementRequest`, and `RenderEnvelope`.

## Guardrails

- Do not use chart-series objects as the authoritative sample store.
- Do not calculate measurements from display-decimated data unless the result explicitly describes that approximation.
- Do not use simple subsampling or averaging when a single-sample excursion must remain visible.
- Do not connect lines across missing samples, clock resets, or acquisition sessions without an explicit interpolation policy.
- Do not publish every sample or pointer move through application-wide reactive state.
- Do not copy the full history for every frame or append.
- Do not label a frozen display as stopped acquisition, or a stopped stream as disconnected.
- Do not treat software trigger preview as hardware trigger evidence.
- Do not present an FFT without sample-rate, window, length, normalization, and unit semantics.
- Do not claim real-time behavior without a defined deadline, latency budget, and measured evidence.
- Do not let UI measurements become protection, safety, or control authority unless the system architecture explicitly establishes that role.
