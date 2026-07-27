# Core Geometry and Coordinates

## Contents

- Coordinate spaces
- Transform ownership
- Pixel conventions
- Numerical policy
- Domain model
- Optional semantics seam

## Coordinate Spaces

Name every coordinate value by its space. Use distinct value types where the language permits.

| Space | Meaning | Lifetime |
|---|---|---|
| Image `I` | Continuous coordinates over source pixels | Stable and persistable |
| View `V` | Logical UI coordinates such as WPF DIPs, CSS pixels, or Qt logical pixels | Transient |
| Device `D` | Physical display pixels after DPI/device scaling | Rendering-only |

Use `V = M_VI · I` for image-to-view navigation. Use homogeneous 3×3 affine matrices for translation, scale, rotation, reflection, and shear.

For hit testing, map stable geometry into view space and compare against a view-space tolerance. This keeps a six-pixel handle easy to acquire at every zoom and works under anisotropic transforms.

## Transform Ownership

Give one `ViewportTransform` authority over `M_VI` and its inverse. Recompute or invalidate the inverse atomically with the forward transform.

Provide explicit operations:

- `image_to_view(point)`;
- `view_to_image(point)`;
- `image_vector_to_view(vector)`;
- `view_tolerance_to_image_region(radius)` when spatial queries need a candidate region;
- cursor-anchored zoom;
- pan in view space;
- rotation around an explicit image or view anchor;
- fit modes that return a transform rather than mutating geometry.

For zoom at a view anchor `a`, preserve the image point under the cursor:

1. Calculate `i = inverse(M_VI) · a`.
2. Apply the new scale or compose a scale around `a`.
3. Adjust translation so the new transform maps `i` back to `a`.

Do not implement zoom by independently changing a scale property and guessing a new offset.

## Pixel Conventions

Choose and document one image convention:

- Treat integer coordinates as pixel centers; or
- Treat integer coordinates as pixel corners and centers as half-integers.

Use the same convention for display, snapping, ROI bounds, sampling, and export. State whether a rectangular ROI uses continuous bounds, inclusive pixel indices, or half-open sample bounds. Convert deliberately at raster I/O boundaries.

Define:

- origin location;
- positive x/y directions;
- angle zero and positive rotation direction;
- whether displayed orientation changes labels only or also editing commands;
- behavior outside image bounds.

## Numerical Policy

- Use double precision for transforms, geometry, and accumulated calculations.
- Preserve original points and recompute derived geometry; avoid repeated destructive transforms.
- Compare using a scale-aware tolerance appropriate to the operation.
- Detect singular and near-singular transforms before inversion.
- Normalize angles at a documented boundary.
- Reject or explicitly represent degenerate lines, polygons, and ROIs.
- Delay integer conversion until raster sampling, array indexing, or device-pixel output.

Test round trips with representative and extreme points:

```text
I ≈ view_to_image(image_to_view(I))
V ≈ image_to_view(view_to_image(V))
```

## Domain Model

Prefer data models independent of rendering:

```text
Annotation
  id
  kind
  geometry in Image space
  style reference
  label/metadata
  visibility, locked

RegionOfInterest
  geometry
  sampling/boundary semantics
  optional mask or operation metadata
```

Persist the geometry, its coordinate convention, and any schema version needed to interpret it. Keep hover state, edit handles, viewport transforms, and render caches transient.

## Keep Optional Semantics Behind a Seam

The core editor owns image-space geometry. Keep physical units, calibration, measurement validity, and accuracy claims outside this model.

When a request activates the metrology branch, pass an immutable geometry snapshot across its seam and receive a derived result. The optional module may reference core geometry by stable ID and revision, but it must not mutate that geometry or make the viewport transform authoritative for physical meaning.
