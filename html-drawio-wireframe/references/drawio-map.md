# HTML → draw.io map

Read this only when you change the exporter, read a draw.io file the user drew by hand, or draw directly in draw.io.

The style names below are the keys of `STYLES` in `scripts/wireframe2drawio.py`, and the strings are the same. Change both together. The `mxgraph.mockup.*` strings come from draw.io's own palette source (`jgraph/drawio`, `src/main/webapp/js/diagramly/sidebar/Sidebar-Mockup.js`), with the colours changed to grey. Mockup shape names written from memory often do not exist and render as empty boxes, so do not invent new ones. Copy a new one from that file and open it in draw.io before you use it.

## File layout

- **Pages:** one page per size × state, named `mobile / ready`, `desktop / ready` and so on. The diagram id is the name as a slug (`mobile-ready`).
- **Layers, bottom to top:**
  - `wireframe`: cell `_layer-wireframe`, style `locked=1;`.
  - `標註`: cell `_layer-annotation`.
  - `我的註記`: cell `_layer-notes`.
  - A layer is `<mxCell id="…" value="<name>" parent="0"/>`.
- **Geometry:**
  - The screen starts at (40, 70). Cell `_frame` is the screen outline.
  - `_title` is the page title at y = 30.
  - `_notes-list` is the numbered notes, 280 wide, 40 px right of the frame.
  - All cells sit directly on their layer with absolute coordinates, without nested groups. 1 CSS px = 1 draw.io unit, measured in the browser.
- **Cell ids:**
  - An element with a `data-id` keeps it as its cell id.
  - An element without one gets `<nearest data-id>~<tag><n>`, for example `post-card-2~div2~h31`. The part before the first `~` is always the nearest data-id, or `root`.
  - Derived cells:

    | Cell id | What it is |
    |---|---|
    | `<id>~b0` … `<id>~b3` | border lines (top, right, bottom, left) |
    | `<id>~dot` | radio dot |
    | `_n<note>~<id>` | note badge |
    | `_l~<id>` | id label (`--labels`) |

  - Ids that start with `_` belong to the generator.
- **Re-export:** Everything on `wireframe` and `標註` is regenerated. Cells on `我的註記` are copied to the page with the same name. Their `source`/`target` keep working because the ids are stable. A reference to an id that no longer exists is removed, and the exporter warns. The reader also accepts compressed `<diagram>` content and `<object>` / `<UserObject>` wrappers, which draw.io writes when a cell has data.

## Element → shape (export)

| HTML | Style | Added per cell |
|---|---|---|
| `button` | `button` | Normal: stroke `#666666`, fill `#ffffff`. Selected (`aria-pressed`, `aria-current`, `aria-selected`) or `.primary`: `#333333` with white text. `disabled`: stroke `#bbbbbb`, fill `#eeeeee`, text `#999999`. |
| `input` (text, email, url, tel, number, date …) | `textbox` | `verticalAlign=middle`. Text `#888888` when only a placeholder is shown. |
| `input type=search` | `search` | Same colour rule as `textbox`. |
| `input type=password` | `password` | The label is dots. |
| `textarea` | `textbox` | `verticalAlign=top`, `spacingTop` from padding, line breaks kept. |
| `select` | `select` | The label is the selected option. |
| `input type=checkbox` | `checkbox` / `checkbox-on` | Choice depends on `checked`. |
| `input type=radio` | `radio` / `radio-on` + `radio-dot` | The dot is 60 % of the size, centred. |
| `.img` | `image` | |
| `.icon` | `icon` | |
| `.skel` | `skeleton` | `arcSize=50` up to 16 px tall, else `8`. |
| `.chip` | `chip` | Fill and stroke like `button`; the text is the label. |
| Leaf text (`h1`–`h3`, `p`, `span`, `a`, `label`, `small`, `li`, `td`, `th` …) | `text` | `align` from `text-align`; font size, colour, bold, italic and underline from the browser. One line: `whiteSpace=nowrap`. Several lines: `whiteSpace=wrap`, 6 px wider. |
| Element with a full border or a non-white background | `box` | `fillColor` and `strokeColor` from the browser. With text: `align` and `spacing*` from the padding. |
| Element with 1–3 border sides (the page header) | `rule` | One 1 px filled rectangle per side. |
| `hr` | `rule` | |
| Container with a `data-id` and nothing visible | `box` | `fillColor=none;strokeColor=none;`: an anchor for arrows and `--read-notes`. |
| `img`, `svg`, `canvas`, `video`, `iframe` …, or an unsupported `input` type | `unsupported` | The label is `<tag>`. The exporter warns. |
| `data-note` | `badge` (標註) | At (x − 9, y − 9), 20 px apart for several notes. |
| Page title, notes list, `--labels` | `title`, `notes`, `id-label` (標註) | |

Every label is HTML (`html=1`), escaped, with `<br>` for line breaks. Fonts are `fontFamily=Helvetica`. The template also uses Helvetica, then Arial, so text widths match. Chinese text falls back to a system font on both sides and can differ by a few pixels.

## Style strings

