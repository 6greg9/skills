---
name: wpf-industrial-brutalist-ui
description: Design or redesign rigid, high-contrast WPF interfaces inspired by Swiss industrial print, machinery controls, technical manuals, and tactical telemetry. Use for WPF/XAML operator consoles, engineering tools, factory or laboratory workstations, dense monitoring dashboards, technical editors, or desktop interfaces that need square geometry, visible grids, mechanical typography, explicit status, and minimal decoration. Preserve usability, accessibility, and the project's existing architecture.
---

# WPF Industrial Brutalist UI

Build disciplined mechanical interfaces, not decorative military cosplay. Make structure visible, data legible, and state unmistakable. Preserve the existing WPF toolkit, bindings, commands, automation identifiers, and operating workflows.

## Choose one visual mode

Select one mode from the brief and use it across the entire surface.

### Swiss Industrial

Use a light, print-like substrate with heavy sans-serif headings, carbon-black structure, asymmetric type scale, and one hazard-red accent. Favor technical manuals, machine documentation, editors, and strongly branded tools.

Suggested starting palette:

- canvas: `#F2F1EC` or `#E9E7E1`;
- foreground: `#111111`;
- secondary text: `#555550`;
- structural border: `#111111`;
- accent and alarm: `#E31B23`.

### Tactical Telemetry

Use a dark, dense instrumentation surface with monospaced data, compact labels, strict compartments, and direct status reporting. Favor live monitoring, diagnostics, laboratory tools, and operator consoles.

Suggested starting palette:

- canvas: `#101010`;
- surface: `#171717`;
- foreground: `#E8E8E4`;
- secondary text: `#A6A69F`;
- structural border: `#555550`;
- alarm: `#FF3038`.

Use green, amber, or cyan only for defined states. Do not turn terminal green into the general text color.

Do not mix light print panels and dark terminal panels merely for visual interest. A separate diagnostic view may use another mode only when it is clearly a different operational context.

Before editing, state:

> Reading this as: `<Swiss industrial or tactical telemetry>` for `<operator and task>`, prioritizing `<critical data or action>` at `<density>`.

## Define hard-edged resources

Centralize theme values in `ResourceDictionary` files.

- Use `DynamicResource` for theme-dependent brushes.
- Use a short spacing scale based on 4 DIPs.
- Use square corners. Set general corner radius to 0.
- Use 1-DIP borders for normal structure and 2-DIP borders for active focus, selection, or alarm emphasis.
- Use no gradients, blur, glass, translucent panels, or soft consumer-style shadows.
- Enable layout rounding and pixel snapping so grid lines render cleanly.
- Keep one accent or alarm family. Do not scatter unrelated saturated colors.

Do not use `AllowsTransparency="True"` just to remove standard chrome. Retain native window behavior unless the user explicitly requests a custom title bar and the implementation preserves resizing, system commands, DPI behavior, and accessibility.

## Use typography as structure

Use two roles:

- **Structural sans:** heavy or semibold Windows-compatible sans for titles, zone numbers, and major actions.
- **Technical mono:** the existing monospace family, Cascadia Mono, or Consolas for telemetry, identifiers, coordinates, measurements, logs, and keyboard shortcuts.

Apply these limits:

- Reserve uppercase and wide tracking for short labels, status codes, and section markers.
- Keep instructions, messages, and body copy in normal casing.
- Use large numerals only when they communicate a primary reading or zone identity.
- Align numeric values and units consistently.
- Never make operational data tiny to imitate a terminal.
- Do not add an unlicensed display font or font file.

## Engineer the layout

- Use `Grid` as the primary layout system.
- Make major zones explicit with full-width dividers, aligned tracks, and visible boundaries.
- Use `SharedSizeGroup` for repeated labels, units, and property values.
- Use `GridSplitter` only where operators benefit from adjustable work areas.
- Alternate dense data regions with deliberate breathing room around the most important reading or action.
- Avoid floating cards. Treat the window as one engineered instrument divided into functional compartments.
- Avoid `Canvas` for normal layout. Use it only for genuine schematics, plots, crosshairs, or spatial overlays.
- Support resizing, minimum dimensions, high-DPI scaling, and intentional scrolling.

Do not add random barcodes, registration marks, crosshairs, coordinates, revision strings, or hazard stripes. Use industrial markers only when they label real zones, versions, equipment, or safety states.

## Design operational components

### Commands and navigation

- Use rectangular buttons with strong borders and direct labels.
- Make the primary action unmistakable without making every action red.
- Separate destructive and emergency actions from routine commands.
- Show selected navigation through border weight, inversion, or a single accent edge.
- Use one geometric icon family. Do not use emoji or decorative ASCII as icon replacements.

### Data and telemetry

- Keep `DataGrid` rows compact but readable, normally 28-34 DIPs.
- Use visible column structure where comparison matters.
- Align numbers, timestamps, units, and identifiers predictably.
- Distinguish selected, stale, invalid, acknowledged, and alarmed data.
- Do not fabricate telemetry, serial numbers, coordinates, or machine status for visual texture.

### Inputs and controls

- Give inputs visible boundaries and strong keyboard focus.
- Keep labels persistent; do not depend on placeholder text.
- Place units beside numeric inputs.
- Use segmented controls, toggle buttons, progress bars, and gauges only when their state is immediately readable.
- Show validation beside the affected field and explain recovery.

### Status and alarms

Define a small semantic state set such as:

- normal;
- attention;
- alarm;
- offline;
- unknown.

Give each state a text label or icon in addition to color. Reserve flashing for an active, time-critical alarm, respect system animation preferences, and stop flashing after acknowledgement when the domain allows it.

## Keep effects subordinate

Use analog texture only when the user explicitly asks for it.

- Keep scanlines, noise, dithering, and phosphor glow out of text and data regions.
- Use a single static, low-opacity overlay instead of per-control effects.
- Do not apply expensive effects to scrolling containers.
- Prefer preprocessed image assets over runtime bitmap effects.
- Verify that texture does not reduce contrast or create moire at high DPI.

Use almost no motion. Limit state transitions to short opacity or `RenderTransform` changes. Do not animate layout, run ambient loops, or stagger the appearance of operational data.

## Cover complete states

Implement and inspect:

- default, pointer-over, pressed, keyboard-focus, disabled, and selected controls;
- connected, disconnected, loading, stale, empty, error, and no-data surfaces as applicable;
- normal, attention, alarm, acknowledged, offline, and unknown status;
- light or dark theme variants only when the product actually supports both;
- keyboard-only navigation and screen-reader names for icon-only controls.

Do not sacrifice discoverability or safety to maintain the visual style.

## Reject brutalist failure modes

Do not ship:

- all-uppercase body text;
- tiny low-contrast terminal text;
- hazard red on routine content;
- thick borders around every nested element;
- fake military language or meaningless machine identifiers;
- CRT effects over tables, forms, or logs;
- broken resize behavior presented as intentional brutalism;
- unlabeled symbols that operators must guess;
- decorative alarms or blinking;
- an interface that looks harsh but hides state or hierarchy.

Industrial brutalism should feel engineered, not broken.

## Verify the real window

Run:

```powershell
dotnet build
```

Launch and inspect the application when possible. Check normal and narrow window sizes, high-DPI scaling, grid-line sharpness, keyboard focus, text clipping, dense data readability, alarm contrast, scrolling performance, and every operational state affected by the change.

Do not claim visual verification when the window could not be observed. Report the build result, the mode selected, the sizes inspected, and any state that remains unverified.
