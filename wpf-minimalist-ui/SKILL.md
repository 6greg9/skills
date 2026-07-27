---
name: wpf-minimalist-ui
description: Design or redesign restrained, editorial, information-first WPF interfaces with monochrome surfaces, precise typography, flat hierarchy, limited color, and minimal elevation. Use for minimalist WPF/XAML windows, productivity tools, settings and property panels, document-style apps, quiet premium desktop UI, Notion- or Linear-inspired layouts, or removing generic card-heavy styling from an existing WPF application.
---

# WPF Minimalist UI

Build calm desktop interfaces whose hierarchy comes from typography, alignment, spacing, and thin dividers rather than decoration. Keep the application recognizably Windows-native and preserve its existing architecture and control library.

## Read before designing

1. Inspect the shell, representative views, `App.xaml`, resource dictionaries, installed control packages, theme support, and current window behavior.
2. Identify the screen's primary job and the information users scan most often.
3. Preserve existing bindings, commands, validation, keyboard flows, automation identifiers, and window behavior during redesigns.
4. Reuse the current WPF toolkit. Do not add a second control library for aesthetic reasons.

State one direction line before editing:

> Reading this as: a `<surface>` where `<primary information or action>` leads, using a quiet `<warm or cool>` monochrome system at `<spacious, balanced, or operational>` density.

## Use a restrained token system

Define the palette and measurements in shared `ResourceDictionary` files.

Use these light-theme families as a starting point, then adapt them to the product:

- canvas: warm off-white around `#FBFBFA`;
- surface: white or a near-canvas neutral;
- primary text: charcoal around `#2F3437`, not absolute black;
- secondary text: muted gray around `#787774`;
- border: a quiet neutral around `#E7E7E4`;
- primary action: charcoal with white text;
- semantic colors: muted red, blue, green, and amber used only for meaning.

For dark mode, create a real dark dictionary rather than inverting colors. Use deep neutral surfaces, soft white text, restrained borders, and the same semantic meanings.

- Use `DynamicResource` for all theme-dependent brushes.
- Use one accent family and reserve it for selection, focus, links, or the primary action.
- Use spacing based on a short 4-DIP scale.
- Use corner radii of 0, 4, 6, or 8 DIPs. Reserve pill shapes for small tags or status badges.
- Avoid gradients, neon, glass effects, colored glows, and heavy shadows.
- Use no elevation by default. When separation cannot be expressed by spacing or a border, use one very soft shadow style.

## Build hierarchy with type

- Prefer the project's current system UI font. Use Segoe UI or an available Windows system family when no brand typeface exists.
- Do not introduce a serif or display font merely to signal premium design.
- Keep page titles compact, normally 20-28 DIPs. Desktop workspace is valuable.
- Use a small, stable hierarchy: page title, section title, body, label, and caption.
- Use weight and spacing before changing color or size.
- Keep secondary text readable; muted does not mean low contrast.
- Use a monospace family only for code, identifiers, measurements, or keyboard shortcuts.
- Enable layout rounding and pixel snapping where thin borders otherwise render softly.

## Compose flat desktop layouts

- Use `Grid` for page structure, forms, property rows, and aligned tool areas.
- Use `SharedSizeGroup` for repeated labels and values.
- Prefer whitespace, headings, and 1-DIP dividers over nested cards.
- Use a bordered container only when it represents a real object, selectable region, or independent scroll surface.
- Keep content margins deliberate: usually 24-32 DIPs for main views and 12-16 DIPs inside compact groups.
- Choose one density for the surface. Use 32-36 DIP controls for operational tools and 36-40 DIP controls for relaxed settings or document UI.
- Support window resizing with star sizing, sensible minimums, and a single intentional scrolling strategy.
- Keep navigation quiet. Indicate selection with a subtle background, text weight, or edge marker rather than a saturated block.

## Treat common controls consistently

### Actions

- Style one clear primary button with a solid near-black or brand-accent fill.
- Style secondary buttons as flat outlined or quiet text actions.
- Keep destructive actions visually separate and reveal strong danger color only where the risk matters.
- Avoid large pill buttons, shadows, and press animations that move surrounding layout.

### Inputs and forms

- Align labels and fields on a stable grid.
- Use quiet borders with a clear focus treatment.
- Place validation beside the field and explain how to recover.
- Avoid placeholder-only labels and avoid enclosing every field in an additional card.

### Lists and tables

- Use subtle row dividers or spacing; avoid decorative zebra striping unless it materially improves long-row tracking.
- Keep headers compact and visually quieter than the data.
- Use a restrained selection fill that preserves text contrast.
- Align numeric data consistently and expose sorting state clearly.

### Tags, shortcuts, and status

- Use small muted fills for tags and semantic status, with readable foreground colors.
- Render keyboard shortcuts as compact bordered keycaps using a monospace font.
- Use one existing icon family. Do not use emoji or font-dependent Unicode symbols as interface icons.

## Keep motion almost invisible

- Use no animation unless it explains state or preserves spatial continuity.
- Limit transitions to short opacity or `RenderTransform` changes, normally 120-180 ms.
- Avoid staggered reveals, ambient animation, bouncing, continuous loops, and layout-property animation.
- Disable nonessential animation when the system indicates that client-area animation is off.

## Cover complete states

Implement and visually check:

- default, pointer-over, pressed, keyboard-focus, and disabled control states;
- selected, checked, expanded, and validation states where applicable;
- loading, empty, error, and no-results states for data surfaces;
- visible focus and logical keyboard traversal;
- light and dark themes when supported.

Do not use color as the only signal. Give icon-only actions accessible names and tooltips.

## Reject minimalist clichés

Do not mistake minimalism for:

- hiding useful labels or commands;
- making all text gray and low contrast;
- surrounding every item with a rounded white card;
- filling empty space with oversized headings;
- reducing every action to an unlabeled icon;
- copying a macOS title bar onto a Windows application;
- removing borders that communicate focus, grouping, or input affordance;
- shipping attractive success states without operational states.

Remove decoration, not information.

## Verify the real window

Run:

```powershell
dotnet build
```

Launch and inspect the application when possible. Check normal and narrow window sizes, high-DPI scaling, keyboard-only operation, text clipping, baseline alignment, scroll behavior, light and dark themes, and every state the edited surface supports.

Do not claim visual verification when the window could not be observed. Report the build result, the sizes and themes inspected, and any state that remains unverified.
