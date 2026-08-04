# Measurements and Spectrum Analysis

## Contents

- Measurement contract
- Cursor and region measurements
- Statistical measurements
- Frequency-domain analysis
- Derived-signal provenance
- Presentation

## Define the Measurement Contract

Every result must identify:

- source acquisition/channel and revision;
- raw or derived signal;
- exact interval/sample selection and boundary convention;
- calibration and unit;
- quality/gap handling;
- algorithm, parameters, and version where reportability matters;
- validity, warnings, and optional uncertainty.

Compute from raw or declared analysis data. Never read values back from screen pixels or an opaque display-decimated series.

## Implement Cursor Measurements

Keep cursor positions in stable time/value coordinates. Render their handles in view space.

Common results include:

- time cursors: `tA`, `tB`, `Δt = tB - tA`;
- reciprocal: `f = 1 / |Δt|`, invalid when `Δt` is zero or below a justified resolution;
- voltage/value cursors: `yA`, `yB`, `Δy`;
- intersection/sample readout with interpolation policy stated;
- phase difference only with frequency/reference semantics defined.

Distinguish a free cursor from one snapped to a sample, peak, edge, zero crossing, or derived feature. Display the snap target and source channel.

## Define Region Statistics

Specify whether interval boundaries are closed, open, or half-open and how irregular timestamps are weighted. Handle gaps and invalid samples explicitly.

For samples `x_i`, define the intended variants:

- mean;
- minimum, maximum, peak-to-peak;
- total RMS `sqrt(mean(x_i^2))`;
- AC RMS after subtracting the declared mean/trend;
- standard deviation with population/sample convention;
- integral/area using the correct time spacing;
- duty cycle, pulse width, rise/fall time, overshoot, or domain metrics with threshold rules.

Do not treat sample count as duration for irregular data. Do not format more significant digits than the acquisition/calibration justifies.

## Make FFT and Spectrum Semantics Explicit

Before computing a discrete FFT, require:

- uniform sample spacing or an explicit resampling/nonuniform method;
- effective sample rate and clock provenance;
- selected time interval and sample count `N`;
- gap/invalid-sample policy;
- DC removal or detrending choice;
- window function and its coherent/noise gain treatment;
- one-sided or two-sided output;
- amplitude, power, PSD, ASD, dB, or other normalization;
- output unit and reference for logarithmic scales.

Use frequency bins derived from the effective sample rate and `N`. Respect the Nyquist limit. Treat zero padding as denser spectral interpolation, not improved physical resolution. Explain spectral leakage and window tradeoffs when they affect interpretation.

Do not apply an ordinary FFT directly to irregular timestamps without a declared conversion or suitable alternative. Do not bridge gaps as if samples were continuous.

Keep FFT display reduction separate from FFT computation. For large spectra, use a reduction appropriate to magnitude/power semantics and preserve narrow peaks required by the product.

## Track Derived Signals

For filtering, resampling, demodulation, differentiation, integration, envelope, or channel math, record:

- source revisions;
- operation graph and parameters;
- causal/noncausal behavior;
- phase/group delay;
- boundary/transient behavior;
- output sample/time mapping;
- output unit and quality propagation.

Show delay or alignment effects when comparing raw and processed traces. Reject stale results after source or parameter revision changes.

## Present Results Honestly

Label approximate, incomplete, clipped, gapped, saturated, or low-confidence results. Include a path to the source region and settings. Keep preview measurements visually distinct from committed/reportable results.

Export measurement definitions and provenance with values when reproducibility matters. UI agreement with a formula does not establish sensor, clock, or calibration accuracy.
