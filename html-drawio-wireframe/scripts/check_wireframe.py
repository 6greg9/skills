#!/usr/bin/env python3
"""Rule check and screenshots for an HTML wireframe made from assets/template.html.

Usage:
    python check_wireframe.py FILE.html [--shots DIR] [--json] [--browser NAME]

Checks the authoring rules in the template's header comment: real tags, the class kit,
layout-only CSS, text only in leaf elements, no positioning / transforms / background
images, @container with the 640px breakpoint, data-id, data-when, notes, horizontal
overflow, and a few hints about unrealistic data. With --shots it saves one PNG per
state (both sizes side by side, note badges on).

Exit code: 0 no errors (warnings are hints), 1 errors found, 2 could not run.
Needs Python 3.9+ and Playwright: pip install playwright && playwright install chromium
(--browser chrome or msedge uses an installed browser instead of Chromium).
"""
import argparse
import json
import sys
from pathlib import Path

STATIC_JS = r"""
() => {
  const KIT = new Set(['row','col','grow','wrap','gap-1','gap-2','gap-3','pad-1','pad-2','pad-3',
    'center','between','end','box','img','icon','skel','chip','primary','muted','strong','mobile-only','desktop-only']);
  const LANDMARK = new Set(['main','header','footer','nav','aside','section','article','form','table','dialog','ul','ol','fieldset']);
  const CONTROL = new Set(['button','input','select','textarea']);
  const BANNED = {
    img: 'use class "img" for pictures', svg: 'use class "icon" or "img"', canvas: 'use class "img"',
    video: 'use class "img"', audio: 'remove it', iframe: 'use class "img"', object: 'use class "img"',
    embed: 'use class "img"', picture: 'use class "img"', script: 'scripts are not allowed in the screen',
    link: 'not allowed in the screen', style: 'put CSS in #screen-style'
  };
  const LAYOUT_PROP = /^(display|flex(-[a-z]+)?|gap|row-gap|column-gap|align-[a-z]+|justify-[a-z]+|place-[a-z]+|order|width|min-width|max-width|height|min-height|max-height|inline-size|block-size|min-inline-size|max-inline-size|min-block-size|max-block-size|padding(-[a-z-]+)?|margin(-[a-z-]+)?|overflow(-[a-z]+)?|box-sizing|aspect-ratio|grid(-[a-z-]+)?|text-align|white-space|text-overflow)$/;
  const out = [];
  const add = (sev, rule, msg, where) => out.push({ sev, rule, msg, where: where || '' });
  const states = (document.body.dataset.states || '').split(/\s+/).filter(Boolean);
  const tpl = document.getElementById('screen');
  const notesLi = [...document.querySelectorAll('#notes li')];
  const noteNums = new Set(notesLi.map((li) => li.dataset.note).filter(Boolean));

  if (!tpl) { add('error', 'structure', '<template id="screen"> is missing'); return out; }
  if (!document.getElementById('screen-style')) add('error', 'structure', '<style id="screen-style"> is missing');
  if (!states.length) add('error', 'structure', '<body data-states> is missing or empty');
  if (!document.getElementById('notes')) add('warn', 'structure', '#notes list is missing');
  notesLi.forEach((li, i) => { if (!li.dataset.note) add('warn', 'note', 'note ' + (i + 1) + ' in #notes has no data-note number', '#notes'); });

  const root = tpl.content;
  const path = (el) => {
    const bits = [];
    let e = el;
    while (e && e.localName) {
      if (e.dataset && e.dataset.id) { bits.unshift(e.dataset.id); break; }
      bits.unshift(e.localName + (e.classList && e.classList.length ? '.' + [...e.classList].join('.') : ''));
      e = e.parentElement;
    }
    return bits.join(' > ');
  };
  const rootEls = [...root.children];
  if (rootEls.length !== 1) add('error', 'root', 'template#screen must contain exactly one root element, found ' + rootEls.length);
  const all = [...root.querySelectorAll('*')];

  // CSS in #screen-style
  const definedClasses = new Set();
  const sheet = document.getElementById('screen-style') && document.getElementById('screen-style').sheet;
  const hasContainerRule = typeof CSSContainerRule !== 'undefined';
  const containerClasses = new Set();
  const walk = (rules, inContainer) => {
    for (const r of rules) {
      if (r instanceof CSSStyleRule) {
        const sel = r.selectorText;
        (sel.match(/\.(-?[_a-zA-Z][\w-]*)/g) || []).forEach((c) => { definedClasses.add(c.slice(1)); if (inContainer) containerClasses.add(c.slice(1)); });
        if (/:(hover|focus|focus-within|focus-visible|active|checked|target|visited|disabled|enabled|invalid|valid)\b/.test(sel))
          add('error', 'css-state', 'selector "' + sel + '" depends on interaction state; use data-when instead', '#screen-style');
        if (/::?(before|after)/.test(sel)) add('error', 'css-visual', 'selector "' + sel + '" generates content', '#screen-style');
        const bad = new Set();
        const family = (p) => /^border-.*radius/.test(p) ? 'border-radius' : p.startsWith('box-shadow') ? 'box-shadow' : p.startsWith('text-') ? p.split('-').slice(0, 2).join('-') : p.split('-')[0];
        for (let i = 0; i < r.style.length; i++) { const p = r.style[i]; if (!LAYOUT_PROP.test(p)) bad.add(family(p)); }
        if (bad.size) add('error', 'css-visual', 'selector "' + sel + '" sets non-layout properties (' + [...bad].join(', ') + '); #screen-style is layout-only', '#screen-style');
        if (r.cssRules && r.cssRules.length) walk(r.cssRules, inContainer);
      } else if (r instanceof CSSMediaRule) {
        add('error', 'media-query', '@media ' + r.conditionText + ' is viewport based; use @container', '#screen-style');
      } else if (hasContainerRule && r instanceof CSSContainerRule) {
        const cond = r.conditionText || r.cssText.slice(0, 60);
        const widths = [...cond.matchAll(/(min|max)-width\s*:\s*([\d.]+)px/g)].map((m) => parseFloat(m[2]));
        if (!widths.length || widths.some((w) => ![640, 639.98, 639.99].includes(w)) || /height/.test(cond))
          add('error', 'breakpoint', '@container ' + cond + ' must use the 640px width breakpoint', '#screen-style');
        walk(r.cssRules, true);
      } else {
        add('error', 'css-rule', 'unsupported rule in #screen-style: ' + r.cssText.slice(0, 50), '#screen-style');
      }
    }
  };
  if (sheet) walk(sheet.cssRules, false);

  // markup
  const ids = new Map();
  const textLeaves = [];
  for (const el of all) {
    const tag = el.localName;
    const where = path(el);
    if (BANNED[tag]) add('error', 'tag', '<' + tag + '> is not allowed: ' + BANNED[tag], where);
    if (el.hasAttribute('style')) add('error', 'inline-style', 'inline style attribute; use a layout class in #screen-style', where);
    for (const a of el.attributes) if (/^on/i.test(a.name)) add('error', 'inline-handler', a.name + ' handler is not allowed', where);
    if ((tag === 'div' || tag === 'span') && (el.hasAttribute('role') || el.hasAttribute('tabindex')))
      add('error', 'tag-semantics', '<' + tag + '> with role/tabindex; use a real tag (button, a, input, nav ...)', where);
    for (const c of el.classList) {
      if (!KIT.has(c) && !definedClasses.has(c))
        add('error', 'class', 'class "' + c + '" is not in the kit and not defined in #screen-style', where);
    }
    // text only in leaf elements
    const hasText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    const hasEl = [...el.children].some((c) => c.localName !== 'br');
    if (hasText && hasEl) add('error', 'text-mixed', 'text and child elements are mixed; wrap the loose text in <span> or <p>', where);
    if (hasText && !hasEl) {
      textLeaves.push(el.textContent.trim());
      if (tag === 'div') add('warn', 'tag-semantics', '<div> holds only text; prefer p, span, h1-h3, label or small', where);
    }
    // data-id
    const id = el.dataset.id;
    if (id) {
      if (!/^[a-z][a-z0-9]*(-[a-z0-9]+)*$/.test(id)) add('error', 'data-id', 'data-id "' + id + '" must be kebab-case (a-z, 0-9, -)', where);
      if (ids.has(id)) add('error', 'data-id', 'data-id "' + id + '" is used more than once', where);
      ids.set(id, el);
    } else if (el === rootEls[0] || LANDMARK.has(tag)) {
      add('error', 'data-id', '<' + tag + '> needs a data-id', where);
    } else if (CONTROL.has(tag) || el.classList.contains('box')) {
      add('warn', 'data-id', '<' + tag + (el.classList.contains('box') ? '.box' : '') + '> has no data-id; feedback cannot name it', where);
    }
    // states
    if (el.dataset.when !== undefined) {
      const toks = el.dataset.when.split(/\s+/).filter(Boolean);
      if (!toks.length) add('error', 'data-when', 'empty data-when', where);
      for (const t of toks) {
        const s = t[0] === '!' ? t.slice(1) : t;
        if (!states.includes(s)) add('error', 'data-when', 'data-when refers to "' + s + '", which is not in <body data-states>', where);
      }
    }
    // notes
    if (el.dataset.note !== undefined) {
      for (const n of el.dataset.note.split(/\s+/).filter(Boolean))
        if (!noteNums.has(n)) add('error', 'note', 'data-note="' + n + '" has no <li data-note="' + n + '"> in #notes', where);
    }
  }
  // sibling groups with identical text
  for (const parent of [root, ...all]) {
    const kids = [...parent.children];
    const byTag = {};
    kids.forEach((k) => (byTag[k.localName] = byTag[k.localName] || []).push(k));
    for (const tag of Object.keys(byTag)) {
      const g = byTag[tag];
      if (g.length >= 3) {
        const texts = g.map((k) => k.textContent.replace(/\s+/g, ' ').trim());
        if (texts[0] && texts.every((t) => t === texts[0]))
          add('warn', 'realistic-data', g.length + ' sibling <' + tag + '> elements have identical text; vary the content', path(g[0]));
      }
    }
  }
  const joined = textLeaves.join(' \n ');
  const ph = joined.match(/lorem|ipsum|\bfoo\b|\bxxx+\b|sample text|placeholder text|text here/i);
  if (ph) add('warn', 'realistic-data', 'placeholder-looking text ("' + ph[0] + '"); use realistic content');
  if (textLeaves.length && Math.max(...textLeaves.map((t) => t.length)) < 40)
    add('warn', 'realistic-data', 'no long text anywhere; include the longest plausible title and summary');
  // states
  for (const d of ['ready', 'loading', 'empty', 'error'])
    if (!states.includes(d)) add('warn', 'states', 'default state "' + d + '" is not in data-states; fine only if the screen cannot have it');
  const usedStates = new Set();
  all.forEach((el) => { if (el.dataset.when) el.dataset.when.split(/\s+/).forEach((t) => usedStates.add(t[0] === '!' ? t.slice(1) : t)); });
  const usedClasses = new Set(all.flatMap((el) => [...el.classList]));
  const unused = [...definedClasses].filter((c) => !usedClasses.has(c));
  if (unused.length)
    add('warn', 'unused-css', 'classes defined in #screen-style but not used: .' + unused.join(', .') + ' (left over from the example?)', '#screen-style');
  if (![...containerClasses].some((c) => usedClasses.has(c)) && !root.querySelector('.mobile-only, .desktop-only'))
    add('warn', 'responsive', 'no @container rule for a used class and no mobile-only/desktop-only: check that mobile is not just a squeezed desktop');
  for (const s of states.length > 1 ? states : []) {
    const positive = all.some((el) => el.dataset.when && el.dataset.when.split(/\s+/).some((t) => t === s));
    const negative = all.some((el) => el.dataset.when && el.dataset.when.split(/\s+/).some((t) => t[0] === '!' && t.slice(1) !== s));
    if (!positive && !negative) add('warn', 'states', 'state "' + s + '" has no data-when content, so it looks like every other state');
  }
  return out;
}
"""

