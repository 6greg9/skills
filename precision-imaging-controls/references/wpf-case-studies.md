# WPF Imaging Case Studies

Use these public experiments as concrete evidence about WPF imaging behavior. Extract the demonstrated technique, identify its hidden assumptions, and rewrite it behind the framework-neutral boundaries defined by this skill. Do not treat a dated sample project as a production control or a canonical architecture.

## Source and License Policy

- Link to source rather than copying large code sections into a project or this skill.
- Verify the current license of every repository before reusing code. Public visibility alone does not grant reuse rights; follow [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
- The reviewed `2026WPF` repository declares an [MIT License](https://github.com/gogowaten/2026WPF/blob/master/LICENSE). Recheck the license and preserve required notices when copying a substantial portion.
- Treat older or unlicensed examples as reading material. Reimplement the underlying idea from the platform and domain requirements unless permission is available.
- Re-verify source behavior against the current revision when a detail affects correctness. The observations below were reviewed on 2026-07-26.

## Translate Experiments into Production Patterns

| Source | Observe | Retain | Rewrite or reject |
|---|---|---|---|
| [`BitmapSourceVisualizer`](https://github.com/gogowaten/2026WPF/tree/master/BitmapSourceVisualizer) | `ScrollViewer`, image scaling, nearest-neighbor display, pixel grid, pan, pixel probe, navigator, and viewport rectangle compose a useful viewer feature set. [`DrawTextRGBA.cs`](https://github.com/gogowaten/2026WPF/blob/master/BitmapSourceVisualizer/DrawTextRGBA.cs) draws only visible pixel labels through `OnRender`. | Separate the viewport, pixel inspector, navigator, and transient overlay. Cull work to the inverse-transformed visible image region and suspend expensive labels during rapid navigation. | Replace independent scale/scroll calculations with one invertible `ViewportTransform` and cursor-anchored zoom. Do not allocate a `CroppedBitmap`, conversion object, byte array, or text layout per pixel or pointer move; normalize or cache an appropriate pixel buffer. Do not assume every source is four-byte BGRA. |
| [`20260209`](https://github.com/gogowaten/2026WPF/tree/master/20260209) and [`ResizeAdorner8handle`](https://github.com/gogowaten/2026WPF/tree/master/20260330_03_ResizeAdorner8handle) | `Thumb` and `Adorner` make rectangle selection, movement, and four- or eight-direction resizing easy to inspect. | Model semantic handles such as north-west, edge-east, and body. Capture the pointer for one edit session and expose visible resize feedback. | Keep ROI geometry in image coordinates rather than `Canvas.Left`, `Canvas.Top`, `Width`, and `Height`. Inverse-transform view deltas, keep handles screen-constant, enforce constraints explicitly, and commit one undo transaction. |
| [`BezierAdorner`](https://github.com/gogowaten/2026WPF/tree/master/20260321_BezierAdorner) and [`GeoLineEx_ObserveCollectionPoint`](https://github.com/gogowaten/2026WPF/tree/master/20260505_GeoLineEx_ObserveCollectionPoint) | Adorners can follow Bezier controls and a changing point collection; custom `Shape` geometry can account for stroke bounds. | Give polygon, polyline, and curve tools stable vertex identities and explicit add, remove, move, commit, and cancel behavior. Use stroke-aware bounds for rendering and candidate culling. | Do not normalize persisted points merely to simplify a visual's local bounds. Do not let an adorner own authoritative vertices. Separate image geometry, local render geometry, and view-space handles so bounds updates cannot drift the ROI. |
| [`GeoLine_Group_Editing`](https://github.com/gogowaten/2026WPF/tree/master/20260510_01_GeoLine_Group_Editing) | Recursive data/templates demonstrate selection, current item, grouping, ungrouping, and Z-order in a canvas editor. | Use stable IDs, deterministic ordering, explicit parent/child ownership, and semantic selection. Make group edits transactional. | Do not store live controls in the domain model. Keep hover, current handle, and visual containers transient. Add undo/redo, versioned persistence, and cancellation behavior before treating the scene model as durable. |
| [`20260301`](https://github.com/gogowaten/2026WPF/tree/master/20260301) | `ItemsControl`, a Canvas items panel, data templates, behavior, and editor service show one route from models to selectable visuals. | Keep model-to-view projection separate from selection and tool services. Publish committed semantic changes rather than raw WPF events. | Treat incomplete sample commands and mutable UI-facing lists as exploratory. Define observable selection semantics, ownership, and tests instead of inheriting the sample's exact service boundaries. |
| [`Pixtack4`](https://github.com/gogowaten/Pixtack4) | Image, text, rectangle, ellipse, geometry, freehand, group, root, resize, anchor, clipboard, serialization, and export features form an integrated editor case study. See [`ItemData.cs`](https://github.com/gogowaten/Pixtack4/blob/main/Pixtack4/ItemData.cs), [`ResizeAdorner.cs`](https://github.com/gogowaten/Pixtack4/blob/main/Pixtack4/ResizeAdorner.cs), and [`Generic.xaml`](https://github.com/gogowaten/Pixtack4/blob/main/Pixtack4/Themes/Generic.xaml). | Derive a product feature inventory and study how selection, grouping, Z-order, templates, serialization, and export interact end to end. | Do not reproduce the large all-purpose control. Split document state, viewport, selection, tool sessions, history, rendering, clipboard, and export behind narrow interfaces. Do not let a WPF control tree or serializer dictate the persisted schema. |
| [`ElementToBitmap`](https://github.com/gogowaten/2026WPF/tree/master/20260524_01_ElementToBitmap), [`PngDpi`](https://github.com/gogowaten/2026WPF/tree/master/20260628_PngDpi), and [`Test_Pbgra32`](https://github.com/gogowaten/2026WPF/tree/master/20260705_Test_Pbgra32) | `VisualBrush`, `DrawingVisual`, `RenderTargetBitmap`, encoder round trips, DPI, pixel format, and premultiplied alpha expose export boundaries that a viewer can otherwise hide. | Make export bounds, scale, target DPI, background, alpha mode, pixel format, color policy, and annotation inclusion explicit inputs. Test decoded output rather than trusting encoder settings. | Handle both layout and render transforms deliberately. Calculate memory from dimensions and bytes per pixel. Do not use an encoded debugger preview for bit-exact validation of 16-bit, float, or premultiplied sources. |
| [`20180226forMyBlog`](https://github.com/gogowaten/20180226forMyBlog), [`2020WPF`](https://github.com/gogowaten/2020WPF), and [`2021WPF`](https://github.com/gogowaten/2021WPF) | Small projects explore quantization, thresholding, dithering, gamma, resize kernels, SIMD, compositing, and SSIM with WPF bitmap APIs. | Extract pure pixel operations with explicit source and destination formats. Preserve representative algorithm variants as tests or benchmarks when the product needs them. | Do not run long nested loops on the UI thread or infer production quality from a visual demo. Specify stride, channel order, alpha, transfer function, edge policy, numeric range, cancellation, and expected error; add golden images and measured benchmarks. |
| [`Pixtrim2`](https://github.com/gogowaten/Pixtrim2) and [`ScreenCapture`](https://github.com/gogowaten/ScreenCapture) | Crop presets, clipboard monitoring, window/client bounds, virtual-screen coordinates, cursor composition, and Win32 capture reveal input-boundary edge cases. | Normalize captured pixels and crop geometry into a documented image space before the editor sees them. Test multi-monitor, negative desktop coordinates, DPI, alpha, cursor hotspots, and clipboard formats. | Treat legacy GDI interop and large code-behind files as audit targets. Verify resource ownership and current capture API suitability rather than copying the acquisition layer into a reusable control. |

## Apply a Production Rewrite Checklist

Before accepting a technique from a sample, answer all of the following:

### Coordinates and Geometry

- Which space owns every point, vector, rectangle, and tolerance?
- Is one forward/inverse transform authoritative?
- Are pixel centers, ROI boundaries, axes, rotation, and out-of-bounds behavior explicit?
- Can repeated zoom, rotate, resize, group, ungroup, save, and load occur without geometry drift?

### Interaction

- Does each gesture have `begin`, `update`, `commit`, and idempotent `cancel` paths?
- What happens on Escape, capture loss, tool switch, window deactivation, or model deletion?
- Are handle size and hit tolerance defined in view/device units while geometry stays stable?
- Does one gesture produce one undoable transaction?

### Rendering and Pixels

- Is work culled to the visible region and scheduled at a bounded frame rate?
- Are decoded pixels, tiles, geometries, and text layouts cached behind correct revision keys?
- Are source pixel format, stride, bit depth, channel order, alpha mode, DPI, and color transfer explicit?
- Are sampling and quantitative analysis tied to source or explicitly processed data rather than an ambiguous displayed bitmap?

### Verification

- Are transform round trips, cursor-anchored zoom, mixed DPI, rotation, and extreme zoom tested?
- Are cancellation, overlap priority, snapping hysteresis, and undo/redo tested without the UI framework?
- Are export dimensions, decoded DPI, pixel format, alpha, and overlay alignment asserted?
- Are frame-time and memory claims measured with a stated image size, bit depth, annotation count, and device?

## Choose a Reading Route

- For an image viewer or pixel inspector, start with `BitmapSourceVisualizer`, then inspect the export and DPI experiments.
- For rectangle or ellipse ROI editing, follow `20260209` into the eight-handle adorner.
- For polygon, polyline, or Bezier editing, continue through the vertex-observing `GeoLine` example and group editor.
- For an annotation/editor product, use `Pixtack4` as a feature inventory and apply the decomposition rules above.
- For CPU pixel processing, use the 2018, 2020, and 2021 experiments to identify algorithms, then reimplement them as tested non-UI services.
- For capture or crop workflows, inspect `ScreenCapture` and `Pixtrim2`, then audit every OS, DPI, clipboard, and resource-lifetime assumption.
