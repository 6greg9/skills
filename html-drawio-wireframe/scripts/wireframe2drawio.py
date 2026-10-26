#!/usr/bin/env python3
"""Export an HTML wireframe to draw.io, and read the user's draw.io annotations back.

Usage:
    python wireframe2drawio.py FILE.html [--out DIR] [--labels] [--browser NAME]
    python wireframe2drawio.py FILE.html --read-notes [--json]
    python wireframe2drawio.py FILE.generated.drawio --read-notes [--json]

Export writes two files next to the HTML (or into --out):
    <name>.generated.drawio   one page per size x state ("mobile / ready" ...), layers
                              "wireframe" (locked), "標註" and "我的註記"
    <name>.tree.txt           the layout tree
Everything is regenerated on every run except the cells on the "我的註記" layer, which are
carried over (matched by page name). Arrows keep pointing at the same data-id.
Warnings are rule violations in the HTML; fix them there.

--read-notes lists every note, sticky, text and arrow on the "我的註記" layer, with the
data-ids it covers or points at. It needs only Python. Export needs Python 3.9+ and
Playwright: pip install playwright && playwright install chromium
"""
import argparse
import base64
import copy
import html
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

ORIGIN_X, ORIGIN_Y = 40, 70
NOTES_W = 280
LAYER_WIRE, LAYER_ANN, LAYER_MINE = "_layer-wireframe", "_layer-annotation", "_layer-notes"
NAME_WIRE, NAME_ANN, NAME_MINE = "wireframe", "標註", "我的註記"
LINE_COLOR = "#9a9a9a"

# Base style per shape. The mxgraph.mockup.* strings come from draw.io's own palette
# (Sidebar-Mockup.js) with colours made grey. references/drawio-map.md lists the same
# names; keep the two in sync. Colours, fonts and wrapping are appended per cell, and a
# key that appears later in a style string wins.
STYLES = {
    "frame": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;",
    "box": "rounded=0;whiteSpace=wrap;html=1;",
    "rule": "rounded=0;html=1;strokeColor=none;",
    "text": "text;html=1;strokeColor=none;fillColor=none;spacing=0;",
    "button": "html=1;shadow=0;dashed=0;align=center;strokeWidth=1;shape=mxgraph.mockup.buttons.button;mainText=;buttonStyle=round;whiteSpace=wrap;",
    "textbox": "html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.text.textBox;strokeColor=#999999;mainText=;align=left;spacingLeft=4;whiteSpace=wrap;",
    "search": "html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.searchBox;strokeColor=#999999;mainText=;strokeColor2=#666666;align=left;spacingLeft=3;whiteSpace=wrap;",
    "password": "html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.pwField;strokeColor=#999999;mainText=;align=left;spacingLeft=3;",
    "select": "html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.comboBox;strokeColor=#999999;fillColor=#f0f0f0;fillColor2=#cccccc;mainText=;align=left;spacingLeft=4;",
    "checkbox": "html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.rrect;rSize=0;fillColor=#eeeeee;strokeColor=#999999;gradientColor=#cccccc;",
    "checkbox-on": "html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.forms.checkbox;fillColor=#aaaaaa;gradientColor=#666666;strokeColor=#444444;",
    "radio": "html=1;shadow=0;shape=ellipse;fillColor=#eeeeee;strokeColor=#999999;gradientColor=#cccccc;",
    "radio-on": "html=1;shadow=0;shape=ellipse;fillColor=#aaaaaa;gradientColor=#666666;strokeColor=#444444;",
    "radio-dot": "html=1;shape=ellipse;fillColor=#444444;strokeColor=none;",
    "image": "html=1;shadow=0;dashed=0;strokeWidth=1;shape=mxgraph.mockup.graphics.simpleIcon;strokeColor=#999999;fillColor=#eeeeee;",
    "icon": "ellipse;whiteSpace=wrap;html=1;fillColor=#cccccc;strokeColor=#999999;",
    "skeleton": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e2e2e2;strokeColor=none;",
    "chip": "rounded=1;arcSize=50;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacing=0;",
    "unsupported": "rounded=0;whiteSpace=wrap;html=1;dashed=1;fillColor=none;strokeColor=#d4380d;fontColor=#d4380d;fontSize=11;",
    "badge": "ellipse;whiteSpace=wrap;html=1;fillColor=#d4380d;strokeColor=#ffffff;fontColor=#ffffff;fontSize=10;fontStyle=1;spacing=0;",
    "title": "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#333333;",
    "notes": "text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacing=6;fontSize=11;fontColor=#333333;strokeColor=#d4380d;fillColor=#fff8f0;",
    "id-label": "text;html=1;fontSize=8;fontColor=#8a8a8a;align=left;verticalAlign=top;spacing=0;strokeColor=none;fillColor=none;",
}

