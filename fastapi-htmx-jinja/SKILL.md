---
name: fastapi-htmx-jinja
description: Conventions for server-rendered web UIs on FastAPI/Starlette with Jinja2, jinja2-fragments and htmx 2.x - one template per feature with swappable blocks, page-vs-fragment routes, StrictUndefined contexts, forms with 422 validation errors, out-of-band swaps, polling and SSE via sse-starlette, CSRF, and tests. Use whenever writing, reviewing or debugging Jinja templates with hx-* attributes, FastAPI routes that return HTML or TemplateResponse, block or fragment rendering, htmx forms that do nothing on error, or SSE status panels, and when building a Python admin page, CRUD or recipe editor, or an MES or equipment status dashboard, even if htmx is not named yet. Not for SPA frontends or high-frequency graphics (use a JS island).
---

# FastAPI + Jinja2 + htmx

Opinionated conventions for server-rendered UIs on FastAPI. Status colors and alarm display on
equipment screens follow `industrial-hmi-style-guide`; if the project already has backend or
service-layer conventions, keep them and plug these routes on top.

Everything below was run and tested on 2026-10-14 with FastAPI 0.143, Starlette 1.8,
jinja2-fragments 1.12, sse-starlette 3.5 and Python 3.12.

## When to use / not use

Use for: admin and management screens, CRUD, recipe/parameter editors, lot/wafer/alarm history,
status panels that refresh a region every ~1s or slower.

Do NOT use for: high-frequency graphical views (many moving elements, robot/FOUP/wafer maps
animating, >2 Hz updates), canvas/SVG animation, heavy client-side state (drag-and-drop
scheduling, offline editing). Use a Vite + React/Svelte island fed by WebSocket JSON for those,
embedded in an otherwise htmx page.

## Pinned versions (state them in the project, never mix)

- htmx **2.0.x**, self-hosted in `static/vendor/` (no CDN: fab networks are often offline).
  htmx 4.x is a separate major line with breaking changes; do not copy 4.x syntax into a 2.x
  project. Upgrade only deliberately, via the official migration guide.
- htmx extensions (e.g. `htmx-ext-sse`) are **separate files** in 2.x, also self-hosted.
- `jinja2-fragments` for block rendering, `sse-starlette` for SSE, `python-multipart` for forms.
- Alpine.js 3 (optional) for purely local UI state.

## Project layout

```
app/
  main.py
  web.py                # templates object, is_htmx(), render(), render_block_str()
  routers/
    api/                # JSON, include in OpenAPI
    pages/              # HTML, APIRouter(include_in_schema=False)
  services/             # business logic shared by api/ and pages/
  templates/
    base.html
    ports/index.html    # full page; fragments are {% block %}s inside it
    components/macros.html   # badges, buttons, field rows with error display
  static/vendor/htmx.min.js, sse.js, alpine.min.js
```

Rule: one feature = one template file containing both the full page and its swappable blocks
(Locality of Behavior). The page route and its fragment routes live in the same router module.

## Core setup

```python
# app/web.py
from fastapi import Request
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from jinja2_fragments import render_block
from jinja2_fragments.fastapi import Jinja2Blocks

env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "jinja2"]),
    undefined=StrictUndefined,   # typos / missing context keys raise instead of rendering ""
)
# Macros as a global, used as {{ ui.status_badge(p) }}. A block rendered on its own does not
# see {% from ... import %} lines outside it, so top-of-template imports break fragments.
env.globals["ui"] = env.get_template("components/macros.html").module

def common_ctx(request: Request) -> dict:
    """Values base.html reads on every page."""
    return {"csrf_token": get_csrf_token(request)}   # the project's session/CSRF helper

templates = Jinja2Blocks(env=env, context_processors=[common_ctx])

def is_htmx(request: Request) -> bool:
    # History restores (cache miss) also send HX-Request: true but need the full page
    return (request.headers.get("HX-Request") == "true"
            and request.headers.get("HX-History-Restore-Request") != "true")

def render(request: Request, name: str, ctx: dict, block: str | list[str] | None = None,
           status_code: int = 200, headers: dict | None = None):
    """Full page normally; for htmx requests the named block, or several blocks in order."""
    kw = {}
    if block and is_htmx(request):
        kw = {"block_names": block} if isinstance(block, list) else {"block_name": block}
    resp = templates.TemplateResponse(request, name, ctx, status_code=status_code,
                                      headers=headers, **kw)
    resp.headers["Vary"] = "HX-Request"
    return resp

def render_block_str(name: str, block: str, **ctx) -> str:
    """Render one block to a string (for SSE). No request, no context processors."""
    return render_block(templates.env, name, block, **ctx)
```

