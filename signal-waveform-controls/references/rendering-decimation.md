# Rendering and Faithful Decimation

## Contents

- Rendering contract
- Reduction algorithms
- Multiresolution storage
- Frame scheduling
- Panes, axes, and DPI
- Performance evidence

## Separate Three Data Paths

Maintain distinct paths:

1. **Raw path:** authoritative samples and quality.
2. **Analysis path:** exact or explicitly transformed samples for measurements.
3. **Render path:** view-dependent summaries optimized for pixels.

Changing zoom may select a different render level; it must not change raw data or silently change committed measurement definitions.

## Match Reduction to Signal Semantics

When many samples map to one horizontal pixel bucket, preserve information relevant to the product:

- analog trace: retain first, minimum, maximum, and last plus quality/gap evidence;
- spike-sensitive trace: use a min/max envelope or equivalent extremum-preserving method;
- digital/state trace: retain every transition or an equivalent transition summary;
- band/range trace: retain lower/upper envelope;
- density/event trace: aggregate counts with an explicit meaning.

Simple stride subsampling can miss narrow events. Averaging can erase peaks and change amplitude. Use them only when that distortion is acceptable and visible in the contract.

Bucket against the time mapping and viewport, not merely fixed source-array offsets when irregular sampling is possible. Include samples needed to connect bucket boundaries without drawing across gaps.

## Build Replaceable Multiresolution Summaries

For long histories, maintain chunk summaries or a pyramid containing enough statistics for the promised render semantics. Key summaries by acquisition, channel, raw revision, calibration/processing revision, and level.

Choose a level from visible time span and plot width. At high zoom, render exact samples or steps. At low zoom, render envelopes. Cancel stale reduction work after the viewport or source revision changes.

Treat summaries as caches. Rebuild them from authoritative data and test them against adversarial signals.

## Schedule Frames, Not Samples

Let acquisition append at its own cadence. Publish the newest consistent watermark and render at a bounded frame cadence. Coalesce invalidations and skip obsolete frames rather than queueing every update.

Invalidate separately:

- new samples;
- viewport/timebase;
- vertical scale/offset or channel layout;
- cursor/trigger/region overlays;
- labels/legend/status;
- display-processing revision.

Do not allocate or copy the entire visible history each frame. Reuse typed/contiguous buffers and batch uploads/appends. Bound CPU and GPU caches.

## Keep Panes and Axes Coherent

Use one authoritative time viewport for synchronized panes unless the product explicitly supports independent timebases. Map each channel through its own declared amplitude scale/offset and unit.

Keep these view-space constants where appropriate:

- cursor lines and handles;
- trigger marker and threshold affordances;
- stroke widths and selection hit radii;
- text, status badges, and measurement labels.

Show zero/reference levels, clipping, gaps, and disabled/hidden channels deliberately. Avoid smoothing curves that imply values never sampled.

Size backing surfaces for actual DPI/device-pixel ratio while keeping interaction in logical coordinates. Rebuild device-dependent resources after monitor/DPI/context changes.

## Use GPU Rendering for a Measured Reason

Prefer an existing high-throughput engine before writing custom GPU code. Use GPU paths when channel count, data density, fills, spectrograms, or refresh requirements justify the complexity.

Account for buffer upload cost, context/device loss, precision, antialiasing, readback/export, and driver variability. Keep a deterministic CPU reference for reduction and measurement even when drawing is GPU-backed.

## Report Performance Reproducibly

Record:

- channels, sample rate, retained samples, and visible samples;
- uniform/irregular timing, gaps, and processing;
- viewport pixel size and device scale;
- append chunk size and cadence;
- render/update rate, input latency, CPU/GPU, allocations, and memory;
- hardware, OS, runtime, and chart-engine version;
- reduction level/algorithm and whether ingestion lost data.

Distinguish acquisition throughput, store throughput, reduction latency, render time, and end-to-end visible latency.
