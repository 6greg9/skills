# Acquisition, Trigger, and Streaming

## Contents

- State model
- Producer/consumer boundary
- Buffering and backpressure
- Trigger semantics
- Freeze, stop, and reconnect

## Model Orthogonal State

Do not collapse these facts into one `isRunning` flag:

- connection/transport;
- device configuration;
- acquisition lifecycle;
- trigger arm/wait/capture state;
- viewer live-follow/frozen/review state;
- data freshness and quality;
- storage/retention state.

A useful acquisition lifecycle is:

```text
disconnected -> idle -> configuring -> armed -> waiting-trigger
                                      |             |
                                      +-> acquiring <-+
                                             |
                                      complete | stopped | faulted
```

Adapt it to the authoritative device API. Preserve unknown/ambiguous outcomes during timeouts or reconnects.

Snapshot the effective configuration with each acquisition: channel setup, requested/effective sample rate, coupling/range where relevant, trigger, pre/post sizes, clock, calibration revisions, and device/session identity.

## Bound the Producer/Consumer Boundary

Ingest data off the UI thread. Validate and append chunks in batches. Notify rendering with lightweight revision/watermark changes rather than one event per sample.

Choose and document:

- maximum queued chunks/bytes;
- ring-buffer duration or sample capacity;
- copy versus ownership-transfer rules;
- late/out-of-order window;
- drop, overwrite, block, spill-to-disk, or disconnect policy;
- how every loss becomes visible in sequence and quality metadata.

Never silently discard data to keep the chart responsive. It may be acceptable to skip render frames; it is different from losing acquisition data.

Use one publication boundary so readers observe consistent sample data, metadata, and watermark. Avoid exposing a buffer while a producer mutates its visible region.

## Define Trigger Semantics

Represent a trigger configuration explicitly:

```text
TriggerConfig
  authority: hardware | software
  source channel
  type: edge | window | pulse | external | domain-specific
  slope/direction
  level and unit
  hysteresis
  holdoff
  pre_trigger and post_trigger extents
  coupling/filter if supported
  configuration revision
```

Keep configuration, armed state, trigger detection, and captured trigger event separate. An observed trigger contains acquisition ID, source, exact index/time, configuration revision, quality, and device evidence.

For software triggers, define chunk-boundary behavior, filter delay, interpolation, hysteresis, re-arm, and latency. Use a stateful detector across chunks. Do not scan each chunk independently and miss crossings at its boundary.

For hardware triggers, treat controller/device evidence as authoritative. UI rendering or software detection may preview the threshold but must not overwrite the recorded hardware trigger index.

## Retain Pre/Post Data Correctly

Use a circular pre-trigger buffer sized from effective sample rate and requested duration/sample count. After detection, capture the declared post-trigger extent and seal the capture atomically.

Specify whether the trigger sample belongs to pre or post, whether counts are inclusive, and how gaps or dropped data affect completion. Show incomplete captures as incomplete; do not pad silently.

## Distinguish Viewer and Acquisition Actions

- **Freeze display:** stop following newest data while ingestion continues.
- **Resume live-follow:** move the viewport to the newest retained window.
- **Stop acquisition:** request the producer/device to stop and await observed completion.
- **Disconnect:** transport is unavailable; execution outcome may be uncertain.
- **Review:** navigate a sealed or retained dataset without implying live state.

Do not auto-jump a user from frozen review to live-follow when new chunks arrive. Show unseen data/newest time and provide an explicit return-to-live action.

## Reconcile Reconnects

On reconnect, obtain device/session identity, current configuration, acquisition state, last acknowledged sequence/index, and clock mapping. Start a new acquisition identity when continuity cannot be proven. Render an explicit discontinuity rather than joining unrelated timelines.

Reject late callbacks and worker results from obsolete acquisition revisions. Never replay an ambiguous start/stop/configuration request automatically unless the protocol makes it idempotent and reconciliation proves it safe.