```text
frame        rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;
box          rounded=0;whiteSpace=wrap;html=1;
rule         rounded=0;html=1;strokeColor=none;
text         text;html=1;strokeColor=none;fillColor=none;spacing=0;
button       html=1;shadow=0;dashed=0;align=center;strokeWidth=1;shape=mxgraph.mockup.buttons.button;mainText=;buttonStyle=round;whiteSpace=wrap;
textbox      html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.text.textBox;strokeColor=#999999;mainText=;align=left;spacingLeft=4;whiteSpace=wrap;
search       html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.searchBox;strokeColor=#999999;mainText=;strokeColor2=#666666;align=left;spacingLeft=3;whiteSpace=wrap;
password     html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.pwField;strokeColor=#999999;mainText=;align=left;spacingLeft=3;
select       html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.comboBox;strokeColor=#999999;fillColor=#f0f0f0;fillColor2=#cccccc;mainText=;align=left;spacingLeft=4;
checkbox     html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.rrect;rSize=0;fillColor=#eeeeee;strokeColor=#999999;gradientColor=#cccccc;
checkbox-on  html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.checkbox;fillColor=#aaaaaa;gradientColor=#666666;strokeColor=#444444;
radio        html=1;shadow=0;shape=ellipse;fillColor=#eeeeee;strokeColor=#999999;gradientColor=#cccccc;
radio-on     html=1;shadow=0;shape=ellipse;fillColor=#aaaaaa;gradientColor=#666666;strokeColor=#444444;
radio-dot    html=1;shape=ellipse;fillColor=#444444;strokeColor=none;
image        html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.graphics.simpleIcon;strokeColor=#999999;fillColor=#eeeeee;
icon         ellipse;whiteSpace=wrap;html=1;fillColor=#cccccc;strokeColor=#999999;
skeleton     rounded=1;whiteSpace=wrap;html=1;fillColor=#e2e2e2;strokeColor=none;
chip         rounded=1;arcSize=50;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacing=0;
unsupported  rounded=0;whiteSpace=wrap;html=1;dashed=1;fillColor=none;strokeColor=#d4380d;fontColor=#d4380d;fontSize=11;
badge        ellipse;whiteSpace=wrap;html=1;fillColor=#d4380d;strokeColor=#ffffff;fontColor=#ffffff;fontSize=10;fontStyle=1;spacing=0;
title        text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#333333;
notes        text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacing=6;fontSize=11;fontColor=#333333;strokeColor=#d4380d;fillColor=#fff8f0;
id-label     text;html=1;fontSize=8;fontColor=#8a8a8a;align=left;verticalAlign=top;spacing=0;strokeColor=none;fillColor=none;
```

When you append keys to a style, a key that comes later replaces an earlier one. For example, `button` followed by `strokeColor=#333333;fillColor=#333333;fontColor=#ffffff;` is a selected button.

## Reading a hand-drawn file (shape → HTML)

Use the style to decide what each shape stands for. Infer nesting from containment, and merge pages that show the same screen in another size or state. Record every guess as a note.

| Shape in draw.io (style contains …) | HTML |
|---|---|
| `mockup.buttons.button`, `mockup.buttons.multiButton`, or a small rounded rectangle with short centred text | `button`; a dark fill means `.primary` or a selected toggle |
| `mockup.text.textBox`, `mockup.forms.rrect` wider than tall | `input`; taller than about 50 px means `textarea` |
| `mockup.forms.searchBox` | `input type="search"` |
| `mockup.forms.pwField` | `input type="password"` |
| `mockup.forms.comboBox` | `select` |
| `mockup.forms.checkbox`, or a 15 px square `forms.rrect` with a label on its right | `input type="checkbox"` (checked / not checked) |
| Small ellipse with a label on its right (`labelPosition=right`) | `input type="radio"` |
| `mockup.graphics.simpleIcon`, a rectangle with an X, or any picture or chart shape | `.img`, plus a note on what it shows |
| Small circle without text | `.icon` |
| Pill (`rounded=1`, `arcSize` 40 or more) with short text | `.chip`; a dark fill means selected |
| Light grey bar without text | `.skel` (state `loading`) |
| `mockup.containers.browserWindow` or another outer frame | The screen itself; its width tells mobile (< 640) from desktop |
| Rectangle that holds other shapes | `section`, `article`, `nav`, `header`, `form` or `.box`, by position and content |
| `text` | `h1` (about 20 px or more, bold), `h2` / `h3` (16–19 px), else `p`, `span`, `label` or `small` |
| Horizontal line (`shape=line`, `mockup.markup.line`, or a 1–2 px tall rectangle) | `hr`, or the border of a header or footer |
| Grid of cells, `swimlane` / table shapes | `table` |
| `stickyNote`, `shape=note`, callouts | A note for `#notes`, not part of the screen |
| Sliders, progress bars, maps, video players and other mockup widgets | `.img` placeholder plus a note, or a real control if one fits |

## Drawing directly in draw.io

Do this only when the user asks for a hand-editable sketch.

- **Pages:** one page per size × state, named like the exporter's pages. Use a 10 px grid (`gridSize=10`) and frames 375 (mobile) and 1024 (desktop) wide.
- **Styles:** only the strings above. Put the visible text in the cell value; a placeholder uses `fontColor=#888888`.
- **Groups:** group the shapes of one block (Ctrl+G) and name the group in its tooltip or label with the block's id-style name (`result-bar`). Then the user can refer to it.
- **Layers:** `wireframe` for the screen, `我的註記` empty for the user, so that `wireframe2drawio.py FILE.drawio --read-notes` works on it too.
- **Handover:** mention once that the HTML route is easier to change and to check.

## What does not carry over

- Hover, focus, animation and scrolling. States must be explicit `data-when` states.
- Clipping. A child clipped by `overflow: hidden` is exported at its full size, so avoid clipping content in a wireframe.
- Shadows, gradients and real images. A wireframe does not need them.
