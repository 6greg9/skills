---
name: go-templ-htmx
description: Conventions and an agent build loop for type-safe server-rendered web UIs in Go - net/http (Go 1.25+), templ (a-h/templ) components and htmx 2.x, shipped as one binary with embedded assets. Covers project layout, page-vs-fragment handlers, element IDs and form fields as Go constants, forms with 422 validation, out-of-band swaps, polling and SSE, CrossOriginProtection, and tests. Use whenever writing, reviewing or debugging .templ files, templ generate or _templ.go compile errors, Go HTML handlers, or htmx attributes in a Go project, and when building a Go admin page, CRUD or recipe editor, or an MES or equipment status dashboard that should run on offline PCs, even if templ or htmx is not named yet. Not for SPA frontends or high-frequency graphics (use a JS island).
---

# Go + templ + htmx

Opinionated conventions for server-rendered UIs in Go. The point of this stack is a tight
feedback loop: templates are compiled Go, so wrong field names, wrong types and wrong
fragment/element IDs fail at `go build`, not in the browser. Use that loop (see "Agent loop").

Everything below was compiled and tested on 2026-10-14 with Go 1.27.1 and templ v0.3.1070.

## When to use / not use

Use for: admin and management screens, CRUD, recipe/parameter editors, lot/wafer/alarm history,
MES/DB-backed dashboards, status panels refreshing every ~1s or slower. Strong fit when
deployment wants a single binary with no runtime (offline fab PCs, equipment PCs).

Do NOT use for: high-frequency graphical views (many moving elements, robot/FOUP/wafer maps,
>2 Hz), canvas/SVG animation, heavy client-side state. Embed a Vite + React/Svelte island fed by
WebSocket JSON for those.

Equipment comms: Go has thinner SECS/GEM and PLC (MC protocol) library support than Python. If
the web layer must talk to equipment directly, check library maturity first; otherwise keep
equipment I/O in its existing service and have the Go app read from DB / message bus / gRPC.

Status colors and alarm presentation on equipment screens: follow `industrial-hmi-style-guide`.

## Pinned versions

- Go **1.25+** (method/path routing, `http.FileServerFS`, `http.CrossOriginProtection`).
- templ **v0.3.x**, pinned as a Go tool so every machine and agent uses the same generator. The
  CLI and the runtime are the same module, so one command pins both:
  ```
  go get -tool github.com/a-h/templ/cmd/templ@v0.3.<pinned>
  go tool templ generate
  ```
- htmx **2.0.x**, extensions (`htmx-ext-sse`) as separate files, all self-hosted via `go:embed`
  (no CDN: fab networks are often offline). Do not mix in htmx 4.x syntax.
- Alpine.js 3 optional, for purely local UI state.
- No web framework. `net/http` only, unless the project already uses one.

## Project layout

```
cmd/server/main.go          # wiring: config, services, mux, server timeouts
internal/
  web/
    server.go               # Routes(), Handlers
    render.go               # IsHTMX, Render, writeSSE
    static.go               # //go:embed static
    static/vendor/          # htmx.min.js, sse.js, alpine.min.js
    ports.go, recipes.go    # handlers per feature (+ input validation)
  views/
    layout.templ
    config.go               # htmxConfig, form field name constants, view-model structs
    components/*.templ      # badges, buttons, form fields
    ports.templ             # page + its swappable sub-components
    recipes.templ
  service/                  # business logic, no HTTP, no HTML
  model/                    # domain types, validated inputs
```

`web` imports `views`, never the reverse: view-model structs a component takes (e.g. the raw
`RecipeForm`) live in `views`, validated inputs (`RecipeInput`) in `model`.

Generated `*_templ.go` files ARE committed (so `go build` works without the templ CLI); CI fails
if `go tool templ generate` produces a diff. Never hand-edit `*_templ.go`.

## Agent loop (run after every change)

```
go tool templ fmt ./internal/views
go tool templ generate
go vet ./...
go test ./...
```

An edit is not done until all four pass. Compile errors in generated code point back to the
`.templ` source: fix the `.templ`, never the generated file.

Dev server with live reload:
```
go tool templ generate --watch --proxy="http://localhost:8080" --cmd="go run ./cmd/server"
```

## Core helpers

```go
// internal/web/render.go
package web

// IsHTMX: history restores (cache miss) also send HX-Request: true but need the full page.
func IsHTMX(r *http.Request) bool {
	return r.Header.Get("HX-Request") == "true" &&
		r.Header.Get("HX-History-Restore-Request") != "true"
}

// Render writes a component. Set HX-* response headers BEFORE calling it.
func Render(w http.ResponseWriter, r *http.Request, c templ.Component, status int) {
	w.Header().Set("Vary", "HX-Request")
	templ.Handler(c, templ.WithStatus(status)).ServeHTTP(w, r)
}
```