EXTRACT_JS = r"""
(sizeName) => {
  const screen = WF.frame(sizeName);
  const sr = screen.getBoundingClientRect();
  const warnings = [];
  const SKIP = new Set(['script', 'style', 'template', 'link', 'meta', 'title', 'noscript', 'option', 'optgroup']);
  const UNSUPPORTED = new Set(['img', 'svg', 'canvas', 'video', 'audio', 'iframe', 'object', 'embed', 'picture']);
  const INPUT_OK = new Set(['text', 'search', 'email', 'url', 'tel', 'number', 'password', 'checkbox', 'radio', 'date', 'time', 'datetime-local', 'month', 'week']);
  const seen = new Map();
  const rgb = (c) => {
    const m = c && c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);
    if (p.length > 3 && p[3] === 0) return null;
    return '#' + p.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
  };
  const warn = (rule, msg, el) => warnings.push({ rule, msg, where: (el.dataset && el.dataset.id) || el.localName });
  const walk = (el) => {
    const tag = el.localName;
    if (SKIP.has(tag) || el.hidden) return [];
    const cs = getComputedStyle(el);
    if (cs.display === 'none') return [];
    const kids = [...el.children].filter((k) => k.localName !== 'br');
    const kidNodes = kids.flatMap(walk);
    if (cs.display === 'contents') return kidNodes;
    const r = el.getBoundingClientRect();
    if (r.width < 0.5 && r.height < 0.5) return kidNodes;
    const id = el.dataset.id || null;
    if (id) { seen.set(id, (seen.get(id) || 0) + 1); if (seen.get(id) === 2) warn('data-id', 'data-id "' + id + '" is used more than once', el); }
    if (['absolute', 'fixed', 'sticky'].includes(cs.position)) warn('position', 'position:' + cs.position + ' is not measured faithfully', el);
    if (cs.transform !== 'none') warn('transform', 'transform is not carried to draw.io', el);
    if (cs.backgroundImage !== 'none') warn('background-image', 'background image is not carried to draw.io', el);
    const unsupported = UNSUPPORTED.has(tag) || (tag === 'input' && !INPUT_OK.has(el.type));
    if (unsupported) warn('unsupported', '<' + tag + (tag === 'input' ? ' type=' + el.type : '') + '> has no draw.io shape; drawn as a dashed box', el);
    const hasEl = kids.length > 0 && tag !== 'select';
    const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join('').trim();
    let text = '';
    if (tag === 'select') { const o = el.options[el.selectedIndex]; text = o ? o.textContent.trim() : ''; }
    else if (tag === 'textarea') { text = el.value.trim(); }
    else if (tag === 'input') { text = el.type === 'password' ? '•'.repeat((el.value || '').length || 6) : (el.getAttribute('value') !== null ? el.value : (el.placeholder || '')); }
    else if (!hasEl) {
      text = [...el.childNodes].map((n) => (n.nodeType === 3 ? n.textContent.replace(/\s+/g, ' ') : n.localName === 'br' ? '\n' : '')).join('').replace(/ *\n */g, '\n').trim();
    } else if (own) warn('text-mixed', 'text mixed with child elements is not exported: "' + own.slice(0, 30) + '"', el);
    const side = (k) => parseFloat(cs['border' + k + 'Width']) > 0 && !['none', 'hidden'].includes(cs['border' + k + 'Style']);
    const sides = ['Top', 'Right', 'Bottom', 'Left'].map(side);
    const bcol = ['Top', 'Right', 'Bottom', 'Left'].map((k, i) => (sides[i] ? rgb(cs['border' + k + 'Color']) : null)).find(Boolean) || null;
    const fs = parseFloat(cs.fontSize);
    const lh = parseFloat(cs.lineHeight) || fs * 1.2;
    const align = cs.textAlign === 'start' ? 'left' : cs.textAlign === 'end' ? 'right' : cs.textAlign;
    const pl = parseFloat(cs.paddingLeft), pr = parseFloat(cs.paddingRight), pt = parseFloat(cs.paddingTop), pb = parseFloat(cs.paddingBottom);
    return [{
      tag, id, cls: [...el.classList], x: r.left - sr.left, y: r.top - sr.top, w: r.width, h: r.height,
      text, type: el.type || '', checked: el.checked === true, disabled: el.disabled === true,
      pressed: el.getAttribute('aria-pressed') === 'true' || el.getAttribute('aria-selected') === 'true' || ['true', 'page'].includes(el.getAttribute('aria-current')) || el.classList.contains('primary'),
      empty: tag === 'input' && el.getAttribute('value') === null,
      notes: el.dataset.note ? el.dataset.note.split(/\s+/).filter(Boolean) : [],
      unsupported,
      st: { color: rgb(cs.color) || '#222222', bg: rgb(cs.backgroundColor), border: bcol, sides, fs, bold: parseInt(cs.fontWeight, 10) >= 600,
            italic: cs.fontStyle === 'italic', underline: (cs.textDecorationLine || '').includes('underline'), align, pl, pr, pt, pb,
            lines: Math.max(1, Math.round((r.height - pt - pb) / lh)) },
      children: kidNodes,
    }];
  };
  const nodes = [...screen.children].flatMap(walk);
  const notes = [...document.querySelectorAll('#notes li')].map((li) => ({ n: li.dataset.note || '', kind: li.dataset.kind || '', text: li.textContent.replace(/\s+/g, ' ').trim() }));
  return { w: sr.width, h: sr.height, nodes, warnings, notes };
}
"""


