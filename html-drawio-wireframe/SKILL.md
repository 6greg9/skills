---
name: html-drawio-wireframe
description: Low-fidelity UI wireframes as one self-contained HTML file per screen (semantic tags, mobile and desktop frames side by side, ready/loading/empty/error states, numbered notes), checked by script and exported to a multi-page draw.io file built from verified mockup shapes, plus a text layout tree. Use whenever the user wants a wireframe, low-fi mockup, screen sketch or page layout draft (線框圖、wireframe、畫面草稿、版面配置、低保真), wants a wireframe to open or annotate in draw.io / diagrams.net, sends draw.io notes, a sketch or a screenshot to apply to a wireframe, or asks for a screen's layout tree or component tree before coding, even if they only say "sketch the page" or "what should this screen look like". Not for polished visual design, brand styling or production UI code.
---

# HTML → draw.io wireframes

One HTML file per screen is the source of truth. A browser renders it in both sizes and every state. A script converts it to draw.io by measuring what the browser laid out, so no coordinate is ever guessed, and the markup ports almost directly into components later. The draw.io file is a generated, read-only snapshot for annotating and sharing; changes always go into the HTML.

Paths below are relative to this skill's directory.

| File | Use |
|---|---|
| `assets/template.html` | Starting point for every wireframe. Contains a worked example (an article search page) and, in its header comment, the authoring rules. Read that comment before writing. |
| `scripts/check_wireframe.py` | Rule check plus one screenshot per state. Run it after every edit. |
| `scripts/wireframe2drawio.py` | Export to `.generated.drawio` and `.tree.txt`; `--read-notes` reads the user's draw.io annotations. |
| `references/drawio-map.md` | HTML → draw.io mapping and verified style strings. Read it only when changing the export or drawing directly in draw.io. |

The scripts need Python 3.9+ and Playwright (`pip install playwright && playwright install chromium`). On a PC that cannot download Chromium, skip `playwright install` and add `--browser chrome` or `--browser msedge` to use an installed browser. `--read-notes` needs only Python.

## Making a wireframe

1. **Understand the screen.** From the spec or the conversation, pin down what the screen is for, what content and controls it has, which states it needs, and what differs on mobile. Default states are ready, loading, empty and error; add others such as `submitting` or `menu-open` when an interaction changes the layout. If something would change the structure and can't be inferred, ask. Otherwise make a reasonable call and record it as a numbered note, so the assumption is visible.
2. **Copy the template** next to the spec: `specs/mockups/NNN-name.html` if the project has a `specs/` folder, otherwise wherever the user wants it. Replace the example content completely: `<title>`, the toolbar title, `<template id="screen">`, `<style id="screen-style">`, `#notes` and `<body data-states>`. Leave the base styles and the script alone; the checker and the exporter depend on them.
3. **Write the screen following the header rules.** Each rule exists because of how the file is used later:
   - Real tags (`button`, `input`, `nav`, `article`, `table` …): the exporter maps tags to draw.io shapes, and the markup becomes component code.
   - Only the small class kit (`row col grow … img icon skel chip box`) plus layout-only classes defined in `screen-style`: this keeps it low-fi, and every element maps to a known shape.
   - Text only in leaf elements: the exporter measures each text box, and text mixed with child elements can't be measured.
   - No absolute, fixed or sticky positioning, transforms or background images: what the browser measures must be what draw.io shows.
   - Sizes through `@container` (640px breakpoint, `mobile-only` / `desktop-only`), states through `data-when`: the exporter enumerates every size × state, and states driven by JS or hover would be invisible to it.
   - `data-id` on meaningful blocks: it becomes the stable draw.io cell id and the name the user can use in feedback ("move result-bar up").
   - Realistic data: the longest plausible title, missing fields, zero items and many items. A wireframe exists to expose layout problems, and tidy placeholder text hides them.
4. **Check, then look.** Run `python scripts/check_wireframe.py <file> --shots <tmp-dir>` and fix every error. Then view each screenshot. The script catches rule violations, not bad layouts, so look for cramped or empty areas, misalignment, states that don't read clearly, and mobile layouts that are just a squeezed desktop.
5. **Hand it over.** Give the path and mention that it opens directly in a browser, where the toolbar switches state, size and notes. List the notes that are open questions. For alternatives, make separate files (`-b`, `-c`) with genuinely different layouts, not cosmetic variations.

## Exporting to draw.io

`python scripts/wireframe2drawio.py <file.html>` writes two files next to the HTML:

- `<name>.generated.drawio`: one page per size × state (`mobile / ready` …), with the layers `wireframe` (locked), `標註` and `我的註記`.
- `<name>.tree.txt`: the layout tree.

Re-run it after every HTML change. Anything the user drew on the `我的註記` layer survives re-export and everything else is regenerated, so never hand-edit the generated file. Warnings printed by the exporter are rule violations; fix them in the HTML.

## Applying feedback

- **From draw.io:** run `python scripts/wireframe2drawio.py <file.html> --read-notes` (or pass the `.drawio` file directly). It lists every note, sticky, text or arrow on the `我的註記` layer of each page, with the `data-id`s it covers or points at. Apply the changes to the HTML, check, re-export. If a note can't be interpreted, say so instead of guessing.
- **From a screenshot, sketch or chat message:** the same loop. Edit the HTML, check, and re-export if a draw.io file exists.
- **From a draw.io file the user drew by hand (not generated):** treat it as a sketch. Read the shapes (the mapping table in `references/drawio-map.md`, read in reverse, says what each mockup shape stands for), infer nesting from containment, and merge pages that show the same screen in another size or state. Then build a fresh wireframe from the template, and record every interpretation you weren't sure of as a note.

## Layout tree and component tree

The layout tree (`.tree.txt`) is generated. Paste it into the spec or use it to review structure; don't write one by hand.

A component tree is a design decision, so propose one and let the user decide. Derive it from the wireframe: which components, their props, and which component owns which state. Call out two things the layout tree hides: blocks that are really one component in different sizes (a tag filter shown as a row on mobile and a sidebar on desktop), and which component switches between the states.

```text
SearchPage            state: query, tag, status, posts
├─ SearchBox          props: value, onChange
├─ TagFilter          props: tags, selected, onSelect, layout("row" | "column")
└─ ResultList         props: status, posts, onRetry, onClear
   ├─ PostCard ×N
   ├─ EmptyState
   └─ ErrorState
```

If the project's spec template has a 元件樹 section, put it there.

## Drawing directly in draw.io

Do this only when the user explicitly wants a hand-editable draw.io sketch instead of an HTML wireframe. Use only the style strings in `references/drawio-map.md`; mockup shape names written from memory often don't exist and render as empty boxes. Use one page per size × state, a 10px grid, and groups for related shapes. Mention briefly that the HTML route is easier to iterate on.