VIEW_JS = r"""
(sizeName) => {
  const screen = WF.frame(sizeName);
  const sr = screen.getBoundingClientRect();
  const out = [];
  const add = (sev, rule, msg, where) => out.push({ sev, rule, msg, where: where || '' });
  const path = (el) => {
    const bits = [];
    let e = el;
    while (e && e !== screen) {
      if (e.dataset && e.dataset.id) { bits.unshift(e.dataset.id); break; }
      bits.unshift(e.localName + (e.classList.length ? '.' + [...e.classList].join('.') : ''));
      e = e.parentElement;
    }
    return bits.join(' > ');
  };
  const els = [...screen.querySelectorAll('*')].filter((e) => !e.closest('[hidden]'));
  const clipped = (el) => {
    for (let a = el.parentElement; a && a !== screen; a = a.parentElement)
      if (getComputedStyle(a).overflowX !== 'visible') return true;
    return false;
  };
  const over = [];
  for (const el of els) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none') continue;
    if (['absolute', 'fixed', 'sticky'].includes(cs.position)) add('error', 'position', 'position:' + cs.position + ' is not allowed', path(el));
    if (cs.transform !== 'none' || (cs.translate && cs.translate !== 'none') || (cs.rotate && cs.rotate !== 'none') || (cs.scale && cs.scale !== 'none'))
      add('error', 'transform', 'transform is not allowed', path(el));
    if (cs.backgroundImage !== 'none') add('error', 'background-image', 'background images are not allowed', path(el));
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    const dx = Math.max(r.right - sr.right, sr.left - r.left);
    if (dx > 0.5 && !clipped(el)) over.push({ el, dx });
    if (cs.overflowX !== 'visible' && el.scrollWidth > el.clientWidth + 1 && el.children.length === 0 && el.textContent.trim())
      add('warn', 'clipped-text', 'text is cut off (' + (el.scrollWidth - el.clientWidth) + 'px) by overflow:' + cs.overflowX, path(el));
  }
  for (const o of over) {
    if (over.some((p) => p.el !== o.el && o.el.contains(p.el))) continue;
    add('error', 'overflow-x', 'sticks out of the ' + sizeName + ' frame by ' + Math.round(o.dx) + 'px', path(o.el));
  }
  const mark = [...screen.querySelectorAll('[data-id]')].filter((e) => !e.closest('[hidden]'));
  const seen = new Set();
  for (const e of mark) { if (seen.has(e.dataset.id)) add('error', 'data-id', 'data-id "' + e.dataset.id + '" appears twice in this view', e.dataset.id); seen.add(e.dataset.id); }
  return out;
}
"""


