# WPF Mapping

Use WPF as an adapter around the framework-neutral imaging model.

## Recommended Boundaries

- Host the viewport in a custom `FrameworkElement`/`Control` when rendering is specialized.
- Keep stable geometry, tools, and history in ordinary .NET types. Keep optional extension state there only when its branch is active.
- Expose configuration and committed state through dependency properties, commands, and view models.
- Keep pointer capture, cursor changes, frame scheduling, and transient tool sessions near the control/controller.
- Publish semantic changes to the view model; avoid updating application-wide bindings on every mouse move.

Use `System.Windows.Media.Matrix` or an equivalent double-precision transform as the WPF-facing representation. Keep one authoritative transform service rather than mixing `RenderTransform`, `Canvas.Left`, scroll offsets, and ad hoc scale values.

WPF input and layout coordinates are DIPs. Treat device-pixel conversion as a rendering concern and test per-monitor DPI changes.

## Select a Renderer

- Use `OnRender`/`DrawingContext` for a moderate number of vector overlays and simple invalidation.
- Use `DrawingVisual` children when independently invalidated retained visuals materially help.
- Use `WriteableBitmap` for CPU-generated rasters that update in bounded regions.
- Use `D3DImage`, a GPU-backed interop layer, or another specialized surface for very large images, high-rate frames, or shader-based adjustment.

Do not create thousands of `Shape` or `Thumb` elements for dense annotations. Use lightweight rendered geometry and create semantic edit handles in the interaction layer.

Freeze immutable `Freezable` resources when safe. Cache pens, brushes, text layouts, and geometries by semantic style and DPI-aware keys.

## Map Input

- Normalize mouse, stylus, and touch before tool dispatch.
- Capture the initiating mouse/stylus/touch device during a drag.
- Handle capture loss and window deactivation as cancellation.
- Use `CompositionTarget.Rendering` or a controlled invalidation loop to coalesce high-frequency preview updates when needed.
- Keep routed-event handling deliberate so parent scroll viewers and the imaging viewport do not both consume navigation gestures.

Define whether the viewport lives inside a `ScrollViewer`. For precision navigation, a custom viewport transform is often clearer than combining a scroll viewer with independent zoom/rotation.

## Fit MVVM Without Forcing It

Put these in view models or application services:

- selected document/image identity;
- persisted annotations and ROIs;
- active tool choice and settings;
- display settings and optional extension settings when active;
- undoable commands and committed selection.

Keep these inside the control or injected interaction controller:

- hover target;
- captured pointer identity;
- drag threshold and live pointer samples;
- transient preview geometry;
- frame caches and device resources.

Make the control replaceable in tests by keeping domain operations independent of WPF types.

## Verify WPF-Specific Risks

- Verify layout versus render transform interactions.
- Verify `GetPosition` against the intended element.
- Verify DPI transitions between monitors.
- Verify stylus promotion does not duplicate mouse actions.
- Verify lost capture, context menus, and modal dialogs cancel or suspend safely.
- Verify text and handles remain screen-constant under rotation and zoom.