```python
# app/main.py
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)                 # pages router: include_in_schema=False
app.include_router(api.router, prefix="/api")
```

**StrictUndefined is mandatory.** Default Jinja silently renders undefined variables as empty
strings, which hides AI mistakes. With StrictUndefined:
- Every route passes every key its template reads, including empty defaults (`"errors": {}`,
  `"form": {}`, `"oob": False`).
- Optional values use `{{ x | default('') }}` or `{% if x is defined %}`; plain
  `{% if form.name %}` on a missing key raises.
- Each context dict for a template is built by one helper function per feature (e.g.
  `recipe_ctx(...)`), so full-page and fragment routes cannot drift apart.
- Cross-cutting values that `base.html` reads (`csrf_token`, current user) come from a context
  processor `common_ctx(request) -> dict`, never passed by hand in each route.

`TemplateResponse(request, name, context, ...)`: request is the FIRST positional arg. The old
form `TemplateResponse(name, {"request": request, ...})` is deprecated; never generate it.

## base.html essentials

```html
<meta name="htmx-config" content='{
  "responseHandling": [
    {"code":"204","swap":false},
    {"code":"[23]..","swap":true},
    {"code":"422","swap":true},
    {"code":"[45]..","swap":false,"error":true},
    {"code":"...","swap":false}
  ]
}'>
<script src="{{ url_for('static', path='vendor/htmx.min.js') }}" defer></script>
<body hx-headers='{"X-CSRF-Token": "{{ csrf_token }}"}'>
```

By default htmx 2.x does NOT swap 4xx/5xx responses. The config above makes 422 (form
validation errors) swap. Without it, invalid forms look like "nothing happened".

## Fragment pattern

Put the whole swappable element (including its hx-* attributes) inside a block, render the
block in place in the page, and swap `outerHTML`. The full page and the fragment then emit
identical markup.

```html
{# templates/ports/index.html #}
{% extends "base.html" %}
{% block content %}
<h1>Load ports</h1>
{% block ports_panel %}
<div id="ports-panel" hx-get="/ports" hx-trigger="every 2s" hx-swap="outerHTML">
  {% for p in ports %}{{ ui.status_badge(p) }}{% endfor %}
</div>
{% endblock %}
{% endblock %}
```

```python
@router.get("/ports")
async def ports(request: Request, svc: PortService = Depends()):
    return render(request, "ports/index.html", {"ports": await svc.list()}, block="ports_panel")
```

## Conventions (enforce these)

1. **Explicit targeting**: every element with hx-get/post/put/patch/delete states `hx-target`
   (or `"this"`) and `hx-swap` explicitly. Do not rely on attribute inheritance (implicit in 2.x,
   opt-in in 4.x; explicit is correct for both).
2. **IDs**: swappable regions use `id="<feature>-<thing>"`, e.g. `ports-panel`, `recipe-form`,
   `alarm-table`. The block name is the same with underscores: `ports_panel`.
3. **Swap mode**: default to `outerHTML` on a region whose root carries the id and hx-*
   attributes, so the fragment is self-describing.
4. **One route, two shapes**: page routes return the full page normally and a block when
   `is_htmx()`. Do not create parallel `/partials/...` routes unless a fragment has no
   full-page home.
5. **One request, one target.** If a response can be two different fragments (form with errors
   vs. updated table), make the element that sent the request the target and deliver the other
   region out-of-band (see Forms), or retarget explicitly with `HX-Retarget` / `HX-Reswap`.
6. **Logic stays in Python**: templates format and loop; no business rules, unit conversion or
   state decisions in Jinja.
7. **Macros for repeated UI** in `components/macros.html`, called through the `ui` global.
8. **One owner per DOM region** (see next section).

