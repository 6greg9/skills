# Verification and Acceptance

## Contents

- Test layers
- Signal/time tests
- Streaming and trigger tests
- Reduction fidelity
- Measurement and FFT tests
- Interaction and platform tests
- Performance evidence

## Test in Layers

1. Test time mapping, sample selection, quality propagation, trigger math, reduction, and measurements as pure code.
2. Test acquisition/viewer/tool state machines with synthetic events and chunks.
3. Test storage, worker, and renderer adapters with controlled schedules and failures.
4. Test the selected chart engine's visual and interaction behavior.
5. Run representative end-to-end streaming, freeze/review, trigger, cursor, and export workflows.

Use deterministic synthetic signals and fixed seeds. Retain golden expectations independently of the renderer.

## Verify Signal and Time Semantics

Cover:

- exact index/tick/time conversion over short and long durations;
- viewport-relative conversion and label reconstruction;
- uniform and irregular sampling;
- timestamp wrap/reset/drift-mapping revisions;
- chunk ordering, duplicates, overlap, missing sequence, and gaps;
- calibration revision and unit conversion;
- digital transitions and quality spans;
- new acquisition/session discontinuities.

Test values near numeric precision boundaries and negative/relative times where supported.

## Verify Streaming and Trigger State

Drive:

- connect, configure, arm, wait, acquire, complete, stop, fault, and disconnect;
- freeze while ingestion continues and explicit return to live;
- bounded queue/ring overwrite/drop/spill behavior;
- sustained and burst throughput;
- reconnect with continuity proven and unproven;
- trigger crossing across a chunk boundary;
- rising/falling direction, hysteresis, holdoff, and re-arm;
- exact pre/post sample counts and incomplete capture;
- stale callback/result rejection by acquisition revision.

Assert that every data loss becomes explicit and that ambiguous commands are not silently reported as successful.

## Prove Reduction Fidelity

Include adversarial sequences:

- one-sample positive and negative impulses between ordinary samples;
- alternating min/max faster than pixel density;
- square waves with narrow pulses;
- long flat lines plus one excursion;
- `NaN`/invalid spans and sequence gaps;
- clipping/saturation and overrange;
- irregularly spaced bursts;
- transitions on bucket boundaries.

Verify the displayed envelope contains required extrema, never bridges gaps, preserves digital transitions as promised, and converges to exact samples when zoomed in.

## Verify Measurements and Spectrum

Use known vectors for:

- cursor `Δt`, `Δy`, and guarded reciprocal;
- mean, min/max, peak-to-peak, total RMS, AC RMS, standard deviation, and integral;
- interval-boundary and irregular-time weighting;
- sine waves at exact and non-bin frequencies;
- DC plus AC components;
- window coherent gain and chosen amplitude normalization;
- one/two-sided spectra, PSD/ASD units, and Nyquist behavior;
- zero padding without false resolution claims;
- gaps, invalid samples, clipping, and calibration changes;
- filter delay and derived-signal provenance.

Compare against an independently calculated reference within operation-specific tolerances.

## Exercise Interaction and Rendering

Cover:

- cursor-anchored horizontal zoom;
- pan bounds and retained-data overwrite;
- synchronized panes by exact time;
- cursor, trigger, region, and channel-scale begin/update/commit/cancel;
- pointer capture loss, Escape, focus loss, and mode/source changes;
- overlap hit priority and view-space tolerance;
- keyboard navigation and accessible value/status output;
- non-100% DPI, resize, fullscreen, and context/device recreation;
- export with units, status, cursor/trigger overlays, and source context.

Assert one semantic commit/undo record per completed gesture and none after cancellation.

## Report Performance Evidence

State the tested:

- channels, sample rates, chunk sizes, history, and visible window;
- renderer size, device scale, target refresh, and interaction;
- hardware, OS, runtime, and library versions;
- ingestion/store/reduction/render latency distributions;
- pointer latency, Dispatcher/main-thread load, allocations, CPU/GPU, and memory;
- queue high-water mark, dropped/overwritten samples, and skipped render frames.

Pass only against explicit product budgets. A smooth demo does not prove sustained acquisition integrity or measurement correctness.
