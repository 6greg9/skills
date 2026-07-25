---
name: wpf-design-taste
description: Design, build, or refine polished WPF desktop interfaces that avoid generic template styling. Use for WPF/XAML windows, pages, dialogs, dashboards, settings screens, control styling, theme resources, visual redesigns, and UI polish in native WPF or an existing WPF control library. Preserve the project's architecture and design system unless the user asks to change them.
---

# WPF Design Taste

Create a coherent desktop interface from the product brief instead of decorating a default WPF layout. Keep the process small: read the app, choose a direction, establish tokens, implement complete states, and inspect the running window.

## Read the app before styling

1. Inspect the project files, target framework, `App.xaml`, merged resource dictionaries, main shell, representative views, and installed UI packages.
2. Identify the current architecture and control system: native WPF, MaterialDesignInXaml, WPF UI/Fluent, MahApps, HandyControl, or a custom library.
3. Reuse one established system. Do not mix control libraries or introduce a new one merely to make the UI look modern.
4. For a redesign, preserve working behavior, bindings, commands, automation identifiers, and keyboard flows.
5. Ask one concise question only when the visual direction genuinely cannot be inferred.

Before editing, state one line:

> Reading this as: `<surface>` for `<audience>`, with a `<visual language>` direction, using `<existing toolkit or native WPF>`.

## Establish a small visual system

Make four decisions and use them consistently:

- **Hierarchy:** Decide what must be noticed first, second, and last.
- **Density:** Choose spacious, balanced, or operational. Desktop tools may be dense without becoming cramped.
- **Geometry:** Choose one corner-radius family and one control-height scale.
- **Color:** Use neutral surfaces plus one accent family unless the product already has brand colors.

Centralize reusable values in `ResourceDictionary` files:

- theme brushes for window, surface, border, primary text, secondary text, accent, success, warning, and danger;
- spacing values based on a short scale such as 4, 8, 12, 16, 24, and 32;
- no more than three general corner radii;
- typography roles for page title, section title, body, label, and caption;
- shared styles for repeated controls.

Use `DynamicResource` for brushes that change with the theme. Use fixed colors only when they are deliberate brand constants. Keep light and dark theme values in separate dictionaries when both themes exist.

## Compose the interface

- Use `Grid` for page structure and alignment. Use `StackPanel` only for simple one-dimensional groups.
- Prefer alignment, whitespace, separators, and typography before adding containers.
- Use cards only when a raised or bounded region communicates real grouping. Do not wrap every section in a rounded rectangle.
- Keep primary actions visually dominant and place destructive actions away from routine actions.
- Align labels, fields, icons, and baselines deliberately. Use `SharedSizeGroup` for repeated form or property layouts.
- Support resizing with sensible `MinWidth`, `MaxWidth`, star sizing, and scrolling. Avoid `Canvas` or absolute positioning for normal application layout.
- Use one icon family already present in the project. Do not use emoji or font-dependent Unicode symbols as interface icons.
- Keep animation rare and functional. Prefer short opacity or transform transitions; avoid continuous motion and layout-property animation.

## Style controls as a family

Design repeated controls together, not one at a time:

- buttons: primary, secondary, quiet, and destructive;
- text inputs, selectors, toggles, and validation messages;
- navigation items and selected states;
- lists, tables, and empty rows;
- dialogs, flyouts, and notifications.

For every interactive control, cover:

- default;
- pointer over;
- pressed;
- keyboard focus;
- disabled;
- selected or checked when applicable;
- validation error when applicable.

Keep focus visible. Preserve access keys and keyboard navigation. Use automation names for icon-only actions. Do not convey state by color alone.

## Avoid recognizable AI defaults

Do not ship:

- purple-blue glow or gradient styling without a brand reason;
- a sample-dashboard layout with identical metric cards as the automatic answer;
- excessive shadows, pills, glass effects, or rounded containers;
- hard-coded light backgrounds or dark text that break theme switching;
- low-contrast secondary text;
- oversized headings that waste desktop workspace;
- arbitrary font changes when Segoe UI or the existing family fits the product;
- polished success states with missing loading, empty, error, or validation states.

The goal is not maximal novelty. Make the interface specific to its users, information, and operating context.

## Work with existing libraries

- Follow the package version and resource keys already installed; verify them before referencing new keys.
- Use the library's official controls and theme resources instead of imitating its appearance by hand.
- Customize through a thin token and style layer. Avoid replacing every control template unless the brief requires a strongly bespoke product.
- Add a dependency only when it provides a coherent design system or a required control, not for a single decorative effect.

If the task also requires a MaterialDesignInXaml MVVM shell and `$wpf-materialdesign-mvvm` is available, use that skill for architecture and this skill for visual decisions.

## Redesign in impact order

For an existing screen:

1. Capture or inspect the current UI before changing it.
2. Name the three highest-impact problems, usually hierarchy, spacing, density, contrast, or state clarity.
3. Fix tokens and page structure before polishing individual controls.
4. Reuse the improved styles across the affected surface.
5. Keep the redesign inside the requested scope.

## Verify before finishing

Run the relevant build and tests, at minimum:

```powershell
dotnet build
```

Launch the app and inspect the real window when the environment permits. Check:

- normal and narrow window sizes;
- 100% and high-DPI scaling when available;
- light and dark themes when supported;
- keyboard-only navigation and visible focus;
- text clipping, truncated labels, overlapping controls, and unwanted scrollbars;
- loading, empty, error, disabled, and validation states that the screen supports;
- contrast and readability of text, icons, and actions.

Do not claim visual verification if the window could not be launched or observed. Report what was built, what was visually checked, and any remaining unverified state.
