# Optional Calibration and Measurement

Load this reference only when the request requires physical units, calibration, image-to-world or stage mappings, reportable measurements, accuracy or uncertainty claims, or inspection pass/fail decisions. Pixel-only annotation and ROI editing stay in the core model.

## Contents

- Activate the branch
- Define the seam
- Represent calibration
- Calculate measurements
- Preserve result identity
- Prove the vertical slice
- Verify claims

## Activate the Branch

Determine:

- whether results are display aids, reportable measurements, or pass/fail inputs;
- the required physical frame, units, measurands, and allowed claims;
- the image or acquisition artifact that results must reference;
- the calibration source, applicability, revision, and validity;
- the required accuracy, uncertainty, and evidence.

State unresolved items as assumptions or blockers. Do not invent calibration values, accuracy targets, uncertainty, or regulatory suitability.

This branch is ready only when the intended result and the evidence required to trust it are explicit.

## Define the Seam

Keep the static editor authoritative for image-space geometry. Let a separate measurement module consume immutable snapshots:

```text
GeometrySnapshot
  annotation_id
  geometry_revision
  geometry in Image space
  source_artifact_id and revision

MeasurementContext
  requested measurand
  calibration snapshot
  target physical frame

MeasurementResult
  value and unit
  geometry, source, and calibration revisions
  method and version
  validity status
  uncertainty when required by the claim
```

Return results rather than mutating annotations. Associate a result with stable IDs and revisions so callers can detect stale data.

Use separate pixel and calibrated adapters only when both behaviors are real product requirements. Do not add a speculative measurement interface to a pixel-only editor.

## Represent Calibration

Represent calibration as versioned data, not formatted text or viewport scale:

```text
CalibrationSnapshot
  id and revision
  mapping: Image -> named physical frame
  unit
  provenance and timestamp
  device, objective, or configuration applicability
  validity region and status
  uncertainty model or explicit unknown status
```

Keep image-to-physical calibration separate from image-to-view navigation. Add lens distortion or another non-affine mapping as an explicit stage rather than hiding it inside an affine matrix.

Bind every reported result to the exact calibration revision used. Recalculation creates a new result; it does not silently rewrite a historical result.

## Calculate Measurements

Calculate in the named physical frame:

- distance: length between mapped endpoints when the measurand is a point-to-point chord;
- polyline: sum physical segment lengths for affine mappings;
- angle: calculate between physical vectors when anisotropic scale or shear is possible;
- polygon area: use the shoelace formula on mapped vertices only for affine mappings;
- circle or ellipse: transform or fit the geometry in physical space rather than multiplying by one average scale.

For a non-affine mapping `F`, image-space straight edges may become physical curves. Define whether the measurand follows mapped boundaries or connects mapped vertices. Use the local Jacobian, numerical integration, or adaptive tessellation with a validated error bound; do not treat mapped vertices alone as a general nonlinear area solution.

Treat rulers and scale bars as view artifacts derived from the calibration and viewport. They are never calibration sources.

Format values at presentation time. Base reported precision on the source resolution and uncertainty, not on available floating-point digits.

## Preserve Result Identity

Persist semantic geometry independently from derived results. When results must survive for audit or export, persist:

- geometry, source, calibration, and method revisions;
- value, unit, validity, and uncertainty status;
- whether the result is current, stale, superseded, recomputed, or invalid.

Without a valid calibration, report pixels or pixel-squared values and label them explicitly. Never substitute a nominal pixel size silently.

## Prove the Vertical Slice

After the core image/ROI slice passes:

1. Supply one versioned calibration adapter.
2. Derive one line measurement from an immutable geometry snapshot.
3. Display the value without changing core geometry.
4. Change or invalidate the calibration and show the old result as stale.
5. Save and reload the geometry plus result provenance.
6. Verify the formula, units, revision binding, and invalid states.

Generalize to area, angle, stage coordinates, or pass/fail only after this slice works.

## Verify Claims

Separate software consistency from physical validity.

Test:

- affine, anisotropic, rotated, and reflected calibration fixtures;
- non-affine reference mappings and validity-region edges when supported;
- result invalidation after source, geometry, calibration, or method changes;
- absence of physical units when calibration is missing or invalid;
- serialization and reload of all result revisions;
- rounding and unit presentation independently from calculation precision.

An accuracy claim additionally requires documented calibration evidence, acquisition-system error and uncertainty, relevant distortion or field-position effects, repeatability/reproducibility evidence, and a defined reporting policy.

For decision-ready output, include the intended result, coordinate frames, calibration applicability, formulas, result schema, uncertainty or unknown status, acceptance evidence, and unresolved assumptions.
