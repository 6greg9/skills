# PySide6 and Qt Adapter

Use PySide6/Qt as the shell around domain-owned acquisition, storage, reduction, interaction, and measurement services.

## Keep Data Contiguous

Use NumPy arrays or another explicit contiguous buffer contract for numeric samples. Define dtype, byte order, shape, stride, ownership, mutability, and lifetime when data crosses device SDK, C/C++, NumPy, worker, and renderer boundaries.

Avoid Python object-per-sample models and repeated list/array conversion. Append or publish bounded chunks. Do not mutate arrays still visible to the renderer.

## Keep Acquisition off the GUI Thread

Read/decode/store/reduce in workers or device callbacks with a bounded queue. Deliver batched immutable results or revision notifications to the GUI thread through an appropriate queued mechanism. Coalesce plot updates with a timer/frame cadence rather than emitting one signal per sample.

Cancel obsolete jobs and reject results by acquisition/source revision. Keep GUI objects in the GUI thread and make teardown safe during active streaming.

## Select and Wrap the Plot Engine

Evaluate pyqtgraph for live scientific traces and test its `clipToView`, automatic downsampling, and peak reduction against the product's spike/gap requirements. Use NumPy arrays directly where supported. Evaluate Qt Graphs/Charts for simpler native views and Matplotlib for analysis/publication-oriented output.

Profile line width, antialiasing, scatter symbols, finite-value checks, and OpenGL options with representative data. Do not enable an optimization that changes gap or quality semantics without tests.

Keep `PlotDataItem`, `ViewBox`, cursor lines, and library transforms behind an adapter. Store exact samples/time in domain services and synchronize panes using exact time rather than scene coordinates.

## Integrate Qt State

Use signals for semantic state and bounded batch notifications. Do not broadcast raw high-rate data through many Python slots. Keep transient hover/drag state in the viewer/controller and commit trigger/cursor/region changes once per gesture.

Use `QTimer` or the selected engine's update mechanism to bound repaint cadence. Release timers, signals, workers, native buffers, and plot items when a document/view closes.

## Verify Qt Risks

- Verify queued delivery does not grow without bound.
- Verify NumPy/native buffer ownership across threads.
- Verify high-DPI logical/device coordinates and mixed-monitor changes.
- Verify mouse/tablet/touch synthesis and capture cancellation.
- Verify downsampling preserves single-sample peaks, steps, and gaps.
- Verify close/reopen does not leak workers, signals, or plot resources.
