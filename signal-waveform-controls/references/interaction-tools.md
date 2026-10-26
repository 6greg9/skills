# Waveform Interaction Tools

## Contents

- Viewer modes
- Semantic input and hit testing
- Tool lifecycle
- Linked panes
- Live/frozen behavior
- Accessibility

## Keep Modes Explicit

Model at least the modes the product supports:

- live-follow;
- frozen review;
- historical/playback;
- triggered capture review;
- disconnected/stale.

Keep the active interaction tool separate from viewer mode:

- inspect/crosshair;
- pan and zoom;
- time/value cursors;
- analysis region/gate;
- trigger level/time marker;
- channel scale/offset;
- annotation or event marker.

Do not let event-handler order decide which action owns a gesture.

## Normalize Input

Translate framework events into semantic samples containing pointer ID/device, logical-view position, buttons, modifiers, timestamp, and the mapped time/value under the relevant pane. Keep wheel normalization, drag thresholds, double-click, pointer capture, and keyboard mapping in the platform adapter.

Use view-space hit radii for cursors, handles, thresholds, and traces. Return semantic targets such as `CursorHandle`, `TriggerLevel`, `RegionEdge`, `Trace`, `PaneBackground`, and include channel/pane identity plus view-space distance.

Prioritize active handles over trace bodies and background navigation. Resolve overlapping traces deterministically and support cycling or a chooser when necessary.

## Use Transactional Tool Sessions

Give editable tools a lifecycle:

```text
ready -> begin -> preview -> commit
                    |
                  cancel
```

Capture the initiating pointer. Make cancellation idempotent. Restore the pre-gesture setting on Escape, capture loss, deactivation, mode switch, source revision loss, or invalid mapping.

Commit one semantic change per completed gesture. Keep hover, live preview, and raw pointer movement out of undo history and application-wide state.

For trigger edits, distinguish a preview threshold from configuration accepted by the acquisition authority. Show pending, effective, rejected, and revision-mismatch states.

## Define Navigation

Use cursor-anchored horizontal zoom unless the product specifies another anchor. Preserve the time under the pointer. Define vertical zoom per pane/channel and prevent accidental changes to acquisition range when the action only changes display scale.

Support:

- horizontal pan/zoom over retained data;
- return-to-live action;
- fit capture/selection;
- exact-sample zoom level;
- keyboard cursor nudge and region resize;
- optional overview/minimap for long captures.

When frozen, never jump to newest data merely because samples arrive. When retention overwrites frozen data, warn before or as the visible source becomes unavailable.

## Synchronize Panes Semantically

Share one `TimeViewport` across panes where appropriate. Synchronize crosshair/cursors by exact time, not by copying screen x coordinates. Map each pane independently to its amplitude axis.

When panes use different clocks or alignments, synchronize through an explicit time-mapping model and show uncertainty/discontinuity. Do not imply sample alignment from visual proximity alone.

## Preserve Signal Meaning

- Draw analog signals as lines/envelopes without decorative smoothing by default.
- Draw digital signals as steps with visible transitions.
- Show gaps and invalid spans.
- Keep cursor labels tied to source channel/unit.
- Distinguish raw, filtered, averaged, and display-reduced traces.
- Keep trigger markers and acquisition status visible while editing.

Provide keyboard-operable cursor/region controls, accessible names, non-canvas measurement values, focus indication, and patterns/text in addition to color for channel and quality distinctions.