# ---------------------------------------------------------------- helpers

def fmt(v):
    v = round(float(v), 1)
    return ("%g" % v) if v != int(v) else str(int(v))


def lab(text):
    return html.escape(text, quote=False).replace("\n", "<br>")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def vertex(cid, value, style, x, y, w, h, parent):
    c = ET.Element("mxCell", {"id": cid, "value": value, "style": style, "vertex": "1", "parent": parent})
    ET.SubElement(c, "mxGeometry", {"x": fmt(x), "y": fmt(y), "width": fmt(w), "height": fmt(h), "as": "geometry"})
    return c


def font(n, color=None):
    s = n["st"]
    style = (1 if s["bold"] else 0) | (2 if s["italic"] else 0) | (4 if s["underline"] else 0)
    return "fontFamily=Helvetica;fontSize=%d;fontColor=%s;fontStyle=%d;" % (max(8, round(s["fs"])), color or s["color"], style)


def wrap(n):
    """Single-line labels must not wrap in draw.io, whose text metrics differ slightly."""
    return "whiteSpace=nowrap;" if n["st"]["lines"] <= 1 else "whiteSpace=wrap;"


def spacing(n):
    s = n["st"]
    return "spacingLeft=%d;spacingRight=%d;spacingTop=%d;spacingBottom=%d;" % (round(s["pl"]), round(s["pr"]), round(s["pt"]), round(s["pb"]))


# ---------------------------------------------------------------- HTML -> cells