## Mixing htmx with other JS: one owner per region

Every DOM region has exactly one owner: full-page server render, htmx, Alpine, a JS island
(React/Svelte), or hand-written JS. Conflicts only happen when two owners touch the same region.

- **Hand-written listeners**: never bind directly to elements inside a swappable region. Use
  event delegation on `document` / a stable ancestor, or initialise in `htmx.onLoad(el => ...)`.
- **JS islands** (React/Svelte, canvas maps): mount them in a container htmx never swaps. A swap
  would remove the island without unmounting it, leaking sockets and timers. Talk to it via
  custom events, not by swapping around it.
- **Alpine**: state inside a swapped region is lost. Keep Alpine-owned UI state outside swapped
  regions, or restore it from server-rendered attributes.
- **One update source per region**: polling OR SSE, never both. Never a hand-rolled
  `EventSource` and the htmx SSE extension on the same endpoint.
- **No global `hx-boost`**. If boosting is ever enabled, opt plain forms/links out with
  `hx-boost="false"`.
- Mark island containers explicitly, e.g. `<div id="wafer-map" data-owner="island">`, so humans
  and agents can see the boundary.

## Forms

The form targets itself. A validation error re-renders the form block (422); success returns a
fresh form plus the updated table out-of-band, so neither outcome lands in the wrong place.

```html
{% block recipe_form %}
<form id="recipe-form" hx-post="/recipes" hx-target="this" hx-swap="outerHTML">
  <label>Name <input name="name" value="{{ form.name | default('') }}"></label>
  {{ ui.field_error(errors, "name") }}
  ...
</form>
{% endblock %}
{% block recipe_table %}
<table id="recipe-table"{% if oob %} hx-swap-oob="true"{% endif %}>...</table>
{% endblock %}
```

```python
class RecipeIn(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    temp_c: float = Field(ge=0, le=400)

def recipe_ctx(recipes, form=None, errors=None, oob=False) -> dict:
    return {"recipes": recipes, "form": form or {}, "errors": errors or {}, "oob": oob}

@router.post("/recipes")
async def create_recipe(request: Request, svc: RecipeService = Depends()):
    data = dict(await request.form())
    try:
        recipe = RecipeIn.model_validate(data)
    except ValidationError as e:
        errors = {str(err["loc"][0]): err["msg"] for err in e.errors()}
        return render(request, "recipes/index.html", recipe_ctx(await svc.list(), data, errors),
                      block="recipe_form", status_code=422)
    await svc.create(recipe)
    return render(request, "recipes/index.html", recipe_ctx(await svc.list(), oob=True),
                  block=["recipe_form", "recipe_table"], headers={"HX-Trigger": "recipe-created"})
```

Validate manually (not via a `Form()` Pydantic model param) when the form must re-render with
errors, because FastAPI's automatic 422 returns JSON, not HTML.

## Response headers cheat sheet

| Header | Use |
|---|---|
| `HX-Trigger` | fire client event (toast, or refresh another region listening with `hx-trigger="recipe-created from:body"`) |
| `HX-Redirect` | full navigation after success |
| `HX-Refresh: true` | reload page |
| `HX-Retarget` / `HX-Reswap` | server decides where an error/alt fragment goes |
| `HX-Push-Url` | update address bar |

Out-of-band: htmx 2.x processes `hx-swap-oob` on any element in the response, nested or not
(`htmx.config.allowNestedOobSwaps` defaults to true). So a block must carry `hx-swap-oob` only
when rendered for an out-of-band update (the `oob` flag above), never unconditionally: rendered
inside a normal fragment, it would be pulled out of that fragment. Keep OOB elements at the top
level of the response for clarity (a block list like `["recipe_form", "recipe_table"]` does that).

## Live status

- **Polling** (default, simplest): `hx-trigger="every 2s"`. Return status **286** to stop
  polling (e.g. job finished).
- **SSE** (many clients or sub-second): the container holds the connection; the region swaps
  its inner content and has no polling attributes (one update source per region).