```go
// internal/web/static.go
//go:embed static
var embedded embed.FS

func StaticFS() fs.FS { sub, _ := fs.Sub(embedded, "static"); return sub }
```

```go
// internal/web/server.go
func Routes(h *Handlers) http.Handler {
	mux := http.NewServeMux()
	mux.Handle("GET /static/", http.StripPrefix("/static/", http.FileServerFS(StaticFS())))
	mux.HandleFunc("GET /ports", h.Ports)
	mux.HandleFunc("GET /sse/status", h.StatusSSE)
	mux.HandleFunc("GET /recipes", h.Recipes)
	mux.HandleFunc("POST /recipes", h.CreateRecipe)
	mux.HandleFunc("POST /recipes/{id}/delete", h.DeleteRecipe) // r.PathValue("id")
	return http.NewCrossOriginProtection().Handler(mux)
}
```

## Fragment pattern: components, not string fragments

A page is a component composed of sub-components. A handler returns the whole page normally
and the sub-component directly for htmx requests. This is type-checked end to end.

```templ
// internal/views/ports.templ
package views

const PortsPanelID = "ports-panel"

templ PortsPage(ports []model.Port) {
	@Layout("Load ports") {
		<h1>Load ports</h1>
		@PortsPanel(ports)
	}
}

templ PortsPanel(ports []model.Port) {
	<div id={ PortsPanelID } hx-get="/ports" hx-trigger="every 2s" hx-swap="outerHTML">
		@PortBadges(ports)
	</div>
}

templ PortBadges(ports []model.Port) {
	for _, p := range ports {
		@components.PortBadge(p)
	}
}
```

```go
func (h *Handlers) Ports(w http.ResponseWriter, r *http.Request) {
	ports, err := h.svc.ListPorts(r.Context())
	if err != nil { http.Error(w, "ports unavailable", 500); return }
	if IsHTMX(r) {
		Render(w, r, views.PortsPanel(ports), http.StatusOK)
		return
	}
	Render(w, r, views.PortsPage(ports), http.StatusOK)
}
```

Use `@templ.Fragment(id)` + `templ.WithFragments(id)` only when a swappable region is not worth
its own component.

## Conventions (enforce these)

1. **IDs are Go constants** (`PortsPanelID = "ports-panel"`), used for `id={ ... }` and for any
   `hx-target={ "#" + PortsPanelID }` elsewhere. Never repeat an ID as a string literal.
2. **Explicit targeting**: every request element states `hx-target` (or `"this"`) and
   `hx-swap`. No reliance on attribute inheritance.
3. **Swap mode**: `outerHTML` on a component whose root carries the id and hx-* attributes; the
   sub-component is the fragment.
4. **One route, two shapes** (page vs sub-component via `IsHTMX`). No parallel `/partials/`
   routes unless a fragment has no page.
5. **One request, one target.** If a response can be two different fragments (form with errors
   vs. updated table), make the element that sent the request the target and deliver the other
   region out-of-band (see Forms), or retarget explicitly with `HX-Retarget` / `HX-Reswap`.
6. **Logic stays in Go services**. Components take already-shaped view data (small view-model
   structs), not DB rows or services.
7. **Components take explicit params**; avoid `ctx` values for page data (not type-checked).
   Only cross-cutting things (CSRF token, current user) go through context.
8. **One owner per DOM region** (see next section).

## Mixing htmx with other JS: one owner per region

templ and htmx never conflict (templ runs on the server, htmx in the browser). Conflicts only
happen when two browser-side owners touch the same DOM region. Every region has exactly one
owner: full-page render, htmx, Alpine, a JS island (React/Svelte), or hand-written JS.

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
- Island container IDs are Go constants too, and marked explicitly, e.g.
  `<div id={ WaferMapID } data-owner="island">`, so humans and agents can see the boundary.

## Layout essentials

```templ
templ Layout(title string) {
	<!DOCTYPE html>
	<html lang="en">
		<head>
			<meta charset="utf-8"/>
			<meta name="viewport" content="width=device-width, initial-scale=1"/>
			<title>{ title }</title>
			<meta name="htmx-config" content={ htmxConfig }/>
			<script src="/static/vendor/htmx.min.js" defer></script>
		</head>
		<body>
			{ children... }
		</body>
	</html>
}
```

```go
// views/config.go — makes 422 (form validation errors) swap; htmx 2.x does not swap 4xx/5xx by default
const htmxConfig = `{"responseHandling":[{"code":"204","swap":false},{"code":"[23]..","swap":true},{"code":"422","swap":true},{"code":"[45]..","swap":false,"error":true},{"code":"...","swap":false}]}`
```