class PageBuilder:
    def __init__(self, name, data, labels=False, origin=(ORIGIN_X, ORIGIN_Y)):
        self.name, self.data, self.labels = name, data, labels
        self.ox, self.oy = origin
        self.wire, self.ann = [], []
        self.ids = set(["0", LAYER_WIRE, LAYER_ANN, LAYER_MINE, "_frame", "_title", "_notes-list"])
        self.counters = {}
        self.warnings = []

    def unique(self, cid):
        base, k = cid, 1
        while cid in self.ids:
            k += 1
            cid = "%s~dup%d" % (base, k)
        if cid != base:
            self.warnings.append(("data-id", 'id "%s" collides; used "%s"' % (base, cid), base))
        self.ids.add(cid)
        return cid

    def cell_id(self, n, parent_cid):
        if n["id"]:
            return self.unique(n["id"])
        key = (parent_cid, n["tag"])
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.unique("%s~%s%d" % (parent_cid or "root", n["tag"], self.counters[key]))

    def add(self, cid, value, style, x, y, w, h, layer=None):
        (self.ann if layer == "ann" else self.wire).append(
            vertex(cid, value, style, x, y, w, h, LAYER_ANN if layer == "ann" else LAYER_WIRE))

    def rule_lines(self, cid, n, x, y, w, h):
        sides = n["st"]["sides"]
        col = n["st"]["border"] or LINE_COLOR
        spec = [(0, x, y, w, 1), (1, x + w - 1, y, 1, h), (2, x, y + h - 1, w, 1), (3, x, y, 1, h)]
        for i, lx, ly, lw, lh in spec:
            if sides[i]:
                self.add("%s~b%d" % (cid, i), "", STYLES["rule"] + "fillColor=%s;" % col, lx, ly, lw, lh)

    def emit(self, n, parent_cid=None):
        cid = self.cell_id(n, parent_cid)
        s = n["st"]
        x, y, w, h = self.ox + n["x"], self.oy + n["y"], n["w"], n["h"]
        tag, cls, text = n["tag"], set(n["cls"]), n["text"]
        full, partial = all(s["sides"]), any(s["sides"]) and not all(s["sides"])
        bg = s["bg"] if s["bg"] not in (None, "#ffffff") else None
        stroke = s["border"] or LINE_COLOR
        draw_children = True

        if n["unsupported"]:
            self.add(cid, lab("<%s>" % tag if not text else text), STYLES["unsupported"], x, y, w, h)
        elif tag == "hr":
            self.add(cid, "", STYLES["rule"] + "fillColor=%s;" % stroke, x, y, w, max(1, h))
        elif tag == "input" and n["type"] in ("checkbox", "radio"):
            self.checkbox_or_radio(cid, n, x, y, w, h)
        elif tag == "input" and n["type"] == "search":
            self.add(cid, lab(text), STYLES["search"] + font(n, "#888888" if n["empty"] else "#333333") + wrap(n), x, y, w, h)
        elif tag == "input" and n["type"] == "password":
            self.add(cid, lab(text), STYLES["password"] + font(n, "#666666"), x, y, w, h)
        elif tag == "input":
            self.add(cid, lab(text), STYLES["textbox"] + "verticalAlign=middle;" + font(n, "#888888" if n["empty"] else "#333333") + wrap(n), x, y, w, h)
        elif tag == "textarea":
            self.add(cid, lab(text), STYLES["textbox"] + "verticalAlign=top;spacingTop=%d;" % round(s["pt"]) + font(n, "#333333"), x, y, w, h)
        elif tag == "select":
            self.add(cid, lab(text), STYLES["select"] + font(n, "#333333") + wrap(n), x, y, w, h)
        elif "img" in cls:
            self.add(cid, "", STYLES["image"], x, y, w, h)
        elif "icon" in cls:
            self.add(cid, "", STYLES["icon"], x, y, w, h)
        elif "skel" in cls:
            self.add(cid, "", STYLES["skeleton"] + "arcSize=%d;" % (50 if h <= 16 else 8), x, y, w, h)
        elif "chip" in cls:
            dark = n["pressed"]
            self.add(cid, lab(text), STYLES["chip"] + "fillColor=%s;strokeColor=%s;" % ("#333333" if dark else "#ffffff", "#333333" if dark else stroke) + font(n, "#ffffff" if dark else None) + wrap(n), x, y, w, h)
            draw_children = not text
        elif tag == "button":
            dark, off = n["pressed"], n["disabled"]
            fill, line, fc = ("#333333", "#333333", "#ffffff") if dark else (("#eeeeee", "#bbbbbb", "#999999") if off else ("#ffffff", "#666666", "#222222"))
            self.add(cid, lab(text), STYLES["button"] + "strokeColor=%s;fillColor=%s;" % (line, fill) + font(n, fc) + wrap(n), x, y, w, h)
        else:
            has_text = bool(text) and not n["children"]
            if full or bg:
                st = STYLES["box"] + "fillColor=%s;strokeColor=%s;" % (bg or "none", stroke if full else "none")
                if has_text:
                    st += "align=%s;verticalAlign=middle;" % (s["align"] if s["align"] in ("left", "center", "right") else "left") + spacing(n) + font(n) + wrap(n)
                self.add(cid, lab(text) if has_text else "", st, x, y, w, h)
            elif has_text:
                self.text_cell(cid, n, x, y, w, h)
            elif n["id"] and n["children"]:
                self.add(cid, "", STYLES["box"] + "fillColor=none;strokeColor=none;", x, y, w, h)
            if partial:
                self.rule_lines(cid, n, x, y, w, h)
            if has_text:
                draw_children = False

        for i, num in enumerate(n["notes"]):
            self.add("_n%s~%s" % (num, cid), num, STYLES["badge"], x - 9 + i * 20, y - 9, 18, 18, "ann")
        if self.labels and n["id"] and n["children"] and w >= 60:
            self.add("_l~%s" % cid, n["id"], STYLES["id-label"], x + 2, y + 1, min(w - 4, 200), 11, "ann")
        if draw_children:
            for c in n["children"]:
                self.emit(c, cid)

    def text_cell(self, cid, n, x, y, w, h):
        s = n["st"]
        align = s["align"] if s["align"] in ("left", "center", "right") else "left"
        single = s["lines"] <= 1
        pad = 0 if single else 6
        tx = x - (pad / 2 if align == "center" else pad if align == "right" else 0)
        style = STYLES["text"] + "align=%s;verticalAlign=middle;" % align + font(n) + ("whiteSpace=nowrap;" if single else "whiteSpace=wrap;overflow=hidden;")
        self.add(cid, lab(n["text"]), style, tx, y, w + pad, h)

    def checkbox_or_radio(self, cid, n, x, y, w, h):
        on = "-on" if n["checked"] else ""
        self.add(cid, "", STYLES[n["type"] + on], x, y, w, h)
        if n["type"] == "radio" and n["checked"]:
            d = round(w * 0.6)
            self.add(cid + "~dot", "", STYLES["radio-dot"], x + (w - d) / 2, y + (h - d) / 2, d, d)

    def build(self, existing_notes, notes_list):
        sw, sh = self.data["w"], self.data["h"]
        self.wire.append(vertex("_frame", "", STYLES["frame"], self.ox, self.oy, sw, sh, LAYER_WIRE))
        for n in self.data["nodes"]:
            self.emit(n, None)
        self.ann.append(vertex("_title", "%s · %dpx" % (self.name, round(sw)), STYLES["title"], self.ox, 30, 400, 24, LAYER_ANN))
        if notes_list:
            body, height = [], 12
            for item in notes_list:
                tag = {"question": " (open question)", "assumption": " (assumption)"}.get(item["kind"], "")
                body.append("<b>%s</b>%s %s" % (html.escape(item["n"]), html.escape(tag), html.escape(item["text"])))
                height += max(1, -(-len(item["text"] + tag) // 40)) * 14 + 6
            self.ann.append(vertex("_notes-list", "<br>".join(body), STYLES["notes"], self.ox + sw + 40, self.oy, NOTES_W, height, LAYER_ANN))
        mine = [] if not existing_notes else [copy.deepcopy(e) for e in existing_notes]
        for e in mine:
            for c in e.iter("mxCell"):
                if c.get("parent") == "__layer__":
                    c.set("parent", LAYER_MINE)
        # dangling references on user cells
        all_ids = set(self.ids)
        for e in mine:
            all_ids.add(e.get("id"))
        for e in mine:
            c = e if e.tag == "mxCell" else e.find("mxCell")
            for attr in ("source", "target"):
                if c is not None and c.get(attr) and c.get(attr) not in all_ids:
                    self.warnings.append(("notes", 'your note "%s" pointed at "%s", which no longer exists on page "%s"; the arrow end is now free' % (e.get("id"), c.get(attr), self.name), e.get("id")))
                    del c.attrib[attr]
        pw = self.ox + sw + 40 + NOTES_W + 40
        ph = self.oy + sh + 60
        model = ET.Element("mxGraphModel", {"dx": "1400", "dy": "800", "grid": "1", "gridSize": "10", "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(int(pw)), "pageHeight": str(int(ph)), "math": "0", "shadow": "0"})
        root = ET.SubElement(model, "root")
        ET.SubElement(root, "mxCell", {"id": "0"})
        ET.SubElement(root, "mxCell", {"id": LAYER_WIRE, "value": NAME_WIRE, "style": "locked=1;", "parent": "0"})
        ET.SubElement(root, "mxCell", {"id": LAYER_ANN, "value": NAME_ANN, "parent": "0"})
        ET.SubElement(root, "mxCell", {"id": LAYER_MINE, "value": NAME_MINE, "parent": "0"})
        for c in self.wire + self.ann + mine:
            root.append(c)
        return model


# ---------------------------------------------------------------- draw.io files

def decode_diagram(d):
    """Return the mxGraphModel element of a <diagram>, compressed or not."""
    m = d.find("mxGraphModel")
    if m is not None:
        return m
    text = (d.text or "").strip()
    if not text:
        return None
    raw = zlib.decompress(base64.b64decode(text), -15)
    return ET.fromstring(urllib.parse.unquote(raw.decode("utf-8")))


def read_diagrams(path):
    tree = ET.parse(path)
    root = tree.getroot()
    diagrams = [root] if root.tag == "diagram" else root.findall("diagram")
    out = []
    for d in diagrams:
        model = decode_diagram(d)
        if model is not None:
            out.append((d.get("name") or d.get("id") or "page", model))
    return out


def cells_of(model):
    """Normalised cells: dicts with id, outer element, mxCell, parent, value."""
    out = []
    for el in model.find("root"):
        if el.tag == "mxCell":
            cell = el
            value = el.get("value", "")
        elif el.tag in ("object", "UserObject"):
            cell = el.find("mxCell")
            if cell is None:
                continue
            value = el.get("label", "")
        else:
            continue
        out.append({"id": el.get("id"), "el": el, "cell": cell, "parent": cell.get("parent"), "value": value})
    return out


def layers_of(cells):
    wire = mine = None
    for c in cells:
        if c["parent"] == "0":
            if c["value"] == NAME_MINE or c["id"] == LAYER_MINE:
                mine = c
            elif c["value"] == NAME_WIRE or c["id"] == LAYER_WIRE:
                wire = c
    return wire, mine


def user_cells(cells, mine):
    if mine is None:
        return []
    keep, ids = [], {mine["id"]}
    changed = True
    while changed:
        changed = False
        for c in cells:
            if c["id"] not in ids and c["parent"] in ids:
                ids.add(c["id"])
                keep.append(c)
                changed = True
    return keep


def load_existing_notes(path):
    notes = {}
    for name, model in read_diagrams(path):
        cells = cells_of(model)
        _, mine = layers_of(cells)
        els = []
        for c in user_cells(cells, mine):
            el = copy.deepcopy(c["el"])
            inner = el if el.tag == "mxCell" else el.find("mxCell")
            if c["parent"] == mine["id"]:
                inner.set("parent", "__layer__")
            els.append(el)
        if els:
            notes[name] = els
    return notes


# ---------------------------------------------------------------- tree

def tree_lines(nodes, prefix=""):
    lines = []
    for i, n in enumerate(nodes):
        last = i == len(nodes) - 1
        name = n["id"] or "·"
        cls = "".join("." + c for c in n["cls"][:3])
        bits = ["%s  <%s%s>  %d×%d" % (name, n["tag"], cls, round(n["w"]), round(n["h"]))]
        if n["text"] and not n["children"]:
            t = n["text"].replace("\n", " ")
            bits.append('"%s"' % (t if len(t) <= 48 else t[:45] + "..."))
        if n["notes"]:
            bits.append("[note %s]" % ",".join(n["notes"]))
        lines.append(prefix + ("└─ " if last else "├─ ") + "  ".join(bits))
        lines += tree_lines(n["children"], prefix + ("   " if last else "│  "))
    return lines


# ---------------------------------------------------------------- export

def find_browser(p, name):
    order = [name] if name else ["chromium", "chrome", "msedge"]
    errors = []
    for n in order:
        try:
            return p.chromium.launch() if n == "chromium" else p.chromium.launch(channel=n)
        except Exception as e:  # noqa: BLE001
            errors.append("%s: %s" % (n, str(e).splitlines()[0]))
    sys.exit("could not start a browser (%s). Run: playwright install chromium" % "; ".join(errors))


def export(html_path, out_dir, labels, browser_name):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright is missing. Run: pip install playwright && playwright install chromium")
    src = Path(html_path)
    out_dir = Path(out_dir) if out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    drawio_path = out_dir / (src.stem + ".generated.drawio")
    tree_path = out_dir / (src.stem + ".tree.txt")
    existing = {}
    if drawio_path.exists():
        try:
            existing = load_existing_notes(drawio_path)
        except Exception as e:  # noqa: BLE001
            sys.exit("could not read the existing %s (%s); move it away or fix it, your notes are not touched" % (drawio_path.name, e))
    pages, warnings, views = [], [], []
    with sync_playwright() as p:
        browser = find_browser(p, browser_name)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.goto(src.resolve().as_uri())
        try:
            page.wait_for_function("window.WF && WF.ready", timeout=5000)
        except Exception:  # noqa: BLE001
            browser.close()
            sys.exit("the page did not start (window.WF missing); is it made from assets/template.html?")
        page.evaluate("document.fonts.ready")
        states = page.evaluate("WF.states")
        sizes = list(page.evaluate("WF.sizes").keys())
        page.evaluate("WF.setSize('both')")
        for state in states:
            page.evaluate("(s) => WF.setState(s)", state)
            for size in sizes:
                views.append((size, state, page.evaluate(EXTRACT_JS, size)))
        browser.close()
    mxfile = ET.Element("mxfile", {"host": "wireframe2drawio", "agent": "wireframe2drawio.py", "version": "1"})
    used = set()
    total_cells = 0
    tree_out = ["# %s" % src.name, "# layout tree; ids are data-id, · marks an element without one", ""]
    first_tree = {}
    for size, state, data in views:
        name = "%s / %s" % (size, state)
        b = PageBuilder(name, data, labels)
        model = b.build(existing.pop(name, None), data["notes"])
        for rule, msg, where in b.warnings:
            warnings.append((rule, msg, where))
        for w in data["warnings"]:
            warnings.append((w["rule"], w["msg"], w["where"]))
        did = slug(name)
        while did in used:
            did += "-x"
        used.add(did)
        d = ET.SubElement(mxfile, "diagram", {"id": did, "name": name})
        d.append(model)
        total_cells += len(b.wire) + len(b.ann)
        body = tree_lines(data["nodes"])
        text = "\n".join(body)
        tree_out.append("## %s  (%d×%d)" % (name, round(data["w"]), round(data["h"])))
        if text in first_tree:
            tree_out.append("(same as %s)" % first_tree[text])
        else:
            first_tree[text] = name
            tree_out += body
        tree_out.append("")
    for name, els in existing.items():
        warnings.append(("notes", 'page "%s" no longer exists; %d of your note cell(s) on it were dropped' % (name, len(els)), name))
    ET.indent(mxfile, space=" ")
    ET.ElementTree(mxfile).write(drawio_path, encoding="utf-8", xml_declaration=False)
    tree_path.write_text("\n".join(tree_out), encoding="utf-8")
    seen = set()
    for rule, msg, where in warnings:
        key = (rule, msg, where)
        if key not in seen:
            seen.add(key)
            print("WARN  %-15s %s  (%s)" % (rule, msg, where))
    print("wrote %s (%d pages, %d cells) and %s; %d warning(s)" % (drawio_path, len(views), total_cells, tree_path.name, len(seen)))


# ---------------------------------------------------------------- read notes

def strip_html(s):
    s = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", s or "", flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def style_info(style):
    d, flags = {}, set()
    for tok in (style or "").split(";"):
        if not tok:
            continue
        if "=" in tok:
            k, v = tok.split("=", 1)
            d[k] = v
        else:
            flags.add(tok)
    return d, flags


def kind_of(c):
    cell = c["cell"]
    d, flags = style_info(cell.get("style"))
    if cell.get("edge") == "1":
        return "arrow"
    if "stickyNote" in (cell.get("style") or "") or "note" in flags or d.get("shape") in ("note", "note2"):
        return "sticky"
    if "text" in flags or d.get("shape") == "text":
        return "text"
    return "shape"


def geom_of(c, by_id, layer_ids):
    g = c["cell"].find("mxGeometry")
    if g is None:
        return None
    x, y = float(g.get("x", 0)), float(g.get("y", 0))
    w, h = float(g.get("width", 0)), float(g.get("height", 0))
    p = by_id.get(c["parent"])
    while p is not None and p["id"] not in layer_ids:
        pg = p["cell"].find("mxGeometry")
        if pg is not None:
            x += float(pg.get("x", 0))
            y += float(pg.get("y", 0))
        p = by_id.get(p["parent"])
    return x, y, w, h


def data_id(cid):
    return (cid or "").split("~")[0]


def read_notes(path, as_json):
    p = Path(path)
    if p.suffix.lower() == ".html":
        p = p.with_name(p.stem + ".generated.drawio")
    if not p.exists():
        sys.exit("not found: %s (run the export first)" % p)
    result = []
    for name, model in read_diagrams(p):
        cells = cells_of(model)
        by_id = {c["id"]: c for c in cells}
        wire, mine = layers_of(cells)
        if mine is None or wire is None:
            continue
        layer_ids = {c["id"] for c in cells if c["parent"] == "0"}
        blocks = []
        for c in cells:
            if c["parent"] == wire["id"] and c["cell"].get("vertex") == "1" and not c["id"].startswith("_"):
                g = geom_of(c, by_id, layer_ids)
                if g and g[2] > 0 and g[3] > 0:
                    blocks.append((c["id"], g))

        def smallest_at(px, py):
            best = None
            for cid, (x, y, w, h) in blocks:
                if x <= px <= x + w and y <= py <= y + h and (best is None or w * h < best[1]):
                    best = (cid, w * h)
            return data_id(best[0]) if best else None

        for c in user_cells(cells, mine):
            kind = kind_of(c)
            item = {"page": name, "id": c["id"], "kind": kind, "text": strip_html(c["value"]), "covers": [], "points_at": []}
            cell = c["cell"]
            if kind == "arrow":
                g = cell.find("mxGeometry")
                for attr, tag in (("source", "sourcePoint"), ("target", "targetPoint")):
                    ref = cell.get(attr)
                    if ref and ref in by_id and by_id[ref]["parent"] == wire["id"]:
                        item["points_at"].append(data_id(ref))
                    elif g is not None:
                        pt = next((e for e in g.findall("mxPoint") if e.get("as") == tag), None)
                        if pt is not None:
                            hit = smallest_at(float(pt.get("x", 0)), float(pt.get("y", 0)))
                            if hit and attr == "target":
                                item["points_at"].append(hit)
                            elif hit and attr == "source":
                                item["from"] = hit
                item["points_at"] = sorted(set(item["points_at"]) - {None})
            else:
                g = geom_of(c, by_id, layer_ids)
                if g:
                    nx, ny, nw, nh = g
                    inside = [(cid, bg) for cid, bg in blocks if bg[0] >= nx - 2 and bg[1] >= ny - 2 and bg[0] + bg[2] <= nx + nw + 2 and bg[1] + bg[3] <= ny + nh + 2 and cid != "_frame"]
                    inside = [(cid, bg) for cid, bg in inside if not any(o != cid and bo[2] * bo[3] > bg[2] * bg[3] and bo[0] <= bg[0] + 1 and bo[1] <= bg[1] + 1 and bo[0] + bo[2] >= bg[0] + bg[2] - 1 and bo[1] + bo[3] >= bg[1] + bg[3] - 1 for o, bo in inside)]
                    ids = [data_id(cid) for cid, _ in inside]
                    if not ids:
                        hit = smallest_at(nx + nw / 2, ny + nh / 2)
                        ids = [hit] if hit else []
                    item["covers"] = sorted(set(i for i in ids if i), key=ids.index)
            result.append(item)
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if not result:
        print("no notes on the '%s' layer of %s" % (NAME_MINE, p.name))
        return
    page = None
    for it in result:
        if it["page"] != page:
            page = it["page"]
            print("\n== %s" % page)
        head = '[%s] %s' % (it["id"], it["kind"])
        if it["text"]:
            head += '  "%s"' % it["text"].replace("\n", " / ")
        print(head)
        if it["covers"]:
            print("    covers:    " + ", ".join(it["covers"]))
        if it["points_at"]:
            print("    points at: " + ", ".join(it["points_at"]) + ("   (from %s)" % it["from"] if it.get("from") else ""))
        if it["kind"] == "arrow" and not it["points_at"]:
            print("    points at: (nothing on the wireframe)")
        if it["kind"] != "arrow" and not it["covers"]:
            print("    covers:    (nothing on the wireframe)")
    print("\n%d note(s) on %d page(s)" % (len(result), len({r["page"] for r in result})))


def main():
    ap = argparse.ArgumentParser(description="Export an HTML wireframe to draw.io, or read draw.io notes.")
    ap.add_argument("file", help=".html wireframe (or .drawio with --read-notes)")
    ap.add_argument("--read-notes", action="store_true", help="list the notes on the '我的註記' layer")
    ap.add_argument("--json", action="store_true", help="with --read-notes: print JSON")
    ap.add_argument("--out", metavar="DIR", help="write the outputs here instead of next to the HTML")
    ap.add_argument("--labels", action="store_true", help="draw small data-id labels on container blocks (標註 layer)")
    ap.add_argument("--browser", choices=["chromium", "chrome", "msedge"], help="browser to use (default: try all)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if not Path(a.file).exists():
        sys.exit("file not found: %s" % a.file)
    if a.read_notes:
        read_notes(a.file, a.json)
    else:
        if Path(a.file).suffix.lower() != ".html":
            sys.exit("export needs the .html wireframe; use --read-notes for a .drawio file")
        export(a.file, a.out, a.labels, a.browser)


if __name__ == "__main__":
    main()
