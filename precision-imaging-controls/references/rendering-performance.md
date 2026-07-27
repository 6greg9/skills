# Rendering, Layers, and Performance

## Contents

- Layer architecture
- Geometry and style
- Invalidations and caching
- Large-image strategy
- Image adjustment
- DPI and text

## Use a Layered Scene

Render in a stable order:

1. checkerboard/background;
2. source image or tile pyramid;
3. image-space masks, heatmaps, contours, and ROI fills;
4. annotation geometry;
5. selected geometry and edit handles;
6. transient previews, snap guides, and crosshair;
7. rulers, axes, scale bar, labels, and HUD.

Clip image-space content to the viewport or image boundary as required. Keep HUD elements in view space. Give each layer an explicit invalidation cause so a cursor move does not force image decoding or mask regeneration.

Use a hybrid design:

- retain domain geometry and expensive cached resources;
- render transient overlays immediately from a snapshot;
- expose one frame-consistent snapshot to rendering and hit testing.

## Distinguish Geometry from Style

Keep core annotation geometry in image coordinates. Define style semantics independently:

- model-scaled strokes for regions that should grow with the image;
- screen-constant strokes and handles for interaction affordances;
- screen-constant text with image-anchored placement;
- selected, hovered, disabled, invalid, locked, and preview variants.

Do not mutate model geometry to achieve constant-size visuals. Transform geometry, then draw the affordance in view space.

Make the active hit target and selected control point visually unambiguous. Avoid using color as the only state signal.

## Invalidate Deliberately

Separate at least:

- image content invalidation;
- viewport transform invalidation;
- persistent overlay invalidation;
- transient interaction invalidation;
- HUD/layout invalidation.

Cache decoded images, tiles, paths, glyph layouts, mask textures, and feature indices only behind clear keys. Include source revision, geometry revision, zoom or level-of-detail bucket, and device scale where they affect the result. Include an optional extension revision only for artifacts derived from that extension.

Drive rapid pointer feedback from a frame scheduler rather than issuing unbounded repaints. Retain the most recent semantic pointer state and render it on the next frame.

## Scale to Large Images

For images larger than comfortable GPU texture or memory limits:

- use a tile pyramid or demand-loaded tiles;
- choose level of detail from projected pixel density;
- prefetch around the visible region and navigation direction;
- cancel obsolete decode requests after fast navigation;
- bound CPU and GPU caches;
- render a coarser fallback until detailed tiles arrive;
- keep annotations independent of tile availability.

Avoid copying the full image per frame. Avoid converting immutable source pixels just to draw overlays.

Use spatial indexing for dense annotations and contours. Cull by the inverse-transformed viewport, then perform precise view-space rendering and hit testing.

## Keep Image Adjustment Non-Destructive

Represent brightness, contrast, gamma, window/level, channel mixing, LUTs, and false color as a display pipeline. Preserve source data unless the user requests an exported derivative.

Apply adjustments consistently to all visible tiles. Keep quantitative sampling tied to source or explicitly processed data, not an ambiguous screenshot of the display pipeline.

State whether overlays are affected by image color transforms. Normally render overlays afterward so their semantic colors remain stable.

## Handle DPI and Text

Treat WPF DIPs, CSS pixels, and Qt logical pixels as logical view units, then account for device scale in the rendering surface.

- Resize backing buffers using the actual device-pixel ratio.
- Rebuild device-dependent resources when the ratio changes.
- Verify mixed-DPI monitor movement.
- Align one-device-pixel strokes only at the final rendering stage.
- Format image-coordinate labels independently of geometry precision.
- Prevent labels from obscuring critical handles; use deterministic placement and collision fallback.

Expose non-canvas equivalents for essential values and actions where accessibility matters. Provide keyboard selection, nudge, delete, cancel, and commit paths for editable controls.
