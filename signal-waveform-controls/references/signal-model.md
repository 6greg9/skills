# Signal, Time, and Quality Model

## Contents

- Core vocabulary
- Time representations
- Samples and gaps
- Units and calibration
- Storage and provenance

## Use Stable Domain Terms

Define these concepts separately:

- **Channel:** stable identity plus signal metadata and calibration.
- **Acquisition:** one configured capture or continuous session with a unique identity.
- **Sample:** value associated with an index/time and quality.
- **Sample chunk:** ordered batch from one acquisition/channel or synchronized channel group.
- **Trace:** visual projection of one raw or derived signal.
- **Viewport:** visible time and amplitude mapping.
- **Derived signal:** filtered, transformed, resampled, or mathematically combined output with provenance.
- **Measurement:** result produced from a declared signal revision and interval.

Do not use `series` to mean raw storage, chart object, channel, and derived output simultaneously.

## Represent Time Deliberately

For uniform sampling, prefer an exact model:

```text
time(i) = epoch + (start_index + i) * sample_period
```

Represent the epoch, sample index, and rational/integer clock relationship precisely enough for the required duration. If the hardware exposes ticks, retain tick frequency and conversion provenance.

For irregular sampling, store timestamps with each sample or chunk and require monotonicity rules. Preserve the distinction between event time, device time, receive time, and display time.

Convert to floating-point relative coordinates near the current viewport origin for rendering:

```text
x_view = seconds(sample_time - viewport_origin)
```

This prevents long absolute timestamps from erasing sub-millisecond or smaller deltas in a chart axis. Reconstruct labels from the exact time representation.

Record clock resets, wraparound, drift corrections, and synchronization changes as explicit discontinuities or mapping revisions.

## Model Samples and Gaps

Use a chunk contract such as:

```text
SampleChunk
  acquisition_id
  channel_set_id
  sequence
  start_index or start_time
  sample_period or timestamps
  values by channel
  quality spans or flags
  source/configuration revision
```

Validate length, ordering, channel identity, and time mapping at ingestion. Define duplicate and out-of-order handling. Detect gaps from sequence/index/time evidence instead of relying only on `NaN` values.

Represent quality in spans when per-sample objects would be wasteful. Include domain-relevant states such as valid, missing, invalid, saturated, clipped, overrange, estimated, or late. Render a gap by default; interpolate only under a named policy and never mutate raw data to hide it.

Draw digital/state channels with step semantics. Preserve transition ordering and zero-duration events where the source model permits them.

## Separate Raw Values and Calibration

Retain raw counts when reproducibility matters. Model calibration as a mapping with:

- unit and dimensional meaning;
- gain/offset or nonlinear transfer function;
- sensor/probe identity and range;
- revision, provenance, validity interval, and optional uncertainty;
- clipping/overrange behavior.

Do not infer physical units from axis labels. Apply the correct calibration revision for the acquisition. If calibration changes during a session, split the mapping revision explicitly.

Distinguish ADC resolution, effective noise floor, calibrated accuracy, and display formatting. They are not interchangeable.

## Preserve Provenance

Keep raw acquisition append-only or immutable after sealing. Identify every derived output by:

- source acquisition/channel revisions;
- exact interval and sample selection;
- processing graph or operation/version;
- parameters and boundary behavior;
- output unit and time mapping;
- creation time and software version when reportability requires it.

Store viewport, trace style, cursor positions, and analysis requests separately from raw samples. Persist derived arrays only when recomputation cost, audit, or external interchange justifies them.

Use bounded stores intentionally:

- ring buffer for recent live history;
- sealed capture for triggered acquisitions;
- chunked or memory-mapped storage for long review sessions;
- multiresolution summaries as replaceable acceleration data.

Never let cache eviction silently change a committed measurement without marking the source unavailable or recomputing from an authoritative store.