```html
{# templates/ports/live.html #}
<div hx-ext="sse" sse-connect="/sse/status">
  <div id="ports-panel" sse-swap="ports">
    {% block port_badges %}{% for p in ports %}{{ ui.status_badge(p) }}{% endfor %}{% endblock %}
  </div>
</div>
```

```python
from sse_starlette.sse import EventSourceResponse

@router.get("/sse/status", include_in_schema=False)
async def status_stream(request: Request):
    async def gen():
        async for snap in bus.subscribe():
            if await request.is_disconnected():
                break
            yield {"event": "ports",
                   "data": render_block_str("ports/live.html", "port_badges", ports=snap)}
    return EventSourceResponse(gen())
```

`EventSourceResponse` handles multi-line HTML in `data`; a hand-rolled `StreamingResponse` must
prefix EVERY line with `data: `. `render_block_str` has no request and no context processors:
blocks pushed over SSE must not use `url_for` or `csrf_token`.

Keep the source of truth in the backend (PLC/equipment layer). The browser only renders
snapshots; never compute equipment state in JS.

## htmx 2.x syntax traps (frequent AI mistakes)

- Inline handlers: `hx-on:click="..."`, htmx events `hx-on::after-request="..."` (double colon).
  NOT `hx-on="click: ..."` (1.x).
- `DELETE` sends parameters in the **query string**, not the body. Read them with `Query`, or
  use POST.
- Extensions are not bundled; load the extension file and declare `hx-ext`.
- `hx-swap-oob` is processed anywhere in the response, including nested elements (see above).
- Extended selectors are valid in `hx-target`: `this`, `closest tr`, `find .x`, `next`,
  `previous`.
- Swapping a region destroys any Alpine state inside it: keep Alpine-managed state outside
  swapped regions, or restore it from server-rendered attributes.

## Jinja / jinja2-fragments traps

- A block rendered alone only sees its own context: `{% from ... import %}` written outside the
  block is undefined inside it (fails loudly under StrictUndefined). Use the `ui` global, or
  put the import inside the block.
- Block names share one namespace with `base.html`: a fragment block named like a base block
  (`title`, `content`) silently overrides it. Use feature-prefixed names (`recipe_form`).

## Security

- Jinja autoescape stays on (default for `.html`). Never apply `|safe` to user or
  equipment-provided strings.
- Cookie-session auth: send the CSRF token via `hx-headers` on `<body>` and verify it on all
  non-GET routes. Use `SameSite=Lax` cookies.
- Keep `htmx.config.selfRequestsOnly` at its 2.x default (true). `allowEval` (default true) is
  needed by `hx-on:*` and trigger filters; under a CSP without `unsafe-eval`, drop those
  features rather than loosening the CSP.

## Testing

```python
def test_ports_fragment(client):
    r = client.get("/ports", headers={"HX-Request": "true"})
    assert r.status_code == 200
    assert 'id="ports-panel"' in r.text
    assert "<html" not in r.text

def test_ports_full_page(client):
    assert "<html" in client.get("/ports").text
```

Test both shapes for every page route (and the full page for `HX-History-Restore-Request`).
For every form, test the 422 path (form block with errors and the typed values, no table) and
the success path (fresh form, `hx-swap-oob` table, `HX-Trigger`), and that the page render has
no `hx-swap-oob`. For SSE, `client.get("/sse/status")` against a bus that yields one snapshot
and ends, then assert the `event:` / `data:` lines.

## Review checklist

- [ ] Every request element has explicit `hx-target`/`hx-swap`; one request never needs two different targets
- [ ] Swapped region id matches between page and fragment; block name matches id
- [ ] `TemplateResponse(request, ...)` new signature
- [ ] Environment uses `StrictUndefined`; contexts built by one helper per feature; macros via the `ui` global
- [ ] 422 swaps (responseHandling config present) and the form re-renders with errors
- [ ] `hx-swap-oob` only on explicitly OOB renders
- [ ] No 1.x syntax (`hx-on="..."`), no 4.x-only syntax
- [ ] Assets self-hosted, versions pinned
- [ ] Page routes `include_in_schema=False`
- [ ] Heavy real-time graphics delegated to a JS island, not htmx
- [ ] Each DOM region has one owner; no islands or direct listeners inside swapped regions; one update source per region
