# Verification and Acceptance

## Contents

- Test layers
- Numerical invariants
- Interaction scenarios
- Rendering and performance
- Completion evidence

## Test in Layers

1. Test geometry, constraints, and transforms without a UI framework.
2. Test tool state transitions with synthetic semantic pointer samples.
3. Test the platform adapter's event normalization and pointer capture.
4. Test rendered snapshots or visual invariants at representative DPI and zoom values.
5. Run a small number of end-to-end gestures on the real control.

Prefer generated points and property tests for invertible transforms. Use fixed examples for pixel-boundary semantics and user-visible coordinate formatting.

## Verify Numerical Invariants

Cover:

- image → view → image round trips;
- view → image → view round trips;
- cursor-anchored zoom preserving the point under the cursor;
- pan preserving scale and rotation;
- rotation around the documented anchor;
- singular/near-singular transform rejection;
- no unintended rounding after repeated edits;
- explicit pixel-center and ROI boundary cases.

Choose tolerances from coordinate scale and product requirements. Do not use one arbitrary epsilon for every test.

## Exercise Interaction State

For every editable tool, cover:

- begin, preview, commit;
- Escape cancellation;
- pointer capture loss;
- tool switch or document close mid-gesture;
- click without exceeding drag threshold;
- out-of-bounds drag;
- zero-size and self-intersecting geometry when relevant;
- overlapping hit targets and deterministic priority;
- snapping acquire, retain, release, and visible guide;
- constrained drag with modifier changes;
- undo and redo as one transaction;
- keyboard nudge and deletion;
- mouse, touch, and pen paths required by the product.

Assert both the final model and the absence of unwanted history entries after cancellation.

## Verify Rendering and Performance

Test:

- minimum, normal, and maximum supported zoom;
- rotated and mirrored views if supported;
- 100%, fractional, and mixed-monitor DPI;
- handle, stroke, and label screen size;
- label collision and clipping;
- viewport resize and fit policy;
- dense annotations and contours;
- missing/late tiles during fast navigation;
- cache invalidation after image, style, or geometry changes;
- GPU/context recreation when applicable;
- source-image immutability under display adjustment.

Measure rather than guess. Record representative hardware, image dimensions, bit depth, annotation count, and interaction used for any frame-time or memory claim.

## Report Completion Evidence

At handoff, report:

- image/view/device coordinate conventions exercised;
- automated checks run and their results;
- manual gestures or visual states inspected;
- performance dataset and result if performance was in scope;
- untested devices, browsers, DPI modes, or render backends;
- assumptions that still constrain persistence or performance.