def launch(p, name):
    order = [name] if name else ["chromium", "chrome", "msedge"]
    errors = []
    for n in order:
        try:
            return p.chromium.launch() if n == "chromium" else p.chromium.launch(channel=n)
        except Exception as e:  # noqa: BLE001 - report which browsers failed
            errors.append("%s: %s" % (n, str(e).splitlines()[0]))
    sys.exit("could not start a browser (%s). Run: playwright install chromium" % "; ".join(errors))


def run(path, shots, browser_name):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright is missing. Run: pip install playwright && playwright install chromium")
    findings = []
    with sync_playwright() as p:
        browser = launch(p, browser_name)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(Path(path).resolve().as_uri())
        try:
            page.wait_for_function("window.WF && WF.ready", timeout=5000)
        except Exception:  # noqa: BLE001
            browser.close()
            sys.exit("the page did not start (window.WF missing). Page errors: %s" % (errors or "none"))
        page.evaluate("document.fonts.ready")
        page.add_style_tag(content="#toolbar{position:static !important}")
        states = page.evaluate("WF.states")
        sizes = list(page.evaluate("WF.sizes").keys())
        for f in page.evaluate(STATIC_JS):
            f["views"] = []
            findings.append(f)
        page.evaluate("WF.setSize('both')")
        for state in states:
            page.evaluate("(s) => WF.setState(s)", state)
            for size in sizes:
                for f in page.evaluate(VIEW_JS, size):
                    f["views"] = ["%s / %s" % (size, state)]
                    findings.append(f)
            if shots:
                out = Path(shots)
                out.mkdir(parents=True, exist_ok=True)
                page.evaluate("WF.setNotes(true)")
                page.locator("#stage").screenshot(path=str(out / ("%s.png" % state)))
        for e in errors:
            findings.append({"sev": "error", "rule": "script", "msg": "page error: " + e, "where": "", "views": []})
        browser.close()
    merged = {}
    for f in findings:
        key = (f["sev"], f["rule"], f["msg"], f["where"])
        if key in merged:
            merged[key]["views"] += f["views"]
        else:
            merged[key] = f
    order = {"error": 0, "warn": 1}
    return sorted(merged.values(), key=lambda f: (order[f["sev"]], f["rule"], f["where"]))


def main():
    ap = argparse.ArgumentParser(description="Check an HTML wireframe against the template rules.")
    ap.add_argument("file")
    ap.add_argument("--shots", metavar="DIR", help="save one PNG per state into DIR")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--browser", choices=["chromium", "chrome", "msedge"], help="browser to use (default: try all)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if not Path(a.file).is_file():
        sys.exit("file not found: %s" % a.file)
    findings = run(a.file, a.shots, a.browser)
    errors = [f for f in findings if f["sev"] == "error"]
    warns = [f for f in findings if f["sev"] == "warn"]
    if a.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            views = ""
            if f["views"]:
                views = "  [%s]" % ", ".join(f["views"][:3] + (["+%d more" % (len(f["views"]) - 3)] if len(f["views"]) > 3 else []))
            where = "  (%s)" % f["where"] if f["where"] else ""
            print("%-5s %-15s %s%s%s" % (f["sev"].upper(), f["rule"], f["msg"], where, views))
        print("%s: %d error(s), %d warning(s)%s" % (Path(a.file).name, len(errors), len(warns), "; screenshots in " + a.shots if a.shots else ""))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
