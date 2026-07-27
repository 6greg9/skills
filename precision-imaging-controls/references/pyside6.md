# PySide6 and Qt Mapping

Use Qt widgets and events as adapters around the framework-neutral imaging model.

## Choose the View Architecture

- Use `QGraphicsView`/`QGraphicsScene` when scene transforms, item selection, and a moderate retained item graph fit the product.
- Use a custom `QWidget` with `QPainter` for controlled immediate-mode overlays.
- Use `QOpenGLWidget` or another GPU surface for large textures, shader-based adjustment, or high-rate frames.
- Combine a raster/GPU image surface with a lightweight semantic overlay rather than creating an item per dense feature.

When using `QGraphicsView`, define whether image coordinates equal scene coordinates. Keep any active optional-extension mapping separate from the scene transform. Do not persist item/device positions without converting to image space.

Use `QPointF`, `QRectF`, and `QTransform` for floating-point paths through the adapter. Keep the domain model free of Qt types if reuse or headless tests matter.

## Map Input

- Normalize `QMouseEvent`, `QTabletEvent`, wheel, touch, and gesture events into semantic pointer samples.
- Use event positions from the correct widget/viewport.
- Own grabs only for active drags and handle cancellation when the window deactivates or the target disappears.
- Define event acceptance so parent scroll areas and the viewport do not both navigate.
- Coalesce repaint requests with `update()`; avoid synchronous `repaint()` on pointer motion.

Map modifiers and shortcuts through Qt actions where user reconfiguration and focus routing matter. Keep Escape, commit, delete, nudge, and finish-path semantics consistent across tools.

## Integrate Signals and Undo

Emit signals for semantic preview changes only when observers truly need them. Emit committed model changes for normal application state and persistence. Avoid flooding Python slots across layers at pointer frequency.

Use `QUndoStack`/`QUndoCommand` or an equivalent domain history. Create one command per completed gesture and restore the prior model on cancel.

Keep worker threads away from GUI objects. Decode tiles, run feature detection, or calculate masks in workers, then deliver immutable results back to the GUI thread. Cancel obsolete jobs during navigation or document changes.

## Render Correctly

- Apply `QTransform` consistently and save/restore `QPainter` state by layer.
- Draw screen-constant handles in view/widget coordinates.
- Account for `devicePixelRatioF()` in backing images, textures, and caches.
- Avoid repeated `QImage`/NumPy copies; define ownership, stride, format, and lifetime explicitly.
- Cache `QPainterPath`, text layout, and converted images behind revision-aware keys.

## Verify Qt-Specific Risks

- Verify logical versus device coordinates on high-DPI displays.
- Verify `QGraphicsView` viewport coordinates versus scene coordinates.
- Verify wheel `angleDelta()` and `pixelDelta()` behavior.
- Verify tablet events are not handled again as synthesized mouse events.
- Verify OpenGL context loss/recreation and widget reparenting.
- Verify signal lifetime and worker cancellation when a document closes.