## Forms

The form targets itself. A validation error re-renders the form (422); success returns a fresh
form plus the updated table out-of-band, so neither outcome lands in the wrong place.

```go
// views/config.go
const (
	FieldName  = "name"    // used by name={ FieldName } in .templ and by the handler
	FieldTempC = "temp_c"
)
type RecipeForm struct{ Name, TempC string } // raw strings, re-rendered as typed on error

// web/recipes.go
func validateRecipe(f views.RecipeForm) (model.RecipeInput, map[string]string) {
	errs := map[string]string{}
	in := model.RecipeInput{Name: strings.TrimSpace(f.Name)}
	if in.Name == "" || len(in.Name) > 32 { errs[views.FieldName] = "1–32 characters" }
	t, err := strconv.ParseFloat(f.TempC, 64)
	if err != nil || t < 0 || t > 400 { errs[views.FieldTempC] = "0–400 °C" } else { in.TempC = t }
	return in, errs
}

func (h *Handlers) CreateRecipe(w http.ResponseWriter, r *http.Request) {
	f := views.RecipeForm{Name: r.PostFormValue(views.FieldName), TempC: r.PostFormValue(views.FieldTempC)}
	in, errs := validateRecipe(f)
	if len(errs) > 0 {
		Render(w, r, views.RecipeFormView(f, errs), http.StatusUnprocessableEntity)
		return
	}
	if err := h.svc.CreateRecipe(r.Context(), in); err != nil { http.Error(w, "save failed", 500); return }
	recipes, _ := h.svc.ListRecipes(r.Context())
	w.Header().Set("HX-Trigger", "recipe-created") // e.g. a toast
	Render(w, r, templ.Join(views.RecipeFormView(views.RecipeForm{}, nil), views.RecipeTable(recipes, true)), http.StatusOK)
}
```

```templ
templ RecipeFormView(f RecipeForm, errs map[string]string) {
	<form id={ RecipeFormID } hx-post="/recipes" hx-target="this" hx-swap="outerHTML">
		<label>Name <input name={ FieldName } value={ f.Name } aria-invalid?={ errs[FieldName] != "" }/></label>
		if msg := errs[FieldName]; msg != "" {
			<small class="error">{ msg }</small>
		}
		...
	</form>
}

// oob=true only in the POST response; the page renders the plain table.
templ RecipeTable(recipes []model.Recipe, oob bool) {
	<table
		id={ RecipeTableID }
		if oob {
			hx-swap-oob="true"
		}
	>
		...
	</table>
}
```

## Response headers cheat sheet

| Header | Use |
|---|---|
| `HX-Trigger` | client event (toast, or another region with `hx-trigger="recipe-created from:body"`) |
| `HX-Redirect` | full navigation after success |
| `HX-Refresh: true` | reload page |
| `HX-Retarget` / `HX-Reswap` | server decides where an error/alt fragment goes |
| `HX-Push-Url` | update address bar |

Set headers before `Render` (headers are frozen once the status is written).

Out-of-band: htmx 2.x processes `hx-swap-oob` on any element in the response, nested or not
(`htmx.config.allowNestedOobSwaps` defaults to true). So a component must carry `hx-swap-oob`
only when it is meant to be swapped out-of-band (an `oob bool` parameter as above), never
unconditionally: rendered inside a normal fragment, it would be pulled out of that fragment.
Put OOB components at the top level of the response with `templ.Join(...)` for clarity.

## Live status

- **Polling** (default): `hx-trigger="every 2s"`. Return **286** to stop
  (`Render(w, r, c, 286)`).
- **SSE**: the container holds the connection; the region swaps its inner content and has no
  polling attributes (one update source per region). The handler pushes the inner component.

```templ
templ PortsLive(ports []model.Port) {
	<div hx-ext="sse" sse-connect="/sse/status">
		<div id={ PortsPanelID } sse-swap="ports">
			@PortBadges(ports)
		</div>
	</div>
}
```

```go
func (h *Handlers) StatusSSE(w http.ResponseWriter, r *http.Request) {
	rc := http.NewResponseController(w)
	_ = rc.SetWriteDeadline(time.Time{}) // server WriteTimeout would otherwise kill the stream
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	updates := h.bus.Subscribe(r.Context())
	w.WriteHeader(http.StatusOK)
	_ = rc.Flush() // send headers now, not at the first event
	for {
		select {
		case <-r.Context().Done():
			return
		case snap := <-updates:
			var buf bytes.Buffer
			if err := views.PortBadges(snap).Render(r.Context(), &buf); err != nil { return }
			writeSSE(w, "ports", buf.String())
			if err := rc.Flush(); err != nil { return }
		}
	}
}

func writeSSE(w io.Writer, event, data string) {
	fmt.Fprintf(w, "event: %s\n", event)
	for _, line := range strings.Split(data, "\n") { // every line needs its own "data: "
		fmt.Fprintf(w, "data: %s\n", line)
	}
	io.WriteString(w, "\n")
}
```

Keep the source of truth in the backend; the browser only renders snapshots.

## templ syntax traps (frequent AI mistakes)

- Call components with `@Comp(args)`, not `{ Comp(args) }`. Text/values use `{ expr }`.
- Attributes: `id={ v }`; boolean: `disabled?={ cond }`; conditional classes:
  `class={ "badge", templ.KV("badge-alarm", p.Alarm) }`; a conditional attribute is an `if`
  block inside the tag (see `RecipeTable`).
- Children: declare nothing, render with `{ children... }`; pass with `@Layout("t") { ... }`.
- JSON in attributes (e.g. `hx-vals`): `hx-vals={ templ.JSONString(v) }`, never string
  concatenation.
- Dynamic URLs in `href`/`src` go through templ's URL sanitization; use `templ.URL(...)` for
  computed values.
- `templ.Raw` / `templ.SafeURL` bypass escaping: never with user or equipment-provided data.
- Keep JS out of `.templ` beyond `hx-on:*` and Alpine attributes; no `<script>` blocks building
  HTML.
- Go code (constants, view-model types) may sit at the top level of a `.templ` file;
  `templ fmt` also sorts its imports.

## htmx 2.x traps

- `hx-on:click="..."`, `hx-on::after-request="..."` (not 1.x `hx-on="click: ..."`).
- `DELETE` sends params in the query string; this skill uses `POST /x/{id}/delete` to avoid it.
- Extensions must be loaded and declared with `hx-ext`.
- `hx-swap-oob` is processed anywhere in the response, including nested elements (see above).
- 4xx/5xx responses are not swapped unless `responseHandling` says so (422 above).
- Swapping destroys Alpine state inside the swapped region.

## Security

- templ autoescapes text and attributes; keep it that way.
- `http.NewCrossOriginProtection()` wraps the mux: it rejects cross-origin non-GET requests
  (Sec-Fetch-Site / Origin) with 403. Add token CSRF only if old browsers or non-browser clients
  matter.
- Cookies `HttpOnly`, `SameSite=Lax`, `Secure` behind TLS.
- Keep `htmx.config.selfRequestsOnly` at its default (true). `allowEval` (default true) is
  needed by `hx-on:*` and trigger filters; under a CSP without `unsafe-eval`, drop those
  features rather than loosening the CSP.
- Server: set `ReadHeaderTimeout`, `ReadTimeout`, `IdleTimeout`; `WriteTimeout` is cleared
  per-request only for SSE.

## Testing

```go
func TestPortsFragment(t *testing.T) {
	srv := httptest.NewServer(web.Routes(testHandlers(t)))
	defer srv.Close()
	req, _ := http.NewRequest("GET", srv.URL+"/ports", nil)
	req.Header.Set("HX-Request", "true")
	res, _ := http.DefaultClient.Do(req)
	body, _ := io.ReadAll(res.Body)
	if !strings.Contains(string(body), `id="ports-panel"`) || strings.Contains(string(body), "<html") {
		t.Fatalf("expected fragment, got %s", body)
	}
}
```

Per route, test both shapes (fragment, and full page also for `HX-History-Restore-Request`).
Per form, test the 422 path (form with errors and the typed values) and the success path
(fresh form, OOB table, `HX-Trigger`), and that the page render carries no `hx-swap-oob`.
Component-level tests render into a `bytes.Buffer` with `views.X(...).Render(ctx, &buf)`.
For SSE, read the stream with a context timeout and assert the `event:` / `data:` lines.

## Review checklist

- [ ] Agent loop passes: `templ fmt`, `templ generate` (no diff), `go vet`, `go test`
- [ ] templ CLI pinned as a Go tool (`tool` line in go.mod)
- [ ] Element IDs and form field names are constants, not repeated literals
- [ ] Every request element has explicit `hx-target`/`hx-swap`; one request never needs two different targets
- [ ] HX-* headers set before `Render`; 422 for validation errors; htmx-config present
- [ ] `hx-swap-oob` only on explicitly OOB renders, never unconditionally on a reusable component
- [ ] No `templ.Raw`/`SafeURL` on untrusted data; CrossOriginProtection wraps the mux
- [ ] Assets embedded and self-hosted; no htmx 1.x/4.x syntax
- [ ] Heavy real-time graphics delegated to a JS island, not htmx
- [ ] Each DOM region has one owner; no islands or direct listeners inside swapped regions; one update source per region
